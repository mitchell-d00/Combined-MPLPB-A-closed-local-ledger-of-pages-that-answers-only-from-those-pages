/* Pinned WebLLM loader diagnostics. No ledger access, training or telemetry. */
(function(root){
'use strict';
const clone=value=>JSON.parse(JSON.stringify(value));
function bounded(value,max=1500){try{return String(value).slice(0,max);}catch{return '[unprintable]';}}
function describeError(error,depth=0){
 const result={name:bounded(error?.name||'Error',100),message:bounded(error?.message||error,4000)};
 if(error?.stack)result.stack=bounded(error.stack,6000);
 if(error?.cause&&depth<2)result.cause=describeError(error.cause,depth+1);
 return result;
}
class Loader{
 constructor(options={}){
  this.env=options.env||root;this.onChange=options.onChange||(()=>{});this.attempts=[];this.omittedAttempts=0;this.loading=false;this.requiresReload=false;
 }
 snapshot(){return {schema:'mplpb-model-load-report-v1',notice:'Local runtime diagnostics, not model reasoning or source evidence. No upload or training is performed. Older events/attempts may be omitted; omissions are counted.',limits:{attempts:3,events_per_attempt:120,log_characters:1500,error_stack_characters:6000},omitted_attempts:this.omittedAttempts,attempts:clone(this.attempts)};}
 emit(kind,data){
  const attempt=this.attempts.at(-1);attempt.events.push({kind,at:new Date().toISOString(),data});
  if(attempt.events.length>120){attempt.events.shift();attempt.omitted_events++;}
  try{this.onChange(this.snapshot());}catch{/* Diagnostic display must not change model execution. */}
 }
 phase(name){this.attempts.at(-1).phase=name;this.emit('phase',{name});}
 async load(){
  if(this.loading)throw Error('A model load is already in progress');
  if(this.requiresReload)throw Error('Reload this page before retrying model initialization. The source tools remain available.');
  this.loading=true;
  const attempt={number:(this.attempts.at(-1)?.number||0)+1,started_at:new Date().toISOString(),status:'loading',phase:'preflight',events:[],omitted_events:0};
  this.attempts.push(attempt);if(this.attempts.length>3){this.attempts.shift();this.omittedAttempts++;}
  let engine,recordLogs=true;
  try{
   const nav=this.env.navigator;
   this.emit('browser',{user_agent:bounded(nav.userAgent||'',600),device_memory_GB_hint:typeof nav.deviceMemory==='number'?nav.deviceMemory:null,notice:'A browser hint is not measured available RAM.'});
   if(!nav.gpu)throw Error('This browser does not expose WebGPU. MPLPB remains available without the optional model.');
   const adapter=await nav.gpu.requestAdapter();if(!adapter)throw Error('No usable browser GPU was found.');
   const limits={};for(const key of ['maxBufferSize','maxStorageBufferBindingSize','maxComputeWorkgroupStorageSize','maxComputeInvocationsPerWorkgroup'])limits[key]=Number.isFinite(adapter.limits[key])?adapter.limits[key]:null;
   this.emit('gpu_adapter',{features:Array.from(adapter.features).slice(0,128).map(x=>bounded(x,100)).sort(),limits});
   this.phase('configuration');
   const configResponse=await this.env.fetch(new URL('ai/model.json',this.env.document.baseURI));
   if(!configResponse.ok)throw Error('Optional model assets are unavailable in this build; use the published browser site.');
   const configuration=await configResponse.json();
   attempt.model={id:configuration.model_id,runtime:configuration.runtime,record:configuration.record};
   if(!adapter.features.has('shader-f16'))throw Error('This Phi-4 format requires WebGPU shader-f16 support.');
   const minimum=configuration.minimum_tensor_buffer_bytes;
   if(!Number.isFinite(minimum)||minimum<=0||limits.maxBufferSize===null||limits.maxStorageBufferBindingSize===null||limits.maxBufferSize<minimum||limits.maxStorageBufferBindingSize<minimum)throw Error('This GPU cannot establish the buffer capacity required by the model.');
   this.phase('runtime_download');
   const runtimeResponse=await this.env.fetch(new URL('ai/webllm.mjs',this.env.document.baseURI));
   if(!runtimeResponse.ok)throw Error('Optional runtime download failed.');
   const bytes=await runtimeResponse.arrayBuffer();
   this.phase('runtime_integrity');
   const hash=Array.from(new Uint8Array(await this.env.crypto.subtle.digest('SHA-256',bytes))).map(n=>n.toString(16).padStart(2,'0')).join('');
   if(hash!==configuration.runtime.sha256)throw Error('Optional runtime bytes differ from the pinned build.');
   this.emit('runtime_verified',{sha256:hash,bytes:bytes.byteLength});
   this.phase('runtime_import');
   let runtime;
   if(this.env.importRuntime)runtime=await this.env.importRuntime(bytes);
   else{
    const url=URL.createObjectURL(new Blob([bytes],{type:'text/javascript'}));
    try{runtime=await import(url);}finally{URL.revokeObjectURL(url);}
   }
   this.phase('engine_initialization');
   // Constructor + reload is the documented equivalent of CreateMLCEngine.
   // Retaining the instance permits an unload attempt after failed initialization.
   engine=new runtime.MLCEngine({appConfig:{model_list:[configuration.record]},logLevel:'INFO',initProgressCallback:progress=>{
    attempt.last_progress={text:bounded(progress.text),progress:Number.isFinite(progress.progress)?progress.progress:null,time_elapsed:Number.isFinite(progress.timeElapsed)?progress.timeElapsed:null};
    this.emit('progress',clone(attempt.last_progress));
   }});
   // WebLLM 0.2.87 passes this instance logger to TVM's __console_log import.
   // It is version-pinned; fail visibly if that expected hook changes. No global
   // console is replaced and logs after initialization are not retained here.
   if(typeof engine.logger!=='function')throw Error('The pinned runtime loader logger is unavailable.');
   const originalLogger=engine.logger;
   engine.logger=(...args)=>{if(recordLogs)this.emit('runtime_log',{text:bounded(args.map(x=>bounded(x)).join(' '))});try{originalLogger(...args);}catch{}};
   await engine.reload(configuration.model_id);
   recordLogs=false;attempt.status='ready';attempt.phase='ready';this.emit('ready',{notice:'Initialization resolved. Download progress alone did not establish readiness; response quality is not certified.'});
   return {engine,configuration};
  }catch(error){
   attempt.status='failed';attempt.failed_phase=attempt.phase;this.requiresReload=attempt.phase==='engine_initialization';attempt.requires_page_reload=this.requiresReload;attempt.error=describeError(error);this.emit('failure',clone(attempt.error));
   if(engine){let timer;try{
    await Promise.race([engine.unload(),new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error('Runtime cleanup timed out after 3000 ms')),3000);})]);
    this.emit('cleanup',{result:'unload_completed',notice:'Not a guarantee that every partial GPU allocation was reclaimed.'});
   }catch(cleanupError){this.emit('cleanup',{result:'unload_incomplete',error:describeError(cleanupError)});}finally{clearTimeout(timer);}}
   throw error;
  }finally{recordLogs=false;this.loading=false;}
 }
}
root.MPLPBModelLoader={Loader,describeError};
if(typeof module==='object'&&module.exports)module.exports=root.MPLPBModelLoader;
})(typeof globalThis==='object'?globalThis:this);
