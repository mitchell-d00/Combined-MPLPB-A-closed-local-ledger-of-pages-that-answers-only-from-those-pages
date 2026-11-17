"""Real isolated Chromium UI check of documentary source assertion composition."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
from tools.browser_release_smoke import preview_server
p=argparse.ArgumentParser();p.add_argument('--dist',required=True);p.add_argument('--output',required=True);args=p.parse_args();checks=[]
with sync_playwright() as pw,preview_server(args.dist) as url:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 context=browser.new_context();page=context.new_page();page.goto(url,wait_until='domcontentloaded')
 page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden",timeout=150000)
 page.locator('[data-view="chat"]').first.click();page.locator('#chat-auto-wiki').set_checked(False)
 def open_form():
  container=page.locator('details').filter(has=page.locator('#collection-form')).first
  if not container.evaluate('(e)=>e.open'):container.locator('summary').first.click()
 open_form();page.locator('#collection-name').fill('Documentary proof UI test');page.locator('#collection-form button[type="submit"]').click()
 expect(page.locator('#collection-status')).to_contain_text('Created Documentary proof UI test',timeout=60000)
 corpus=page.locator('#corpus').input_value();checks.append('create_disposable_collection_through_ui')
 def add(title,body):
  page.locator('[data-view="chat"]').first.click();open_form();page.locator('#source-title').fill(title)
  page.locator('#source-url').fill('https://example.org/'+title.lower().replace(' ','-'));page.locator('#source-text').fill(body)
  page.locator('#source-form button[type="submit"]').click();expect(page.locator('#collection-status')).to_contain_text('Saved '+title,timeout=60000)
 def ask(q):
  page.locator('[data-view="ask"]').first.click();page.locator('#ask-reader-mode').select_option('supported')
  page.locator('#question').fill(q);page.locator('#ask-button').click();expect(page.locator('#ask-button')).to_be_enabled(timeout=60000)
 add('Appointment record','Ruth Stone appointed Mira Vale. Orin Hale appointed Lena Grey.')
 ask('Who appointed Mira Vale, and who appointed Lena Grey?')
 expect(page.locator('#results .outcome')).to_have_text('SUPPORTED SOURCE ASSERTIONS',timeout=60000)
 expect(page.locator('#results .card')).to_have_count(2);checks.append('checked_compound_source_answer_visible')
 page.locator('#results [data-page]').first.click();expect(page.locator('#page-dialog')).to_be_visible()
 expect(page.locator('#page-content .page-text')).to_contain_text('Ruth Stone appointed Mira Vale.');page.locator('#close-dialog').click()
 checks.append('inspect_exact_supporting_source')
 ask('Who appointed Mira Vale, and why did this cause the war?')
 expect(page.locator('#results .outcome')).to_have_text('PARTIAL SOURCE EVIDENCE',timeout=60000)
 expect(page.locator('#results')).to_contain_text('cause the war');expect(page.locator('#results')).to_contain_text('Historical truth is not independently verified')
 checks.append('partial_source_answer_does_not_inherit_causal_support')
 result=page.evaluate('async c => await MPLPB.query("Who appointed Mira Vale, and why did this cause the war?",{corpus:c})',corpus)
 assert result['data']['reader']['answer_contract']['kind']=='partial_answer'
 assert result['data']['reader']['answer_supported'] is False
 add('Contrary record','Ruth Stone did not appoint Mira Vale.')
 ask('Who appointed Mira Vale?');expect(page.locator('#results .outcome')).to_have_text('EVIDENCE CONFLICT',timeout=60000)
 expect(page.locator('#results')).to_contain_text('historical contradiction are not established');checks.append('opposed_sources_do_not_choose_a_winner_or_merge_events')
 add('Position A','We held the northern coastal defensive position until dawn.')
 add('Position B','We held the northern coastal defensive position until noon.')
 ask('Compare the wording about the northern coastal defensive position.')
 expect(page.locator('#results .outcome')).to_have_text('PARTIAL SOURCE EVIDENCE',timeout=60000)
 expect(page.locator('#results')).to_contain_text('dawn');expect(page.locator('#results')).to_contain_text('noon')
 checks.append('exact_wording_comparison_visible_without_historical_correction')
 add('Expedition account','The expedition was delayed because of heavy rain.')
 ask('Why was the expedition delayed?')
 expect(page.locator('#results .outcome')).to_have_text('PARTIAL SOURCE EVIDENCE',timeout=60000)
 expect(page.locator('#results')).to_contain_text('heavy rain')
 expect(page.locator('#results')).to_contain_text('does not independently establish historical causation')
 checks.append('explicit_source_cause_visible_with_historical_truth_limit')
 add('Framed draft', '(This is Professor Clara Reed\'s reconstruction of Iris Vale\'s "original Rough draught" of the Harbor Charter before it was revised by the council.)\n\nWe hold these rules to be fair and binding.')
 add('Framed transcript', 'Note: The following text is a transcription of the copper engraving of the parchment Harbor Charter.\n\nWe hold these rules to be clear and binding.')
 framed_question="Compare the opening rule claim in Iris Vale's rough draft and the final Harbor Charter transcript. What wording changed and what remained?"
 ask(framed_question)
 expect(page.locator('#results .outcome')).to_have_text('SUPPORTED SOURCE ASSERTIONS',timeout=60000)
 expect(page.locator('#results')).to_contain_text('fair');expect(page.locator('#results')).to_contain_text('clear')
 expect(page.locator('#results')).to_contain_text('Historical authenticity and finality are not independently verified')
 checks.append('complete_source_comparison_has_checked_role_witnesses_and_scope')
 ask(framed_question+' Why did the council change it?')
 expect(page.locator('#results .outcome')).to_have_text('PARTIAL SOURCE EVIDENCE',timeout=60000)
 checks.append('completion_does_not_hide_additional_motive_obligation')
 add('Letter inspection', 'NORA REED TO IRIS VALE. Haven, March 3rd, 1841.\nMy dear Sir,\nI have told Arun Hale to send you by post (if possible) a copy of my atlas.')
 q="Who arranged for Iris Vale to receive Nora Reed's atlas, and which dated letter records the arrangement?"
 ask(q)
 expect(page.locator('#results .outcome')).to_have_text('SUPPORTED SOURCE ASSERTIONS',timeout=60000)
 expect(page.locator('#results .question-obligations')).to_contain_text('Question parts')
 expect(page.locator('#results .question-obligations li')).to_have_count(2)
 expect(page.locator('#results')).to_contain_text('canonical ')
 expect(page.locator('#results')).to_contain_text('Actual fulfillment')
 data=page.evaluate('async ([c,q]) => (await MPLPB.query(q,{corpus:c})).data.reader.answer_contract',[corpus,q])
 assert data['answer_supported'] and len(data['claims'][0]['citations'])==3
 assert data['claims'][0]['proposition']['receipt_verified'] is False
 assert data['claims'][0]['proposition']['dispatch_verified'] is False
 checks.append('complete_recorded_arrangement_has_three_witnesses_and_obligation_view')
 ask(q+' Did delivery occur?')
 expect(page.locator('#results .outcome')).not_to_have_text('SUPPORTED SOURCE ASSERTIONS',timeout=60000)
 checks.append('delivery_question_does_not_inherit_arrangement_completion')
 context.close();browser.close()
with Path(args.output).open('x') as f:json.dump({'status':'passed','real_browser':'system Chromium with ZIP-built WebAssembly engine','checks':checks,'independent_human_validation':'NOT RUN','human_usability_measured':False},f,indent=2)
print('PASS documentary Chromium UI:',len(checks),'checks')
