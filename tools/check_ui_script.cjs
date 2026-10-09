// Local script tests only: no browser, rendered layout or external requests.
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2],'utf8'),script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const fixtures=JSON.parse(fs.readFileSync(0,'utf8'));
function runtime(protocol='http:',saved={}){
 const elements={},storage={...saved},requests=[],documentEvents={};
 class Element {
  constructor(id){this.id=id;this.value='';this.hidden=['workspace','connection','ask','history','experiment','help'].includes(id);this.events={};this.dataset={};this.classList={toggle(){}};this.innerHTML='';this.textContent='';this.open=false;this.tagName='DIV';}
  addEventListener(key,fn){this.events[key]=fn;} setAttribute(){} showModal(){this.open=true;} close(){this.open=false;} focus(){this.focused=true;}
  set innerHTML(value){this.html=value;if(this.tagName==='SELECT'&&!this.value){this.value=(value.match(/value="([^"]*)"/)||[])[1]||'';}}get innerHTML(){return this.html;}
 }
 for(const [,tag,id] of html.matchAll(/<([\w-]+)[^>]*\bid="([^"]+)"/g)){elements[id]=new Element(id);elements[id].tagName=tag.toUpperCase();}
 for(const key of ['theme','setting','profile','page-status'])elements[key].value=({theme:'light',setting:'fantasy',profile:'internal','page-status':'all'})[key];
 const tabs=['explore','ask','chat','history','experiment','help'].map(key=>{const e=new Element('tab-'+key);e.dataset.view=key;return e;});
 let hold=null;
 const context=vm.createContext({console,URL,URLSearchParams,Date,Number,String,JSON,Error,matchMedia:()=>({matches:false}),location:{protocol,search:''},localStorage:{getItem:k=>storage[k]||null,setItem:(k,v)=>storage[k]=v},document:{getElementById:k=>{assert.ok(elements[k],k);return elements[k];},querySelectorAll:q=>q==='[data-view]'?tabs:['explore','ask','chat','history','experiment','help'].map(k=>elements[k]),documentElement:{dataset:{}},addEventListener:(key,fn)=>documentEvents[key]=fn},fetch:async(url,options)=>{
 requests.push(url);const u=new URL(url,'http://localhost');let data,status=200;
 if(u.pathname==='/api/state')data=fixtures.state;
 else if(u.pathname==='/api/inventory')data=fixtures.inventory[u.searchParams.get('corpus')+'|'+u.searchParams.get('profile')];
 else if(u.pathname==='/api/query'){const q=JSON.parse(options.body);data=fixtures.queries[q.corpus+'|'+q.profile+'|'+q.question];if(hold){const resolve=hold;hold=null;await new Promise(resolve);}}
 else if(u.pathname==='/api/chat'){const q=JSON.parse(options.body);assert.equal(q.default_chat,true);data=fixtures.chats[q.message];if(q.message==='load MPLPB')assert.deepEqual(q.loaded_corpora,['logic','system']);}
 else if(u.pathname==='/api/chat/resume')data=fixtures.resume;
 else if(u.pathname==='/api/chat/reset')data={reset:true};
 else if(u.pathname==='/api/page'){data=fixtures.pages[u.searchParams.get('corpus')+'|'+u.searchParams.get('profile')+'|'+u.searchParams.get('path')];if(!data){status=400;data={error:'Page withheld'};}}
 else if(u.pathname==='/api/history')data=fixtures.history;
 else if(u.pathname==='/api/experiment')data=fixtures.experiment;
 assert.ok(data,'fixture missing for '+url);return{ok:status===200,json:async()=>data};
 }});
 vm.runInContext(script,context);
 return {elements,context,storage,requests,documentEvents,run:code=>vm.runInContext(code,context),holdNext:fn=>hold=fn};
}
async function tick(){for(let i=0;i<20;i++)await Promise.resolve();}
(async()=>{
 const r=runtime();await tick();
 assert.equal(r.elements['guide-invitation'].hidden,false);r.elements['guide-skip'].events.click();assert.equal(r.storage['mplpb-guide-choice'],'self');assert.equal(r.elements['guide-invitation'].hidden,true);
 assert.equal(r.elements.workspace.hidden,false);assert.match(r.elements['page-map'].innerHTML,/CANNED-0001/);assert.equal(r.elements['eligible-count'].textContent,2);
 await r.run('query()');assert.match(r.elements.results.innerHTML,/AMBIGUOUS/);assert.match(r.elements.results.innerHTML,/2 separate sources/);
 await r.run('page("canned-0001.html")');assert.equal(r.elements['page-dialog'].open,true);assert.match(r.elements['page-content'].innerHTML,/Synthetic reader fixture/);
 r.elements['ask-page'].events.click();await tick();assert.equal(r.elements['page-dialog'].open,false);assert.equal(r.elements.question.value,'Phrynomedusa vanzolinii');assert.match(r.elements.results.innerHTML,/RETURN/);
 r.elements.profile.value='external';r.elements.profile.events.change();await tick();assert.equal(r.elements['eligible-count'].textContent,0);assert.match(r.elements['page-map'].innerHTML,/withheld by external/);
 await r.run('page("canned-0001.html")');assert.equal(r.elements['page-dialog'].open,false);
 r.elements.corpus.value='dogs';r.elements.profile.value='internal';r.run('corpusChanged()');await tick();await r.run('query()');assert.match(r.elements.results.innerHTML,/Which meaning do you want/);assert.match(r.elements.results.innerHTML,/dog breeds/);
 await r.run('history()');assert.match(r.elements['history-results'].innerHTML,/ACTIVE HEAD/);assert.match(r.elements['history-results'].innerHTML,/Earlier engine\/checker pins/);
 await r.run('experiment()');assert.match(r.elements['experiment-results'].innerHTML,/8 \/ 9/);
 const injected=r.run(`sourceCard({...${JSON.stringify(fixtures.queries['canned|internal|Phrynomedusa vanzolinii'].gate.sources[0])},title:'<img src=x onerror=evil()>',text:'<script>evil()</script>'})`);
 assert.ok(!injected.includes('<img'));assert.ok(!injected.includes('<script>'));assert.ok(injected.includes('&lt;img'));
 r.elements.corpus.value='logic';r.elements.profile.value='internal';await r.run('chatSend(\"relate Dungeons and Dragons -> game\")');assert.match(r.elements['chat-messages'].innerHTML,/TYPE-2/);await r.run('chatSend(\"who made you?\")');assert.match(r.elements['chat-messages'].innerHTML,/Mitchell D. McPhetridge/);
 const resumed=runtime('http:',r.storage);await tick();assert.match(resumed.elements['chat-messages'].innerHTML,/Mitchell D. McPhetridge/);assert.match(resumed.elements['chat-messages'].innerHTML,/TYPE-2/);assert.match(resumed.elements['chat-status'].textContent,/resumed/);
 assert.match(r.run('linkText("Visit https://example.org/path?q=1&x=2.")'),/href="https:\/\/example.org\/path\?q=1&amp;x=2"/);
 assert.ok(!r.run('linkText("javascript:alert(1) <img src=x> https://user:pass@example.org")').includes('<a'));
 assert.match(r.run('chatText("First\\nLast",["First","Last"])'),/data-topic="Last"/);
 assert.match(r.run('linkText("https://en.wikipedia.org/wiki/Fossil_(disambiguation).")'),/href="https:\/\/en.wikipedia.org\/wiki\/Fossil_\(disambiguation\)"/);
 const prefs=JSON.parse(r.storage['mplpb-ui-preferences']);assert.deepEqual(Object.keys(prefs).sort(),['corpus','profile','setting','theme']);
 r.elements.corpus.value='canned';r.elements.profile.value='internal';r.elements.question.value='How do I clear mplpb some or all?';await r.run('query()');assert.match(r.elements.results.innerHTML,/App help/);assert.match(r.elements.results.innerHTML,/Clear selected MPLPBs/);
 await r.run('chatSend("guide me")');assert.match(r.elements['chat-messages'].innerHTML,/Step 1 of 4/);assert.match(r.elements['chat-messages'].innerHTML,/data-suggest/);
 await r.run('chatSend("show my MPLPB")');assert.match(r.elements['chat-messages'].innerHTML,/data-topic="Budget guide"/);
 r.elements['chat-messages'].events.click({target:{closest:selector=>selector==='[data-topic]'?{dataset:{topic:'Budget guide'}}:null}});await tick();assert.match(r.elements['chat-messages'].innerHTML,/Topic selected: Budget guide/);
 r.elements.corpus.value='canned';r.run('corpusChanged()');await tick();let release;r.holdNext(resolve=>{release=resolve;});const pending=r.run('query()');await tick();r.elements.profile.value='external';r.elements.profile.events.change();release();await pending;assert.equal(r.elements.results.innerHTML,'');
 const off=runtime('file:');await tick();assert.equal(off.requests.length,0);assert.equal(off.elements.connection.hidden,false);assert.equal(off.elements.workspace.hidden,true);
 assert.match(r.elements['chat-mode'].textContent,/MPLPB topic: Budget guide/);
 const beforeChat=r.requests.length;r.elements['chat-send'].disabled=true;r.elements['chat-casual'].events.click();await tick();assert.equal(r.requests.length,beforeChat);r.elements['chat-send'].disabled=false;
 r.elements['chat-casual'].events.click();await tick();assert.match(r.elements['chat-mode'].textContent,/Just chat/);assert.match(r.elements['chat-messages'].innerHTML,/active MPLPB topic is unloaded/);
 r.elements['chat-load-all'].events.click();await tick();assert.match(r.elements['chat-mode'].textContent,/Serious mode/);r.elements['chat-scope'].selectedOptions=[{value:'logic'},{value:'system'}];r.elements['chat-load-selected'].events.click();await tick();assert.match(r.elements['chat-mode'].textContent,/2 MPLPB loaded/);
 assert.match(r.elements['chat-scope'].innerHTML,/value="logic" selected/);assert.match(r.elements['chat-scope-status'].textContent,/2 collections loaded/);
 r.elements['chat-mode-chat'].events.click();await tick();assert.match(r.elements['chat-mode'].textContent,/Just chat/);assert.ok(!r.elements['chat-scope'].innerHTML.includes(' selected'));
 r.elements['chat-mode-serious'].events.click();await tick();assert.match(r.elements['chat-mode'].textContent,/2 MPLPB loaded/);assert.match(r.elements['chat-scope'].innerHTML,/value="system" selected/);
 const freshChat=runtime();await tick();freshChat.elements.corpus.value='logic';await freshChat.run('chatSend("So hi?")');assert.match(freshChat.elements['chat-messages'].innerHTML,/Deterministic chat; not MPLPB-supported/);assert.match(freshChat.elements['chat-mode'].textContent,/0 MPLPB loaded/);
 const footer=r.run(`chatSources({sources:[{title:'<bad>',path:'moon.html',corpus:'moon-corpus',hash:'sha256:abc'}]})`);
 assert.match(footer,/Sources/);assert.match(footer,/data-source-corpus="moon-corpus"/);assert.ok(!footer.includes('<bad>'));assert.match(footer,/&lt;bad&gt;/);
 r.run(`chatMessages=[{role:'assistant',response:{kind:'federated_answers',message:'Visible factual answer',sources:[{title:'Moon',path:'moon.html',corpus:'moon-corpus'}],suggestions:['Tell me more about moon']}}];drawChat()`);
 assert.ok(r.elements['chat-messages'].innerHTML.indexOf('Visible factual answer')<r.elements['chat-messages'].innerHTML.indexOf('aria-label="Sources"'));
 r.run(`drawTopicActions({response_structure:{subject:'Moon'},suggestions:['How big is Moon?','Search Moon']})`);
 assert.match(r.elements['chat-topic-actions'].innerHTML,/How big is Moon/);assert.match(r.elements['chat-topic-label'].textContent,/Moon/);
 r.run(`drawTopicActions({response_structure:{subject:'Dogs'},suggestions:['Tell me about Dogs','Search Dogs']})`);
 assert.match(r.elements['chat-topic-actions'].innerHTML,/Search Dogs/);assert.ok(!r.elements['chat-topic-actions'].innerHTML.includes('Moon'));
 r.run(`drawTopicActions({suggestions:['<script>bad</script>']})`);assert.ok(!r.elements['chat-topic-actions'].innerHTML.includes('<script>'));
 const beforeChoice=r.requests.length;r.elements['chat-send'].disabled=true;r.elements['chat-topic-actions'].events.click({target:{closest:()=>({dataset:{chatRequest:'So hi?'}})}});await tick();assert.equal(r.requests.length,beforeChoice);
 r.elements['chat-send'].disabled=false;r.elements['chat-topic-actions'].events.click({target:{closest:()=>({dataset:{chatRequest:'So hi?'}})}});await tick();assert.equal(r.requests.length,beforeChoice+1);
 console.log('PASS: script workflow, source controls, profile changes, clarification, history, experiment, chat/rule/creator rendering, escaping, preferences, stale responses and file-mode instructions. No browser rendering performed.');
})().catch(e=>{console.error(e);process.exitCode=1;});
