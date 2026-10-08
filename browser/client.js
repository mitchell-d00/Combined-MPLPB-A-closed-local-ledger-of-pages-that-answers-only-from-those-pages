// Embedded worker runtime; transport replaces /api calls, not the MPLPB engine.
const runtimeBundle=JSON.parse(document.getElementById('mplpb-runtime-bundle').textContent);
let runtimeWorker,runtimeCounter=0,runtimeReady,runtimeLocked=false;
const runtimePending=new Map();
function runtimeRequest(operation,extra={}){return new Promise((resolve,reject)=>{const id=++runtimeCounter;runtimePending.set(id,{resolve,reject});runtimeWorker.postMessage({id,operation,...extra});});}
async function browserApi(url,options){await runtimeReady;return runtimeRequest('call',{url,payload:options?.body||''});}
async function initializeBrowserRuntime(){
 $('connection').hidden=false;$('connection-error').textContent='Starting embedded Python in your browser…';
 try{localStorage.setItem('mplpb-storage-probe','1');if(localStorage.getItem('mplpb-storage-probe')!=='1')throw Error('Storage refused');localStorage.removeItem('mplpb-storage-probe');}catch{throw Error('Browser storage is blocked; session resume cannot be guaranteed. Allow storage or use HTTPS hosting.');}
 if(!globalThis.Worker||!globalThis.WebAssembly)throw Error('This browser needs WebAssembly and Web Workers.');
 // Avoid two writers sharing the same browser save filesystem when Web Locks are available.
 if(!navigator.locks)throw Error('This browser lacks Web Locks; a single safe writer cannot be established. Use a current browser or HTTPS hosting.');
 if(navigator.locks){await new Promise((resolve,reject)=>{navigator.locks.request('mplpb-browser-save-v1',{ifAvailable:true},lock=>{if(!lock){reject(Error('MPLPB is already open in another tab. Close that tab before opening this save.'));return;}runtimeLocked=true;resolve();return new Promise(()=>{});}).catch(reject);});}
 const workerURL=URL.createObjectURL(new Blob([runtimeBundle.worker],{type:'text/javascript'}));
 runtimeWorker=new Worker(workerURL);URL.revokeObjectURL(workerURL);
 runtimeWorker.onmessage=e=>{const item=runtimePending.get(e.data.id);if(!item)return;runtimePending.delete(e.data.id);if(e.data.error)item.reject(Error(e.data.error));else item.resolve(e.data.result);};
 runtimeWorker.onerror=e=>{for(const item of runtimePending.values())item.reject(Error(e.message||'Browser runtime failed'));runtimePending.clear();};
 await runtimeRequest('initialize',{bundle:runtimeBundle});$('connection').hidden=true;
}
function startBrowserRuntime(){runtimeReady=initializeBrowserRuntime();runtimeReady.then(()=>boot()).catch(error=>{$('connection').hidden=false;$('connection-error').textContent=error.message;});}
