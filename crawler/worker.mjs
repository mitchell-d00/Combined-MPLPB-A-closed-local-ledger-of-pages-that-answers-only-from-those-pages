// Hosted general-web crawler. Search credentials remain server-side.
const MAX_BYTES=512*1024, MAX_PAGES=5, MAX_FETCHES=10;
export function publicURL(value){
 const u=new URL(value);const h=u.hostname.toLowerCase();
 if(u.protocol!=='https:'||u.username||u.password||u.port||!h.includes('.')||h.endsWith('.local')||h.endsWith('.internal')||h.endsWith('.localhost')||h==='localhost'||h.includes(':')||/^\d+(\.\d+){3}$/.test(h))throw Error('Only public HTTPS hostnames accepted');
 u.hash='';return u;
}
async function bytes(response,max=MAX_BYTES){
 if(Number(response.headers.get('content-length')||0)>max)throw Error('Page exceeds byte limit');
 const reader=response.body.getReader();const chunks=[];let length=0;
 try{while(true){const {done,value}=await reader.read();if(done)break;length+=value.length;if(length>max)throw Error('Page exceeds byte limit');chunks.push(value);}}finally{await reader.cancel();}
 const result=new Uint8Array(length);let at=0;for(const chunk of chunks){result.set(chunk,at);at+=chunk.length;}return result;
}
export function allowedByRobots(text,path){
 const groups=[];let agents=[],rules=[],delay=0,hasRules=false;
 const flush=()=>{if(agents.length)groups.push({agents,rules,delay});agents=[];rules=[];delay=0;hasRules=false;};
 for(const raw of text.split(/\r?\n/)){const line=raw.split('#')[0].trim();const match=/^([^:]+):\s*(.*)$/.exec(line);if(!match)continue;
 const field=match[1].trim().toLowerCase(),value=match[2].trim();
 if(field==='user-agent'){if(hasRules)flush();agents.push(value.toLowerCase());continue;}
 hasRules=true;
 if(field==='crawl-delay')delay=Math.max(delay,Number(value)||0);
 if(['allow','disallow'].includes(field)&&value)rules.push({field,value});
 }flush();
 const specific=groups.filter(g=>g.agents.some(a=>a!=='*'&&'mplpb'.startsWith(a)));
 const selected=specific.length?specific:groups.filter(g=>g.agents.includes('*'));
 if(selected.some(g=>g.delay>0))return false;
 let best=-1,allow=true;
 for(const g of selected)for(const {field,value} of g.rules){const end=value.endsWith('$');const plain=end?value.slice(0,-1):value;
  const pattern=plain.replace(/[.+?^${}()|[\]\\]/g,'\\$&').replace(/\*/g,'.*');
  if(new RegExp('^'+pattern+(end?'$':'')).test(path)&&plain.length>=best){if(plain.length>best||field==='allow'){best=plain.length;allow=field==='allow';}}
 }return allow;
}
function base64(raw){let result='';for(let i=0;i<raw.length;i+=8192)result+=String.fromCharCode(...raw.subarray(i,i+8192));return btoa(result);}
const hash=async raw=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',raw)),x=>x.toString(16).padStart(2,'0')).join('');
export async function crawl(query,env,fetcher=fetch){
 const provider=env.SEARCH_PROVIDER||(env.TAVILY_API_KEY?'tavily':'brave');
 let search;
 if(provider==='tavily'){
  if(!env.TAVILY_API_KEY)throw Error('Tavily search secret is not configured');
  search=await fetcher('https://api.tavily.com/search',{method:'POST',headers:{Authorization:'Bearer '+env.TAVILY_API_KEY,'Content-Type':'application/json'},body:JSON.stringify({query,search_depth:'basic',max_results:5,include_answer:false,include_raw_content:false,auto_parameters:false}),redirect:'error',signal:AbortSignal.timeout(15000)});
 }else if(provider==='brave'){
  if(!env.BRAVE_SEARCH_API_KEY)throw Error('Brave search secret is not configured');
  const searchURL='https://api.search.brave.com/res/v1/web/search?'+new URLSearchParams({q:query,count:'5'});
  search=await fetcher(searchURL,{headers:{'X-Subscription-Token':env.BRAVE_SEARCH_API_KEY,Accept:'application/json'},redirect:'error',signal:AbortSignal.timeout(15000)});
 }else throw Error('Unknown search provider');
 if(!search.ok)throw Error('Search provider HTTP '+search.status);
 const result=JSON.parse(new TextDecoder().decode(await bytes(search,256*1024)));
 const results=(provider==='tavily'?result.results:result.web?.results)||[];
 if(!Array.isArray(results))throw Error('Invalid search results');
 return crawlQueue(query,provider==='tavily'?'Tavily basic search':'Brave Search',results.slice(0,2).map(r=>({url:r.url,title:r.title,parent:null,depth:0})),fetcher);
}
export async function sourceIdentity(left,right){
 const valid=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
 let status='unverified_capture_identity';
 if([left,right].every(s=>valid(s.source_sha256)&&typeof s.raw_base64==='string'&&s.raw_base64.length<=Math.ceil(MAX_BYTES/3)*4)){
  try{
   const raw=[left,right].map(s=>Uint8Array.from(atob(s.raw_base64),c=>c.charCodeAt(0)));
   if(raw.some(r=>r.length>MAX_BYTES))throw Error('Identity byte limit');
   const digests=await Promise.all(raw.map(r=>hash(r)));
   status=digests.some((h,i)=>h!==[left,right][i].source_sha256)?'invalid_capture_hash':digests[0]===digests[1]?'identical_captured_bytes':left.url===right.url?'same_url_changed_bytes':'distinct_or_unresolved_sources';
  }catch{status='invalid_capture_bytes';}
 }
 return {status,
  basis:'Both bounded raw captures are independently hashed and matched to their declared digests before byte identity is accepted; publisher authorship remains unverified.',
  event_identity_established:false,authorship_authenticated:false,independent_corroboration_established:false,
  historical_truth_independently_verified:false};
}
export async function crawlSources(seeds,env={},fetcher=fetch){
 if(!Array.isArray(seeds)||!seeds.length||seeds.length>2)throw Error('Supply one or two explicit public source URLs');
 for(const seed of seeds){
  if(!seed||typeof seed.url!=='string'||seed.url.length>2000||Object.keys(seed).some(k=>!['url','sha256'].includes(k)))throw Error('Invalid historical source seed');
  if(seed.sha256!==undefined&&!/^[a-f0-9]{64}$/.test(seed.sha256))throw Error('Expected hash must be a SHA-256 digest');
 }
 return crawlQueue('', 'Explicit public source URLs',seeds.map(s=>({url:s.url,expected_sha256:s.sha256,parent:null,depth:0})),fetcher);
}
async function crawlQueue(query,provider,queue,fetcher){
 const seen=new Set(),robots=new Map(),sources=[],failures=[],edges=[];
 while(queue.length&&sources.length<MAX_PAGES&&seen.size<MAX_FETCHES){
  const item=queue.shift();let u;
  try{u=publicURL(item.url);if(seen.has(u.href))continue;seen.add(u.href);
   if(!robots.has(u.origin)){
    const response=await fetcher(u.origin+'/robots.txt',{headers:{'User-Agent':'MPLPB/1.0'},redirect:'error',signal:AbortSignal.timeout(10000)});
    if(response.status===404)robots.set(u.origin,'');else if(response.ok)robots.set(u.origin,new TextDecoder().decode(await bytes(response,128*1024)));else throw Error('Robots unavailable: HTTP '+response.status);
   }
   if(!allowedByRobots(robots.get(u.origin),u.pathname+u.search))throw Error('Blocked by robots policy');
   const response=await fetcher(u.href,{headers:{'User-Agent':'MPLPB/1.0',Accept:'text/html,text/plain'},redirect:'error',signal:AbortSignal.timeout(15000)});
   if(!response.ok)throw Error('Source HTTP '+response.status);
   const mime=(response.headers.get('content-type')||'').split(';')[0].trim().toLowerCase();
   if(!['text/html','text/plain'].includes(mime))throw Error('Unsupported source content type');
   const raw=await bytes(response),body=new TextDecoder().decode(raw);
   const capturedHash=await hash(raw);
   if(item.expected_sha256&&item.expected_sha256!==capturedHash)throw Error('Source hash differs from expected pinned bytes');
   sources.push({url:u.href,title:item.title||u.hostname,observed_at:new Date().toISOString(),mime,raw_base64:base64(raw),source_sha256:capturedHash,depth:item.depth,
    expected_hash_matched:item.expected_sha256?true:null,authorship_authenticated:false,historical_truth_independently_verified:false});
   if(item.parent)edges.push({from:item.parent,to:u.href,status:'Navigation link, not evidence of a factual relationship'});
   if(mime==='text/html'&&item.depth<1){let count=0;for(const m of body.matchAll(/<a\b[^>]*\bhref\s*=\s*["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi)){
    try{const target=publicURL(new URL(m[1].replace(/&amp;/g,'&'),u).href);if(target.origin!==u.origin)continue;queue.push({url:target.href,title:m[2].replace(/<[^>]*>/g,'').trim().slice(0,200)||target.pathname,parent:u.href,depth:1});if(++count>=4)break;}catch{}
   }}
  }catch(error){failures.push({url:item.url,reason:error.message});}
 }
 return {schema:1,query,searched_at:new Date().toISOString(),provider,sources,edges,failures,
  limits:{pages:MAX_PAGES,page_fetches:MAX_FETCHES,depth:1,bytes_per_page:MAX_BYTES},notice:'Server-reported public source captures. Search rank and navigation links do not prove topic relevance, truth or authorship.'};
}
export default {async fetch(request,env){
 const origin=request.headers.get('Origin');const headers={'Content-Type':'application/json','Cache-Control':'no-store','Access-Control-Allow-Origin':env.ALLOWED_ORIGIN||'','Vary':'Origin'};
 const reply=(value,status=200)=>new Response(JSON.stringify(value),{status,headers});
 if(!env.ALLOWED_ORIGIN||origin!==env.ALLOWED_ORIGIN)return reply({error:'Origin rejected'},403);
 if(request.method==='OPTIONS')return new Response(null,{status:204,headers:{...headers,'Access-Control-Allow-Methods':'POST','Access-Control-Allow-Headers':'Content-Type,Authorization'}});
 if(request.method!=='POST'||new URL(request.url).pathname!=='/crawl')return reply({error:'Use POST /crawl'},404);
 if(!env.CRAWL_TOKEN||request.headers.get('Authorization')!=='Bearer '+env.CRAWL_TOKEN)return reply({error:'Crawler access token required'},401);
 try{const raw=await bytes(request,4096);const data=JSON.parse(new TextDecoder().decode(raw));
  if(data.seeds!==undefined){if(data.query!==undefined)throw Error('Choose search or explicit source URLs');return reply(await crawlSources(data.seeds,env));}
  if(typeof data.query!=='string'||!data.query.trim()||data.query.length>160)throw Error('Query needs 1–160 characters');return reply(await crawl(data.query.trim(),env));}
 catch(error){return reply({error:error.message},400);}
}};
