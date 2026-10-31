"""Disposable Chromium check of user-built policies in an actual packaged runtime.

Wikipedia traffic is a pinned local HTTP fixture, never represented as live-site
accuracy. No publishing, deployment, personal browser profiles or model calls.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from tools.browser_release_smoke import preview_server


def verify(page, url):
    from playwright.sync_api import expect
    checks, network, errors = [], [], []
    text = 'Study registration requires a booking and two approvals unless a waiver applies.'
    updated = 'Study registration requires a booking and three approvals unless a waiver applies.'
    wiki_text = 'Acquired policy is a collection policy.\n\nAcquired policy requires a reader card and a booking.'
    sha = hashlib.sha1(wiki_text.encode()).hexdigest()
    payload = {'query': {'pages': {'42': {'pageid': 42, 'title': 'Acquired policy', 'revisions': [
        {'revid': 403, 'timestamp': '2026-10-01T00:00:00Z', 'sha1': sha,
         'slots': {'main': {'contentmodel': 'wikitext', '*': wiki_text, 'sha1': sha}}}]}}}}
    def route(request):
        target = request.request.url
        if target.startswith(url):
            return request.continue_()
        if target.startswith('https://simple.wikipedia.org/w/api.php'):
            network.append(target)
            return request.fulfill(status=200, content_type='application/json',
                                   headers={'Access-Control-Allow-Origin': '*'}, body=json.dumps(payload))
        if target.startswith(('data:', 'blob:')):
            return request.continue_()
        errors.append('Unexpected outbound destination: '+urlsplit(target).netloc)
        return request.abort()
    page.context.route('**/*', route)
    page.on('pageerror', lambda exc: errors.append(str(exc)))
    page.goto(url, wait_until='domcontentloaded', timeout=120000)
    page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden", timeout=150000)
    def call(method, *args):
        value = page.evaluate('async ([m,a]) => await MPLPB[m](...a)', [method, args])
        if not value['ok']:
            raise AssertionError(str(value))
        return value['data']
    key = call('createCollection', 'Disposable policy research')['corpus']
    source = {'corpus': key, 'title': 'Study registration', 'url': 'https://example.org/study-registration', 'text': text}
    imported = call('importSource', source)
    assert imported['collection_build']['engine_changed'] is False
    assert imported['capture']['transport'] == 'user-pasted-text'
    checks.append('import_grows_collection_not_engine')
    # Select the collection in the UI and obtain the answer through real controls.
    page.reload(wait_until='domcontentloaded')
    page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden", timeout=150000)
    page.locator('#corpus').select_option(key)
    page.locator('#profile').select_option('internal')
    page.locator('[data-view="ask"]').first.click()
    page.locator('#question').fill('What does study registration require?')
    page.locator('#ask-button').click()
    expect(page.locator('#results .outcome')).to_have_text('SUPPORTED ANSWER', timeout=60000)
    expect(page.locator('#results')).to_contain_text(text)
    expect(page.locator('#results')).to_contain_text('Next step')
    first = call('query', 'What does study registration require?', {'corpus': key})['reader']
    page.locator('#results [data-page]').first.click()
    expect(page.locator('#page-content .page-text')).to_contain_text(text)
    page.locator('#close-dialog').click()
    checks.append('ui_policy_answer_and_citation_inspection')
    call('importSource', dict(source, text=updated))
    answer = call('query', 'What is required for study registration?', {'corpus': key})['reader']
    assert answer['text'] == updated and answer['hash'] != first['hash']
    stale = page.evaluate('async ([p,k]) => await MPLPB.readPage(p,{corpus:k,profile:"internal"})', [first['path'], key])
    assert not stale['ok']
    checks.append('revision_changes_answer_and_invalidates_old_citation')
    chat = call('chat', 'remember Check the waiver. Preserve earlier policy versions.', {'corpus': key})
    sid = chat['session']; exported = call('exportChat', sid)
    page.reload(wait_until='domcontentloaded')
    page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden", timeout=150000)
    restored = call('resumeChat', sid)
    assert restored['chain_intact'] and restored['notes'] == ['Check the waiver. Preserve earlier policy versions.']
    assert call('exportChat', sid) == exported
    page.context.set_offline(True)
    assert call('query', 'What does study registration require?', {'corpus': key})['reader']['text'] == updated
    page.context.set_offline(False)
    checks.append('indexeddb_resume_and_offline_current_answer')
    denied = page.evaluate('async k => await MPLPB.chat("import Acquired policy",{corpus:k,wiki:"simple"})', key)
    assert not denied['ok'] and denied['code'] == 'NETWORK_DISABLED' and not network
    checks.append('acquisition_requires_permission')
    fetched = call('chat', 'import Acquired policy', {'corpus': key, 'wiki': 'simple', 'allowNetwork': True})
    assert fetched['response']['kind'] == 'import' and network
    acquired = call('query', 'What does acquired policy require?', {'corpus': fetched['corpus']})['reader']
    assert acquired['text'] == 'Acquired policy requires a reader card and a booking.'
    checks.append('permitted_fixture_acquisition_builds_answerable_source')
    call('importSource', dict(source, title='Competing registration', url='https://example.org/competing', text=text))
    conflict = call('query', 'What does study registration require?', {'corpus': key})['reader']['answer_contract']
    assert conflict['kind'] == 'conflict' and not conflict['answer_supported']
    checks.append('competing_policy_is_not_ranked_away')
    for width in [1280, 768]:
        page.set_viewport_size({'width': width, 'height': 900})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
    assert not errors, errors
    return {'schema': 'mplpb-browser-collection-policy-check-v1', 'checks_passed': checks,
            'runtime': 'actual Chromium and embedded Pyodide', 'network': 'Wikipedia HTTP fixture, not a live acquisition claim',
            'fixture_source_requests': len(network), 'unexpected_browser_errors': errors,
            'browser_version': page.context.browser.version,
            'human_validation': False, 'full_portable_backup_supported': False}


def main():
    from playwright.sync_api import sync_playwright
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview-dir', required=True, type=Path)
    parser.add_argument('--browser-executable')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Choose a new browser report path')
    with preview_server(args.preview_dir) as url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=args.browser_executable, headless=True,
                                            args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(viewport={'width': 1280, 'height': 900})
        try:
            report = verify(context.new_page(), url)
        finally:
            context.close(); browser.close()
    report['runtime_html_sha256'] = hashlib.sha256((args.preview_dir/'index.html').read_bytes()).hexdigest()
    report['runner_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        stream.write(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
