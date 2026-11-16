"""Post-execution fidelity audit; no semantic scoring and no runtime answer keys."""
from collections import Counter
import argparse
from pathlib import Path
import resource
import tempfile
import time
from mplpb_answers.body_text import body_text
from mplpb_combined.ledger import Ledger
from mplpb_work.source_mapping import digest,reconstruct
from tools.source_roundtrip import original_passage
from tools.unprepared_sources import import_corpus,sha
from tools.unprepared_challenge import read,save,summary


def audit(directory,run):
    directory=Path(directory);run=Path(run);verified=summary(directory,run)
    start=time.perf_counter();cpu=time.process_time();rows=[];raw_cache={}
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)/'ledger';receipt=import_corpus(directory,root)
        if receipt!=read(run/'import-receipt.json'):raise ValueError('Import mismatch')
        records={r.path:r for r in Ledger(root).records};bodies={p:body_text(r.body_html) for p,r in records.items()}
        for case in verified['rows']:
            output=read(run/(case['id']+'.json'));pack=output.get('investigation',{}).get('prose_candidates',{})
            mapped=pack.get('information_map',{});items=mapped.get('mappings',[])+mapped.get('relationships',[])
            valid=0;failures=[];anchors=0;raw_unique=0;sample=None
            for m in items:
                unsigned=dict(m);identity=unsigned.pop('mapping_id',None)
                ok=identity==digest(unsigned) and m.get('answer_supported') is False and m.get('content_truth_verified') is False
                if m.get('verification',{}).get('semantic_relationship')!='NOT VERIFIED':ok=False
                for e in m['evidence']:
                    rec=records.get(e['path']);a=e['body_start'];b=e['body_end'];anchors+=1
                    ok=ok and rec is not None and rec.id==e['source_id'] and rec.hash_actual==e['hash'] and bodies[e['path']][a:b]==e['quote']
                    if not ok:continue
                    key=digest(e)
                    if key not in raw_cache:raw_cache[key]=original_passage(directory,receipt,e);raw_unique+=1
                    if raw_cache[key]['canonical_quote']!=e['quote']:ok=False
                if ok:valid+=1
                else:failures.append(m['mapping_id'])
            # Fresh gate/source recheck of one representative mapping per case.
            # Root relocation is allowed only with equal pinned source/policy state.
            if items:sample=reconstruct(root,output['question'],items[0])
            rows.append({'id':case['id'],'mapping_count':len(items),'mapping_kinds':dict(Counter(m['kind'] for m in items)),
                'exact_mappings_valid':valid,'invalid_mappings':failures,'evidence_anchors_checked':anchors,
                'new_unique_raw_passages_reconstructed':raw_unique,'fresh_gate_reconstruction_sample':sample,
                'candidate_relationship_count':len(mapped.get('relationships',[])),
                'verified_historical_relationships':None,'false_positive_relationship_rate':None,
                'corrections_correctly_detected':None,'missed_relationships':None,'semantic_review':'NOT RUN'})
    return {'schema':'original-mapping-fidelity-audit-v1','run_receipt_sha256':sha((run/'run-receipt.json').read_bytes()),
        'post_run_audit':True,'scope':'Raw/canonical quote and mapping integrity only. No semantic reconstruction quality or independent accuracy claim.',
        'cases':rows,'unique_raw_passages':list(raw_cache.values()),'wall_seconds':time.perf_counter()-start,
        'cpu_seconds':time.process_time()-cpu,'peak_process_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        'human_review_seconds':None,'compute_cost_usd':None,'independent_human_evaluation':'NOT RUN'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory');p.add_argument('run');p.add_argument('--output',required=True);a=p.parse_args();save(a.output,audit(a.directory,a.run))


if __name__=='__main__':main()
