// Local script tests only: no browser, rendered layout or external requests.
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2],'utf8'),script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const fixtures=JSON.parse(fs.readFileSync(0,'utf8'));
function runtime(protocol='http:'){
 const elements={},storage={},requests=[],documentEvents={};
 class Element {
  constructor(id){this.id=id;this.value='';this.hidden=['workspace','connection','ask','history','experiment','help'].includes(id);this.events={};this.dataset={};this.classList={toggle(){}};this.innerHTML='';this.textContent='';this.open=false;this.tagName='DIV';}
  addEventListener(key,fn){this.events[key]=fn;} setAttribute(){} showModal(){this.open=true;} close(){this.open=false;} focus(){this.focused=true;}
  set innerHTML(value){this.html=value;if(this.tagName==='SELECT'&&!this.value){this.value=(value.match(/value="([^"]*)"/)||[])[1]||'';}}get innerHTML(){return this.html;}
 }
 for(const [,tag,id] of html.matchAll(/<([\w-]+)[^>]*\bid="([^"]+)"/g)){elements[id]=new Element(id);elements[id].tagName=tag.toUpperCase();}
 for(const key of ['theme','setting','profile','page-status'])elements[key].value=({theme:'light',setting:'fantasy',profile:'internal','page-status':'all'})[key];
 const tabs=['explore','ask','chat','history','experiment','help'].map(key=>{const e=new Element('tab-'+key);e.dataset.view=key;return e;});
 let hold=null;
 const context=vm.createContext({console,URLSearchParams,Date,Number,String,JSON,Error,matchMedia:()=>({matches:false}),location:{protocol,search:''},localStorage:{getItem:k=>storage[k]||null,setItem:(k,v)=>storage[k]=v},document:{getElementById:k=>{assert.ok(elements[k],k);return elements[k];},querySelectorAll:q=>q==='[data-view]'?tabs:['explore','ask','chat','history','experiment','help'].map(k=>elements[k]),documentElement:{dataset:{}},addEventListener:(key,fn)=>documentEvents[key]=fn},fetch:async(url,options)=>{
 requests.push(url);const u=new URL(url,'http://localhost');let data,status=200;
 if(u.pathname==='/api/state')data=fixtures.state;
 else if(u.pathname==='/api/inventory')data=fixtures.inventory[u.searchParams.get('corpus')+'|'+u.searchParams.get('profile')];
 else if(u.pathname==='/api/query'){const q=JSON.parse(options.body);data=fixtures.queries[q.corpus+'|'+q.profile+'|'+q.question];if(hold){const resolve=hold;hold=null;await new Promise(resolve);}}
 else if(u.pathname==='/api/chat'){const q=JSON.parse(options.body);data=fixtures.chats[q.message];}
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
 const prefs=JSON.parse(r.storage['mplpb-ui-preferences']);assert.deepEqual(Object.keys(prefs).sort(),['corpus','profile','setting','theme']);
 r.elements.corpus.value='canned';r.run('corpusChanged()');await tick();let release;r.holdNext(resolve=>{release=resolve;});const pending=r.run('query()');await tick();r.elements.profile.value='external';r.elements.profile.events.change();release();await pending;assert.equal(r.elements.results.innerHTML,'');
 const off=runtime('file:');await tick();assert.equal(off.requests.length,0);assert.equal(off.elements.connection.hidden,false);assert.equal(off.elements.workspace.hidden,true);
 console.log('PASS: script workflow, source controls, profile changes, clarification, history, experiment, chat/rule/creator rendering, escaping, preferences, stale responses and file-mode instructions. No browser rendering performed.');
})().catch(e=>{console.error(e);process.exitCode=1;});
