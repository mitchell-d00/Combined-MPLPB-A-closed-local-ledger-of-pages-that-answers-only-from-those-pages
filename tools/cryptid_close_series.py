"""Update live navigation from retained immutable run and score records."""
import argparse,json,sys
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.cryptid_trial import read

def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def main(a):
    home=ROOT/'evaluation/cryptid'/a.family.lower();base=read(home/a.baseline);candidate=read(home/a.candidate);transfer=read(home/a.transfer);archive=read(home/a.receipt)
    programme=read(ROOT/'evaluation/cryptid/programme.json');row=next(s for s in programme['series'] if s['family']==a.family)
    row.update(status='COMPLETED_WITH_RETAINED_MISSES' if candidate['counts']['positive_misses'] or transfer['counts']['positive_misses'] else 'COMPLETED_FROZEN_TARGETS_PASS',baseline=dict(base['counts'],score=a.baseline),candidate=dict(candidate['counts'],score=a.candidate,candidate_commit=archive['candidate_commit'],zip_sha256=archive['zip_sha256']),transfer=dict(transfer['counts'],score=a.transfer,status='FAILED_COVERAGE_CONSUMED' if transfer['counts']['positive_misses'] else 'PASS_ONCE_CONSUMED',custody='same-operator; template-visible, no independent blinding'),limitations=a.limitations)
    write(ROOT/'evaluation/cryptid/programme.json',programme)
    rules=read(ROOT/'evaluation/cryptid/shared-rules.json');rules['rules'].append({'rule':a.rule,'responsible_department':'reader','development_cases':[r['id'] for r in read(home/'development/registry.json')['cases']],'consumed_transfer_cases':[r['id'] for r in read(home/a.transfer_registry)['cases']],'protected_operation':row['mechanism'],'remaining_mechanism':a.limitations,'caps_changed':False})
    write(ROOT/'evaluation/cryptid/shared-rules.json',rules)
    text=f'''# {a.family} — local retained study

Last reviewed: 2026-11-25.

Mechanism: {row['mechanism']}

Baseline **{base['counts']['passed']}/{base['counts']['scored']}** → candidate **{candidate['counts']['passed']}/{candidate['counts']['scored']}**; positive misses {base['counts']['positive_misses']} → {candidate['counts']['positive_misses']}; false-supported claims {candidate['counts']['false_support']}. Transfer once: **{transfer['counts']['passed']}/{transfer['counts']['scored']}**, {transfer['counts']['positive_misses']} positive misses, {transfer['counts']['false_support']} false support. Completed, unscored and budget counts remain in each score.

{a.limitations}

Tested committed candidate `{archive['candidate_commit']}`. Scoped ZIP SHA-256 `{archive['zip_sha256']}`. This is not the final full-repository delivery ZIP.

[Development seal](development/freeze.json), [expected claims and withholding](development/key.json), [baseline]({a.baseline}), [candidate]({a.candidate}), [once-only transfer]({a.transfer}), [archive receipt]({a.receipt}). Input records link source hashes, origin, protected operation, budgets and raw run locations. Keys/scorer/generator remain outside the isolated worker. Transfer is now consumed preservation material.

Reproduce development from an extracted candidate with `python tools/cryptid_trial_v3.py --registry evaluation/cryptid/{a.family.lower()}/development/registry.json --implementation EXTRACTED_ROOT --source-commit {archive['candidate_commit']} --output NEW_RUN_DIRECTORY`; use the versioned scorer recorded by the score. Run with functioning host Bubblewrap; never fall back to an unisolated worker.

Same-operator templates, implementation and scoring. Independent preparation/blinding, semantic and historical adjudication, outside-custodian scoring and native OOCC remain **NOT_RUN**. Publication remains **LOCAL_ONLY**.
'''
    p=home/'README.md';p.write_text(text)
    catalog=read(ROOT/'docs/documentation.json');catalog['documents'][str(p.relative_to(ROOT))]={'classification':'current','reviewed_on':'2026-11-25','reason':'Local Cryptid study navigation; retained raw evidence and failures linked.'};write(ROOT/'docs/documentation.json',catalog)
    inventory=read(ROOT/'docs/results.json');r=next(x for x in inventory['families'] if x['family']=='cryptid');r['measurement_status']=f'Local sequential Cryptid studies through {a.family}; per-family counts and failed attempts in programme.json; final integration pending; same-operator, independent evaluations NOT_RUN.'
    for tool in ['tools/cryptid_close_series.py','tools/cryptid_claim_score_v4.py','tools/cryptid_preserve_all.py']:
        if tool not in r['runners']:r['runners'].append(tool)
    write(ROOT/'docs/results.json',inventory)
    h=read(ROOT/'handoff/update.json');h['validation'].append(f"{a.family}: {base['counts']['passed']}/{base['counts']['scored']} -> {candidate['counts']['passed']}/{candidate['counts']['scored']} development; transfer {transfer['counts']['passed']}/{transfer['counts']['scored']} once, false support {transfer['counts']['false_support']}; candidate {archive['candidate_commit']} ZIP SHA256 {archive['zip_sha256']}. {a.limitations}")
    h['next_steps']=[a.next,'Finish all remaining series and clean final full-ZIP checks. LOCAL_ONLY: no push, PR mutation, merge or deployment.'];write(ROOT/'handoff/update.json',h)
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['family','baseline','candidate','transfer','rule','limitations','next']:p.add_argument('--'+n,required=True)
    p.add_argument('--receipt',default='candidate-freeze.json');p.add_argument('--transfer-registry',default='consumed-transfer/registry.json')
    main(p.parse_args())
