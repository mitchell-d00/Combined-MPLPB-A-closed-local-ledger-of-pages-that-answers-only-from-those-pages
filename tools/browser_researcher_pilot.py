"""One fictional researcher's actual UI journey in a disposable Chromium context.

Called by the existing candidate/postdeploy smoke. No personal browser storage,
external source fetching, simulated DOM, model calls, or human usability score.
"""
import json
from tools.evaluate_researcher_pilot import load_suite, DEFAULT_SUITE


def verify(page):
    from playwright.sync_api import expect
    suite, suite_sha = load_suite(DEFAULT_SUITE)
    npc = suite['journeys'][0]
    checks = []

    def checked(name):
        checks.append(name)

    def open_import():
        container = page.locator('details').filter(has=page.locator('#collection-form')).first
        if not container.get_attribute('open') and not container.evaluate('(el) => el.open'):
            container.locator('summary').first.click()

    # Create and import through visible controls, rather than preloading API
    # state. Fictional public URLs are labels; source text is pasted locally.
    page.locator('[data-view="chat"]').first.click()
    page.locator('#chat-auto-wiki').set_checked(False)
    open_import()
    name = 'NPC '+npc['persona']['name']+' full investigation'
    page.locator('#collection-name').fill(name)
    page.locator('#collection-form button[type="submit"]').click()
    expect(page.locator('#collection-status')).to_contain_text('Created '+name, timeout=60000)
    corpus = page.locator('#corpus').input_value()
    if not corpus.startswith('mind-'):
        raise AssertionError('NPC collection was not selected')
    checked('create_collection_through_ui')

    def import_doc(doc):
        open_import()
        page.locator('#source-title').fill(doc['title'])
        page.locator('#source-url').fill(doc['url'])
        page.locator('#source-text').fill(doc['text'])
        page.locator('#source-form button[type="submit"]').click()
        expect(page.locator('#collection-status')).to_contain_text('Saved '+doc['title'], timeout=60000)

    import_doc(npc['documents'][0])
    checked('paste_import_through_ui')

    def ask(question):
        page.locator('[data-view="ask"]').first.click()
        page.locator('#ask-reader-mode').select_option('supported')
        page.locator('#question').fill(question)
        page.locator('#ask-button').click()
        expect(page.locator('#ask-button')).to_be_enabled(timeout=60000)

    question = npc['questions'][1]['question']
    ask(question)
    expect(page.locator('#results .outcome')).to_have_text('SUPPORTED ANSWER', timeout=60000)
    page.locator('#results [data-page]').first.click()
    expect(page.locator('#page-dialog')).to_be_visible()
    expect(page.locator('#page-content .page-text')).to_contain_text(npc['questions'][1]['gold_quotes'][0])
    page.locator('#close-dialog').click()
    checked('ask_and_click_cited_source')

    ask(npc['questions'][2]['question'])
    expect(page.locator('#results .outcome')).not_to_have_text('SUPPORTED ANSWER')
    checked('known_reader_limit_is_not_an_answer')
    # A failed answerable question is retained as a coverage gap, never called
    # correct merely because the refusal control passed.
    page.locator('[data-view="chat"]').first.click()
    import_doc(npc['conflict'])
    ask(npc['conflict']['question'])
    expect(page.locator('#results .outcome')).to_have_text('AMBIGUOUS', timeout=60000)
    checked('conflicting_bulletins_do_not_choose_a_winner')
    page.locator('[data-view="chat"]').first.click()
    page.locator('#chat-input').fill('remember '+npc['note'])
    page.locator('#chat-send').click()
    expect(page.locator('#chat-send')).to_be_enabled(timeout=60000)
    expect(page.locator('#chat-messages .assistant-message').last).to_contain_text('Saved as your declaration')
    storage_key = page.evaluate("document.getElementById('mplpb-runtime-bundle') ? 'mplpb-browser-session-id' : 'mplpb-session-id'")
    sid = page.evaluate('(key) => localStorage.getItem(key)', storage_key)
    if not sid:
        raise AssertionError('NPC chat was not saved')
    checked('save_multisentence_investigation_note')

    def api(method, *args):
        result = page.evaluate('async ([m,a]) => await MPLPB[m](...a)', [method, args])
        if not result['ok']:
            raise AssertionError('NPC browser API failed: '+str(result))
        return result['data']

    before = api('exportChat', sid)
    page.reload(wait_until='domcontentloaded')
    page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden", timeout=150000)
    resumed = api('resumeChat', sid)
    if not resumed['chain_intact'] or npc['note'] not in resumed['notes'] or api('exportChat', sid) != before:
        raise AssertionError('NPC investigation changed or disappeared after reload')
    checked('indexeddb_reload_preserves_note_and_exact_transcript')
    repeated = api('query', npc['conflict']['question'], {'corpus': corpus})['reader']
    if repeated.get('answer_contract', {}).get('kind') != 'conflict':
        raise AssertionError('Fresh query after resume lost the disagreement')
    checked('resume_rechecks_sources')
    return {'schema': 'mplpb-researcher-browser-pilot-v1', 'suite_sha256': suite_sha,
            'persona': npc['id'], 'actual_browser': 'Chromium with running application engine',
            'checks_passed': checks, 'status': 'synthetic_ui_workflow_passed',
            'known_answerable_refusals': 1, 'human_usability_measured': False,
            'product_backup_or_upgrade_tested': False,
            'notice': 'One scripted persona, developer-inspected controls; not six browser users or a human pilot.'}


def main():
    import argparse
    from pathlib import Path
    from playwright.sync_api import sync_playwright
    from tools.browser_release_smoke import preview_server
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview-dir', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Choose a new browser pilot report path')
    with preview_server(args.preview_dir) as url, sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel='chrome', headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        except Exception:
            browser = playwright.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context()
        try:
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda exc: errors.append(str(exc)))
            page.goto(url, wait_until='domcontentloaded', timeout=120000)
            page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden", timeout=150000)
            report = verify(page)
            if errors:
                raise AssertionError('Browser errors: '+str(errors))
        finally:
            context.close(); browser.close()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
