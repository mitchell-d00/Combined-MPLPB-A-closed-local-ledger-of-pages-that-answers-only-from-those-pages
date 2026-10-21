"""Additional real Chromium audit. Disposable contexts; no personal browser state."""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from tools.browser_release_smoke import preview_server


def call(page, method, *args):
    result = page.evaluate('async ([method,args]) => await window.MPLPB[method](...args)', [method, args])
    assert result['ok'], result
    return result['data']


def ready(page, url):
    page.goto(url, wait_until='domcontentloaded', timeout=120000)
    page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden", timeout=150000)
    call(page, 'ready')


def verify(browser, url, output, name):
    context = browser.new_context(viewport={'width': 1280, 'height': 900})
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    ready(page, url)
    runtime = page.evaluate("JSON.parse(document.querySelector('#mplpb-runtime-bundle').textContent).runtime_version")
    collection = call(page, 'createCollection', 'Disposable audit 2026-10-21')['corpus']
    call(page, 'importSource', {'corpus': collection, 'title': 'Lumen Festival',
                              'url': 'https://example.org/audit-lumen',
                              'text': 'The Lumen Festival began in 1998.'})
    q = 'When did the Lumen Festival begin?'
    answer = call(page, 'query', q, {'corpus': collection})['reader']
    assert answer['kind'] == 'return', answer
    assert '1998' in answer['text'] and answer['citation'], answer
    refused = call(page, 'query', 'When did the Other Festival begin?', {'corpus': collection})['reader']
    assert refused['kind'] != 'return', refused
    empty = call(page, 'createCollection', 'Empty audit')['corpus']
    assert call(page, 'query', q, {'corpus': empty})['reader']['kind'] != 'return'
    chat = call(page, 'chat', 'My name is Juniper', {'corpus': collection})
    sid = chat['session']
    exported = call(page, 'exportChat', sid)
    (output / (name+'-transcript.json')).write_text(json.dumps(exported, indent=2)+'\n')
    page.reload(wait_until='domcontentloaded')
    page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden", timeout=150000)
    assert call(page, 'resumeChat', sid)['chain_intact']
    restored = call(page, 'query', q, {'corpus': collection})['reader']
    assert restored['citation'] == answer['citation']
    # A new page in the same isolated origin context must restore IndexedDB too.
    page.close()
    page = context.new_page()
    ready(page, url)
    assert call(page, 'resumeChat', sid)['chain_intact']
    context.set_offline(True)
    offline = call(page, 'query', q, {'corpus': collection})['reader']
    assert offline['kind'] == 'return' and offline['citation'] == answer['citation']
    blocked = page.evaluate("async () => await MPLPB.chat('search Cat',{corpus:'logic'})")
    assert not blocked['ok'] and blocked['code'] == 'NETWORK_DISABLED', blocked
    context.set_offline(False)
    layouts = []
    for width, height in [(1280,900),(390,844),(768,1024)]:
        page.set_viewport_size({'width':width,'height':height})
        page.screenshot(path=str(output/f'{name}-{width}.png'), full_page=True)
        dimensions = page.evaluate('({width:innerWidth, scroll:document.documentElement.scrollWidth})')
        layouts.append(dimensions)
        assert dimensions['scroll'] <= width + 1, dimensions
    # Explicitly enabled external acquisition: record failures as failures, never
    # substitute a fixture for a live service. This is separate from offline gates.
    online = page.evaluate("async () => await MPLPB.chat('import Cat',{corpus:'logic',allowNetwork:true,wiki:'english'})")
    (output/(name+'-online.json')).write_text(json.dumps(online,indent=2)+'\n')
    result = dict(browser=browser.version, runtime=runtime, offline=True,
                  indexeddb_reload=True, new_page_restore=True, citations_preserved=True,
                  source_import=True, transcript_export=True, layouts=layouts,
                  online_result=online, page_errors=errors, ipad_safari_tested=False)
    (output/(name+'-browser.json')).write_text(json.dumps(result,indent=2)+'\n')
    assert not errors, errors
    context.close()
    print('AUDIT BROWSER PASS', name, flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview-dir',required=True)
    parser.add_argument('--live-url')
    parser.add_argument('--output',default='audit-browser-results')
    args=parser.parse_args()
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        try:
            browser=p.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        except Exception:
            browser=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            with preview_server(args.preview_dir) as url:
                verify(browser,url,output,'candidate')
            if args.live_url:
                verify(browser,args.live_url,output,'live')
        finally:
            browser.close()

if __name__=='__main__':main()
