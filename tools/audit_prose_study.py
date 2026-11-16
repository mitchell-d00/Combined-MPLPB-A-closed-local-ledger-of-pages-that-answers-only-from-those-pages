"""Audit all new proposal evidence/authority flags against frozen original projections."""
import argparse
import hashlib
from pathlib import Path
import tempfile
import time
import resource
from tools.unprepared_challenge import read,save,summary,projections
from tools.unprepared_sources import import_corpus
from mplpb_work.source_mapping import reconstruct,digest,_state
from mplpb_combined.reader import PROFILES


def audit(corpus,run):
    corpus=Path(corpus);run=Path(run);summary(corpus,run)
    receipt=read(run/'run-receipt.json');imported=read(run/'import-receipt.json');bodies=projections(corpus,imported)
    start=time.perf_counter();cpu=time.process_time();rows=[]
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)/'ledger'
        if import_corpus(corpus,root)!=imported:raise ValueError('Import mismatch')
        for entry in receipt['cases']:
            out=read(run/(entry['id']+'.json'));pack=out.get('investigation',{}).get('prose_candidates',{}).get('information_map',{}).get('proposed_reconstruction',{})
            items=pack.get('propositions',[])+pack.get('connections',[])+pack.get('qualifications',[])
            state=_state(root,out['question'],PROFILES['internal']);valid=0;anchors=0;errors=[]
            for m in items:
                unsigned=dict(m);identity=unsigned.pop('mapping_id',None)
                ok=identity==digest(unsigned) and m['answer_supported'] is False and m['content_truth_verified'] is False and m['source_state']==state
                for e in m['evidence']:
                    record,body=bodies[e['source_id']];a,b=e['body_start'],e['body_end'];anchors+=1
                    ok=ok and e['hash']==record['hash'] and e['path']==record['path'] and type(a) is int and type(b) is int and 0<=a<b<=len(body) and body[a:b]==e['quote']
                if ok:valid+=1
                else:errors.append(m['mapping_id'])
            sample=reconstruct(root,out['question'],items[0]) if items else None
            rows.append({'case_id':entry['id'],'proposal_objects':len(items),'valid_objects':valid,'evidence_anchors_checked':anchors,
                'invalid_objects':errors,'fresh_gate_sample':sample,'semantic_truth_verified':False})
    return {'schema':'rich-prose-evidence-audit-v1','run_receipt_sha256':hashlib.sha256((run/'run-receipt.json').read_bytes()).hexdigest(),
        'rows':rows,'objects_checked':sum(r['proposal_objects'] for r in rows),'valid_objects':sum(r['valid_objects'] for r in rows),
        'evidence_anchors_checked':sum(r['evidence_anchors_checked'] for r in rows),
        'scope':'Every proposed semantic association and scope node: digest, current policy/source state, pin, path, canonical offsets and quote. Original bytes/projections validated by frozen manifest/import. One fresh reconstruct call per case. Fidelity is not semantic correctness.',
        'wall_seconds':time.perf_counter()-start,'cpu_seconds':time.process_time()-cpu,
        'peak_process_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'independent_human_evaluation':'NOT RUN'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('corpus');p.add_argument('run');p.add_argument('--output',required=True);a=p.parse_args();save(a.output,audit(a.corpus,a.run))


if __name__=='__main__':main()
