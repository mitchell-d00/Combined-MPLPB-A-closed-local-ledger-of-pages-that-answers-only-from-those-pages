"""Summarize observed development smoke results, not semantic answer accuracy."""
import argparse
import collections
import gzip
import json
import pathlib
import re
import statistics

p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('runs',nargs='+');args=p.parse_args()
out=pathlib.Path(args.output);out.mkdir(parents=True,exist_ok=True)
rows=[];network=[];sessions=[];bundles=[]
for folder in map(pathlib.Path,args.runs):
    local_rows=[json.loads(s) for s in (folder/'responses.jsonl').read_text().splitlines()]
    rows.extend(local_rows)
    # Older run-cache metadata retained pilot case/id fields. Correlate calls
    # using append order and the per-turn request count; preserve raw logs.
    call_cases=[r['id'] for r in local_rows for _ in range(r['network_requests'])]
    local_network=[json.loads(s) for s in (folder/'network.jsonl').read_text().splitlines()]
    assert len(call_cases)==len(local_network)
    for i,(case,n) in enumerate(zip(call_cases,local_network),1):
        n['raw_metadata_case']=n.get('case');n['raw_metadata_id']=n.get('id')
        n.update(case=case,id=str(i).zfill(5),worker=folder.name)
        network.append(n)
    for name,dest in [('sessions.jsonl',sessions)]:
        dest.extend(json.loads(s) for s in (folder/name).read_text().splitlines())
    bundles.append(json.loads((folder/'summary.json').read_text())['bundle_manifest'])
rows.sort(key=lambda r:r['id']);assert len({r['id'] for r in rows})==len(rows)
counts=lambda xs:dict(collections.Counter(xs))
compact=[];routing=[];citations=[];social_network=[];errors=[]
for row in rows:
    result=row['result'];r=result.get('response',{});structure=r.get('response_structure',{});frame=r.get('interpretation',{})
    if result.get('_browser_transport_error'):errors.append(row['id'])
    prefixed=bool(re.match(r'^(cool|great|okay|nice|awesome|sure|thanks)\b',row['message'],re.I))
    if prefixed and (frame.get('normalization')!='social_lead_in' or structure.get('intent')=='social_followup'):routing.append(row['id'])
    if 31<=row['turn']<=38 and row['network_requests']:social_network.append(row['id'])
    if structure.get('intent')=='source_exploration':
        displayed=r.get('sources',[]);scopes=r.get('scope_results',[])
        if len(displayed)!=len(scopes) or any(s.get('path')!=x.get('response',{}).get('context',{}).get('path') for s,x in zip(displayed,scopes)):citations.append(row['id'])
    compact.append({**{k:row[k] for k in ['id','user','turn','topic','category','message','elapsed_ms','network_requests']},
        'kind':r.get('kind'),'authority':r.get('authority'),'reply':r.get('message'),
        'resolved':frame.get('resolved'),'normalization':frame.get('normalization'),
        'intent':structure.get('intent'),'mode':r.get('environment',{}).get('mode'),
        'sources':[{k:s.get(k) for k in ['title','corpus','path','hash','id']} for s in r.get('sources',[])],
        'automatic_lookup':result.get('automatic_lookup'),'error':result.get('_browser_transport_error')})
(out/'results.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in compact))
(out/'results.jsonl.gz').write_bytes(gzip.compress((out/'results.jsonl').read_bytes(),mtime=0))
latencies=sorted(r['elapsed_ms']/1000 for r in rows)
summary={'cases':len(rows),'virtual_users':len(sessions),'independent':False,
    'kinds':counts(r.get('kind') for r in compact),'authorities':counts(r.get('authority') for r in compact),
    'lookup_status':counts((r.get('automatic_lookup') or {}).get('status','none') for r in compact),
    'transport_error_cases':errors,'prefix_route_failure_cases':routing,'citation_index_failure_cases':citations,
    'unexpected_social_or_no_search_network_cases':social_network,'session_chains_intact':sum(bool(s['chain_intact']) for s in sessions),
    'prefixed_request_cases':sum(bool(re.match(r'^(cool|great|okay|nice|awesome|sure|thanks)\b',r['message'],re.I)) for r in rows),
    'source_exploration_cases':sum(r['intent']=='source_exploration' for r in compact),
    'category_kinds':{category:counts(r['kind'] for r in compact if r['category']==category) for category in sorted({r['category'] for r in compact})},
    'collections_built':sum(s['collections'] for s in sessions),
    'http_calls_including_run_cache':len(network),'run_cache_hits':sum(bool(n.get('cached_from_this_live_run')) for n in network),
    'http_successes':sum(n.get('http_status')==200 for n in network),'http_failures':sum('error' in n for n in network),
    'unique_successful_urls':len({n['url'] for n in network if n.get('http_status')==200}),
    'timing_seconds':{'median':round(statistics.median(latencies),3),'p95':round(latencies[int(.95*(len(latencies)-1))],3),'max':round(max(latencies),3)},
    'runtime_bundle_consistent':all(b==bundles[0] for b in bundles),'bundle_manifest':bundles[0],
    'semantic_accuracy':'Not scored. No independent human answer labels; completed replies are not correctness guarantees.',
    'limitations':['25 topic families with correlated paraphrases; development cases informed fixes.',
      'Node WebAssembly with real Wikipedia HTTP via paced curl; browser CORS/IndexedDB are outside the 1000-case runner.',
      'Live browser UI acquisition and prefix routing were smoke-tested separately.',
      'Latency includes shared network pacing and four local workers; not a production performance benchmark.']}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(out/'network.jsonl').write_text(''.join(json.dumps(n)+'\n' for n in network))
(out/'sessions.jsonl').write_text(''.join(json.dumps(n)+'\n' for n in sessions))
print(json.dumps({k:v for k,v in summary.items() if k!='bundle_manifest'},indent=2))
