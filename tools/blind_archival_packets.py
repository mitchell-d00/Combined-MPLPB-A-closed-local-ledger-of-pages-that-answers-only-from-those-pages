"""Anonymous paired review packets over frozen original-record study outputs.

No draft reference answers, scores, family labels or implementation versions are
exported. These familiar development questions are not an unseen benchmark.
Export validity checks quotation integrity, not semantic correctness or reviewer
independence. Reuse the existing unprepared review/adjudication protocol.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import secrets
import tempfile

from mplpb_answers.body_text import body_text
from mplpb_combined import provenance_gate as G
from mplpb_combined.ledger import Ledger
from mplpb_combined.reader import PROFILES
from tools.sorter_first_study import FAMILIES, ROOT
from tools.unprepared_challenge import frozen, digest, DIMENSIONS
from tools.unprepared_sources import import_corpus, verify, inside


def sha(raw):return hashlib.sha256(raw).hexdigest()


def blind_output(answer):
    result=copy.deepcopy(answer)
    def visit(value):
        if isinstance(value,dict):
            for k in ('code_sha256','proof_sha256','evidence_proof_sha256','trace'):
                value.pop(k,None)
            if isinstance(value.get('verification'),str):value.pop('verification')
            elif isinstance(value.get('verification'),dict):value['verification'].pop('semantic',None)
            for item in value.values():visit(item)
        elif isinstance(value,list):
            for item in value:visit(item)
    visit(result)
    return result


def load_study(directory):
    directory=Path(directory)
    raw=(directory/'packets.json.gz').read_bytes()
    if len(raw)>32*1024**2:raise ValueError('Study archive exceeds review bound')
    with gzip.open(directory/'packets.json.gz','rb') as stream:
        unpacked=stream.read(64*1024**2+1)
    if len(unpacked)>64*1024**2:raise ValueError('Expanded study exceeds review bound')
    groups=json.loads(unpacked);cases={}
    for group in groups:
        if len(group['ids'])!=len(group['standalone']):raise ValueError('Missing output retained in study')
        for identifier,answer in zip(group['ids'],group['standalone']):
            key=(group['family'],identifier)
            if key in cases:raise ValueError('Duplicate study case')
            cases[key]=answer
    return cases,sha(raw)


def prepare(before,after,output,custody):
    output=Path(output);custody=Path(custody)
    try:custody.resolve().relative_to(output.resolve())
    except ValueError:pass
    else:raise ValueError('Private blinding crosswalk must be outside public output')
    left,left_pin=load_study(before);right,right_pin=load_study(after)
    if set(left)!=set(right) or not 1<=len(left)<=200:raise ValueError('Paired outputs must retain every case within the bound')
    output.mkdir(parents=True,exist_ok=False);custody.mkdir(parents=True,exist_ok=False)
    (output/'packets').mkdir();documents={};crosswalk={};template=[];collections=[]
    swap=secrets.randbelow(2)
    for family in sorted({k[0] for k in left}):
        path,seal=FAMILIES[family];corpus=ROOT/path;frozen(corpus,seal)
        collection=secrets.token_hex(8);collections.append(collection)
        review_root=output/collection
        for folder in ('A','B','source-projections'):(review_root/folder).mkdir(parents=True)
        compatible_items=[]
        with tempfile.TemporaryDirectory() as tmp:
            ledger=Path(tmp)/'ledger';receipt=import_corpus(corpus,ledger)
            imported={r['id']:r for r in receipt['records']}
            originals={s['id']:s for s in verify(corpus)['sources']};original_index={}
            records={r.id:r for r in Ledger(ledger).servable()}
            for key in sorted(k for k in left if k[0]==family):
                a,b=left[key],right[key]
                if a['question']!=b['question']:raise ValueError('Original question changed')
                gate=G.gather(ledger,a['question'],PROFILES['internal'])
                eligible={s['id']:s for s in gate.sources};refs=[]
                for sid,source in eligible.items():
                    document={'source_id':sid,'hash':source['hash'],'path':source['path'],
                              'canonical_body':body_text(records[sid].body_html),'ancestry':source['ancestry']}
                    ref=sha(json.dumps(document,sort_keys=True).encode())
                    documents[ref]=document;refs.append(ref)
                    projection=review_root/'source-projections'/(sid+'.txt')
                    if projection.exists() and projection.read_text()!=document['canonical_body']:raise ValueError('Projection identity collision')
                    projection.write_text(document['canonical_body'])
                    origin=originals[imported[sid]['original_id']]
                    raw=inside(corpus,origin['path']).read_bytes()
                    if sha(raw)!=origin['sha256']:raise ValueError('Original source bytes changed')
                    target=review_root/'originals'/(origin['id']+'.raw')
                    target.parent.mkdir(exist_ok=True)
                    if not target.exists():target.write_bytes(raw)
                    original_index[origin['id']]=dict(origin,review_path=str(target.relative_to(review_root)))
                for answer in (a,b):
                    for claim in answer['claims']:
                        for cite in claim.get('citations',[]):
                            record=records.get(cite['source_id']);s=eligible.get(cite['source_id'])
                            if not record or not s or s['hash']!=cite['hash'] or record.path!=cite['path']:
                                raise ValueError('Output quotation is not currently eligible under its original question')
                            body=body_text(record.body_html);lo,hi=cite['body_start'],cite['body_end']
                            if type(lo) is not int or type(hi) is not int or not 0<=lo<hi<=len(body) or body[lo:hi]!=cite['quote']:
                                raise ValueError('Output quotation changed')
                token=secrets.token_hex(8)
                packet={'schema':'blind-archival-packet-v1','id':token,'question':a['question'],
                        'source_refs':refs,'outputs':{'A':blind_output((a,b)[swap]),'B':blind_output((b,a)[swap])}}
                raw=json.dumps(packet,ensure_ascii=False,sort_keys=True).encode()
                (output/'packets'/(token+'.json')).write_bytes(raw)
                crosswalk[token]={'family':key[0],'case_id':key[1],'A':'after' if swap else 'before',
                                 'B':'before' if swap else 'after','packet_sha256':sha(raw)}
                for arm,answer in packet['outputs'].items():
                    records_for_review=[copy.deepcopy(imported[s['id']]) for s in gate.sources]
                    compatible={'case_id':token,'arm':arm,'question':a['question'],'output':answer,
                        'import_receipt':{'records':records_for_review},
                        'notice':'Anonymous output; inspect complete permitted projections. No draft answer, score or implementation identity is supplied.'}
                    (review_root/arm/(token+'.packet.json')).write_text(json.dumps(compatible,ensure_ascii=False,indent=2)+'\n')
                    compatible_items.append({'case_id':token,'arm':arm,'output_sha256':digest(answer),
                        'packet_sha256':digest(compatible),'judgments':dict.fromkeys(DIMENSIONS),
                        'event':dict.fromkeys(('tp','fp','fn')),'relationship':dict.fromkeys(('tp','fp','fn','negative_opportunities')),
                        'correction':dict.fromkeys(('tp','fp','fn')),'reference_scope':None,'reference_complete_within_scope':None,
                        'chronological_errors':None,'appropriate_refusal':None,'unsupported_answer':None,'outcome':None,
                        'labeling_seconds':None,'correction_seconds':None,'review_seconds':None,'rationale':'','citations':[]})
                template.append({'id':token,'packet_sha256':sha(raw),'A':None,'B':None,
                    'permitted_decisions':['complete_correct','partial_correct','correct_refusal','over_refusal','incorrect','unassessed'],
                    'rationale':'','exact_source_citations':[],'review_seconds':None})
        (review_root/'review-template.json').write_text(json.dumps({'schema':'unprepared-human-review-v1',
            'reviewer_id':'','reviewer_is_human':None,'independence_attestation':'','items':compatible_items,'status':'NOT RUN'},indent=2)+'\n')
        (review_root/'originals-index.json').write_text(json.dumps({'sources':list(original_index.values()),
            'notice':'Exact unchanged public originals for documentary-layer inspection. Case-specific source support still refers to the eligible pinned projections in each packet; exported originals are not ledger authorization.'},indent=2)+'\n')
    with gzip.GzipFile(filename=str(output/'documents.json.gz'),mode='wb',mtime=0) as stream:
        stream.write(json.dumps(documents,ensure_ascii=False,sort_keys=True).encode())
    (custody/'crosswalk.json').write_text(json.dumps({'before_archive_sha256':left_pin,'after_archive_sha256':right_pin,'cases':crosswalk},indent=2)+'\n')
    (output/'review-template.json').write_text(json.dumps({'status':'NOT RUN','reviewer_id':'','reviewer_type':None,
        'independence_attestation':'','items':template,'notice':'Exact quotes and valid JSON do not establish semantic correctness. AI assessment is not human review.'},indent=2)+'\n')
    (output/'STATUS.json').write_text(json.dumps({'status':'NOT RUN','questions':len(left),'review_collections':collections,
        'original_bytes_included':True,'original_bytes_hash_verified':True,
        'question_authorship':'familiar developer questions; not independently unseen','independent_human_review':'NOT RUN',
        'fresh_ai_assessment':'NOT RUN','adjudication':'NOT RUN','metrics':None,
        'review_instructions':'Inspect full supplied source bodies, not citations alone. Assess each output independently with exact quote/offset reasons. Preserve both wrong answers and unnecessary refusals. Do not count dependent appearances as independent witnesses. Human review requires real people; do not simulate reviewers.',
        'human_scoring_command':'python -m tools.unprepared_challenge score COLLECTION REVIEWER1.json REVIEWER2.json --output NEW_SCORE.json (add --adjudication FILE for disagreements). The existing validator checks exact citations; participant identity/independence is not authenticated.'},indent=2)+'\n')
    return len(left)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('before','after','output','custody'):p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args();print('Prepared',prepare(a.before,a.after,a.output,a.custody),'anonymous paired cases; semantic review NOT RUN.')


if __name__=='__main__':main()
