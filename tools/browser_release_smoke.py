"""Chromium end-to-end smoke for the existing live site and a candidate build.

Runs actual JavaScript / Pyodide from the GitHub Pages origin and from the
locally served preview. It never writes to the published site or any shared
browser profile. Each run uses a fresh, isolated browser context.
"""
import argparse
import json
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from threading import Thread

from playwright.sync_api import expect, sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@contextmanager
def preview_server(directory):
    handler = partial(SimpleHTTPRequestHandler, directory=str(Path(directory).resolve()))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield "http://127.0.0.1:%s/" % server.server_port
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


def verify(page, url, updated):
    errors = []
    npc_report = None
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    print("BROWSER LOAD", "candidate-preview" if updated else "published-live", url, flush=True)
    page.goto(url, wait_until="domcontentloaded", timeout=120000)
    page.wait_for_function(
        "() => document.querySelector('#workspace') && "
        "!document.querySelector('#workspace').hidden",
        timeout=150000)
    assert page.locator("#corpus option").count() >= 3, "corpus picker not populated"
    assert page.evaluate("() => typeof window.MPLPB === 'object'"), "public API not initialized"

    page.locator("[data-view='ask']").first.click()
    page.locator("#corpus").select_option("studio")
    page.locator("#question").fill("What is the glaze firing schedule to cone 04?")
    if updated:
        page.locator("#ask-reader-mode").select_option("supported")
    page.locator("#ask-button").click()
    page.locator("#results .outcome").wait_for(timeout=60000)
    outcome = page.locator("#results .outcome").inner_text()
    assert outcome != "SUPPORTED ANSWER", "unsafe cone 04 answer in strict mode"
    print("BROWSER STRICT:", outcome, flush=True)

    if updated:
        page.locator("#ask-reader-mode").select_option("candidates")
        page.locator("#question").fill(
            "What is the glaze firing schedule for cone 6?")
        page.locator("#ask-button").click()
        page.locator("#results .outcome").wait_for(timeout=60000)
        inspection = page.locator("#results .outcome").inner_text()
        assert inspection != "SUPPORTED ANSWER", "inspection mislabeled as answer"
        assert page.locator("#query-status").inner_text().lower().find(
            "candidate inspection only") >= 0
        print("BROWSER INSPECT:", inspection, flush=True)

        # These bundled examples must open source inspection, not pretend that
        # an unsupported answer is warranted by the finite statement grammar.
        page.locator("#ask-reader-mode").select_option("supported")
        page.locator("#samples [data-sample]").first.click()
        page.wait_for_function(
            "() => document.querySelector('#ask-reader-mode')?.value === 'candidates'",
            timeout=10000)
        page.locator("#results .outcome").wait_for(timeout=60000)
        print("BROWSER SAMPLE: candidate inspection selected", flush=True)

        # A supported answer must not inherit the inspection-only caption.
        page.locator("#corpus").select_option("logic")
        page.locator("#profile").select_option("internal")
        page.locator("#ask-reader-mode").select_option("supported")
        page.locator("#question").fill("What is Dungeons and Dragons?")
        page.locator("#ask-button").click()
        expect(page.locator("#results .outcome")).to_have_text(
            "SUPPORTED ANSWER", timeout=60000)
        expect(page.locator("#results .source-notice")).to_contain_text(
            "Source evidence supporting the answer above")
        expect(page.locator("#results .source-notice")).not_to_contain_text(
            "Candidate pages for inspection only")
        page.locator("#ask-reader-mode").select_option("candidates")
        page.locator("#ask-button").click()
        expect(page.locator("#results .outcome")).to_have_text(
            "CANDIDATE ONLY", timeout=60000)
        expect(page.locator("#results .source-notice")).to_contain_text(
            "Candidate pages for inspection only")
        print("BROWSER CAPTIONS: supported and inspection notices separated", flush=True)

        from tools.browser_researcher_pilot import verify as researcher_journey
        npc_report = researcher_journey(page)
        print('NPC_BROWSER '+json.dumps(npc_report), flush=True)

        # Persist the toggle immediately, without requiring a chat submission.
        # Exercise both values and a second preference write before reload.
        page.locator("[data-view='chat']").first.click()
        for enabled in (False, True):
            page.locator("#chat-auto-wiki").set_checked(enabled)
            page.locator("#theme").select_option("dark" if not enabled else "light")
            page.reload(wait_until="domcontentloaded")
            page.wait_for_function(
                "() => document.querySelector('#workspace') && "
                "!document.querySelector('#workspace').hidden", timeout=150000)
            page.locator("[data-view='chat']").first.click()
            expect(page.locator("#chat-auto-wiki")).to_be_checked(checked=enabled)
        print("BROWSER PREFERENCES: automatic lookup off/on survives reload", flush=True)

    page.locator("[data-view='chat']").first.click()
    assert page.locator("#chat-mode-chat").count() == 1
    assert page.locator("#chat-mode-serious").count() == 1
    assert page.locator("#chat-scope").count() == 1
    page.locator("[data-view='explore']").first.click()
    assert page.locator("#page-map").count() == 1
    assert not errors, "Browser JavaScript errors: " + repr(errors)
    print("BROWSER PASS", "candidate-preview" if updated else "published-live",
          flush=True)
    return npc_report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-url", required=True)
    parser.add_argument("--preview-dir", help="Built candidate dist/ directory; omit for deployed-live-only checks")
    parser.add_argument("--live-updated", action="store_true",
                        help="Expect the proposed features on the newly deployed public site")
    parser.add_argument("--npc-report", type=Path, help="New output path for completed synthetic browser journeys")
    args = parser.parse_args()
    if args.npc_report and args.npc_report.exists():
        raise FileExistsError('Choose a new NPC report path')
    npc_reports = []
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel="chrome", headless=True,
                                                  args=["--no-sandbox", "--disable-dev-shm-usage"])
        except Exception:
            browser = playwright.chromium.launch(headless=True,
                                                  args=["--no-sandbox", "--disable-dev-shm-usage"])
        try:
            for url, updated in ((args.live_url, args.live_updated),):
                context = browser.new_context(ignore_https_errors=False)
                try:
                    result = verify(context.new_page(), url, updated)
                    if result:
                        npc_reports.append(result)
                finally:
                    context.close()
            if args.preview_dir:
                with preview_server(args.preview_dir) as url:
                    context = browser.new_context(ignore_https_errors=False)
                    try:
                        result = verify(context.new_page(), url, True)
                        if result:
                            npc_reports.append(result)
                    finally:
                        context.close()
        finally:
            browser.close()
    if args.npc_report:
        args.npc_report.parent.mkdir(parents=True, exist_ok=True)
        with args.npc_report.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps({'synthetic': True, 'journeys': npc_reports}, indent=2)+'\n')


if __name__ == "__main__":
    main()
