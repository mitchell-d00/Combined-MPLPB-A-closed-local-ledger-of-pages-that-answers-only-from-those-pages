// Authored loader/DOM orchestration tests. Runtime and GPU are simulated;
// these do not establish actual neural inference or iPad compatibility.
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {webcrypto}=require('node:crypto');
const {Loader}=require('../browser/ai-model-loader.js');
const bytes=new TextEncoder().encode('an authored runtime fixture');
let checks=[];
async function scenario(name,run){await run();checks.push(name);}
async function fixture(behavior={}){
 const hash=Buffer.from(await webcrypto.subtle.digest('SHA-256',bytes)).toString('hex');
 const config={model_id:'unfamiliar-model',label:'Fixture model',license_spdx:'MIT',description:'Authored fixture',weights:{tensor_download_bytes:1000},minimum_tensor_buffer_bytes:1024,runtime:{sha256:hash,version:'test'},record:{model_id:'unfamiliar-model',vram_required_MB:1,required_features:['shader-f16'],model:'https://example.org/pinned-model/',model_lib:'https://example.org/pinned-lib',integrity:{onFailure:'error',model_lib:'sha256-pinned'}}};
 const catalog={schema:'mplpb-model-catalog-v1',default_model_id:config.model_id,models:[config]};
 const state={fetches:[],fetchOptions:[],constructors:0,unloads:0,forwarded:[]};
 class Engine{
  constructor(options){state.constructors++;state.options=options;this.logger=text=>state.forwarded.push(text);state.engine=this;}
  async reload(id){state.id=id;state.options.initProgressCallback({progress:1,text:'Fetching param cache[66/66]: 100% completed'});if(behavior.reload)await behavior.reload(this,state);}
  async unload(){state.unloads++;if(behavior.unload)await behavior.unload();}
 }
 const env={navigator:{userAgent:'Authored test browser',gpu:{requestAdapter:async()=>({features:new Set(['shader-f16']),limits:{maxBufferSize:2048,maxStorageBufferBindingSize:2048}})}},document:{baseURI:'https://example.org/app/'},crypto:webcrypto,
  fetch:async (url,options)=>{state.fetches.push(String(url));state.fetchOptions.push(options);return String(url).endsWith('models.json')?{ok:true,json:async()=>catalog}:{ok:true,arrayBuffer:async()=>bytes.buffer};},importRuntime:async()=>({MLCEngine:Engine})};
 return {state,config,catalog,env};
}
async function run(){
 await scenario('no GPU reports preflight failure without fetching',async()=>{const f=await fixture();delete f.env.navigator.gpu;const l=new Loader({env:f.env});await assert.rejects(()=>l.load(),/WebGPU/);assert.equal(f.state.fetches.length,0);assert.equal(l.snapshot().attempts[0].failed_phase,'preflight');assert.equal(l.loading,false);});
 await scenario('missing f16 blocks before runtime download',async()=>{const f=await fixture();f.env.navigator.gpu.requestAdapter=async()=>({features:new Set(),limits:{}});const l=new Loader({env:f.env});await assert.rejects(()=>l.load(),/shader-f16/);assert.equal(f.state.fetches.length,1);assert.equal(f.state.constructors,0);});
 await scenario('unknown or inadequate buffer capacity is rejected',async()=>{const f=await fixture();f.env.navigator.gpu.requestAdapter=async()=>({features:new Set(['shader-f16']),limits:{maxBufferSize:2048}});await assert.rejects(()=>new Loader({env:f.env}).load(),/buffer capacity/);assert.equal(f.state.fetches.length,1);});
 await scenario('explicit choice uses its own identity, buffer minimum and runtime record',async()=>{
  const f=await fixture();const second=JSON.parse(JSON.stringify(f.config));second.model_id='second-model';second.record.model_id=second.model_id;second.record.model='https://example.org/second-model/';second.minimum_tensor_buffer_bytes=1536;f.catalog.models.push(second);
  const l=new Loader({env:f.env}),result=await l.load(second.model_id);assert.equal(result.configuration.model_id,second.model_id);assert.equal(f.state.id,second.model_id);assert.equal(f.state.options.appConfig.model_list[0].mplpb_minimum_tensor_buffer_bytes,1536);assert.equal(l.snapshot().attempts[0].selected_model_id,second.model_id);
  await assert.rejects(()=>l.load(f.config.model_id),/Reload this page/);assert.equal(f.state.constructors,1);
 });
 await scenario('unknown selection never downloads the runtime or starts an engine',async()=>{const f=await fixture();await assert.rejects(()=>new Loader({env:f.env}).load('not-in-catalog'),/not in the MIT catalog/);assert.equal(f.state.fetches.length,1);assert.equal(f.state.constructors,0);});
 await scenario('generation failure invalidates ready state and requires reload with retained initialization evidence',async()=>{
  const f=await fixture(),l=new Loader({env:f.env});await l.load();l.invalidate(Error('The current Object has already been disposed'));
  const a=l.snapshot().attempts[0];assert.equal(a.status,'failed');assert.equal(a.failed_phase,'generation');assert(a.events.some(e=>e.kind==='ready'));assert(a.events.some(e=>e.kind==='generation_failure'));assert.equal(l.loaded,false);assert.equal(l.requiresReload,true);
  await assert.rejects(()=>l.load(),/Reload this page/);assert.equal(f.state.constructors,1);
 });
 await scenario('non-MIT model anywhere in catalog fails closed',async()=>{const f=await fixture();f.config.license_spdx='Apache-2.0';await assert.rejects(()=>new Loader({env:f.env}).load(),/Only MIT/);assert.equal(f.state.constructors,0);assert.equal(f.state.fetches.length,1);});
 await scenario('duplicate identities and missing defaults fail before engine allocation',async()=>{const f=await fixture();f.catalog.models.push(f.config);await assert.rejects(()=>new Loader({env:f.env}).load(),/duplicate/);f.catalog.models.pop();f.catalog.default_model_id='missing';await assert.rejects(()=>new Loader({env:f.env}).load(),/Default model/);assert.equal(f.state.constructors,0);});
 await scenario('changed runtime bytes stop before import or initialization',async()=>{const f=await fixture();f.config.runtime.sha256='0'.repeat(64);const l=new Loader({env:f.env});await assert.rejects(()=>l.load(),/pinned build/);assert.equal(f.state.constructors,0);assert.equal(l.snapshot().attempts[0].failed_phase,'runtime_integrity');});
 await scenario('100 percent followed by exit(1) retains runtime evidence and never becomes ready',async()=>{
  const f=await fixture({reload:async engine=>{engine.logger('TVM: authored allocation error detail');throw new Error('Program terminated with exit(1)',{cause:Error('Authored runtime cause')});}}),l=new Loader({env:f.env});
  await assert.rejects(()=>l.load(),/exit\(1\)/);const a=l.snapshot().attempts[0];assert.equal(a.status,'failed');assert.equal(a.last_progress.progress,1);assert.equal(a.failed_phase,'engine_initialization');assert.equal(a.error.cause.message,'Authored runtime cause');assert(a.events.some(e=>e.kind==='runtime_log'&&e.data.text.includes('allocation error detail')));assert(!a.events.some(e=>e.kind==='ready'));assert.equal(f.state.unloads,1);assert.equal(l.requiresReload,true);
  await assert.rejects(()=>l.load(),/Reload this page/);assert.equal(f.state.constructors,1);
 });
 await scenario('100 percent remains loading until reload actually resolves; concurrency blocked',async()=>{
  let release;const pause=new Promise(resolve=>release=resolve);const f=await fixture({reload:async()=>pause}),l=new Loader({env:f.env});const load=l.load();while(!f.state.engine)await new Promise(resolve=>setTimeout(resolve,0));
  assert.equal(l.snapshot().attempts[0].status,'loading');await assert.rejects(()=>l.load(),/already in progress/);release();await load;assert.equal(l.snapshot().attempts[0].status,'ready');assert.equal(f.state.unloads,0);assert(f.state.fetchOptions.every(o=>o.cache==='no-cache'));assert.deepEqual(f.state.options.appConfig.model_list,[{...f.config.record,mplpb_minimum_tensor_buffer_bytes:f.config.minimum_tensor_buffer_bytes}]);
  const count=l.snapshot().attempts[0].events.length;f.state.engine.logger('later inference log');assert.equal(l.snapshot().attempts[0].events.length,count);
 });
 await scenario('cleanup errors preserve original failure and recovery requirement',async()=>{const f=await fixture({reload:async()=>{throw Error('original exit(1)');},unload:async()=>{throw Error('cleanup failed');}}),l=new Loader({env:f.env});await assert.rejects(()=>l.load(),/original exit/);const a=l.snapshot().attempts[0];assert.equal(a.error.message,'original exit(1)');assert(a.events.some(e=>e.kind==='cleanup'&&e.data.result==='unload_incomplete'));assert.equal(l.loading,false);});
 await scenario('hanging cleanup is bounded without clearing source data',async()=>{const f=await fixture({reload:async()=>{throw Error('original exit(1)');},unload:async()=>new Promise(()=>{})}),l=new Loader({env:f.env});await assert.rejects(()=>l.load(),/original exit/);assert.equal(l.loading,false);assert(l.snapshot().attempts[0].events.some(e=>e.kind==='cleanup'&&e.data.error?.message.includes('3000 ms')));});
 await scenario('bounded events and snapshots cannot mutate the retained report',async()=>{const f=await fixture({reload:async e=>{e.logger('MPLPB_GPU_DEVICE_LIMITS '+JSON.stringify({maxBufferSize:2048,maxStorageBufferBindingSize:2048}));for(let n=0;n<140;n++)e.logger('x'.repeat(5000));}}),l=new Loader({env:f.env});await l.load();const report=l.snapshot();assert(report.attempts[0].events.length<=120);assert(report.attempts[0].omitted_events>0);assert.equal(report.attempts[0].browser.user_agent,'Authored test browser');assert.deepEqual(report.attempts[0].gpu_adapter.features,['shader-f16']);assert.equal(report.attempts[0].gpu_device.maxBufferSize,2048);assert(report.attempts[0].events.filter(e=>e.kind==='runtime_log').every(e=>e.data.text.length<=1500));report.attempts.length=0;assert.equal(l.snapshot().attempts.length,1);});
 await scenario('older preflight failures are bounded and omissions explicit',async()=>{const f=await fixture();delete f.env.navigator.gpu;const l=new Loader({env:f.env});for(let n=0;n<5;n++)await assert.rejects(()=>l.load());assert.equal(l.snapshot().attempts.length,3);assert.equal(l.snapshot().omitted_attempts,2);assert.equal(l.snapshot().attempts[0].number,3);});
 await scenario('pinned runtime logger hook changes fail visibly',async()=>{const f=await fixture();f.env.importRuntime=async()=>({MLCEngine:class{async unload(){}}});await assert.rejects(()=>new Loader({env:f.env}).load(),/logger is unavailable/);});
 await scenario('real helper UI exposes initialization failure without a ledger call',async()=>{
  let release;const pause=new Promise(resolve=>release=resolve),f=await fixture({reload:async engine=>{await pause;engine.logger('Specific authored TVM failure');throw Error('Program terminated with exit(1)');}});
  const nodes=new Map();let reloads=0,ledgerCalls=0;
  function element(id){if(!nodes.has(id))nodes.set(id,{value:id==='ai-helper-mode'?'general':'',textContent:'',checked:false,disabled:false,events:{},addEventListener(k,fn){this.events[k]=fn;},replaceChildren(){},append(){},remove(){},click(){return this.events.click?.();}});return nodes.get(id);}
  const context=vm.createContext({...f.env,console,URL,Blob,setTimeout,clearTimeout,location:{reload:()=>reloads++},MPLPB:{listCorpora:async()=>{ledgerCalls++;throw Error('No source operation should be needed');}},document:{...f.env.document,getElementById:element,body:{append(){}},createElement:()=>element('anchor')}});context.window=context;
  for(const name of ['ai-helper.js','ai-model-loader.js','ai-helper-ui.js'])vm.runInContext(fs.readFileSync('browser/'+name,'utf8'),context);
  const load=element('ai-helper-load').click();while(!f.state.engine)await new Promise(resolve=>setTimeout(resolve,0));
  await element('ai-helper-send').click();assert(element('ai-helper-status').textContent.includes('has not been sent'));assert.equal(ledgerCalls,0);
  release();await load;
  assert(element('ai-helper-model-status').textContent.includes('model initialization'));assert(element('ai-helper-load-report').textContent.includes('Specific authored TVM failure'));assert(element('ai-helper-trace').textContent.includes('model_load'));assert.equal(element('ai-helper-use-model').checked,false);assert.equal(element('ai-helper-use-model').disabled,true);assert(element('ai-helper-load').textContent.includes('Reload page'));
  await element('ai-helper-load').click();assert.equal(reloads,1);assert.equal(f.state.constructors,1);assert.equal(ledgerCalls,0);
 });
 await scenario('real pinned WebLLM constructor/logger/unload API works without loading weights',async()=>{
  const zlib=require('node:zlib'),os=require('node:os'),path=require('node:path'),{pathToFileURL}=require('node:url'),{createHash}=require('node:crypto');
  const manifest=JSON.parse(fs.readFileSync('assets/ai/manifest.json','utf8')).runtime;
  const packed=Buffer.concat(manifest.parts.map(part=>{const raw=fs.readFileSync(path.join('assets/ai',part.path));assert.equal(createHash('sha256').update(raw).digest('hex'),part.sha256);return Buffer.from(raw.toString(),'base64');}));
  let raw=zlib.gunzipSync(packed);assert.equal(createHash('sha256').update(raw).digest('hex'),manifest.uncompressed_sha256);
  const {execFileSync}=require('node:child_process');raw=execFileSync(process.env.PYTHON||'python3',['-c','import sys; from tools.build_ai_assets import runtime; sys.stdout.buffer.write(runtime())'],{maxBuffer:16*1024*1024});assert.equal(createHash('sha256').update(raw).digest('hex'),manifest.local_patch?.output_sha256||manifest.uncompressed_sha256);
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'mplpb-loader-api-')),file=path.join(dir,'webllm.mjs'),originalFetch=global.fetch;
  try{fs.writeFileSync(file,raw);global.fetch=()=>{throw Error('No model or source fetch permitted');};const runtime=await import(pathToFileURL(file).href),engine=new runtime.MLCEngine({logLevel:'WARN',appConfig:{model_list:[]}});assert.equal(typeof engine.logger,'function');assert.equal(typeof engine.reload,'function');await engine.unload();}
  finally{global.fetch=originalFetch;fs.rmSync(dir,{recursive:true,force:true});}
 });
 console.log(JSON.stringify({role:'Authored model-loader state/DOM tests with simulated runtime and GPU; not live neural inference or independent human validation',checks:checks.length,passed:true,cases:checks},null,2));
}
run().catch(error=>{console.error(error);process.exitCode=1;});
