// Authored admission/identity controls, not a live publisher or truth evaluation.
import assert from 'node:assert/strict';
const {crawlSources,sourceIdentity}=await import('./worker.mjs');
const raw='The expedition was delayed because of rain.';
const sha=Buffer.from(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw))).toString('hex');
const fetcher=async url=>url.endsWith('/robots.txt')?new Response('User-agent: *\nAllow: /'):new Response(raw,{headers:{'Content-Type':'text/plain'}});
const r=await crawlSources([{url:'https://archive.example/letter',sha256:sha}],{},fetcher);
assert.equal(r.sources.length,1);assert.equal(r.sources[0].source_sha256,sha);
assert.equal(Buffer.from(r.sources[0].raw_base64,'base64').toString(),raw);
assert.equal(r.sources[0].historical_truth_independently_verified,false);
assert.equal(r.provider,'Explicit public source URLs');
const changed=await crawlSources([{url:'https://archive.example/letter',sha256:'0'.repeat(64)}],{},fetcher);
assert.equal(changed.sources.length,0);assert.match(changed.failures[0].reason,/hash/i);
assert.equal(sourceIdentity({url:'https://archive.example/letter',source_sha256:sha},{url:'https://archive.example/letter',source_sha256:'0'.repeat(64)}).status,'same_url_changed_bytes');
const equal=sourceIdentity({url:'https://archive.example/letter',source_sha256:sha},{url:'https://mirror.example/copy',source_sha256:sha});
assert.equal(equal.status,'identical_captured_bytes');assert.equal(equal.independent_corroboration_established,false);assert.equal(equal.event_identity_established,false);
for(const url of ['http://archive.example/a','https://127.0.0.1/a','https://localhost/a','https://user:pass@archive.example/a']){
 const invalid=await crawlSources([{url}],{},fetcher);assert.equal(invalid.sources.length,0);
}
const blocked=await crawlSources([{url:'https://archive.example/private'}],{},async url=>url.endsWith('/robots.txt')?new Response('User-agent: *\nDisallow: /'):fetcher(url));
assert.equal(blocked.sources.length,0);
const incomplete=await crawlSources([{url:'https://archive.example/a'}],{},async url=>url.endsWith('/robots.txt')?new Response('',{status:503}):fetcher(url));
assert.equal(incomplete.sources.length,0);
const unsupported=await crawlSources([{url:'https://archive.example/file.pdf'}],{},async url=>url.endsWith('/robots.txt')?fetcher(url):new Response('PDF',{headers:{'Content-Type':'application/pdf'}}));
assert.equal(unsupported.sources.length,0);
console.log('PASS direct historical crawl: unchanged bytes, pins, changed versions, identity scope, robots and restrictions');
