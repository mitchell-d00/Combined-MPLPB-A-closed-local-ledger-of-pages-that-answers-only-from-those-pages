"""D% execution worker: only source packets and questions, no generator or key."""
import hashlib
import html
import json
from pathlib import Path
import resource
import time


def snapshot(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(root).rglob('*')) if p.is_file()}


def execute(inputs='/study', output='/output'):
    from mplpb_combined.ledger import write, withdraw, Ledger
    from mplpb_combined.reader import PROFILES
    from mplpb_answers.body_text import body_text
    from mplpb_answers.passages import PassageIndex
    from mplpb_answers.pipeline import answer_query
    from mplpb_answers.prose_retrieval import retrieve
    from mplpb_work import sorter_v2
    from mplpb_work.sorter_explorer import label_graph
    inputs=Path(inputs);output=Path(output);case=json.loads((inputs/'case.json').read_text())
    start=time.perf_counter();cpu=time.process_time();reads={'calls':0,'bytes':0}
    raw_snapshot=snapshot(inputs);ledger=Path('/scratch/ledger');receipts=[]
    for number,source in enumerate(case['sources'],1):
        path=inputs/source['path'];raw=path.read_bytes();reads['calls']+=1;reads['bytes']+=len(raw)
        if source['source_class']!='original':continue
        text=raw.decode('utf-8');record=write(ledger,doc_id='SOURCE-%04d'%number,title='Synthetic source '+str(number),
            scope='archival records',body_html='<pre>'+html.escape(text)+'</pre>',origin='machine',
            source_authorship='declared-machine',external=source.get('external',''),not_for=source.get('not_for',''),
            when='2026-11-19T00:00Z')
        receipts.append({'source_id':record.id,'source_file':source['path'],'path':record.path,'hash':record.hash_actual,
                         'raw_sha256':hashlib.sha256(raw).hexdigest(),'canonical_body':body_text(record.body_html)})
        if source.get('retired'):withdraw(ledger,record.id,note='Synthetic current-policy boundary')
        if source.get('corrupt'):
            page=ledger/record.path;page.write_text(page.read_text().replace('wrote','invented',1))
    sealed_before=snapshot(ledger);profile=PROFILES[case['profile']]
    index=PassageIndex(ledger,case['question'],profile)
    budget=case['budget'];retrieval={}
    for name,pack in [('native_facets',retrieve(index,budget['passages'],budget['characters'])),
                      ('simple_bm25',index.retrieve([case['question']],budget['passages'],budget['characters']))]:
        retrieval[name]={'passages':pack['passages'],'search_complete':pack.get('search_complete',False),
                         'eligible_pages':len(index.records),'indexed_passages':len(index.passages)}
    answer=answer_query(ledger,case['question'],profile,max_passages=budget['passages'],max_chars=budget['characters']).contract
    graphs={mode:sorter_v2.sort_directory(inputs/'sources',mode) for mode in ('not-compared','compare')}
    views={mode:label_graph(g,inputs/'sources') for mode,g in graphs.items()}
    assert graphs['not-compared']['nodes']==graphs['compare']['nodes']
    assert views['not-compared']['node_labels']==views['compare']['node_labels']
    assert raw_snapshot==snapshot(inputs) and sealed_before==snapshot(ledger)
    non_authoritative=all(not x['answer_supported'] and not x['historical_truth_independently_verified']
        for v in views.values() for x in v['node_labels']+v['edge_labels'])
    assert non_authoritative
    isolation={'host_workspace_visible':Path('/workspace').exists(),'generator_package_visible':Path('/app/tools').exists(),
               'public_case_only':sorted(p.name for p in inputs.iterdir())==['case.json','sources']}
    assert not isolation['host_workspace_visible'] and not isolation['generator_package_visible'] and isolation['public_case_only']
    result={'case_id':case['id'],'question':case['question'],'profile':case['profile'],
            'answer':answer,'retrieval':retrieval,'source_receipts':receipts,
            'sorter':{'sources':graphs['compare']['sources'],'nodes':graphs['compare']['nodes'],
                      'edges':graphs['compare']['edges'],'complete':graphs['compare']['complete'],
                      'limits_or_exclusions':graphs['compare']['limits_or_exclusions'],
                      'nodes_identical_between_modes':True,'node_labels_identical_between_modes':True,
                      'all_labels_non_authoritative':non_authoritative},
            'isolation':isolation,
            'input_sources_unchanged':True,'ledger_unchanged_by_reading':True,'model_calls':0,
            'measurements':{'cpu_seconds':time.process_time()-cpu,'wall_seconds':time.perf_counter()-start,
                            'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                            'explicit_original_read_calls':reads['calls'],'explicit_original_bytes_read':reads['bytes'],
                            'total_pipeline_source_bytes_read':None}}
    with (output/'result.json').open('x') as stream:json.dump(result,stream,ensure_ascii=False,allow_nan=False)


if __name__=='__main__':execute()
