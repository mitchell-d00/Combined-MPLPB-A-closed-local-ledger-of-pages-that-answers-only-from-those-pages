"""Run from the frozen extracted checkout; write only to a new output directory."""
import hashlib
import json
from pathlib import Path
import resource
import sys
import tempfile
import time
sys.path.insert(0,str(Path.cwd()))
from mplpb_combined.ledger import write
from mplpb_work import sorter_v2 as sorter
from mplpb_work import sorter_explorer as explorer


def main(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    source=Path.cwd()/'examples/fixpack_classing/demo_dump'
    pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir() if p.is_file()}
    start=time.perf_counter();cpu=time.process_time();views={}
    for mode in ('not-compared','compare'):
        graph=sorter.sort_directory(source,mode);views[mode]=explorer.label_graph(graph,source)
        (output/(mode+'.json')).write_text(json.dumps(views[mode],indent=2,ensure_ascii=False)+'\n')
        (output/(mode+'.txt')).write_text(explorer.render(views[mode])+'\n')
    assert views['not-compared']['source_graph']['nodes']==views['compare']['source_graph']['nodes']
    assert views['not-compared']['node_labels']==views['compare']['node_labels']
    ideas=explorer.explore_ideas('What possible connections and disagreements concern the shipment cargo?',dump=source)
    (output/'unofficial-question.json').write_text(json.dumps(ideas,indent=2,ensure_ascii=False)+'\n')
    (output/'unofficial-question.txt').write_text(explorer.render(ideas)+'\n')
    with tempfile.TemporaryDirectory() as tmp:
        write(tmp,doc_id='EXAMPLE-1',title='Fictional archive example',scope='archive',body='Owner: Amara')
        supported=explorer.explore_ideas('What is owner for record EXAMPLE-1?',ledger=tmp)
        refused=explorer.explore_ideas('Did the archive inspection cause an eclipse?',ledger=tmp)
        assert supported['native_mplpb']['result']['answer_supported']
        assert not supported['answer_supported']
        assert not refused['native_mplpb']['result']['answer_supported']
        for name,value in [('separate-native-supported',supported),('separate-native-refusal',refused)]:
            (output/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    assert pins=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir() if p.is_file()}
    summary={'source_scope':'Eight existing fictional demo files,not historical accuracy labels.',
             'nodes_identical_between_modes':True,'node_labels_identical_between_modes':True,
             'mode_counts':{k:{'nodes':len(v['source_graph']['nodes']),'edges':len(v['source_graph']['edges'])} for k,v in views.items()},
             'unofficial_segments':len(ideas['segments']),'model_used':False,'native_support_transferred':False,
             'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,
             'peak_process_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
             'source_bytes_unique':sum(p.stat().st_size for p in source.iterdir() if p.is_file()),
             'total_source_read_bytes':None,'source_hashes_unchanged':pins,
             'live_model_semantic_quality':'NOT RUN','historical_accuracy':None,'human_review_seconds':None}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))


if __name__=='__main__':main(sys.argv[1])
