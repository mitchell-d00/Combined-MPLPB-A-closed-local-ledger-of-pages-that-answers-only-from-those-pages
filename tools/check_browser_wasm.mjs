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
# Simulate a persisted capture produced before the dictionary-routing update.
original_browser_pins = W.code_pins
def historical_browser_pins():
 pins = original_browser_pins()
 pins['browser_adapter_sha256'] = next(iter(B.COMPATIBLE_CAPTURE_ADAPTERS))
 return pins
W.code_pins = historical_browser_pins
`);
const imported=await call('/api/chat',{corpus:'logic',message:'import Cat'});
if(imported.corpus!=='topics'||!imported.response.context)throw Error('WASM source import failed');
await py.runPythonAsync('W.code_pins = original_browser_pins\nB.app = App()');
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
const casual=await call('/api/chat',{corpus:'logic',message:'I like Dungeons and Dragons'});
if(casual.response.kind!=='smalltalk'||casual.response.sources.length||!casual.response.suggestions.includes('yes please'))throw Error('WASM topic offer failed');
const accepted=await call('/api/chat',{corpus:'logic',session:casual.session,message:'yes please'});
if(accepted.response.kind!=='topic'||accepted.response.context.title!=='Dungeons and Dragons')throw Error('WASM accepted topic failed');
const askHelp=await call('/api/query',{corpus:'logic',question:'How do I clear mplpb some or all?'});
if(!askHelp.help||askHelp.reader.kind!=='help'||askHelp.gate.sources.length)throw Error('WASM Ask help routing failed');
const definition=await call('/api/chat',{corpus:'logic',session:sid,message:'define dog'});
if(definition.response.authority!=='lexical_reference'||!definition.response.senses.some(s=>s.id==='02086723-n'))throw Error('WASM dictionary lookup failed');
const dictTopic=await call('/api/chat',{corpus:'logic',session:sid,message:'topic dictionary'});
if(dictTopic.response.reference_topic!=='dictionary')throw Error('WASM dictionary topic failed');
for(const word of ['Japan','.22','100 mL']){
 const entry=await call('/api/chat',{corpus:'logic',session:sid,message:word});
 if(!entry.response.senses?.length||entry.response.language_plan.acquisition.query)throw Error('WASM full headword access failed: '+word);
}
const runSenses=await call('/api/chat',{corpus:'logic',session:sid,message:'run'});
const nextSenses=await call('/api/chat',{corpus:'logic',session:sid,message:'next senses'});
if(runSenses.response.sense_page.total<=12||nextSenses.response.sense_page.offset!==12)throw Error('WASM sense paging failed');
await call('/api/chat',{corpus:'logic',session:sid,message:'topic thesaurus'});
const thesaurus=await call('/api/chat',{corpus:'logic',session:sid,message:'happy'});
if(thesaurus.response.reference_topic!=='thesaurus'||!thesaurus.response.message.includes('Synonyms in this sense:'))throw Error('WASM thesaurus topic failed');
await call('/api/chat',{corpus:'logic',session:sid,message:'leave thesaurus'});

const reference=await call('/api/chat',{corpus:'reference',message:'topic Fossil'});
if(reference.response.context?.title!=='Fossil')throw Error('WASM encyclopedia reference failed');
const moonCollection=await call('/api/collections/create',{name:'Grounded Moon fixture'});
await call('/api/source/import',{corpus:moonCollection.corpus,title:'Moon',url:'https://example.org/moon',text:'The Moon is about 3,474 km in diameter. The Moon is about 4.5 billion years old.'});
const moonSelected=await call('/api/chat',{corpus:moonCollection.corpus,message:'topic Moon'});
const moonSize=await call('/api/chat',{corpus:moonCollection.corpus,session:moonSelected.session,message:'how big is it?'});
if(moonSize.response.kind!=='grounded_answer'||!moonSize.response.message.includes('3,474 km')||moonSize.response.context.title!=='Moon')throw Error('WASM grounded size failed: '+JSON.stringify(moonSize));
const missingMoon=await call('/api/chat',{corpus:moonCollection.corpus,session:moonSelected.session,message:'Who may land on it?'});
if(missingMoon.response.kind!=='unsupported'||missingMoon.response.sources.length||missingMoon.response.source_offer.automatic_fetch!==false)throw Error('WASM unsupported offer failed');
await py.runPythonAsync('B.app = App()');
const moonAge=await call('/api/chat',{corpus:moonCollection.corpus,session:moonSelected.session,message:'and how old is it?'});
if(moonAge.response.kind!=='grounded_answer'||!moonAge.response.message.includes('4.5 billion'))throw Error('WASM persisted grounded context failed');
const unloaded=await call('/api/chat',{corpus:moonCollection.corpus,session:moonSelected.session,message:'just chat'});
if(unloaded.response.context||unloaded.response.response_structure?.mode!=='casual')throw Error('WASM unload failed');
await py.runPythonAsync('B.app = App()');
const casualStory=await call('/api/chat',{corpus:moonCollection.corpus,session:moonSelected.session,message:'My boss yelled at me'});
if(casualStory.response.context||casualStory.response.response_structure?.intent!=='social_followup')throw Error('WASM casual reload failed');
await call('/api/chat',{corpus:'logic',session:sid,message:'just chat'});
const badDay=await call('/api/chat',{corpus:'logic',session:sid,message:'Iv had a bad day'});
if(badDay.response.response_structure?.intent!=='social_invitation')throw Error('WASM social invitation failed');
await py.runPythonAsync('B.app = App()');
const socialYes=await call('/api/chat',{corpus:'logic',session:sid,message:'sure'});
if(socialYes.response.response_structure?.intent!=='social_accept')throw Error('WASM social resume failed');
const socialStory=await call('/api/chat',{corpus:'logic',session:sid,message:'My boss yelled at me'});
if(socialStory.response.sources.length||!socialStory.response.message.includes('frustrating'))throw Error('WASM social boundary failed');
if(socialStory.response.response_structure?.construction?.lexical_choice?.sense!=='00871066-s')throw Error('WASM lexical construction failed');
if(!socialStory.response.message.includes('«My boss yelled at me»'))throw Error('WASM user attribution failed');
const selfChat=await call('/api/chat',{corpus:moonCollection.corpus,session:moonSelected.session,message:'How do you think?'});
if(!selfChat.response.message.includes('explicit rules')||selfChat.response.sources.length)throw Error('WASM general self chat failed');
const loadedScopes=await call('/api/chat',{corpus:moonCollection.corpus,session:moonSelected.session,message:'load MPLPB',loaded_corpora:[moonCollection.corpus,collection.corpus]});
if(loadedScopes.response.environment.corpora.length!==2)throw Error('WASM multi scope load failed');
const federatedMoon=await call('/api/chat',{corpus:moonCollection.corpus,session:moonSelected.session,message:'how big is Moon?'});
if(federatedMoon.response.scope_results?.length!==1||federatedMoon.response.sources[0]?.corpus!==moonCollection.corpus)throw Error('WASM separated answers failed');
const noneLoaded=await call('/api/chat',{corpus:moonCollection.corpus,session:moonSelected.session,message:'load MPLPB',loaded_corpora:[]});
if(noneLoaded.response.environment.mode!=='chat'||noneLoaded.response.context)throw Error('WASM zero scope failed');
const legacyCasual=await call('/api/chat',{corpus:'logic',message:'remember legacy note'});
await py.runPythonAsync('B.app = App()');
for(const message of ["I'm bored",'So you arnt an ai?','What are the rules','So hi?']){
 const r=await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message,default_chat:true});
 if(r.response.kind==='unsupported'||r.response.sources.length||r.response.support_notice!=='Deterministic chat; not MPLPB-supported.')throw Error('WASM screenshot regression: '+message);
}
const potato=await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'say potato',default_chat:true});
if(!potato.response.message.startsWith('potato')||!potato.response.message.includes('?')||potato.response.sources.length)throw Error('WASM playful echo failed');
const exactEcho=await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'say exactly PoTaTo!',default_chat:true});
if(exactEcho.response.message!=='PoTaTo!')throw Error('WASM exact echo failed');
if(potato.response.determination?.basis!=='conversation'||potato.response.determination?.elimination_creates_evidence!==false)throw Error('WASM chat determination failed');
if(moonSize.response.determination?.basis!=='source_assertion')throw Error('WASM source determination failed');
const strictLoad=await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'load MPLPB'});
const seriousEcho=await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'say potato'});
if(!seriousEcho.response.message.startsWith('potato')||seriousEcho.response.determination?.mode!=='focus'||seriousEcho.response.sources.length||!seriousEcho.response.support_notice||JSON.stringify(seriousEcho.response.environment.corpora)!==JSON.stringify(strictLoad.response.environment.corpora))throw Error('WASM loaded-scope conversation failed');
await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'just chat'});
const emotional=await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'I feel worried',default_chat:true});
if(emotional.response.response_structure?.intent!=='casual_emotional_acknowledge'||emotional.response.sources.length)throw Error('WASM emotional acknowledgement failed');
await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'just listen',default_chat:true});
await py.runPythonAsync('B.app = App()');
const listening=await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'I feel sad',default_chat:true});
if(listening.response.message.includes('?')||listening.response.response_structure?.style!=='listen')throw Error('WASM saved emotional preference failed');
const factualTopic=await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'Can you tell me about the Moon',default_chat:true});
if(!factualTopic.response.sources.length||factualTopic.response.response_structure?.intent!=='source_exploration')throw Error('WASM polite factual topic lookup failed');
const factualMore=await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'tell me more',default_chat:true});
if(!factualMore.response.sources.length)throw Error('WASM factual continuation lost sources');
const forumIntro=await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'Say hi to the OpenAI forum and tell them what you are'});
if(!forumIntro.response.language_plan||forumIntro.response.support_label!=='Conversation · not source-backed')throw Error('WASM shared language planner missing');
if(!forumIntro.response.message.startsWith('Hello to the OpenAI forum!')||forumIntro.response.sources.length||forumIntro.response.response_structure?.acts?.length!==2)throw Error('WASM compound introduction failed');
await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'load MPLPB',loaded_corpora:['logic','system']});
await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'chat mode'});
const restoredMode=await call('/api/chat',{corpus:'logic',session:legacyCasual.session,message:'serious mode'});
if(JSON.stringify(restoredMode.response.environment.corpora)!==JSON.stringify(['logic','system']))throw Error('WASM scope restoration failed');
console.log('PASS real WebAssembly: ownership, relation proof, summary, withholding, memory, saved relaunch, fixture imports, isolated collections, offline references, grounded follow-ups and social turn-taking.');
fs.writeFileSync(path.join(path.dirname(htmlPath),'wasm-validation.json'),JSON.stringify({runtime:bundle.runtime_version,passed:true,corpora:state.corpora.map(x=>x.key),ambiguous:ambiguous.reader.kind,relation:relation.response.kind,summary:summary.response.kind,withheld:withheld.reader.kind,chain_intact:saved.chain_intact,fixture_import_passed:true,virtual_save_relaunch_passed:true,browser_layout_tested:false,indexeddb_tested:false,live_wiki_tested:false},null,2));

// Synthetic user conversations must work in the shipped Python/WASM runtime.
for(const mode of ['chat mode','load MPLPB']){
 const start=await call('/api/chat',{corpus:'logic',message:mode});
 const chatSession=start.session;
 for(const [message,expected] of [['Can you tell me about loaded mplpb','Loaded MPLPB collections:'],['Tell me more about loaded mplpb','Loaded MPLPB collections:'],['Could you show me available topics','Available topics:'],['Hi, I’m Alex. How are you?','Alex'],['What is my name?','Alex'],['Hi I’m A what are you','Hi, A!'],['What’s that?','Do you mean MPLPB or little monster?'],['thanks',''],['the second one','chat interface'],['the other one','bounded local collection'],['No I meant little monster','chat interface'],['that','chat interface'],['MPLPB','bounded local collection'],['No little monster what is it','chat interface'],['What can you chat about','your day'],['My friend Sam likes pottery','Sam'],['What does she like?','pottery'],['What’s my name?','call you A'],["My dog's name is Rex",'Rex'],["Actually, my dog's name is Max",'Max'],["What is my dog’s name?",'Max'],['What is 12 times 7?','84'],['If all glimmers are blue and Pip is a glimmer, is Pip blue?','under your premises']]){
  const answer=await call('/api/chat',{corpus:'logic',session:chatSession,message});
  if(!answer.response.message.includes(expected)||answer.response.sources.length)throw Error('WASM dialogue regression: '+message);
 }
 const resumed=await call('/api/chat/resume',{session:chatSession});
 if(!resumed.chain_intact)throw Error('WASM dialogue transcript chain failed');
}
console.log('WASM dialogue scenarios passed');

const naturalWord=await call('/api/chat',{corpus:'logic',message:'Great, could you please give me the definition of orbit'});
if(naturalWord.response.headword!=='orbit'||!naturalWord.response.guidance.actions.some(a=>a.request==='synonyms orbit'))throw Error('WASM natural dictionary guidance failed');
const naturalSelf=await call('/api/chat',{corpus:'logic',session:naturalWord.session,message:'what does MPLPB mean?'});
if(naturalSelf.response.support_label!=='System description')throw Error('WASM reference topic swallowed system description');
const naturalTopic=await call('/api/chat',{corpus:'logic',session:naturalWord.session,message:'Cool, can we talk about Moon?',default_chat:true});
if(naturalTopic.response.interpretation.resolved!=='Tell me about Moon?'||!naturalTopic.response.sources.length)throw Error('WASM natural topic request failed');
if(!naturalTopic.response.guidance.actions.some(a=>a.mode==='draft'))throw Error('WASM exploration drafts missing');
console.log('WASM natural requests and adaptive guidance passed');

const freeTurn=await call('/api/chat',{corpus:'logic',message:'off-the-record free chat'});
const freeSearch=await call('/api/chat',{corpus:'logic',session:freeTurn.session,message:'search private test text',auto_wiki:true});
if(!freeSearch.off_record||freeSearch.response.sources.length||freeSearch.turn_sha256!==null)throw Error('WASM free chat crossed evidence/persistence boundary');
const freeStored=await py.runPythonAsync("any(k.startswith('free:') for k in __import__('browser.bridge',fromlist=['app']).app.sessions)");
if(freeStored)throw Error('WASM persisted ephemeral chat');
const freeResume=await call('/api/chat/resume',{session:freeTurn.session});
if(!freeResume._browser_transport_error)throw Error('WASM free chat unexpectedly resumable');
console.log('WASM off-record source and persistence boundaries passed');

for (const mode of ['chat mode','serious mode','free chat']) {
 const start=await call('/api/chat',{corpus:'logic',message:mode});
 const send=message=>call('/api/chat',{corpus:'logic',session:start.session,message,auto_wiki:true});
 const self=await send('Good morning I’m M how long will you remember my name');
 if(!self.response.message.includes('Hi, M!') || !self.response.message.includes(mode==='free chat'?'ephemeral':'saved transcript'))throw Error('WASM composed memory explanation: '+mode);
 if(!self.response.support_label.toLowerCase().includes('system description'))throw Error('WASM composed self label: '+mode);
 const word=await send('Explain a bee');
 if(word.automatic_lookup || word.response.language_plan?.acquisition?.query)throw Error('WASM unnecessary dictionary acquisition: '+mode);
 if(word.response.authority!=='lexical_reference'||!word.response.lexical_proof||word.response.response_validation.status!=='checked')throw Error('WASM dictionary explanation: '+mode);
 const chosen=await send('sense 1');
 const follow=await send('Explain that');
 if(follow.response.message!==chosen.response.message||follow.response.response_validation.status!=='checked')throw Error('WASM dictionary follow-up: '+mode);
 const activity=await send('small calculation');
 const math=await send('12 times 7');
 if(!activity.response.message.includes('expression')||!math.response.message.includes('84'))throw Error('WASM calculation selection: '+mode);
 const explained=await send('Explain that');
 if(!explained.response.message.includes('12 * 7 = 84')||!explained.response.calculation_proof||explained.response.response_validation.status!=='checked')throw Error('WASM calculation explanation: '+mode);
 await send('change the subject');
 const imagined=await send('I would choose shape shifting');
 if(!imagined.response.message.includes('imagined scenario')||imagined.response.message.includes('felt'))throw Error('WASM hypothetical continuity: '+mode);
}
console.log('WASM structured requests passed in Chat, Serious and free chat');

await py.runPythonAsync(`
from mplpb_combined.ledger import write
write('/app/local/library-fixture-a',doc_id='LIB-A',title='Kettle',scope='kettle color',body='The kettle color is blue.')
write('/app/local/library-fixture-b',doc_id='LIB-B',title='Kettle',scope='kettle color',body='The kettle color is red.')
B.app.corpora['library-a']=('Library A','/app/local/library-fixture-a')
B.app.corpora['library-b']=('Library B','/app/local/library-fixture-b')
async def library_no_network(url):
 raise AssertionError('Library routing must not acquire remote sources')
B.remote=library_no_network
`);
const libraryStart=await call('/api/chat',{corpus:'logic',message:'library ask: What is the kettle color?',auto_wiki:true});
if(libraryStart.response.kind!=='clarify'||libraryStart.response.sources.length)throw Error('WASM library scope ambiguity');
const libraryAnswer=await call('/api/chat',{corpus:'logic',session:libraryStart.session,message:'library choose shelf-library-a',auto_wiki:true});
if(libraryAnswer.response.kind!=='return'||!libraryAnswer.response.message.includes('blue')||libraryAnswer.response.response_validation.status!=='checked')throw Error('WASM library support');
if(!libraryAnswer.response.library_route.path_back.length||libraryAnswer.response.sources[0].corpus!=='library-a')throw Error('WASM library provenance');
const libraryFree=await call('/api/chat',{corpus:'logic',message:'free chat'});
const libraryBlocked=await call('/api/chat',{corpus:'logic',session:libraryFree.session,message:'browse library',auto_wiki:true});
if(libraryBlocked.response.kind!=='clarify'||libraryBlocked.response.sources.length)throw Error('WASM free-chat library boundary');
console.log('WASM library routing, scope clarification and return paths passed');

// The deployed bundle must run the same grammar and retain its authority boundary.
for (const mode of ['just chat', 'serious mode', 'free chat']) {
 const started=await call('/api/chat',{corpus:'logic',message:mode});
 const results=[];
 for(let turn=1;turn<=4;turn++) {
  const result=await call('/api/chat',{corpus:'logic',session:started.session,
   message:turn===1?'brainstorm lantern gardens':'brainstorm',auto_wiki:true});
  const r=result.response, trace=r.response_structure?.construction;
  if(trace?.version!=='idea-grammar-v1'||trace.turn!==turn||trace.space_size!==96)
   throw Error('WASM procedural generation trace: '+mode);
  if(r.sources.length||r.response_structure.factual_claims||trace.mplpb_supported||r.language_plan?.acquisition?.query)
   throw Error('WASM generated ideas crossed evidence/network boundary: '+mode);
  if(r.response_validation.status!=='checked')throw Error('WASM generation skipped validator');
  results.push(r.message);
 }
 if(new Set(results).size!==4)throw Error('WASM brainstorm still repeats after two groups');
}
console.log('WASM deterministic generation and evidence boundaries passed in all three modes');
