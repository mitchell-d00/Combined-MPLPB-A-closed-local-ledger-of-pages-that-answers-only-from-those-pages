"""Visible-control polarity regression; disposable context, no network acquisition."""
import json
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
from tools.browser_release_smoke import preview_server
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--preview-dir',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args()
with preview_server(args.preview_dir) as url, sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page=browser.new_page()
    page.goto(url,wait_until='domcontentloaded',timeout=120000)
    page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden",timeout=150000)
    def call(m,*args):
        r=page.evaluate('async ([m,a]) => await MPLPB[m](...a)',[m,args]);assert r['ok'],r
        return r['data']
    key=call('createCollection','Unfamiliar preservation ledger')['corpus']
    sentence='Prism records must be kept in green cabinet.'
    call('importSource',{'corpus':key,'title':'Preservation rules','url':'https://example.org/preservation','text':sentence})
    page.reload(wait_until='domcontentloaded')
    page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden",timeout=150000)
    page.locator('#corpus').select_option(key)
    page.locator('[data-view="ask"]').first.click()
    page.locator('#question').fill('Where should prism records be kept?')
    page.locator('#ask-button').click()
    expect(page.locator('#results .outcome')).to_have_text('SUPPORTED ANSWER',timeout=60000)
    expect(page.locator('#results')).to_contain_text(sentence)
    before=call('query','Where should prism records be kept?',{'corpus':key})
    call('importSource',{'corpus':key,'title':'Opposing rule','url':'https://example.org/opposition','text':'Prism records must not be kept in green cabinet.'})
    after=call('query','Where should prism records be kept?',{'corpus':key})
    assert after['reader']['kind']=='ambiguous',after
    assert not after['reader']['answer_supported']
    page.locator('#ask-button').click()
    expect(page.locator('#results .outcome')).not_to_have_text('SUPPORTED ANSWER',timeout=60000)
    report=dict(runtime='actual Chromium / embedded Pyodide from extracted source ZIP',before=before,after=after,visible_outcome=page.locator('#results .outcome').inner_text(),checks=['passive paraphrase visible answer','verbatim modality','cross-source denial via public API','visible ambiguity'],human_validation=False)
    Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
    browser.close()
