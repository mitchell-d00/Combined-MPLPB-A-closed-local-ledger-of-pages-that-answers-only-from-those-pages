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
const collection=await call('/api/collections/create',{name:'Dinosaurs smoke'});
await call('/api/source/import',{corpus:collection.corpus,title:'Dinosaurs',url:'https://example.org/dinosaurs',text:'Dinosaurs are a source fixture.'});
const custom=await call('/api/chat',{corpus:collection.corpus,message:'topic Dinosaurs'});
if(custom.response.kind!=='topic')throw Error('WASM collection selection failed');
const customAsk=await call('/api/chat',{corpus:collection.corpus,session:custom.session,message:'what is it?'});
if(customAsk.response.kind!=='return')throw Error('WASM collection chat failed');
const empty=await call('/api/collections/create',{name:'Empty smoke'});
const isolated=await call('/api/query',{corpus:empty.corpus,question:'Dinosaurs'});
if(isolated.reader.kind==='return')throw Error('WASM collections not isolated');
await py.runPythonAsync(`
from urllib.parse import parse_qs, urlsplit
async def crawl_fixture(url):
 if 'list=search' in url:
  return json.dumps({'query':{'search':[{'title':'Cat','pageid':1,'snippet':'not evidence'}]}}).encode(), {'retrieved_at':'2026-10-08T12:01:00Z'}
 return raw, {'url':url,'retrieved_at':'2026-10-08T12:01:00Z','http_status':200}
B.remote = crawl_fixture
`);
const built=await call('/api/chat',{corpus:'logic',session:sid,message:'search cats',wiki:'simple'});
if(built.response?.kind!=='built'||!built.corpus.startsWith('mind-')||built.session===sid)throw Error('WASM automatic collection failed: '+JSON.stringify(built));
const crawlAsk=await call('/api/chat',{corpus:built.corpus,session:built.session,message:'what is it?'});
if(crawlAsk.response.kind!=='return')throw Error('WASM crawl context failed');
const old=await call('/api/chat/resume',{session:sid});
if(old.notes[0]!=='I study dinosaurs')throw Error('WASM new collection overwrote previous chat');
const noBackend=await call('/api/chat',{corpus:'logic',message:'search cats',wiki:'web'});
if(!noBackend._browser_transport_error)throw Error('Unconfigured web crawler did not stop');
const help=await call('/api/chat',{corpus:built.corpus,session:built.session,message:'How do I clear all?'});
if(help.response.kind!=='help'||!help.response.message.includes('Clear all my collections')||help.response.sources.length)throw Error('WASM tutorial help failed');
const extra=await call('/api/collections/create',{name:'Bulk clear fixture'});
const cleared=await call('/api/collections/reset-many',{corpora:[built.corpus,extra.corpus]});
if(cleared.count!==2)throw Error('WASM bulk clear failed');
const retained=await call('/api/chat/resume',{session:sid});
if(retained.notes[0]!=='I study dinosaurs')throw Error('WASM bulk clear touched other chat');
const guide=await call('/api/chat',{corpus:'logic',session:sid,message:'guide me'});
const discussion=await call('/api/chat',{corpus:'logic',session:sid,message:'let’s talk about it'});
if(discussion.response.kind!=='conversation'||discussion.response.sources.length||discussion.response.response_structure.factual_claims!==false)throw Error('WASM conversation boundary failed');
if(guide.response.guide?.step!==1||!guide.response.suggestions.includes('show my MPLPB'))throw Error('WASM guide failed');
const next=await call('/api/chat',{corpus:'logic',session:sid,message:'next step'});
if(next.response.guide?.step!==2)throw Error('WASM guide progression failed');
const askHelp=await call('/api/query',{corpus:'logic',question:'How do I clear mplpb some or all?'});
if(!askHelp.help||askHelp.reader.kind!=='help'||askHelp.gate.sources.length)throw Error('WASM Ask help routing failed');
console.log('PASS real WebAssembly: ownership, relation proof, summary, withholding, memory, saved relaunch, fixture imports and isolated collections.');
fs.writeFileSync(path.join(path.dirname(htmlPath),'wasm-validation.json'),JSON.stringify({runtime:bundle.runtime_version,passed:true,corpora:state.corpora.map(x=>x.key),ambiguous:ambiguous.reader.kind,relation:relation.response.kind,summary:summary.response.kind,withheld:withheld.reader.kind,chain_intact:saved.chain_intact,fixture_import_passed:true,virtual_save_relaunch_passed:true,browser_layout_tested:false,indexeddb_tested:false,live_wiki_tested:false},null,2));
