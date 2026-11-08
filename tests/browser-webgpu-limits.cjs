// Execute actual upstream/patched device negotiation using authored adapters.
// No neural weights or physical GPU are used by these resource-boundary checks.
'use strict';
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict');
const {execFileSync}=require('node:child_process'),{pathToFileURL}=require('node:url'),{createHash}=require('node:crypto'),zlib=require('node:zlib');
const MiB=1024*1024,checks=[];
async function run(){
 const manifest=JSON.parse(fs.readFileSync('assets/ai/manifest.json','utf8')).runtime;
 const packed=Buffer.concat(manifest.parts.map(p=>Buffer.from(fs.readFileSync(path.join('assets/ai',p.path),'utf8'),'base64'))),upstream=zlib.gunzipSync(packed);
 assert.equal(createHash('sha256').update(upstream).digest('hex'),manifest.uncompressed_sha256);
 const active=execFileSync(process.env.PYTHON||'python3',['-c','import sys; from tools.build_ai_assets import runtime; sys.stdout.buffer.write(runtime())'],{maxBuffer:16*1024*1024});
 assert.equal(createHash('sha256').update(active).digest('hex'),manifest.local_patch.output_sha256);
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'mplpb-device-limit-test-')),nav=Object.getOwnPropertyDescriptor(globalThis,'navigator'),originalLog=console.log;
 try{
  const source=(body,extra='')=>Buffer.concat([body,Buffer.from('\nexport const diagnosticTVM=libExports$2;\n'+extra)]);
  fs.writeFileSync(path.join(dir,'upstream.mjs'),source(upstream));fs.writeFileSync(path.join(dir,'active.mjs'),source(active,'export {mplpbValidateDeviceLimits};'));
  const old=await import(pathToFileURL(path.join(dir,'upstream.mjs')).href),current=await import(pathToFileURL(path.join(dir,'active.mjs')).href);
  async function negotiate(runtime,buffer,binding){let requested;const adapter={info:{description:'authored adapter',vendor:'fixture'},features:new Set(['shader-f16']),limits:{maxBufferSize:buffer,maxStorageBufferBindingSize:binding,maxComputeWorkgroupStorageSize:32768,maxStorageBuffersPerShaderStage:16,maxComputeInvocationsPerWorkgroup:1024},requestDevice:async request=>{requested=request;return{limits:request.requiredLimits,features:new Set(request.requiredFeatures)};}};Object.defineProperty(globalThis,'navigator',{configurable:true,value:{gpu:{requestAdapter:async()=>adapter}}});const output=await runtime.diagnosticTVM.detectGPUDevice();return {requested,output};}
  console.log=()=>{};const baseline=await negotiate(old,512*MiB,512*MiB);console.log=originalLog;
  assert.equal(baseline.requested.requiredLimits.maxBufferSize,256*MiB);assert.equal(baseline.requested.requiredLimits.maxStorageBufferBindingSize,128*MiB);assert(baseline.output.device.limits.maxBufferSize<307298304);checks.push('upstream reproduces insufficient negotiated capacity on 512 MiB adapter');
  for(const [buffer,binding] of [[256,128],[384,384],[512,512],[768,512],[1024,1024],[2048,2048]]){
   const r=await negotiate(current,buffer*MiB,binding*MiB),limits=r.requested.requiredLimits;
   assert.equal(limits.maxBufferSize,Math.min(1024,buffer)*MiB);assert.equal(limits.maxStorageBufferBindingSize,Math.min(1024,binding)*MiB);
   assert(limits.maxBufferSize<=buffer*MiB);assert(limits.maxStorageBufferBindingSize<=binding*MiB);
   assert.equal(limits.maxComputeWorkgroupStorageSize,32768);assert.equal(limits.maxStorageBuffersPerShaderStage,10);assert.deepEqual(r.requested.requiredFeatures,['shader-f16']);
   checks.push('bounded actual request for adapter '+buffer+'/'+binding+' MiB');
  }
  const validate=current.mplpbValidateDeviceLimits,min={mplpb_minimum_tensor_buffer_bytes:307298304};
  assert.deepEqual(validate(min,{limits:{maxBufferSize:512*MiB,maxStorageBufferBindingSize:512*MiB}}),{maxBufferSize:512*MiB,maxStorageBufferBindingSize:512*MiB});checks.push('actual negotiated 512 MiB device accepts declared tensor minimum');
  assert.throws(()=>validate(min,{limits:{maxBufferSize:256*MiB,maxStorageBufferBindingSize:128*MiB}}),/Negotiated GPU device cannot hold/);checks.push('actual undersized device rejected even when adapter was sufficient');
  assert.throws(()=>validate(min,{limits:{maxBufferSize:512*MiB,maxStorageBufferBindingSize:256*MiB}}),/maxStorageBufferBindingSize/);checks.push('binding near miss rejected separately from buffer allocation');
  assert.throws(()=>validate({mplpb_minimum_tensor_buffer_bytes:NaN},{limits:{}}),/cannot hold/);assert.throws(()=>validate(min,{limits:{}}),/cannot hold/);checks.push('missing actual limits and invalid declared minimum fail closed');
  validate({},{limits:{maxBufferSize:256*MiB,maxStorageBufferBindingSize:128*MiB}});checks.push('upstream callers without host minimum remain compatible');
  console.log(JSON.stringify({role:'Actual pinned production functions, authored adapter/device values; not physical GPU or neural/human validation',checks:checks.length,passed:true,cases:checks},null,2));
 }finally{console.log=originalLog;if(nav)Object.defineProperty(globalThis,'navigator',nav);else delete globalThis.navigator;fs.rmSync(dir,{recursive:true,force:true});}
}
run().catch(error=>{console.error(error);process.exitCode=1;});
