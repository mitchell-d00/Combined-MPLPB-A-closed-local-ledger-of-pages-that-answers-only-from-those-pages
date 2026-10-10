// Real WASM App/bridge, real Wikipedia HTTP via curl; no fixture source responses.
// Node transport substitutes pyfetch only; this does not test browser CORS/IndexedDB.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {createHash} from 'node:crypto';
const exec=promisify(execFile);
const [coreArg,htmlArg,inputArg,outArg]=process.argv.slice(2);
if(!outArg)throw Error('Usage: node tools/live_conversation_wasm.mjs CORE HTML INPUT.jsonl OUTPUT_DIR');
const core=path.resolve(coreArg),out=path.resolve(outArg);fs.mkdirSync(out,{recursive:true});
const bundle=JSON.parse(fs.readFileSync(htmlArg,'utf8').match(/<script id="mplpb-runtime-bundle" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const hash=b=>createHash('sha256').update(b).digest('hex');
for(const [name,body] of Object.entries(bundle.files))if(hash(Buffer.from(body,'base64'))!==bundle.manifest[name])throw Error('bundle hash mismatch '+name);
const {loadPyodide}=await import(pathToFileURL(path.join(core,'pyodide.mjs')));
const py=await loadPyodide({indexURL:core+path.sep,enableRunUntilComplete:false});
for(const [name,body] of Object.entries(bundle.files)){const p='/app/'+name;py.FS.mkdirTree(path.dirname(p));py.FS.writeFile(p,Buffer.from(body,'base64'));}
let requests=0,currentCase=null;
py.registerJsModule('live_http',{download:async url=>{
 const u=new URL(url);if(!['en.wikipedia.org','simple.wikipedia.org'].includes(u.hostname)||u.pathname!='/w/api.php')throw Error('Unexpected live source');
 requests++;const id=String(requests).padStart(5,'0');
 const target=path.join(out,'http-'+id+'.json');const started=new Date().toISOString();
 try{
 const {stdout}=await exec('python3',['tools/live_wiki_transport.py',url,target,path.resolve(out,'../live-http-cache')],{maxBuffer:3000000});
 const metadata=JSON.parse(stdout);
 const raw=fs.existsSync(target)?fs.readFileSync(target):Buffer.from('');
 if(metadata.http_status!==200)throw Error('Wikipedia HTTP '+metadata.http_status+'; retry after '+metadata.retry_after_seconds+' seconds');
 if(raw.length>2000000)throw Error('Wikipedia response exceeds 2 MB');
 fs.appendFileSync(path.join(out,'network.jsonl'),JSON.stringify({...metadata,case:currentCase,id,sha256:hash(raw),bytes:raw.length})+'\n');
 return JSON.stringify({raw:raw.toString('base64'),metadata});
 }catch(e){fs.appendFileSync(path.join(out,'network.jsonl'),JSON.stringify({case:currentCase,id,url,started,error:String(e.message)})+'\n');throw e;}
}});
await py.runPythonAsync(`import sys,os,json,base64\nsys.path.insert(0,'/app')\nos.chdir('/app')\nfrom browser import bridge as B\nfrom tools.ledger_ui import App\nfrom pathlib import Path\nfrom live_http import download\nasync def live_remote(url):\n    obj=json.loads(await download(url))\n    return base64.b64decode(obj['raw']),obj['metadata']\nB.remote=live_remote`);
const cases=fs.readFileSync(inputArg,'utf8').trim().split('\n').map(JSON.parse);let user=null,sid=null;let count=0;
const rows=[];
for(const c of cases){
 currentCase=c.id;
 if(c.user!==user){user=c.user;sid=null;py.globals.set('_user',user);await py.runPythonAsync("B.app=App(topic_base=Path('/app/local')/str(_user)/'topics')");
 const mode=Number(user.split('-').at(-1))%2===0?'load MPLPB':'just chat';
 py.globals.set('_setup',JSON.stringify({corpus:'logic',message:mode}));
 const setup=JSON.parse(await py.runPythonAsync("await B.call_json('/api/chat',_setup)"));sid=setup.session;
 py.globals.set('_setup',JSON.stringify({corpus:'logic',session:sid,message:'I had a bad day'}));
 const social=JSON.parse(await py.runPythonAsync("await B.call_json('/api/chat',_setup)"));
 fs.appendFileSync(path.join(out,'setup.jsonl'),JSON.stringify({user,mode,setup,social})+'\n');
 }
 const before=requests;const started=Date.now();const data={corpus:'logic',session:sid,message:c.message,wiki:'english',auto_wiki:true,default_chat:true};
 py.globals.set('_data',JSON.stringify(data));let result;
 try{result=JSON.parse(await py.runPythonAsync("await B.call_json('/api/chat',_data)"));}catch(e){result={_browser_transport_error:String(e)};}
 if(result.session)sid=result.session;
 const row={...c,elapsed_ms:Date.now()-started,network_requests:requests-before,result};rows.push(row);
 fs.appendFileSync(path.join(out,'responses.jsonl'),JSON.stringify(row)+'\n');
 count++;if(count%10===0)console.log(JSON.stringify({completed:count,total:cases.length,requests,last:c.message,kind:result.response?.kind,lookup:result.automatic_lookup?.status,error:result._browser_transport_error}));
 if(count===cases.length||cases[count].user!==user){py.globals.set('_sid',sid||'');
 const audit=await py.runPythonAsync("json.dumps({'user':_user,'chain_intact':B.app.export_chat({'session':_sid})['chain_intact'] if _sid else False,'collections':len(B.app.collections.entries())})");fs.appendFileSync(path.join(out,'sessions.jsonl'),audit+'\n');}
}
const summary={cases:rows.length,requests,transport_errors:rows.filter(r=>r.result._browser_transport_error).length,lookup_status:{},kinds:{},source_authorities:{},bundle_manifest:bundle.manifest,independent:false,scope:'Synthetic development smoke: Node WebAssembly, live Wikipedia HTTP, no browser CORS or IndexedDB coverage; no semantic accuracy score.'};
for(const r of rows){const p=r.result;for(const [field,v] of [['lookup_status',p.automatic_lookup?.status||'none'],['kinds',p.response?.kind||'error'],['source_authorities',p.response?.authority||'unspecified']])summary[field][v]=(summary[field][v]||0)+1;}
fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(summary,null,2));
await py.runPythonAsync("import tarfile\nwith tarfile.open('/saved-captures.tar.gz','w:gz') as archive:\n    archive.add('/app/local',arcname='local')");
fs.writeFileSync(path.join(out,'saved-captures.tar.gz'),py.FS.readFile('/saved-captures.tar.gz'));
console.log(JSON.stringify({done:true,cases:summary.cases,requests,errors:summary.transport_errors,kinds:summary.kinds,lookup:summary.lookup_status}));
