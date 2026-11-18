"""Post-run source-only assessment packet; no scores or reference keys copied.

Run from the repo root: python evaluation/fixpack/2026-11-18/build_ai_packet.py STUDY NEW_PACKET
"""
import hashlib
import json
from pathlib import Path
import random
import shutil
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.sorter_first_study import FAMILIES
from tools.unprepared_sources import verify,projected
from tools.unprepared_challenge import read,frozen
from tools.source_roundtrip import original_passage


def build(study,destination):
    study=Path(study);destination=Path(destination)
    # Fail before creating a packet if any native execution is absent/incomplete.
    cases=[]
    for family,(relative,seal) in FAMILIES.items():
        corpus=ROOT/relative;frozen(corpus,seal)
        for q in read(corpus/'questions.json')['cases']:
            row=read(study/family/'direct'/(q['id']+'.json'))
            if row['execution_status']!='completed' or row['question']!=q['question']:
                raise ValueError('Incomplete or changed question')
            cases.append((family,corpus,q,row))
    destination.mkdir(parents=True,exist_ok=False)
    for family,(relative,_) in FAMILIES.items():
        corpus=ROOT/relative;manifest=verify(corpus);folder=destination/family;folder.mkdir()
        (folder/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        for source in manifest['sources']+manifest['provenance_files']:
            p=folder/source['path'];p.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(corpus/source['path'],p)
        receipt=read(study/family/'import-receipt.json')
        (folder/'import-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        # This text is a reversible inspection aid; raw source files remain authority.
        projected_rows=[{'source_id':s['id'],'path':s['path'],'text':projected(s,(corpus/s['path']).read_bytes())[0]} for s in manifest['sources']]
        (folder/'inspection-text.json').write_text(json.dumps(projected_rows,indent=2,ensure_ascii=False)+'\n')
    output=[]
    for family,corpus,q,row in cases:
        receipt=read(study/family/'import-receipt.json');a=row['answer']
        output.append({'id':q['id'],'family':family,'question':q['question'],
            'result':{k:a.get(k) for k in ('kind','answer_supported','text','claims','missing','clarification','diagnostic')},
            'original_evidence':[original_passage(corpus,receipt,e) for c in a.get('claims',[]) for e in c.get('citations',[])]})
    random.Random(18112026).shuffle(output)
    (destination/'cases.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n')
    (destination/'INSTRUCTIONS.json').write_text(json.dumps({
        'task':'Assess each answer against supplied original sources only. Do not inspect repository, prior outputs, expected labels, scores or implementation changes.',
        'required_per_case':['id','assessment: complete_correct|partial_correct|appropriate_refusal|over_refusal|incorrect|uncertain',
                             'source_id and exact quotation for every accepted claim or potentially missed answer',
                             'limitations; distinguish source-attributed statement from event truth'],
        'caution':'A conflict result may mean retrieval ambiguity, not historical contradiction. Unsupported exhaustive responsibility, historical priority or causality must remain unsupported. Do not infer events from document dates or reported instructions.',
        'review_status':'AI assessment only; not human-independent semantic accuracy or unseen evaluation.',
        'write_result':'assessment.json outside this frozen packet; return cited reasons. Unreviewed cases remain explicit.'},indent=2)+'\n')
    files={p.relative_to(destination).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destination.rglob('*')) if p.is_file()}
    (destination/'seal.json').write_text(json.dumps({'files':files,'scores_included':False,'answer_keys_included':False,'change_log_included':False},indent=2)+'\n')


if __name__=='__main__':build(*sys.argv[1:])
