/* Local generation transport. Plain conversation never executes source tools. */
(function(root){
'use strict';
const failure=error=>({name:String(error?.name||'Error').slice(0,100),message:String(error?.message||error).slice(0,4000),stack:String(error?.stack||'').slice(0,6000)});
function create(engine,configuration,{onFatalError=()=>{}}={}){
 let invalid=false;
 const context=configuration.record?.overrides?.context_window_size||2048;
 const provider={identity:{model:configuration.model_id,weights:configuration.weights,license:configuration.license,runtime:configuration.runtime},lastTransport:null};
 async function run(request,onText){
  if(invalid)throw Error('Reload the page before using this AI again. The model runtime is unavailable.');
  const transport={request,identity:provider.identity};provider.lastTransport=transport;
  try{
   const response=await engine.chat.completions.create(request);
   let content='',finishReason;
   if(request.stream){
    for await(const chunk of response){
     content+=chunk.choices?.[0]?.delta?.content||'';
     finishReason=chunk.choices?.[0]?.finish_reason||finishReason;
     transport.visible_response={content,finish_reason:finishReason};
     if(onText)onText(content);
    }
   }else{
    content=response.choices?.[0]?.message?.content;finishReason=response.choices?.[0]?.finish_reason;
    transport.visible_response={content,finish_reason:finishReason,usage:response.usage};
   }
   if(typeof content!=='string'||!content.trim())throw Error('The model returned no text. Try a shorter message.');
   return content;
  }catch(error){
   transport.error=failure(error);
   if(/disposed|device.{0,20}lost|out of memory|exit\(\d+\)|WebGPU.*(?:error|lost)/i.test(transport.error.message)){
    invalid=true;try{onFatalError(error);}catch{/* Preserve the generation error. */}
   }
   throw error;
  }
 }
 provider.chat=async(request,onText)=>{
  const system='You are a local AI assistant helping the user discuss ideas and build MPLPB collections. Answer directly in plain text. Creating or saving a collection or source requires the Build task and human review. Never claim you saved or verified sources in this conversation. Your replies are unverified model text.';
  const budget=Math.min(6000,Math.floor(context*1.5)),original=request.original;
  if(typeof original!=='string'||!original.trim())throw Error('Enter a message first.');
  if(original.length+system.length>budget)throw Error('This message is too long for the selected model. Send a shorter message.');
  const history=[];let used=original.length+system.length;
  for(const turn of [...(request.conversation||[])].reverse()){
   if(used+turn.user.length+turn.assistant.length>budget)break;
   history.unshift({role:'user',content:turn.user},{role:'assistant',content:turn.assistant});used+=turn.user.length+turn.assistant.length;
  }
  return run({messages:[{role:'system',content:system},...history,{role:'user',content:original}],stream:true,temperature:0.3,max_tokens:context<=2048?256:512},onText);
 };
 provider.propose=async(request,schema)=>{
  if(JSON.stringify(request).length>10000)throw Error('The model input is too large. Use a shorter draft or turn off the optional model; no source was written.');
  const content=await run({messages:[{role:'system',content:'You are an optional planner for MPLPB. Return only the requested JSON. Source support comes only from MPLPB. Source writes are unverified drafts needing human approval. Never invent a source-backed answer or claim a draft was saved.'},{role:'user',content:JSON.stringify(request)}],response_format:{type:'json_object',schema:JSON.stringify(schema)},temperature:0.2,max_tokens:context<=2048?512:1024});
  return JSON.parse(content);
 };
 return provider;
}
root.MPLPBBrowserProvider={create};
if(typeof module==='object'&&module.exports)module.exports=root.MPLPBBrowserProvider;
})(typeof globalThis==='object'?globalThis:this);
