// Public JavaScript contract exercised against the real Python browser bridge.
// Standard Node/Python only; isolated save folder and no live source requests.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {spawn}=require('node:child_process'),{createInterface}=require('node:readline');
const html=fs.readFileSync('index.html','utf8');
const code=html.match(/\/\/ BEGIN MPLPB PUBLIC API[^\n]*\n([\s\S]*?)\/\/ END MPLPB PUBLIC API/)[1];
const python=spawn(process.env.PYTHON||'python3',['-u','-c',`
import asyncio, json, sys, tempfile
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import hashlib
from browser import bridge as B
from tools.ledger_ui import App
network_calls=[]
async def fixture_remote(url):
 network_calls.append(url)
 q=parse_qs(urlsplit(url).query)
 if 'srsearch' in q:
  payload={'query':{'search':[{'title':'Cat','pageid':1,'snippet':'navigation only'}]}}
 else:
  assert q['titles']==['Cat']
  text='Cat is an animal in this synthetic API test.'
  payload={'query':{'pages':{'1':{'title':'Cat','pageid':1,'revisions':[{'revid':100,'timestamp':'2026-10-08T12:00:00Z','slots':{'main':{'*':text,'sha1':hashlib.sha1(text.encode()).hexdigest(),'contentmodel':'wikitext'}}}]}}}}
 return json.dumps(payload).encode(), {'url':url,'retrieved_at':'2026-10-08T12:01:00Z','http_status':200}
with tempfile.TemporaryDirectory() as folder:
 B.app=App(topic_base=Path(folder)/'topics')
 with patch.object(B, 'remote', fixture_remote), patch.object(B, 'web_plan', side_effect=AssertionError('Unexpected crawler')), patch('urllib.request.urlopen', side_effect=AssertionError('Unexpected network')):
  for line in sys.stdin:
   request=json.loads(line)
   if request['url']=='test:network-count':
    print(json.dumps(len(network_calls)),flush=True)
    continue
   print(asyncio.run(B.call_json(request['url'],request['payload'])),flush=True)
`],{stdio:['pipe','pipe','inherit']});
const pending=[];
createInterface({input:python.stdout}).on('line',line=>{
 const item=pending.shift();if(!item)return;
 try{const data=JSON.parse(line);if(data._browser_transport_error)throw Error(data._browser_transport_error);item.resolve(data);}catch(e){item.reject(e);}
});
python.on('exit',code=>{for(const item of pending.splice(0))item.reject(Error('Bridge exited: '+code));});
function transport(url,options){return new Promise((resolve,reject)=>{
 pending.push({resolve,reject});python.stdin.write(JSON.stringify({url,payload:options?.body||''})+'\n');
});}
let release;
const started=new Promise(resolve=>release=resolve),calls=[];
const context=vm.createContext({URLSearchParams,api:async(url,options)=>{await started;calls.push(url);return transport(url,options);}});
vm.runInContext(code,context);
const api=context.MPLPB;
function success(result){assert.equal(result.ok,true,JSON.stringify(result));return result.data;}
async function tests(){
 assert.equal(api.version,'1.0.0');assert(Object.isFrozen(api));
 const help=api.help();help.methods.query='changed';assert.notEqual(api.help().methods.query,'changed');
 let settled=false;const waiting=api.ready().then(r=>{settled=true;return r;});
 await new Promise(resolve=>setImmediate(resolve));assert.equal(settled,false);release();
 assert(success(await waiting).corpora.some(c=>c.key==='logic'));
 assert(success(await api.listCorpora()).some(c=>c.key==='studio'));
 const discovered=success(await api.handshake());
 assert.equal(discovered.protocol,'mplpb-agent-handshake');
 assert.equal(discovered.remoteHttpQuery,false);
 assert(discovered.corpora.some(c=>c.key==='logic'));
 assert(api.functions().includes('relay'));

 const q='What is Dungeons and Dragons?';
 const direct=await transport('/api/query',{body:JSON.stringify({corpus:'logic',question:q,profile:'internal'})});
 const answer=success(await api.query(q,{corpus:'logic'}));assert.deepEqual(answer,direct);
 assert.equal(answer.reader.kind,'return');assert(answer.reader.citation);
 const strict=success(await api.relay(q,{corpus:'logic'}));
 assert.equal(strict.reply,answer.reader.text);
 assert.equal(strict.kind,answer.reader.kind);
 assert.deepEqual(strict.decision,answer.reader);
 assert.equal(strict.suggestions.length,0);
 const noAnswer=success(await api.relay('unfindable zzzzzzz',{corpus:'logic'}));
 assert.equal(noAnswer.kind,'not_in_corpus');
 assert.equal(noAnswer.suggestions.length,0);
 assert.equal((await api.relay('hello',{corpus:'logic',mode:'other'})).code,'INVALID_ARGUMENT');
 assert.equal((await api.relay('hello',{corpus:'logic',mode:'chat',includeSuggestions:'yes'})).code,'INVALID_ARGUMENT');
 assert.equal((await api.relay('hello',{corpus:'logic',mode:'query',allowNetwork:true})).code,'INVALID_ARGUMENT');
 const chatRelay=success(await api.relay('hello',{corpus:'logic',mode:'chat'}));
 assert.equal(chatRelay.reply,chatRelay.response.message);
 assert.equal(chatRelay.suggestions.length,0);
 assert.equal(Object.hasOwn(chatRelay.response,'suggestions'),false);
 const optInRelay=success(await api.relay('What could I ask?',{corpus:'logic',mode:'chat',session:chatRelay.session,includeSuggestions:true}));
 assert.equal(optInRelay.reply,optInRelay.response.message);
 assert.deepEqual(optInRelay.suggestions,optInRelay.response.suggestions||[]);

 assert.equal(success(await api.query('Phrynomedusa vanzolinii Hyundai Engineering and Construction',{corpus:'canned'})).reader.kind,'ambiguous');
 assert.equal(success(await api.query('unfindable zzzzzzz',{corpus:'logic'})).reader.kind,'not_in_corpus');
 assert.notEqual(success(await api.query('Phrynomedusa vanzolinii',{corpus:'canned',profile:'external'})).reader.kind,'return');
 const candidates=success(await api.query('Phrynomedusa vanzolinii',{corpus:'canned',mode:'candidates'}));assert.equal(candidates.reader.kind,'candidate_only');
 const pages=success(await api.listPages({corpus:'logic'}));const page=pages.pages.find(p=>p.eligible);
 assert(success(await api.readPage(page.path,{corpus:'logic'})).text);
 assert.equal((await api.readPage('../../LICENSE',{corpus:'logic'})).ok,false);
 const blocked=success(await api.listPages({corpus:'canned',profile:'external'})).pages.find(p=>!p.eligible);
 assert.equal((await api.readPage(blocked.path,{corpus:'canned',profile:'external'})).ok,false);
 success(await api.getHistory({corpus:'logic'}));
 const before=calls.length;
 for(const result of await Promise.all([
  api.query(q),api.query('',{corpus:'logic'}),api.query(q,{corpus:'logic',mode:'invent'}),
  api.chat('hi',{corpus:'logic',auto_wiki:true}),api.chat('hi',{corpus:'logic',session:null}),
  api.chat('hi',{corpus:'logic',allowNetwork:'true'}),api.chat('hi',{corpus:'logic',autoWiki:true}),
  api.chat('hi',{corpus:'logic',wiki:'web'}),
  api.createCollection(''),api.importSource({}),api.listPages([])
 ])){assert.equal(result.ok,false);assert.equal(result.code,'INVALID_ARGUMENT');}
 assert.equal(calls.length,before);
 assert.equal((await api.query(q,{corpus:'missing'})).code,'ENGINE_ERROR');
 // Queue snapshots options before any asynchronous work.
 const opts={corpus:'logic'};const snapshot=api.query(q,opts);opts.corpus='missing';success(await snapshot);
 const chat=success(await api.chat('remember I study dinosaurs',{corpus:'logic'}));
 const session=chat.session;assert(session);
 for(const message of ['search Cat','find Cat','import Cat','please search for Cat','look up Cat','cool, search Cat']){
  const result=await api.chat(message,{corpus:'logic',session});
  assert.equal(result.ok,false,message+': '+JSON.stringify(result));assert.equal(result.code,'NETWORK_DISABLED',message);
 }
 const resumed=success(await api.resumeChat(session));assert.equal(resumed.chain_intact,true);assert.equal(resumed.turns.length,1);
 assert.equal(await transport('test:network-count'),0);
 const found=success(await api.chat('find Cat',{corpus:'logic',allowNetwork:true,wiki:'english'}));
 assert.equal(found.response.kind,'search');assert.equal(await transport('test:network-count'),1);
 const captured=success(await api.chat('import Cat',{corpus:'logic',allowNetwork:true}));
 assert.equal(captured.response.kind,'import');assert.equal(await transport('test:network-count'),2);
 const localFollowup=success(await api.chat('what is it?',{corpus:captured.corpus,session:captured.session}));
 assert.equal(localFollowup.response.kind,'return');assert.equal(await transport('test:network-count'),2);
 // Network permission is per call, never inherited from the prior online turn.
 assert.equal((await api.chat('find Cat',{corpus:captured.corpus,session:captured.session})).code,'NETWORK_DISABLED');
 assert.equal(await transport('test:network-count'),2);
 assert(resumed.notes.includes('I study dinosaurs'));
 const followup=success(await api.chat('what do you remember about me?',{corpus:'logic',session}));assert.equal(followup.session,session);
 assert.equal(success(await api.exportChat(session)).turns.length,2);
 const independent=success(await api.chat('hello',{corpus:'logic'}));assert.notEqual(independent.session,session);
 const collection=success(await api.createCollection('API local fixture'));
 success(await api.importSource({corpus:collection.corpus,title:'Local fixture',url:'https://example.org/local',text:'Local fixture stores supplied text, not fetched content.'}));
 const importedPages=success(await api.listPages({corpus:collection.corpus})).pages;
 assert.equal(importedPages.length,1);
 assert.match(success(await api.readPage(importedPages[0].path,{corpus:collection.corpus})).text,/supplied text/);
 // A supplied title and bytes do not become a strict supported answer.
 assert.notEqual(success(await api.query('Local fixture',{corpus:collection.corpus})).reader.kind,'return');
 success(await api.resetChat(session));assert.equal((await api.resumeChat(session)).ok,false);
 assert.equal(success(await api.listPages({corpus:collection.corpus})).pages.length,1);
 success(await api.query(q,{corpus:'logic'})); // queue survives errors
 const failed=vm.createContext({URLSearchParams,api:async()=>{throw Error('Browser save failed');}});vm.runInContext(code,failed);
 assert.equal((await failed.MPLPB.ready()).ok,false);
 assert.match((await failed.MPLPB.query(q,{corpus:'logic'})).error,/save failed/);
 const online=vm.createContext({URLSearchParams,browserApi:()=>{},api:async(url,options)=>JSON.parse(options.body)});vm.runInContext(code,online);
 const forwarded=success(await online.MPLPB.chat('Tell me about Cat',{corpus:'logic',allowNetwork:true,autoWiki:true,wiki:'english'}));
 assert.equal(forwarded.local_only,false);assert.equal(forwarded.auto_wiki,true);assert.equal(forwarded.wiki,'english');
 assert.equal(success(await online.MPLPB.chat('hello',{corpus:'logic'})).local_only,true);
 assert.equal((await api.chat('hello',{corpus:'logic',allowNetwork:true,autoWiki:true})).code,'INVALID_ARGUMENT');
 console.log('PASS JavaScript API: real engine parity, ambiguity/refusal, delivery profiles, offline default, opt-in Wikipedia fixtures, sessions, imports, validation, readiness and error recovery.');
}
tests().catch(error=>{console.error(error);process.exitCode=1;}).finally(()=>python.stdin.end());
