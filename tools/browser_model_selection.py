"""Real picker interactions with an authored GPU/engine fixture; no neural inference."""
import hashlib
import json


def verify(page, url):
    from playwright.sync_api import expect
    checks=[];external=[];errors=[];catalogs=[];reject_license=False
    runtime=b'''export class MLCEngine {
      constructor(options){this.options=options;this.logger=()=>{};
        globalThis.modelFixture={record:options.appConfig.model_list[0],loads:0};}
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
