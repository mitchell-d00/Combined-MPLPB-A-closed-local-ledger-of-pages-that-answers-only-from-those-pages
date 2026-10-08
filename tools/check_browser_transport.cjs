// Transport/storage ordering checks. No graphical browser or IndexedDB implementation.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),{webcrypto}=require('node:crypto');
const workerCode=fs.readFileSync('browser/worker.js','utf8'),clientCode=fs.readFileSync('browser/client.js','utf8');
async function workerTests(){
 const messages=[],events=[];let rejectSave=false,rejectPython=false;
 const fake={globals:{set:(key,value)=>events.push(key)},FS:{syncfs:(load,cb)=>{events.push('save');cb(rejectSave?Error('quota'):null);}},runPythonAsync:async()=>{events.push('python');if(rejectPython)throw Error('source revision conflict');return '{"ok":true}';}};
 const c=vm.createContext({console,Promise,self:{},postMessage:data=>{events.push('response');messages.push(data);},fake,atob,value:null,Uint8Array,TextDecoder,crypto:webcrypto});
 vm.runInContext(workerCode,c);vm.runInContext('py=fake',c);
 c.self.onmessage({data:{id:1,url:'/api/chat'}});c.self.onmessage({data:{id:2,url:'/api/chat'}});await vm.runInContext('queue',c);
 assert.equal(messages.length,2);assert.deepEqual(events.filter(x=>['python','save','response'].includes(x)),['python','save','response','python','save','response']);
 rejectPython=true;c.self.onmessage({data:{id:3,url:'/api/chat'}});await vm.runInContext('queue',c);assert.match(messages.at(-1).error,/source revision conflict/);assert.deepEqual(events.slice(-2),['save','response']);
 rejectPython=false;rejectSave=true;c.self.onmessage({data:{id:4,url:'/api/chat'}});await vm.runInContext('queue',c);assert.match(messages.at(-1).error,/save failed/);
 const count=events.filter(x=>x==='python').length;c.self.onmessage({data:{id:5,url:'/api/chat'}});await vm.runInContext('queue',c);assert.equal(events.filter(x=>x==='python').length,count);assert.match(messages.at(-1).error,/Runtime stopped/);
 const b=vm.createContext({console,Promise,self:{},postMessage:x=>messages.push(x),atob,Uint8Array,TextDecoder,crypto:webcrypto});vm.runInContext(workerCode,b);
 b.self.onmessage({data:{id:6,operation:'initialize',bundle:{runtime_manifest:{'bad':'00'},runtime:{bad:btoa('bad')}}}});await vm.runInContext('queue',b);assert.match(messages.at(-1).error,/Runtime bytes differ/);
}
async function clientTests(){
 const elements={connection:{hidden:true},'connection-error':{textContent:''}},requests=[],storage={};let booted=false;
 class Worker {constructor(url,options){assert.equal(options.type,'module');}postMessage(data){requests.push(data);queueMicrotask(()=>this.onmessage({data:{id:data.id,result:{ok:true}}}));}}
 const c=vm.createContext({console,Promise,Map,Error,JSON,Blob,URL,Worker,WebAssembly,navigator:{locks:{request:async(name,opts,fn)=>fn({})}},localStorage:{setItem:(k,v)=>storage[k]=v,getItem:k=>storage[k],removeItem:k=>delete storage[k]},document:{getElementById:()=>({textContent:JSON.stringify({worker:'test'})})},$:key=>elements[key],boot:()=>booted=true});
 vm.runInContext(clientCode,c);vm.runInContext('startBrowserRuntime()',c);await vm.runInContext('runtimeReady',c);await Promise.resolve();assert.equal(booted,true);assert.equal(elements.connection.hidden,true);
 const result=await vm.runInContext('browserApi("/api/chat",{body:"{\\"message\\":\\"hi\\"}"})',c);assert.equal(result.ok,true);assert.equal(requests.at(-1).url,'/api/chat');assert.equal(requests.at(-1).payload,'{"message":"hi"}');
}
(async()=>{await workerTests();await clientTests();console.log('PASS browser transport: serialized engine calls, save-before-success, conflict retention, quota stop, embedded hash rejection and client RPC. No browser layout/IndexedDB test.');})().catch(error=>{console.error(error);process.exitCode=1;});
