// Authored tool/communication tests against the actual Python browser adapter.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {spawn}=require('node:child_process'),{createInterface}=require('node:readline');
const {Helper}=require('../browser/ai-helper.js');
const python=spawn(process.env.PYTHON||'python3',['-u','-c',`
import asyncio,json,sys,tempfile
from pathlib import Path
from unittest.mock import patch
from browser import bridge as B
from tools.ledger_ui import App
with tempfile.TemporaryDirectory() as d:
 B.app=App(topic_base=Path(d)/'topics')
 with patch('urllib.request.urlopen',side_effect=AssertionError('No source network permitted')):
  for line in sys.stdin:
   r=json.loads(line)
   print(asyncio.run(B.call_json(r['url'],r['payload'])),flush=True)
`],{stdio:['pipe','pipe','inherit']});
const waiting=[];createInterface({input:python.stdout}).on('line',line=>{const item=waiting.shift();if(!item)return;try{item.resolve(JSON.parse(line));}catch(e){item.reject(e);}});
python.on('exit',code=>{for(const p of waiting.splice(0))p.reject(Error('Native bridge exited '+code));});
function transport(url,options){return new Promise((resolve,reject)=>{waiting.push({resolve,reject});python.stdin.write(JSON.stringify({url,payload:options?.body||''})+'\n');});}
const html=fs.readFileSync('index.html','utf8'),code=html.match(/\/\/ BEGIN MPLPB PUBLIC API[^\n]*\n([\s\S]*?)\/\/ END MPLPB PUBLIC API/)[1];
const ctx=vm.createContext({URLSearchParams,api:transport});vm.runInContext(code,ctx);const api=ctx.MPLPB;
let checks=0;const check=(name,condition)=>{assert(condition,name);checks++;};
async function run(){
 const helper=new Helper(api);
 let unavailable=await helper.turn('Hello',{mode:'general'});
 check('general without model explains capability without a source call',unavailable.authority==='capability_notice'&&!helper.events.some(e=>e.kind==='tool_request'));
 let value=await helper.turn('Synthetic source shelf',{mode:'build',corpus:'logic'});
 check('creation is a draft',value.kind==='draft');check('no unapproved engine write',!helper.events.some(e=>e.kind==='tool_request'));
 helper.cancel();check('cancel has no write',!helper.events.some(e=>e.kind==='tool_request'));
 await helper.turn('Synthetic source shelf',{mode:'build',corpus:'logic'});value=await helper.approve();const corpus=value.data.corpus;
 check('native collection created',corpus.startsWith('mind-'));
 await assert.rejects(()=>helper.approve(),/No pending/);checks++;
 const source={title:'Opaque receipt',url:'https://example.org/opaque-a',text:'The Quillon receiver channel is 7431.'};
 helper.provider={identity:{model:'authored-test-planner'},propose:async()=>({action:'import_source',summary:'Propose an import',title:'Changed title',body:'The Quillon receiver channel is 9999.'})};
 value=await helper.turn('Save the exact supplied source',{mode:'build',corpus,source});
 check('provided text wins over model rewrite',value.draft.args[0].text===source.text&&value.draft.args[0].title===source.title);
 await helper.approve();
 helper.provider={identity:{model:'authored-test-planner'},propose:async()=>({action:'ask',summary:'Ask the selected source',message:'Who manufactured something else?'})};
 const question='What is the Quillon receiver channel?';value=await helper.turn(question,{corpus});
 check('strict source support',value.data.decision.answer_supported===true);check('supported value preserved',value.text.includes('7431'));
 const direct=(await api.relay(question,{corpus,mode:'query'})).data;
 check('reader answer unchanged',value.text===direct.reply);check('citation unchanged',value.data.citation===direct.citation);
 const queryEvent=helper.events.filter(e=>e.kind==='tool_request').at(-1);
 check('original question sent unchanged',queryEvent.data.args[0]===question);check('model rewrite cannot change collection/profile',queryEvent.data.args[1].corpus===corpus&&queryEvent.data.args[1].profile==='internal');
 value=await helper.turn(question,{corpus,profile:'external'});check('external restriction retained',value.data.decision.answer_supported===false);
 helper.provider=null;
 await helper.turn('Opposing source',{mode:'build',corpus,source:{...source,url:'https://example.org/opaque-b',text:'The Quillon receiver channel is not 7431.'}});await helper.approve();
 value=await helper.turn(question,{corpus});check('applicable contradiction remains ambiguity',value.kind==='ambiguous');check('no false support',value.data.decision.answer_supported===false);
 const before=helper.events.filter(e=>e.kind==='tool_request').length;
 helper.provider={identity:{model:'authored-test-planner'},propose:async()=>({action:'create_collection',name:'Harmful unapproved write',summary:'Try changing mode'})};
 await assert.rejects(()=>helper.turn(question,{corpus}),/selected mode/);checks++;
 check('rejected plan cannot call tool',helper.events.filter(e=>e.kind==='tool_request').length===before);
 helper.provider={identity:{model:'authored-test-planner'},propose:async()=>({action:'ask',summary:'Try unknown scope',corpus:'system'})};
 await assert.rejects(()=>helper.turn(question,{corpus}),/Unknown model fields/);checks++;
 let lastRequest;helper.provider={identity:{model:'authored-test-planner'},propose:async request=>{lastRequest=request;return{action:'general',summary:'Offer general conversation',message:'Let us explore your idea.'};}};
 value=await helper.turn('Can we discuss an idea?',{mode:'general',corpus});check('general response is model-labeled',value.authority==='model_written_not_source_backed');
 await helper.turn('Tell me more',{mode:'general',corpus});check('general history supplied explicitly',lastRequest.conversation.length===1);
 check('general conversation cannot access source tools',helper.events.filter(e=>e.kind==='tool_request').length===before);
 helper.provider={identity:{model:'authored-test-planner'},propose:async()=>({action:'import_source',summary:'Draft unverified material',title:'Draft',body:'An unverified proposal.'})};
 value=await helper.turn('Draft a note',{mode:'build',corpus});check('generated URL is not invented external provenance',value.draft.args[0].url.startsWith('https://model-draft.invalid/'));
 check('machine draft visibly labeled',value.draft.args[0].text.startsWith('AI-generated, unverified draft.'));
 helper.cancel();check('draft cancelled',helper.pending===null);
 const plan={id:'align-quillon',steps:[{order:1,action:'Place the sheet flat.',prerequisites:[],conditions:['Only while dry.'],warnings:['Stop if it tears.']},{order:2,action:'Fold the sheet.',prerequisites:[1],conditions:['Align the edges.'],warnings:['Do not force the crease.']}]};
 helper.provider=null;await helper.turn('Import a complete source procedure',{mode:'build',corpus,source:{title:'Source procedure',url:'https://example.org/source-plan',text:'MPLPB-PROCEDURE/1 '+JSON.stringify(plan)}});await helper.approve();
 let remembered={};const firstChat=new Helper(api,null,{saveSessions:value=>remembered=value});
 value=await firstChat.turn('How do I align quillon?',{mode:'chat',corpus});check('procedure conditions preserved',value.text.includes('Only while dry.'));
 value=await firstChat.turn('show warnings',{mode:'chat',corpus});check('procedure clarification asks for step',value.kind==='clarify');
 const restored=new Helper(api,null,{sessions:remembered});value=await restored.turn('step 2',{mode:'chat',corpus});check('restored session continues source clarification',value.text.includes('Do not force the crease.'));
 value=await restored.turn('No, I meant step 1',{mode:'chat',corpus});check('correction recovers exact intended step',value.text.includes('Place the sheet flat.'));
 value=await restored.turn('next step',{mode:'chat',corpus});check('next step does not claim completion',value.kind==='clarify');
 const trace=helper.trace();check('trace contains proposed and actual steps',trace.events.some(e=>e.kind==='model_proposal')&&trace.events.some(e=>e.kind==='tool_result')&&trace.events.some(e=>e.kind==='human_approval'));
 trace.events.length=0;check('export cannot mutate live trace',helper.trace().events.length>0);
 check('trace distinguishes native fallback',helper.events.some(e=>e.kind==='native_fallback'));
 console.log(JSON.stringify({role:'Authored browser-helper contract/real-engine checks; no live model inference or independent human validation',checks,passed:true},null,2));
}
run().catch(error=>{console.error(error);process.exitCode=1;}).finally(()=>python.stdin.end());
