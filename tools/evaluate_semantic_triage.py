"""Frozen authored flagger probes. Fixture expectations are not historical truth."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import time

from mplpb_combined.ledger import write
from mplpb_answers.body_text import body_text
from mplpb_answers.local_narrator import NarratorConfig
from mplpb_work.semantic_triage import flag_pairs

PROBES=[
 ('T1','Mira’s note says the west gate stayed shut during the inspection.',
  'The inspector found the western entrance closed throughout the visit.',['AMBIGUOUS_LINK_CANDIDATE']),
 ('T2','In the signed account, Nora states that every crate arrived.',
  'Nora’s account states that two crates never arrived.',['POTENTIAL_CONTRADICTION']),
 ('T3','The orchard keeper recorded the yield of apple trees.',
  'The engineer upgraded an Apple laptop.',[]),
 ('T4','Worked example: the fictional captain orders every boat to leave.',
  'The station manager ordered every train to stop.',[]),
 ('T5','The witness did not deny that the cart might have arrived.',
  'The register records no verified arrival for the cart.',['AMBIGUOUS_LINK_CANDIDATE']),
 ('T6','The lamp went out before the bell rang.',
  'The bell rang after the lamp went out.',['AMBIGUOUS_LINK_CANDIDATE']),
]


def _hash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);rows=[];expectations=[]
    for ident,left,right,expected in PROBES:
        anchors=[]
        for side,quote in (('A',left),('B',right)):
            record=write(output/'ledger',doc_id=ident+'-'+side,title='Fictional archive probe',scope='archive',
                         body=quote,origin='machine',when='2026-11-18T00:00Z')
            text=body_text(record.body_html)
            anchors.append(dict(source_id=record.id,path=record.path,hash=record.hash_actual,
                                body_start=0,body_end=len(text),quote=text))
        rows.append({'id':ident,'pair':{'left':anchors[0],'right':anchors[1]}})
        expectations.append({'id':ident,'developer_expected_flags':expected})
    (output/'pairs.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
    (output/'expectations.json').write_text(json.dumps(expectations,indent=2)+'\n')
    seal={str(p.relative_to(output)):_hash(p) for p in sorted(output.rglob('*')) if p.is_file()}
    (output/'seal.json').write_text(json.dumps({'files':seal,'scope':'Six authored fictional utility probes; no independent semantic labels.'},indent=2)+'\n')


def run(output,config):
    output=Path(output);seal=json.loads((output/'seal.json').read_text())
    for path,expected in seal['files'].items():
        if _hash(output/path)!=expected:raise ValueError('Probe input changed')
    if (output/'run.json').exists():raise ValueError('Preserve the prior run; use a new prepared directory')
    start=time.perf_counter();cases=[]
    for row in json.loads((output/'pairs.json').read_text()):
        result=flag_pairs(output/'ledger','Review archive passages',[row['pair']],enabled=True,config=config)
        cases.append({'id':row['id'],'result':result})
        (output/'partial-run.json').write_text(json.dumps({'cases':cases},indent=2)+'\n')
    # Expectations are consulted only after all inference requests finish.
    expected={r['id']:set(r['developer_expected_flags']) for r in json.loads((output/'expectations.json').read_text())}
    useful=false=missed=0
    for row in cases:
        flags={x['kind'] for x in row['result']['flags']};wanted=expected[row['id']]
        useful+=len(flags&wanted);false+=len(flags-wanted);missed+=len(wanted-flags)
    result={'schema':'authored-triage-probes-v1','configuration':config.__dict__,'cases':cases,
            'metrics':{'developer_expected_useful_flags':useful,'developer_unexpected_flags':false,
                       'developer_expected_but_missing_flags':missed,'wall_seconds':time.perf_counter()-start,
                       'accepted_schema_responses':sum(c['result']['status'] in {'flagged','model_abstained'} for c in cases),
                       'historical_relationship_precision':None,'historical_relationship_recall':None,
                       'human_review_seconds':None},'independent_human_review':'NOT RUN',
            'environment':{'python':platform.python_version(),'platform':platform.platform()},
            'notice':'Developer utility expectations on six fictional pairs; not ground-truth historical relationships or independent model accuracy.'}
    for path,expected_hash in seal['files'].items():
        if _hash(output/path)!=expected_hash:raise ValueError('Inference altered source bytes')
    with (output/'run.json').open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['metrics'],indent=2))


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('prepare','run'));p.add_argument('output',type=Path)
    p.add_argument('--backend',choices=('ollama','llamacpp','openai'));p.add_argument('--model');p.add_argument('--base-url');a=p.parse_args(argv)
    if a.command=='prepare':prepare(a.output)
    else:
        default=NarratorConfig.from_env();config=NarratorConfig(a.backend or default.backend,a.model or default.model,a.base_url or default.base_url,60)
        run(a.output,config)


if __name__=='__main__':main()
