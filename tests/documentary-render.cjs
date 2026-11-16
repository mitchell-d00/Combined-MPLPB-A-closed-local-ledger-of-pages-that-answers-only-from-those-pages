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
