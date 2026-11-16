"""Replay bounded expert crawling on unchanged, byte-pinned original papers.

Authored and inspected development evidence, not human historical accuracy.
Output is a new report; no original source, frozen probe or report is rewritten.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import subprocess
import tempfile

from mplpb_combined.ledger import write
from mplpb_work.investigation import investigate

ROOT=Path(__file__).resolve().parents[1]
KEYS=('local-web','smart-paper','combined-v3','combined-v1')


def evaluate():
    sources=json.loads((ROOT/'docs/research/mplpb-originality/mplpb-sources.json').read_text())['sources']
    evidence=[]
    with tempfile.TemporaryDirectory(prefix='mplpb-original-history-') as directory:
        for number,key in enumerate(KEYS,1):
            source=sources[key]
            raw=(ROOT/source['path']).read_bytes()
            actual=hashlib.sha256(raw).hexdigest()
            if actual!=source['sha256']:
                raise ValueError('Original source pin changed: '+key)
            record=write(directory,doc_id='ORIGINAL-%04d'%number,title=key,
                         scope='original MPLPB historical document witness',origin='machine',
                         body_html='<pre>'+html.escape(raw.decode())+'</pre>')
            evidence.append({'key':key,'original_path':source['path'],'original_sha256':actual,
                             'historical_ref':source['revision'],'wrapper_id':record.id,
                             'wrapper_hash':record.hash})
        report=investigate(directory,
            'Trace declared relationships between Combined MPLPB, Smart Local MPLPB, and MPLPB as a Local Web; keep historical claims qualified',
            start_source_ids=['ORIGINAL-0003'],max_hops=2)
    expected={'ORIGINAL-0001','ORIGINAL-0002','ORIGINAL-0003','ORIGINAL-0004'}
    summary={'originals_byte_verified':len(evidence),
             'sources_reached':len(report['sources']),
             'expected_originals_reached':{s['id'] for s in report['sources']}==expected,
             'observations_verified':len(report['observations']),
             'traversed_declared_relations':sum(e['status']=='traversed' for e in report['relations']),
             'unresolved_relations':sum(e['status']!='traversed' for e in report['relations']),
             'negative_supersession_qualification_preserved':any(o['kind']=='not_superseded' for o in report['observations']),
             'expert_stages_passed':sum(r['status']=='passed' for r in report['receipts']),
             'answer_supported':report['answer_supported'],
             'truth_verified':report['truth_verified']}
    return {'schema':'historical-expert-replay-v1',
            'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip() if (ROOT/'.git').exists() else 'extracted candidate source',
            'scope':'Authored developer replay on inspected original papers; typed documentary observations only, not general historical answer accuracy.',
            'source_evidence':evidence,'summary':summary,'investigation':report}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='new report path; existing files are never overwritten')
    args=parser.parse_args()
    result=evaluate()
    if args.output:
        with args.output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(result['summary'],indent=2))
    return 0 if result['summary']['expected_originals_reached'] and result['summary']['expert_stages_passed']==3 else 1


if __name__=='__main__':raise SystemExit(main())
