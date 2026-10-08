// Serialized Python operations in a dedicated worker. No host filesystem mounts.
let py, queue=Promise.resolve(), failed=false;
const decode=value=>Uint8Array.from(atob(value),c=>c.charCodeAt(0));
const text=value=>new TextDecoder().decode(decode(value));
const sync=populate=>new Promise((resolve,reject)=>py.FS.syncfs(populate,error=>error?reject(error):resolve()));
async function initialize(bundle){
 for(const [name,expected] of Object.entries(bundle.runtime_manifest)){const digest=await crypto.subtle.digest('SHA-256',decode(bundle.runtime[name]));if(Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,'0')).join('')!==expected)throw Error('Runtime bytes differ: '+name);}
 for(const [name,expected] of Object.entries(bundle.manifest)){const digest=await crypto.subtle.digest('SHA-256',decode(bundle.files[name]));if(Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,'0')).join('')!==expected)throw Error('Bundled source bytes differ: '+name);}
 const core=bundle.runtime, originalFetch=globalThis.fetch;
 const base='https://mplpb-runtime.invalid/';
 globalThis.fetch=(url,options)=>{const target=String(url);if(target.startsWith(base)){const name=target.slice(base.length);if(!core[name])return Promise.reject(Error('Unbundled runtime asset: '+name));return Promise.resolve(new Response(decode(core[name]),{headers:{'Content-Type':name.endsWith('.wasm')?'application/wasm':'application/octet-stream'}}));}return originalFetch(url,options);};
 const moduleURL=URL.createObjectURL(new Blob([text(core['pyodide.asm.mjs'])],{type:'text/javascript'}));
 const loaderURL=URL.createObjectURL(new Blob([text(core['pyodide.js'])],{type:'text/javascript'}));
 await import(loaderURL);
 py=await loadPyodide({indexURL:base,createPyodideModule:(await import(moduleURL)).default,
     lockFileContents:text(core['pyodide-lock.json']),packageBaseUrl:base,packages:[],enableRunUntilComplete:false});
 URL.revokeObjectURL(moduleURL);URL.revokeObjectURL(loaderURL);
 globalThis.fetch=originalFetch;
 for(const [name,value] of Object.entries(bundle.files)){
  if(name.startsWith('/')||name.split('/').includes('..'))throw Error('Invalid bundled path');
  const path='/app/'+name;py.FS.mkdirTree(path.slice(0,path.lastIndexOf('/')));py.FS.writeFile(path,decode(value));
 }
 py.FS.mkdirTree('/mplpb-browser-save-v1');
 py.FS.symlink('/mplpb-browser-save-v1','/app/local');
 if(typeof indexedDB==='undefined')throw Error('Browser storage unavailable. Use a browser with IndexedDB or host this HTML over HTTPS.');
 py.FS.mount(py.FS.filesystems.IDBFS,{},'/mplpb-browser-save-v1');await sync(true);
 await py.runPythonAsync("import sys, os\nsys.path.insert(0, '/app')\nos.chdir('/app')\nfrom browser.bridge import call_json");
 // Probe a durable write before enabling chat: never silently fall back to volatile state.
 py.FS.writeFile('/app/local/.runtime-save-probe',new Uint8Array([1]));await sync(false);
 py.FS.unlink('/app/local/.runtime-save-probe');await sync(false);
 return {runtime:'Pyodide 314.0.7',storage:'IndexedDB',engine:'unchanged Python MPLPB'};
}
self.onmessage=e=>{queue=queue.then(async()=>{const {id,operation,bundle,url,payload}=e.data;try{
 if(failed)throw Error('Runtime stopped after a storage failure. Reload and restore the last durable state.');
 if(operation==='initialize'){const result=await initialize(bundle);postMessage({id,result});return;}
 if(!py)throw Error('Runtime not initialized');
 py.globals.set('_browser_url',url);py.globals.set('_browser_payload',payload||'');
 let result,error;
 try{result=JSON.parse(await py.runPythonAsync('await call_json(_browser_url, _browser_payload)'));if(result._browser_transport_error)error=result._browser_transport_error;}catch(exc){error=String(exc);}
 // Also retain observations archived by an import that was rejected.
 try{await sync(false);}catch(exc){failed=true;throw Error('Browser save failed: '+String(exc));}
 if(error)throw Error(error);postMessage({id,result});
 }catch(error){postMessage({id,error:String(error)});}});};
