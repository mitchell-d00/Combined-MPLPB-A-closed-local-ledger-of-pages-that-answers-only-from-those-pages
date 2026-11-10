"""Real Chromium check of the free helper with the full packaged MPLPB engine.

No live neural-model inference, weights download, paid service or iPad claim.
"""
import argparse
import json
import hashlib
from contextlib import nullcontext
from pathlib import Path
from tools.browser_release_smoke import preview_server


def verify(page,url):
    from playwright.sync_api import expect
    checks=[];outbound=[];errors=[]
    def route(request):
        target=request.request.url
        if target.startswith(url) or target.startswith(('blob:','data:')):return request.continue_()
        outbound.append(target);return request.abort()
    page.context.route('**/*',route)
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.add_init_script("Object.defineProperty(navigator,'gpu',{value:undefined,configurable:true})")
    page.goto(url,wait_until='domcontentloaded',timeout=120000)
    page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden",timeout=150000)
    page.locator('#ai-helper > summary').click()
    expect(page.locator('#ai-helper-corpus option')).not_to_have_count(0,timeout=60000)
    page.locator('#ai-helper-message').fill('Private draft question is not a model-load diagnostic')
    page.locator('#ai-helper-load').click()
    expect(page.locator('#ai-helper-status')).to_contain_text('WebGPU',timeout=30000)
    checks.append('unsupported_gpu_is_explicit_and_no_model_download_is_started')
    expect(page.locator('#ai-helper-model-status')).to_contain_text('browser compatibility check')
    page.locator('#ai-helper-load-report').locator('xpath=ancestor::details[1]/summary').click()
    load_report=json.loads(page.locator('#ai-helper-load-report').inner_text())
    assert load_report['attempts'][-1]['status']=='failed'
    assert load_report['attempts'][-1]['failed_phase']=='preflight'
    checks.append('load_failure_has_a_separate_visible_stage_and_diagnostic_report')
    with page.expect_download() as exported:
        page.locator('#ai-helper-export-load').click()
    saved_report=json.loads(Path(exported.value.path()).read_text())
    assert saved_report==load_report
    assert 'Private draft question' not in json.dumps(saved_report)
    checks.append('model_report_download_matches_display_without_source_questions')
    page.locator('#ai-helper-mode').select_option('general')
    page.locator('#ai-helper-send').click()
    expect(page.locator('#ai-helper-output')).to_contain_text('AI not loaded',timeout=30000)
    expect(page.locator('#ai-helper-output')).not_to_contain_text('Clarification needed')
    checks.append('unloaded_general_chat_is_availability_not_question_clarification')
    page.locator('#ai-helper-mode').select_option('build')
    page.locator('#ai-helper-message').fill('Browser helper research')
    page.locator('#ai-helper-send').click()
    expect(page.locator('#ai-helper-approve')).to_be_visible(timeout=60000)
    check=page.evaluate("async()=>{const r=await MPLPB.listCorpora();return r.data.some(c=>c.label==='Browser helper research')}")
    assert not check
    checks.append('collection_proposal_does_not_write_before_review')
    page.locator('#ai-helper-cancel').click()
    expect(page.locator('#ai-helper-approve')).to_be_hidden()
    checks.append('cancelled_proposal_has_no_save')
    page.locator('#ai-helper-send').click();expect(page.locator('#ai-helper-approve')).to_be_visible()
    page.locator('#ai-helper-approve').click()
    expect(page.locator('#ai-helper-output')).to_contain_text('MPLPB save receipt',timeout=60000)
    page.wait_for_function("() => document.querySelector('#ai-helper-corpus').value.startsWith('mind-')",timeout=30000)
    key=page.locator('#ai-helper-corpus').input_value()
    checks.append('approved_creation_uses_real_native_collection_and_selects_it')
    source=page.locator('#ai-helper-source')
    source.locator('xpath=ancestor::details[1]/summary').click()
    page.locator('#ai-helper-title').fill('Opaque source')
    page.locator('#ai-helper-url').fill('https://example.org/browser-source-a')
    source.fill('The Zorvex receiver channel is 8437.')
    page.locator('#ai-helper-message').fill('Save the exact provided source')
    page.locator('#ai-helper-send').click();expect(page.locator('#ai-helper-approve')).to_be_visible()
    page.locator('#ai-helper-approve').click()
    expect(page.locator('#ai-helper-output')).to_contain_text('MPLPB save receipt',timeout=60000)
    checks.append('reviewed_text_import_is_local_and_source_pinned')
    page.locator('#ai-helper-mode').select_option('ask')
    page.locator('#ai-helper-message').fill('What is the Zorvex receiver channel?')
    page.locator('#ai-helper-send').click()
    expect(page.locator('#ai-helper-output')).to_contain_text('8437',timeout=60000)
    expect(page.locator('#ai-helper-output')).to_contain_text('sha256:')
    checks.append('supported_reply_and_exact_citation_are_visible')
    page.locator('#ai-helper-mode').select_option('build')
    page.locator('#ai-helper-url').fill('https://example.org/browser-source-b')
    source.fill('The Zorvex receiver channel is not 8437.')
    page.locator('#ai-helper-send').click();expect(page.locator('#ai-helper-approve')).to_be_visible()
    page.locator('#ai-helper-approve').click();expect(page.locator('#ai-helper-output')).to_contain_text('MPLPB save receipt',timeout=60000)
    page.locator('#ai-helper-mode').select_option('ask')
    page.locator('#ai-helper-send').click()
    expect(page.locator('#ai-helper-output')).to_contain_text('Ambiguous',timeout=60000)
    checks.append('added_denial_prevents_supported_positive')
    page.locator('#ai-helper-trace').locator('xpath=ancestor::details[1]/summary').click()
    trace=json.loads(page.locator('#ai-helper-trace').inner_text())
    kinds={e['kind'] for e in trace['events']}
    assert {'user_input','native_fallback','approval_required','human_approval','tool_request','tool_result','rendered_output'}<=kinds
    checks.append('actual_events_distinguish_inputs_approvals_and_engine_results')
    plan={'id':'align-quillon','steps':[{'order':1,'action':'Place the sheet flat.','prerequisites':[],'conditions':['Only while dry.'],'warnings':['Stop if it tears.']},{'order':2,'action':'Fold the sheet.','prerequisites':[1],'conditions':['Align the edges.'],'warnings':['Do not force the crease.']}]}
    page.evaluate('async ([corpus,text])=>MPLPB.importSource({corpus,title:"Procedure source",url:"https://example.org/helper-plan",text})',[key,'MPLPB-PROCEDURE/1 '+json.dumps(plan)])
    page.locator('#ai-helper-mode').select_option('chat')
    page.locator('#ai-helper-message').fill('How do I align quillon?');page.locator('#ai-helper-send').click()
    expect(page.locator('#ai-helper-output')).to_contain_text('Only while dry.',timeout=60000)
    page.locator('#ai-helper-message').fill('show warnings');page.locator('#ai-helper-send').click()
    expect(page.locator('#ai-helper-output')).to_contain_text('Which step',timeout=60000)
    page.reload(wait_until='domcontentloaded');page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden",timeout=150000)
    page.locator('#ai-helper > summary').click();expect(page.locator('#ai-helper-corpus')).to_have_value(key,timeout=60000)
    page.locator('#ai-helper-mode').select_option('chat');page.locator('#ai-helper-message').fill('step 2');page.locator('#ai-helper-send').click()
    expect(page.locator('#ai-helper-output')).to_contain_text('Do not force the crease.',timeout=60000)
    checks.append('saved_native_session_recovers_pending_step_after_real_page_reload')
    assert not outbound,outbound
    assert not errors,errors
    return {'role':'Authored Chromium workflow on actual WebAssembly MPLPB; no live-model inference or independent human validation',
            'checks_passed':checks,'outbound_requests':outbound,'page_errors':errors,'corpus':key,
            'model_downloaded':False,'iPad_verified':False,'trace':trace,'initial_model_load_report':load_report}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    location=parser.add_mutually_exclusive_group(required=True)
    location.add_argument('--preview-dir',type=Path)
    location.add_argument('--live-url',help='Published URL; writes are only to the isolated test browser storage')
    parser.add_argument('--browser-executable',default='/usr/bin/chromium')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error('Choose a new output path; preserve earlier reports')
    from playwright.sync_api import sync_playwright
    server=preview_server(args.preview_dir) if args.preview_dir else nullcontext(args.live_url.rstrip('/')+'/')
    with server as url,sync_playwright() as playwright:
        browser=playwright.chromium.launch(executable_path=args.browser_executable,headless=True,args=['--no-sandbox'])
        try:
            context=browser.new_context(viewport={'width':1100,'height':850})
            report=verify(context.new_page(),url)
            # Fresh storage exercises the default and model switching separately
            # from source workflow persistence. GPU/engine success is a fixture.
            from tools.browser_model_selection import verify as verify_models
            with browser.new_context(viewport={'width':810,'height':1080},has_touch=True,accept_downloads=True) as model_context:
                report['model_selection']=verify_models(model_context.new_page(),url)
            report['target_kind']='candidate_preview' if args.preview_dir else 'published_site'
            report['target']=str(args.preview_dir) if args.preview_dir else url
            report['implementation_sha256']={name:hashlib.sha256((Path(__file__).resolve().parents[1]/name).read_bytes()).hexdigest() for name in ('browser/ai-helper.js','browser/ai-model-loader.js','browser/ai-helper-ui.js','tools/browser_free_helper.py')}
            if args.preview_dir:report['preview_sha256']=hashlib.sha256((args.preview_dir/'index.html').read_bytes()).hexdigest()
        finally:browser.close()
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checks':len(report['checks_passed']),'passed':True},indent=2))


if __name__=='__main__':main()
