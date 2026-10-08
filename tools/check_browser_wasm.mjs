import {pathToFileURL} from 'node:url';
import path from 'node:path';
const core=path.resolve(process.argv[2]||'');
const htmlPath=path.resolve(process.argv[3]||'dist/MPLPB_Browser.html');
if(!process.argv[2])throw Error('Usage: node tools/check_browser_wasm.mjs CORE_DIRECTORY [HTML]');
const {loadPyodide}=await import(pathToFileURL(path.join(core,'pyodide.mjs')));
import fs from 'node:fs';
const html=fs.readFileSync(htmlPath,'utf8');
const bundle=JSON.parse(html.match(/<script id="mplpb-runtime-bundle" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const py=await loadPyodide({indexURL:core+path.sep,enableRunUntilComplete:false});
for(const [name,encoded] of Object.entries(bundle.files)){
 const path='/app/'+name;py.FS.mkdirTree(path.slice(0,path.lastIndexOf('/')));py.FS.writeFile(path,Buffer.from(encoded,'base64'));
}
await py.runPythonAsync("import sys, os\nsys.path.insert(0, '/app')\nos.chdir('/app')\nfrom browser.bridge import call_json");
async function call(route,data){py.globals.set('_u',route);py.globals.set('_d',data===undefined?'':JSON.stringify(data));return JSON.parse(await py.runPythonAsync('await call_json(_u,_d)'));}
const state=await call('/api/state'); console.log('corpora',state.corpora.map(x=>x.key));
const ambiguous=await call('/api/query',{corpus:'canned',question:'Phrynomedusa vanzolinii Hyundai Engineering and Construction'});
if(ambiguous.reader.kind!=='ambiguous')throw Error('wrong name guard');
const relation=await call('/api/chat',{corpus:'logic',message:'relate Dungeons and Dragons -> game'});
if(relation.response.kind!=='relations')throw Error('wrong relation');
const sid=relation.session;
await call('/api/chat',{corpus:'logic',session:sid,message:'remember I study dinosaurs'});
const summary=await call('/api/chat',{corpus:'logic',session:sid,message:'summarize Dungeons and Dragons'});
if(!summary.response.extractive)throw Error('wrong summary');
const withheld=await call('/api/query',{corpus:'canned',profile:'external',question:'Phrynomedusa vanzolinii'});
if(withheld.reader.kind==='return')throw Error('external leaked');
const saved=await call('/api/chat/resume',{session:sid});if(!saved.chain_intact||saved.notes[0]!=='I study dinosaurs')throw Error('resume failed');
await py.runPythonAsync(`
import hashlib, json
from browser import bridge as B
from tools.ledger_ui import App
from tools import wiki_live_eval as W
B.app = App()
assert any('I study dinosaurs' in s.get('mind', {}).get('notes', []) for s in B.app.sessions.values())
source = "Cat is a synthetic source fixture."
raw = json.dumps({'query': {'pages': {'1': {'title': 'Cat', 'pageid': 1,
 'revisions': [{'revid': 100, 'timestamp': '2026-10-08T12:00:00Z', 'slots': {'main':
 {'*': source, 'sha1': hashlib.sha1(source.encode()).hexdigest(), 'contentmodel': 'wikitext'}}}]}}}}).encode()
async def fixture_remote(url):
 return raw, {'url': url, 'retrieved_at': '2026-10-08T12:01:00Z', 'http_status': 200}
B.remote = fixture_remote
`);
const imported=await call('/api/chat',{corpus:'logic',message:'import Cat'});
if(imported.corpus!=='topics'||!imported.response.context)throw Error('WASM source import failed');
const importedAsk=await call('/api/chat',{corpus:'topics',session:imported.session,message:'what is it?'});
if(importedAsk.response.kind!=='return')throw Error('WASM imported context failed');
console.log('PASS real WebAssembly: ownership ambiguity, relation proof, summary, external withholding, memory, saved transcript/relaunch and fixture source import.');
fs.writeFileSync(path.join(path.dirname(htmlPath),'wasm-validation.json'),JSON.stringify({runtime:bundle.runtime_version,passed:true,corpora:state.corpora.map(x=>x.key),ambiguous:ambiguous.reader.kind,relation:relation.response.kind,summary:summary.response.kind,withheld:withheld.reader.kind,chain_intact:saved.chain_intact,fixture_import_passed:true,virtual_save_relaunch_passed:true,browser_layout_tested:false,indexeddb_tested:false,live_wiki_tested:false},null,2));
