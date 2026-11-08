/* Public, optional browser helper. No remote AI API, keys or automatic training. */
(function(){
'use strict';
const el=id=>document.getElementById(id),panel=el('ai-helper');if(!panel)return;
let helper,provider=null,configuration;
const sessionKey='mplpb-optional-helper-session-ids-v1',scopeKey='mplpb-optional-helper-selected-collection-v1';
function readSaved(key,fallback){try{return JSON.parse(localStorage.getItem(key))||fallback;}catch{return fallback;}}
function rememberScope(value){try{localStorage.setItem(scopeKey,JSON.stringify(value));}catch{}}
const status=message=>{el('ai-helper-status').textContent=message;};
const trace=()=>{el('ai-helper-trace').textContent=JSON.stringify({...helper?.trace(),model_load:loader.snapshot()},null,2);};
const loader=new MPLPBModelLoader.Loader({onChange:report=>{
 const attempt=report.attempts.at(-1);if(!attempt)return;
 el('ai-helper-load-report').textContent=JSON.stringify(report,null,2);
 const stage={preflight:'browser compatibility check',configuration:'configuration check',runtime_download:'runtime download',runtime_integrity:'runtime verification',runtime_import:'runtime startup',engine_initialization:'model initialization',ready:'ready'}[attempt.failed_phase||attempt.phase]||attempt.phase;
 el('ai-helper-model-status').textContent=attempt.status==='loading'?('AI is still loading: '+(attempt.last_progress?.text||stage)+'. Download progress alone does not mean it is ready for chat.'):
  attempt.status==='ready'?'Model initialization completed. You can now send a general-chat request.':
  'AI failed during '+stage+': '+attempt.error.message+' Open Model loading details for the recorded runtime messages.';
 trace();
}});
function download(value,name){
 const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'})),link=document.createElement('a');
 link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
async function ready(){
 if(!helper)helper=new MPLPBHelper.Helper(window.MPLPB,provider,{sessions:readSaved(sessionKey,{}),saveSessions:sessions=>localStorage.setItem(sessionKey,JSON.stringify(sessions))});
 const result=await window.MPLPB.listCorpora();if(!result.ok)throw Error(result.error);
 const current=el('ai-helper-corpus').value||readSaved(scopeKey,null)||el('corpus')?.value;
 el('ai-helper-corpus').replaceChildren();
 for(const row of result.data){const option=document.createElement('option');option.value=row.key;option.textContent=row.label||row.key;el('ai-helper-corpus').append(option);}
 if(result.data.some(row=>row.key===current))el('ai-helper-corpus').value=current;
 return helper;
}
function output(value){
 const labels={capability_notice:'Helper availability',mplpb_query:'MPLPB source check',mplpb_conversation:'MPLPB conversation',model_written_not_source_backed:'AI-written conversation · not source-backed',requires_human_approval:'Draft awaiting your review',source_management_receipt:'MPLPB save receipt',model_proposal:'AI suggestion · not source evidence'};
 const outcomes={unavailable:'AI not loaded',return:value.data?.decision?.answer_supported?'Supported answer':'Reply',ambiguous:'Ambiguous source result',not_in_corpus:'Answer not established',clarify:'Clarification needed',partial:'Partial source evidence',saved:'Saved',draft:'Review before saving',model_chat:'General AI chat'};
 el('ai-helper-output').textContent=(labels[value.authority]||'MPLPB reply')+' · '+(outcomes[value.kind]||'Reply')+'\n\n'+value.text+(value.data?.citation?'\n\n'+value.data.citation:'');
 el('ai-helper-evidence').textContent=value.data?JSON.stringify(value.data,null,2):'';
 const draft=value.draft;
 el('ai-helper-review').textContent=!draft?'':draft.kind==='collection'?'Proposed collection name:\n'+draft.args[0]:'Proposed source\nTitle: '+draft.args[0].title+'\nRecorded URL: '+draft.args[0].url+'\n\nExact text to save:\n'+draft.args[0].text+'\n\nThe URL is recorded attribution; no external page was fetched. Change your request or source fields and send again to replace this draft.';
 el('ai-helper-approve').hidden=value.kind!=='draft';el('ai-helper-cancel').hidden=value.kind!=='draft';trace();
}
panel.addEventListener('toggle',()=>{if(panel.open)ready().catch(error=>status(error.message));});
el('ai-helper-send').addEventListener('click',async()=>{
 const button=el('ai-helper-send');button.disabled=true;
 try{
  const mode=el('ai-helper-mode').value;
  if(mode==='general'&&loader.loading){status('The model is still loading. Your general-chat message has not been sent.');return;}
  const app=await ready();rememberScope(el('ai-helper-corpus').value);app.provider=el('ai-helper-use-model').checked?provider:null;
  const source=mode==='build'&&el('ai-helper-source').value.trim()?{title:el('ai-helper-title').value,url:el('ai-helper-url').value,text:el('ai-helper-source').value}:null;
  const result=await app.turn(el('ai-helper-message').value,{mode,corpus:el('ai-helper-corpus').value,profile:el('profile')?.value||'internal',source});
  output(result);status(app.provider?'AI proposed this action; inspect the recorded calls below.':'This turn used the existing MPLPB engine or manual draft; optional AI was not used.');
 }catch(error){status(error.message);trace();}finally{button.disabled=false;}
});
el('ai-helper-approve').addEventListener('click',async()=>{
 const button=el('ai-helper-approve');button.disabled=true;
 try{const saved=await helper.approve();output(saved);await ready();if(saved.data?.corpus){el('ai-helper-corpus').value=saved.data.corpus;rememberScope(saved.data.corpus);}status('Saved through MPLPB. Saving does not verify the text or its authorship.');}
 catch(error){status(error.message);trace();}finally{button.disabled=false;}
});
el('ai-helper-cancel').addEventListener('click',()=>{helper?.cancel();el('ai-helper-approve').hidden=true;el('ai-helper-cancel').hidden=true;el('ai-helper-review').textContent='';trace();status('Draft cancelled; no save was requested.');});
el('ai-helper-export').addEventListener('click',()=>download({...helper?.trace(),model_load:loader.snapshot()},'mplpb-helper-trace.json'));
el('ai-helper-export-load').addEventListener('click',()=>download(loader.snapshot(),'mplpb-model-load-report.json'));
el('ai-helper-load').addEventListener('click',async()=>{
 const button=el('ai-helper-load');
 if(loader.requiresReload){location.reload();return;}
 button.disabled=true;
 try{
  status('Loading the optional model. You can still use the source tools. General chat becomes available only after initialization finishes.');
  const loaded=await loader.load(),engine=loaded.engine;configuration=loaded.configuration;
  provider={identity:{model:configuration.model_id,weights:configuration.weights,license:configuration.license,runtime:configuration.runtime},
   propose:async(request,schema)=>{
    if(JSON.stringify(request).length>10000)throw Error('The model input is too large. Use a shorter draft or turn off the optional model; no source was written.');
    const actualRequest={messages:[{role:'system',content:'You are an optional conversational planner for MPLPB. Return only the requested JSON. Show a brief action summary, not private reasoning. Source support comes only from MPLPB; never fabricate a source-backed answer. General chat is explicitly unverified. You are software, not a person or the author of supplied work. Source writes are drafts needing human approval.'},{role:'user',content:JSON.stringify(request)}],response_format:{type:'json_object',schema:JSON.stringify(schema)},temperature:0.2,max_tokens:1024};
    provider.lastTransport={request:actualRequest,identity:provider.identity};
    const response=await engine.chat.completions.create(actualRequest);
    provider.lastTransport.visible_response={content:response.choices?.[0]?.message?.content,finish_reason:response.choices?.[0]?.finish_reason,usage:response.usage};
    const content=response.choices?.[0]?.message?.content;if(typeof content!=='string')throw Error('Model did not return a plan');
    return JSON.parse(content);
   }};
  if(helper)helper.provider=provider;el('ai-helper-use-model').checked=true;el('ai-helper-use-model').disabled=false;
  status('Pretrained Phi-4-mini loaded in this browser. No training has run; your conversations are not being sent for training.');
  button.textContent='Model loaded';
 }catch(error){
  provider=null;if(helper)helper.provider=null;el('ai-helper-use-model').checked=false;el('ai-helper-use-model').disabled=true;
  status('Optional AI unavailable: '+error.message+' The ordinary MPLPB tools still work. Export the model load report to inspect this failure.');
  button.disabled=false;if(loader.requiresReload)button.textContent='Reload page to retry AI';
 }finally{trace();}
});
})();
