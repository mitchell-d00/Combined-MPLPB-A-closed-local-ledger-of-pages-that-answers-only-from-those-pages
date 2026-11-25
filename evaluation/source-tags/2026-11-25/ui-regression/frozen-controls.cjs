// Authored rendering controls; no semantic or human-validation score.
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('index.html','utf8');
const code=html.slice(html.indexOf('function renderAssisted('),html.indexOf('async function query('));
const results={innerHTML:''};
const context=vm.createContext({$:id=>{assert.equal(id,'results');return results;},esc:x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))});
vm.runInContext(code,context);
const contract={mode:'strict',kind:'partial_answer',documentary_support:{source_support_claims:1},diagnostic:{message:'Checked source statement'},
 missing:['Dispatch not established'],claims:[{text:'A source reports a request <script>',qualifiers:['if possible'],citations:[{quote:'I asked Orin to send the report.',source_id:'SOURCE-1',hash:'sha256:pin',path:'source-1.html'}]}]};
context.result={reader:{answer_contract:contract}};
vm.runInContext('render(result)',context);
assert(results.innerHTML.includes('PARTIAL SOURCE EVIDENCE'));
assert(results.innerHTML.includes('Historical truth is not independently verified'));
assert(results.innerHTML.includes('Dispatch not established'));
assert(results.innerHTML.includes('if possible'));
assert(results.innerHTML.includes('data-page="source-1.html"'));
assert(!results.innerHTML.includes('<script>'));
contract.kind='supported_answer';contract.missing=[];
vm.runInContext('render(result)',context);
assert(results.innerHTML.includes('SUPPORTED SOURCE ASSERTIONS'));
console.log('PASS documentary rendering: checked/partial statements, missing scope, qualifiers, source inspection and escaping');

context.result={reader:{answer_contract:{
 mode:'strict',kind:'partial_answer',diagnostic:{message:'See the decision for each requested field.'},
 missing:['shelf code'],claims:[{text:'Date Written: 1841-05-17',citations:[{quote:'Date Written: 1841-05-17',source_id:'FOLIO-1',hash:'sha256:pin',path:'folio-1.html'}]}],
 question_parts:[{field:'date written',status:'verified'},{field:'shelf code',status:'unresolved',diagnostic:{message:'Missing <field>.',next_steps:['Inspect the exact label.']}}]
}}};
vm.runInContext('render(result)',context);
assert(results.innerHTML.includes('Requested fields'));
assert(results.innerHTML.includes('Missing &lt;field&gt;.'));
assert(results.innerHTML.includes('Inspect the exact label.'));
assert(results.innerHTML.includes('data-page="folio-1.html"'));
assert(!results.innerHTML.includes('Source procedure inspection'));

// Verified field cards follow citation pins, not lexical retrieval order.
const controls={results,
 'ask-reader-mode':{value:'supported'},'monster-reason':{checked:false}};
context.$=id=>controls[id];context.linkText=x=>String(x);
vm.runInContext(html.slice(html.indexOf('function sourceCard('),html.indexOf('function renderAssisted(')),context);
const a={id:'A',path:'a.html',hash:'sha256:a',title:'Uncited first match',text:'Different date.',origin:'machine',origin_depth:1,matched_terms:['date'],unmatched_terms:[]};
const b={id:'B',path:'b.html',hash:'sha256:b',title:'Verified second page',origin:'machine',origin_depth:1};
const exact={mode:'strict',kind:'supported_answer',answer_supported:true,verification:{semantic:'bounded_explicit_field'},
 claims:[{text:'Inspection Date: 1901-06-07',citations:[{source_id:'B',path:'b.html',hash:'sha256:b',field:'inspection date',quote:'Inspection Date: 1901-06-07'}]}],sources:[b]};
context.result={reader:{kind:'return',profile:'internal',title:b.title,text:'Inspection Date: 1901-06-07',answer_contract:exact},
 gate:{sources:[a,{...b,text:'Inspection Date: 1901-06-07',matched_terms:[],unmatched_terms:[]}],unmatched_terms:[],excluded:[],lexical_coverage:1}};
vm.runInContext('render(result)',context);
assert(results.innerHTML.includes('data-page="b.html"'));
assert(!results.innerHTML.includes('data-page="a.html"'));
assert(results.innerHTML.includes('data-source-hash="sha256:b"'));
// A verified field owner can fall outside the lexical candidate list.
context.result.gate.sources=[a];
vm.runInContext('render(result)',context);
assert(results.innerHTML.includes('data-page="b.html"'));
assert(!results.innerHTML.includes('data-page="a.html"'));
controls['ask-reader-mode'].value='candidates';
context.result.gate.sources=[a,{...b,text:'Inspection Date: 1901-06-07',matched_terms:[],unmatched_terms:[]}];
vm.runInContext('render(result)',context);
assert(results.innerHTML.includes('data-page="a.html"'));
assert(results.innerHTML.includes('data-page="b.html"'));
console.log('PASS exact-field source cards: cited owner, omitted lexical owner, pins and unchanged candidate inspection');
