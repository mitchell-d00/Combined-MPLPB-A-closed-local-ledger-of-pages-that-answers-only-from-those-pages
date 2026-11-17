import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.browser_release_smoke import preview_server, verify
from playwright.sync_api import sync_playwright
with preview_server('dist') as url, sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    context=browser.new_context()
    page=context.new_page()
    journeys=verify(page,url,True)
    page.locator("[data-view='ask']").first.click()
    page.locator('#corpus').select_option('logic')
    page.locator('#question').fill('What is Dungeons and Dragons?')
    page.locator('#ask-reader-mode').select_option('supported')
    page.locator('#ask-button').click()
    page.wait_for_function("() => document.querySelector('#results')?.textContent.includes('Outside-world confirmation is required')",timeout=60000)
    content=page.locator('#results').inner_text()
    assert 'coherent false original' in content
    assert 'SUPPORTED ANSWER' in content
    result=page.evaluate("async () => (await window.MPLPB.query('What is Dungeons and Dragons?',{corpus:'logic'})).data.reader.answer_contract")
    assert result['answer_supported']
    assert result['source_assurance']['outside_world_confirmation_required']
    assert not result['verification']['truth_verified']
    print(json.dumps({'browser':browser.version,'candidate_only':True,'new_notice_visible':True,'supported_source_not_truth':True,'journeys':journeys}))
    browser.close()
