"""Check Bastet I/O after the existing Cryptid claim scorer has run."""
import argparse
from collections import Counter
from pathlib import Path

from tools.cryptid_trial_v5 import read, save, sha

ROOT=Path(__file__).resolve().parents[3]


def score(registry, key_file, raw, prior):
    freeze=read(registry.with_name('freeze.json'))
    assert sha(registry)==freeze['registry_sha256']
    assert sha(key_file)==freeze['key_sha256']
    assert sha(Path(__file__))==freeze['harness'][str(Path(__file__).relative_to(ROOT))]
    contracts=read(key_file)
    run=read(raw/'run.json')
    checked=read(prior)
    assert checked['run_sha256']==sha(raw/'run.json') and checked['key_sha256']==sha(key_file)
    per_id={row['id']:row for row in checked['cases']}
    rows=[]
    questions=set()
    for case,attempt in zip(read(registry)['cases'],run['cases'],strict=True):
        ident=case['id']
        assert attempt['id']==ident
        packet_path=ROOT/case['packet']/'case.json'
        assert sha(packet_path)==case['files']['case.json']
        packet=read(packet_path)
        original=packet['question']
        questions.add(original)
        target=contracts[ident]['io']
        if attempt['execution_status']!='completed':
            rows.append(dict(id=ident,outcome='execution_failure',executed=False))
            continue
        path=raw/ident/'result.json'
        assert sha(path)==attempt['raw_sha256']
        result=read(path)
        answer=result['answer']
        assert answer['question']==original
        diagnostic=answer['diagnostic']
        claims=answer['claims']
        actual=[]
        for claim in claims:
            for c in claim['citations']:
                witness=c.get('original_witness',{})
                actual.append({k:c.get(k) for k in ('source_id','quote','body_start','body_end')} |
                              {k:witness.get(k) for k in ('start_byte','end_byte','body_html_sha256')})
        cites_equal=actual==target['witnesses']
        diagnostic_ok=(diagnostic['code']==target['diagnostic'] if target['diagnostic']=='supported'
                       else bool(diagnostic.get('code')))
        withholding=target['kind']=='abstain'
        passed=(per_id[ident]['passed'] and answer['kind']==target['kind'] and cites_equal
                and answer['missing']==target['missing'] and diagnostic_ok)
        records={r['id']:r for r in result['records']}
        selected_id=target['selected_source']
        picked=records.get(selected_id)
        receipt=answer.get('documentary_support',{}).get('named_source_selection')
        eligible_ids={source['id'] for source in packet['sources'] if not source.get('withdraw')}
        eligible_pin=bool(picked and selected_id in eligible_ids and receipt and receipt==dict(
            status='verified',source_id=selected_id,path=picked['path'],hash=picked['hash']))
        invalid_selection=bool(receipt and receipt.get('status')=='verified' and not eligible_pin)
        selection_verified=eligible_pin or (not withholding and passed and not invalid_selection)
        if invalid_selection:
            outcome='incorrect_selection'
        elif passed:
            outcome='withhold' if withholding else 'complete'
        elif answer['answer_supported'] or claims:
            outcome='unsupported'
        else:
            outcome='miss'
        rows.append(dict(id=ident,outcome=outcome,executed=True,kind=answer['kind'],missing=answer['missing'],
                         diagnostic=diagnostic, exact_witnesses=cites_equal,
                         verified_document_selection=selection_verified,
                         verified_attribution=not withholding and passed,
                         required_selection=selected_id,
                         selection_or_proof_obligation=target.get('selection_or_proof_obligation'),
                         proof_stage_control=(withholding and (
                             eligible_pin and diagnostic['code']=='named_report_content_unresolved'
                             or not selected_id and diagnostic['code']=='named_report_source_unresolved')),
                         raw_sha256=sha(path)))
    return dict(reader=run['reader_commit'],cases=len(rows),distinct_questions=len(questions),
                counts=dict(Counter(r['outcome'] for r in rows)),rows=rows,
                evidence='First output retained. Interpretation-only controls establish safe refusal only.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('registry','key','run','prior','output'):
        parser.add_argument('--'+name, required=True, type=Path)
    args=parser.parse_args()
    save(args.output,score(args.registry,args.key,args.run,args.prior))
