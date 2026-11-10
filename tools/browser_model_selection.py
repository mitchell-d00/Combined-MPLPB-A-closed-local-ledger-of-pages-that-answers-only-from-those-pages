"""Real picker interactions with an authored GPU/engine fixture; no neural inference."""
import hashlib
import json


def verify(page, url):
    from playwright.sync_api import expect
    checks=[];external=[];errors=[];catalogs=[];reject_license=False
    runtime=b'''export class MLCEngine {
      constructor(options){this.options=options;this.logger=()=>{};
        globalThis.modelFixture={record:options.appConfig.model_list[0],loads:0,requests:[],pauseReplies:true};
        this.chat={completions:{create:async request=>{
          const state=globalThis.modelFixture;state.requests.push(request);
          if(state.failNext)throw Error('The current Object has already been disposed');
          if(request.stream)return(async function*(){
            yield {choices:[{delta:{content:'Hello'}}]};
            if(state.pauseReplies)await new Promise(resolve=>globalThis.releaseReplyFixture=resolve);
            yield {choices:[{delta:{content:' from the local AI'},finish_reason:'stop'}]};
          })();
          return {choices:[{message:{content:JSON.stringify({action:'create_collection',summary:'Propose a reviewed collection',name:'AI chat builder fixture'})},finish_reason:'stop'}]};
        }}};}
      async reload(id){globalThis.modelFixture.id=id;globalThis.modelFixture.loads++;
        this.options.initProgressCallback({progress:0.26,text:'Authored loading fixture'});
        await new Promise(resolve=>globalThis.releaseModelFixture=resolve);}
      async unload(){}
    }'''
    runtime_hash=hashlib.sha256(runtime).hexdigest()
    def route(request):
        nonlocal reject_license
        target=request.request.url
        if target.endswith('/ai/models.json'):
            data=request.fetch().json();catalogs.append(data)
            for model in data['models']:model['runtime']['sha256']=runtime_hash
            if reject_license:data['models'][0]['license_spdx']='Apache-2.0'
            return request.fulfill(json=data)
        if target.endswith('/ai/webllm.mjs'):
            return request.fulfill(body=runtime,content_type='text/javascript')
        if target.startswith(url) or target.startswith(('blob:','data:')):return request.continue_()
        external.append(target);return request.abort()
    page.context.route('**/*',route)
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.add_init_script("""Object.defineProperty(navigator,'gpu',{configurable:true,value:{
      requestAdapter:async()=>({features:new Set(['shader-f16']),limits:{
        maxBufferSize:536870912,maxStorageBufferBindingSize:536870912}})}});""")
    def opened():
        page.wait_for_function("() => window.MPLPB && !document.querySelector('#workspace').hidden",timeout=150000)
        page.locator('#ai-helper > summary').click()
    page.goto(url,wait_until='domcontentloaded',timeout=120000);opened()
    select=page.locator('#ai-helper-model');button=page.locator('#ai-helper-load')
    expect(select).to_be_enabled(timeout=30000)
    data=catalogs[-1]
    assert all(model['license_spdx']=='MIT' for model in data['models'])
    expect(select).to_have_value(data['default_model_id'])
    expect(select.locator('option')).to_have_count(len(data['models']))
    expect(page.locator('#ai-helper-model-info')).to_contain_text('0.80 GB weights')
    assert not page.evaluate('() => !!globalThis.modelFixture')
    checks.append('MIT choices show sizes and smallest default without loading weights')
    chosen=data['models'][1];select.select_option(chosen['model_id'])
    expect(page.locator('#ai-helper-model-info')).to_contain_text(chosen['label'])
    button.click()
    page.wait_for_function('() => !!globalThis.releaseModelFixture',timeout=30000)
    expect(select).to_be_disabled();expect(button).to_be_disabled()
    fixture=page.evaluate('() => globalThis.modelFixture')
    assert fixture['id']==chosen['model_id']
    assert fixture['record']['model']==chosen['record']['model']
    assert fixture['record']['mplpb_minimum_tensor_buffer_bytes']==chosen['minimum_tensor_buffer_bytes']
    checks.append('explicit selection reaches engine with its own pins and resource minimum; controls lock while loading')
    page.evaluate('() => globalThis.releaseModelFixture()')
    expect(page.locator('#ai-helper-use-model')).to_be_checked()
    expect(page.locator('#ai-helper-status')).to_contain_text(chosen['label']+' loaded')
    expect(select).to_be_enabled()
    with page.expect_download() as exported:page.locator('#ai-helper-export-load').click()
    from pathlib import Path
    report=json.loads(Path(exported.value.path()).read_text())
    assert report['attempts'][-1]['model']['id']==chosen['model_id']
    assert report['attempts'][-1]['status']=='ready'
    checks.append('ready state and exported report identify the loaded model')
    # Exercise actual UI-to-provider-to-helper dispatch. Neural output is a fixture.
    page.locator('#ai-helper-mode').select_option('general')
    prompt=page.locator('#ai-helper-message');send=page.locator('#ai-helper-send')
    for width,height in [(810,1080),(375,812)]:
        page.set_viewport_size({'width':width,'height':height})
        log=page.locator('#ai-helper-messages').bounding_box();box=prompt.bounding_box();button_box=send.bounding_box()
        assert box['y']>=log['y']+log['height']
        assert abs(button_box['y']+button_box['height']-box['y']-box['height'])<2
        assert button_box['x']+button_box['width']<=width
    before=send.bounding_box()['y']
    page.locator('#ai-helper-source').evaluate('(e)=>e.closest("details").open=true')
    assert abs(send.bounding_box()['y']-before)<1
    checks.append('iPad and narrow layouts keep prompt/Send directly below response window and above expanded source import')
    prompt.fill('Hello <script>globalThis.badChatHtml=true</script>')
    send.click();expect(page.locator('#ai-helper-output')).to_contain_text('Hello')
    page.wait_for_function('() => !!globalThis.releaseReplyFixture')
    expect(send).to_be_disabled();expect(select).to_be_disabled()
    prompt.press('Enter')
    assert page.evaluate('() => globalThis.modelFixture.requests.length')==1
    page.evaluate('() => {globalThis.modelFixture.pauseReplies=false;globalThis.releaseReplyFixture()}')
    expect(page.locator('#ai-helper-output')).to_contain_text('Hello from the local AI')
    expect(prompt).to_have_value('')
    actual=page.evaluate('() => globalThis.modelFixture.requests[0]')
    assert 'response_format' not in actual and actual['stream'] is True
    assert actual['messages'][-1]['content']=='Hello <script>globalThis.badChatHtml=true</script>'
    assert not page.evaluate('() => !!globalThis.badChatHtml')
    checks.append('Send streams a plain-text reply, escapes transcript text and blocks duplicate sends')
    prompt.fill('Tell me more');prompt.press('Enter')
    expect(prompt).to_have_value('');expect(page.locator('#ai-helper-output')).to_contain_text('Hello from the local AI')
    assert page.evaluate('() => globalThis.modelFixture.requests[1].messages.some(m=>m.role==="assistant"&&m.content==="Hello from the local AI")')
    checks.append('Enter sends the next message with prior chat context')
    page.locator('#ai-helper-mode').select_option('build');prompt.fill('Create a collection for my notes');send.click()
    expect(page.locator('#ai-helper-approve')).to_be_visible()
    assert not page.evaluate('async()=> (await MPLPB.listCorpora()).data.some(c=>c.label==="AI chat builder fixture")')
    page.locator('#ai-helper-approve').click()
    expect(page.locator('#ai-helper-output')).to_contain_text('MPLPB save receipt')
    assert page.evaluate('async()=> (await MPLPB.listCorpora()).data.some(c=>c.label==="AI chat builder fixture")')
    checks.append('AI Build proposes a collection and real MPLPB creates it only after review')
    page.locator('#ai-helper-mode').select_option('general');page.evaluate('() => globalThis.modelFixture.failNext=true')
    prompt.fill('Trigger the authored failure');send.click()
    expect(page.locator('#ai-helper-output')).to_contain_text('disposed')
    expect(button).to_have_text('Reload AI after error')
    expect(page.locator('#ai-helper-use-model')).to_be_disabled()
    expect(page.locator('#ai-helper-use-model')).not_to_be_checked()
    failed=json.loads(page.locator('#ai-helper-load-report').text_content())
    assert failed['attempts'][-1]['failed_phase']=='generation'
    assert page.evaluate('async()=> (await MPLPB.ready()).ok')
    checks.append('disposed generation invalidates readiness, keeps original diagnostic and offers reload while source engine remains available')
    page.set_viewport_size({'width':810,'height':1080})
    other=data['models'][2];select.select_option(other['model_id'])
    expect(page.locator('#ai-helper-use-model')).not_to_be_checked()
    expect(page.locator('#ai-helper-use-model')).to_be_disabled()
    expect(button).to_have_text('Reload page to load selection')
    assert page.evaluate('() => globalThis.modelFixture.loads')==1
    button.click();opened()
    expect(select).to_be_enabled();expect(select).to_have_value(other['model_id'])
    assert not page.evaluate('() => !!globalThis.modelFixture')
    checks.append('switch revokes old provider and reloads with persisted selection before another allocation')
    page.evaluate("() => localStorage.setItem('mplpb-optional-helper-model-id-v1',JSON.stringify('retired-model'))")
    page.reload(wait_until='domcontentloaded');opened()
    expect(select).to_be_enabled();expect(select).to_have_value(data['default_model_id'])
    checks.append('unavailable saved selection recovers to smallest default')
    reject_license=True
    page.reload(wait_until='domcontentloaded');opened()
    expect(page.locator('#ai-helper-model-info')).to_contain_text('Only MIT')
    expect(button).to_be_disabled()
    assert page.evaluate('async()=> (await MPLPB.ready()).ok')
    checks.append('non-MIT catalog disables AI loading while real source engine remains usable')
    assert not external,external
    assert not errors,errors
    return {'scope':'Real Chromium and WebAssembly source engine with authored GPU, runtime and runtime-hash fixtures. No weights downloaded, neural inference or physical iPad validation.',
            'checks_passed':checks,'external_requests':external,'page_errors':errors}
