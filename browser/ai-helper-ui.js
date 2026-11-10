/* Public, optional browser helper. No remote AI API, keys or automatic training. */
(function(){
'use strict';
const el=id=>document.getElementById(id),panel=el('ai-helper');if(!panel)return;
let helper,provider=null,configuration,modelCatalog,sending=false;
const modelKey='mplpb-optional-helper-model-id-v1';
const sessionKey='mplpb-optional-helper-session-ids-v1',scopeKey='mplpb-optional-helper-selected-collection-v1';
function readSaved(key,fallback){try{return JSON.parse(localStorage.getItem(key))||fallback;}catch{return fallback;}}
function rememberScope(value){try{localStorage.setItem(scopeKey,JSON.stringify(value));}catch{}}
const status=message=>{el('ai-helper-status').textContent=message;};
const trace=()=>{el('ai-helper-trace').textContent=JSON.stringify({...helper?.trace(),model_load:loader.snapshot()},null,2);};
const loader=new MPLPBModelLoader.Loader({onChange:report=>{
 const attempt=report.attempts.at(-1);if(!attempt)return;
 el('ai-helper-load-report').textContent=JSON.stringify(report,null,2);
 const stage={preflight:'browser compatibility check',configuration:'configuration check',runtime_download:'runtime download',runtime_integrity:'runtime verification',runtime_import:'runtime startup',engine_initialization:'model initialization',generation:'AI reply generation',ready:'ready'}[attempt.failed_phase||attempt.phase]||attempt.phase;
 el('ai-helper-model-status').textContent=attempt.status==='loading'?('AI is still loading: '+(attempt.last_progress?.text||stage)+'. Download progress alone does not mean it is ready for chat.'):
  attempt.status==='ready'?'Model initialization completed. You can now send a general-chat request.':
  'AI failed during '+stage+': '+attempt.error.message+' Open Model loading details for the recorded runtime messages.';
 trace();
}});
function download(value,name){
 const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'})),link=document.createElement('a');
 link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function modelChoice(){
 const model=modelCatalog?.models.find(row=>row.model_id===el('ai-helper-model').value);
 if(!model)return;
 el('ai-helper-model-info').textContent=model.label+' · MIT license · '+(model.weights.tensor_download_bytes/1e9).toFixed(2)+' GB weights · estimated '+(model.record.vram_required_MB/1000).toFixed(2)+' GB working memory before browser overhead. '+model.description;
 try{localStorage.setItem(modelKey,JSON.stringify(model.model_id));}catch{}
 if(loader.loaded||loader.requiresReload){
  provider=null;if(helper)helper.provider=null;el('ai-helper-use-model').checked=false;el('ai-helper-use-model').disabled=true;
  el('ai-helper-load').disabled=false;el('ai-helper-load').textContent='Reload page to load selection';
  status('Model selection saved. Reload before loading it so two models are not kept in memory.');
 }else{el('ai-helper-load').textContent='Load '+model.label;}
}
async function initializeModels(){
 const select=el('ai-helper-model'),button=el('ai-helper-load');select.disabled=true;button.disabled=true;
 try{
  modelCatalog=await loader.catalog();select.replaceChildren();
  for(const model of modelCatalog.models){const option=document.createElement('option');option.value=model.model_id;option.textContent=model.label+' · MIT · '+(model.weights.tensor_download_bytes/1e9).toFixed(2)+' GB';select.append(option);}
  const saved=readSaved(modelKey,null);select.value=modelCatalog.models.some(row=>row.model_id===saved)?saved:modelCatalog.default_model_id;
  modelChoice();select.disabled=false;button.disabled=false;
 }catch(error){el('ai-helper-model-info').textContent=error.message;status('Optional model selection unavailable: '+error.message+' The MPLPB source tools remain available.');}
}
el('ai-helper-model').addEventListener('change',modelChoice);
async function ready(loadSources=true){
 if(!helper)helper=new MPLPBHelper.Helper(window.MPLPB,provider,{sessions:readSaved(sessionKey,{}),saveSessions:sessions=>localStorage.setItem(sessionKey,JSON.stringify(sessions))});
 if(!loadSources)return helper;
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
 scrollMessages();
}
function scrollMessages(){const log=el('ai-helper-messages');log.scrollTop=log.scrollHeight;}
function addMessage(speaker,text){
 const row=document.createElement('article'),label=document.createElement('strong'),body=document.createElement('pre');
 label.textContent=speaker;body.textContent=text;body.style.whiteSpace='pre-wrap';body.style.overflowWrap='anywhere';row.append(label,body);
 const history=el('ai-helper-history');history.append(row);
 while(history.childElementCount>40)history.firstElementChild.remove();
}
panel.addEventListener('toggle',()=>{if(panel.open)ready().catch(error=>status(error.message));});
async function sendMessage(event){
 event?.preventDefault();if(sending)return;
 const mode=el('ai-helper-mode').value,input=el('ai-helper-message'),message=input.value;
 if(mode==='general'&&loader.loading){status('The model is still loading. Your general-chat message has not been sent.');return;}
 if(!message.trim()){status('Type a message in the prompt below the conversation, then press Send.');input.focus();return;}
 sending=true;
 const button=el('ai-helper-send');button.disabled=true;button.textContent='Sending…';input.readOnly=true;
 el('ai-helper-mode').disabled=true;el('ai-helper-model').disabled=true;el('ai-helper-load').disabled=true;el('ai-helper-use-model').disabled=true;
 el('ai-helper-messages').setAttribute('aria-busy','true');
 if(el('ai-helper-output').textContent)addMessage('AI helper',el('ai-helper-output').textContent);
 addMessage('You',message);el('ai-helper-output').textContent='Waiting for a reply…';scrollMessages();status('Sending your message…');
 try{
  const app=await ready(mode!=='general');rememberScope(el('ai-helper-corpus').value);app.provider=el('ai-helper-use-model').checked?provider:null;
  const source=mode==='build'&&el('ai-helper-source').value.trim()?{title:el('ai-helper-title').value,url:el('ai-helper-url').value,text:el('ai-helper-source').value}:null;
  const result=await app.turn(message,{mode,corpus:el('ai-helper-corpus').value,profile:el('profile')?.value||'internal',source,onText:text=>{
   el('ai-helper-output').textContent='AI reply · unverified model text\n\n'+text;status('AI is replying…');scrollMessages();
  }});
  output(result);if(input.value===message)input.value='';
  status(result.kind==='draft'?'Review the proposed draft before saving.':result.kind==='model_chat'?'AI reply complete · unverified model text.':'This reply used the existing MPLPB engine or reviewed builder.');
 }catch(error){
  el('ai-helper-output').textContent='Request failed\n\n'+error.message+(loader.requiresReload?'\n\nThe AI runtime is unavailable. Use Reload AI after error before trying it again. Your MPLPB source tools remain available.':'');
  status(error.message+' Export this tab’s interaction trace for chat diagnostics.');scrollMessages();trace();
 }finally{
  sending=false;button.disabled=false;button.textContent='Send';input.readOnly=false;
  el('ai-helper-mode').disabled=false;el('ai-helper-model').disabled=!modelCatalog;el('ai-helper-load').disabled=loader.loaded||!modelCatalog;el('ai-helper-use-model').disabled=!provider;
  el('ai-helper-messages').setAttribute('aria-busy','false');
 }
}
el('ai-helper-send').addEventListener('click',sendMessage);
el('ai-helper-form').addEventListener('submit',sendMessage);
el('ai-helper-message').addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing)sendMessage(event);});
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
 if(loader.requiresReload||loader.loaded){location.reload();return;}
 button.disabled=true;el('ai-helper-model').disabled=true;
 try{
  status('Loading the optional model. You can still use the source tools. General chat becomes available only after initialization finishes.');
  const loaded=await loader.load(el('ai-helper-model').value),engine=loaded.engine;configuration=loaded.configuration;
  provider=MPLPBBrowserProvider.create(engine,configuration,{onFatalError:error=>{
   provider=null;if(helper)helper.provider=null;el('ai-helper-use-model').checked=false;el('ai-helper-use-model').disabled=true;
   loader.invalidate(error);el('ai-helper-load').disabled=false;el('ai-helper-load').textContent='Reload AI after error';
  }});
  if(helper)helper.provider=provider;el('ai-helper-use-model').checked=true;el('ai-helper-use-model').disabled=false;
  status(configuration.label+' loaded in this browser. No training has run; your conversations are not being sent for training.');
  button.textContent='Model loaded';
 }catch(error){
  provider=null;if(helper)helper.provider=null;el('ai-helper-use-model').checked=false;el('ai-helper-use-model').disabled=true;
  status('Optional AI unavailable: '+error.message+' The ordinary MPLPB tools still work. Export the model load report to inspect this failure.');
  button.disabled=false;if(loader.requiresReload)button.textContent='Reload page to retry AI';
 }finally{el('ai-helper-model').disabled=false;trace();}
});
initializeModels();
})();
