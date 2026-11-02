"""Actual Chromium procedure inspection, clarification, reload and partial evidence."""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from tools.browser_release_smoke import preview_server


def verify(page,url):
    page.goto(url,wait_until='domcontentloaded',timeout=120000)
    ready="() => window.MPLPB && !document.querySelector('#workspace').hidden"
    page.wait_for_function(ready,timeout=150000)
    def call(method,*args):
        r=page.evaluate('async ([m,a]) => await MPLPB[m](...a)',[method,args])
        assert r['ok'],r
        return r['data']
    key=call('createCollection','Procedure recovery fixture')['corpus']
    body=('Procedure: align-vexon\n1. Place the vane flat.\nPrerequisites: none\n'
          'Conditions: Only while dry.\nWarnings: Do not use a wet frame.\n'
          '2. Close the cover.\nPrerequisites: 1\nConditions: Wait until aligned.\nWarnings: Stop if the cover binds.')
    call('importSource',dict(corpus=key,title='Vane plan',url='https://example.org/vane-plan',text=body))
    page.reload(wait_until='domcontentloaded');page.wait_for_function(ready,timeout=150000)
    page.locator('#corpus').select_option(key)
    page.locator('[data-view="ask"]').first.click()
    page.locator('#question').fill('How do I align vexon?');page.locator('#ask-button').click()
    expect(page.locator('#results .outcome')).to_have_text('SUPPORTED ANSWER',timeout=60000)
    expect(page.locator('#results')).to_contain_text('Stop if the cover binds.')
    # Use visible chat controls and explicitly load the selected collection.
    page.locator('[data-view="chat"]').first.click()
    page.locator('#chat-scope').select_option([key])
    page.locator('#chat-load-selected').click()
    expect(page.locator('#chat-send')).to_be_enabled(timeout=60000)
    def send(message):
        page.locator('#chat-input').fill(message);page.locator('#chat-send').click()
        expect(page.locator('#chat-send')).to_be_enabled(timeout=60000)
        return page.locator('#chat-messages .assistant-message').last
    expect(send('How do I align vexon?')).to_contain_text('Step 1:')
    expect(send('show warnings')).to_contain_text('Which step')
    page.reload(wait_until='domcontentloaded');page.wait_for_function(ready,timeout=150000)
    expect(send('step 1')).to_contain_text('Do not use a wet frame.')
    expect(send('next step')).to_contain_text('does not prove completion')
    expect(send('inspect next step')).to_contain_text('Stop if the cover binds.')
    expect(send('No, I meant step 1')).to_contain_text('Place the vane flat.')
    incomplete=body.replace('align-vexon','fold-nacre').replace('Warnings: Stop if the cover binds.','')
    call('importSource',dict(corpus=key,title='Incomplete plan',url='https://example.org/incomplete-plan',text=incomplete))
    partial=call('query','How do I fold nacre?',{'corpus':key})['reader']
    assert partial['answer_contract']['kind']=='partial_answer' and not partial['answer_supported'],partial
    page.locator('[data-view="ask"]').first.click()
    page.locator('#question').fill('How do I fold nacre?');page.locator('#ask-button').click()
    expect(page.locator('#results .outcome')).to_have_text('PARTIAL SOURCE EVIDENCE',timeout=60000)
    expect(page.locator('#results')).not_to_contain_text('Local-model assessment')
    return dict(runtime='actual Chromium / embedded Pyodide',human_validation=False,
                checks=['natural Ask and source constraints','explicitly loaded chat collection',
                        'focused step clarification','reload recovery','no inferred completion',
                        'explicit next-step inspection','step correction','partial exact-source evidence','faithful strict partial label'],
                partial=partial)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preview-dir',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('--browser-executable',default='/usr/bin/chromium')
    args=parser.parse_args()
    with preview_server(args.preview_dir) as url,sync_playwright() as p:
        browser=p.chromium.launch(executable_path=args.browser_executable,headless=True,args=['--no-sandbox'])
        try: result=verify(browser.new_page(),url)
        finally: browser.close()
    result['runtime_sha256']=hashlib.sha256((args.preview_dir/'index.html').read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(result['checks']),'browser procedure checks')
