// Focused policy workflow against actual packaged Python/WebAssembly, not a DOM.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const [coreArg, htmlArg, output] = process.argv.slice(2);
if (!coreArg || !htmlArg || !output) throw Error('Usage: node tools/check_collection_wasm.mjs CORE HTML NEW_REPORT');
if(fs.existsSync(output))throw Error('Report history must not be overwritten');
const core=path.resolve(coreArg), html=fs.readFileSync(htmlArg,'utf8');
const bundle=JSON.parse(html.match(/<script id="mplpb-runtime-bundle" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const {loadPyodide}=await import(pathToFileURL(path.join(core,'pyodide.mjs')));
const py=await loadPyodide({indexURL:core+path.sep,enableRunUntilComplete:false});
for(const [name,encoded] of Object.entries(bundle.files)){
 const dest='/app/'+name;py.FS.mkdirTree(dest.slice(0,dest.lastIndexOf('/')));py.FS.writeFile(dest,Buffer.from(encoded,'base64'));
}
await py.runPythonAsync("import sys,os,json,hashlib\nsys.path.insert(0,'/app')\nos.chdir('/app')\nfrom browser import bridge as B");
async function call(route,data){py.globals.set('_route',route);py.globals.set('_payload',JSON.stringify(data??null));return JSON.parse(await py.runPythonAsync('await B.call_json(_route,_payload)'));}
const key=(await call('/api/collections/create',{name:'Packaged policy fixture'})).corpus;
const source={corpus:key,title:'Equipment borrowing',url:'https://example.org/equipment',text:'Equipment borrowing requires two approvals and a deposit of 45 credits unless a waiver applies.'};
const imported=await call('/api/source/import',source);
assert.equal(imported.collection_build.engine_changed,false);
const q='What does equipment borrowing require?';
const first=(await call('/api/query',{corpus:key,question:q})).reader;
assert.equal(first.text,source.text);assert.equal(first.answer_supported,true);
const page=await call('/api/page?'+new URLSearchParams({corpus:key,path:first.path,profile:'internal'}));
assert.equal(page.hash,first.hash);assert.ok(page.text.includes(first.text));
const update={...source,text:source.text.replace('two approvals','three approvals').replace('45','72')};
await call('/api/source/import',update);
assert.equal((await call('/api/query',{corpus:key,question:'What is required for equipment borrowing?'})).reader.text,update.text);
assert.ok((await call('/api/page?'+new URLSearchParams({corpus:key,path:first.path,profile:'internal'})))._browser_transport_error);
const chat=await call('/api/chat',{corpus:key,message:'remember Inspect the waiver. Preserve the old policy.'});
const before=await call('/api/chat/export',{session:chat.session});
// Disk-backed state reload in the WASM process. Actual browser IndexedDB/UI
// remains a separate Chromium check; this does not impersonate that browser.
await py.runPythonAsync('from tools.ledger_ui import App\nB.app=App()');
assert.deepEqual(await call('/api/chat/export',{session:chat.session}),before);
assert.ok((await call('/api/chat/resume',{session:chat.session})).chain_intact);
assert.equal((await call('/api/query',{corpus:key,question:q})).reader.text,update.text);
await call('/api/source/import',{...source,title:'Conflicting policy',url:'https://example.org/competing'});
assert.equal((await call('/api/query',{corpus:key,question:q})).reader.answer_contract.kind,'conflict');
assert.equal((await call('/api/query',{corpus:key,question:q,profile:'external'})).reader.answer_supported,false);
await py.runPythonAsync(`
payload_text='Acquired policy is a source reference.\\n\\nAcquired policy requires a card and a booking.'
sha=hashlib.sha1(payload_text.encode()).hexdigest()
payload={'query':{'pages':{'42':{'pageid':42,'title':'Acquired policy','revisions':[{'revid':403,'timestamp':'2026-10-01T00:00:00Z','sha1':sha,'slots':{'main':{'contentmodel':'wikitext','*':payload_text,'sha1':sha}}}]}}}}
network_calls=[]
async def fixture(url):
 network_calls.append(url)
 return json.dumps(payload).encode(), {'retrieved_at':'2026-10-31T00:00:00Z','http_status':200,'url':url}
B.remote=fixture
`);
const fetched=await call('/api/chat',{corpus:key,message:'import Acquired policy',wiki:'simple'});
assert.equal(fetched.response.kind,'import');
assert.equal((await call('/api/query',{corpus:fetched.corpus,question:'What does acquired policy require?'})).reader.text,'Acquired policy requires a card and a booking.');
const report={schema:'packaged-collection-policy-wasm-v1',passed:true,runtime:'actual Pyodide 314.0.7',
 checks:['import_build_metadata','verbatim_policy_and_conditions','citation_hash_and_body','changed_values_and_revision','retired_citation_rejected','saved_note_reopen','explicit_conflict','delivery_withholding','fixture_network_acquisition'],
 html_sha256:crypto.createHash('sha256').update(html).digest('hex'),runner_sha256:crypto.createHash('sha256').update(fs.readFileSync(process.argv[1])).digest('hex'),
 browser_ui_or_indexeddb_tested:false,live_network_source_tested:false,human_validation:false};
fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(report));
