"""Verify and replay the committed 73-positive/20-control reference evidence.

This checks local declarations and frozen development expectations, not external
truth, source authorship, independent language accuracy or default eligibility.
"""
import argparse
import hashlib
import json
from pathlib import Path
from tools import build_reference_corpus as C

ROOT=Path(__file__).resolve().parents[1]
BUNDLE=ROOT/'evaluation/reference-corpus-reproduction'
INPUTS=('reference_corpus/catalog.v1.json','reference_corpus/probes.v1.json',
        'reference_corpus/probes.v1.pre-amendment.json','reference_corpus/PROBE_AMENDMENTS.md')
FIELDS=('kind','correct_supported','quote','document_id','document_sha256','depth','origin','derived_from')


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(bundle=BUNDLE):
    bundle=Path(bundle)
    run=json.loads((bundle/'run.json').read_text())
    for name in INPUTS:
        if file_hash(ROOT/name)!=run['frozen_inputs'][name]:
            raise ValueError('Frozen input differs: '+name+'; do not silently rewrite historical evidence')
    expected=json.loads((bundle/'files.sha256.json').read_text())
    actual={p.relative_to(bundle).as_posix():file_hash(p) for p in (bundle/'releases').rglob('*')
            if p.is_file() and p.name!='.lock'}
    actual.update({name:file_hash(bundle/name) for name in ('run.json','results.csv','tests.txt','build-summary.json')})
    if actual!=expected:
        raise ValueError('Committed snapshot or report inventory differs from its recorded hashes')
    catalog,probes=C.load()
    C.validate_catalog(catalog,probes)
    manifest=json.loads((bundle/'releases/release-audit.json').read_text())
    if tuple(v['version'] for v in manifest['versions'])!=C.RELEASES:
        raise ValueError('Missing or reordered release stage')
    results=[]
    for item in manifest['versions']:
        version=item['version'];root=bundle/'releases'/('v'+version)/'ledger'
        if version not in C.RELEASES:raise ValueError('Unknown release stage')
        selected=[f for f in catalog['facts'] if f['stage']<=C.RELEASES.index(version)]
        C.validate_ledger(root,catalog,selected)
        stored=json.loads((root.parent/'audit.json').read_text())
        rows,metrics=C.score(root,probes['probes'])
        if metrics!=stored['metrics'] or metrics!=item['metrics'] or len(rows)!=len(stored['rows']):
            raise ValueError('Replay metrics differ in '+version)
        for now,old in zip(rows,stored['rows']):
            if now['id']!=old['id'] or any(now[k]!=old[k] for k in FIELDS):
                raise ValueError('Replay evidence differs in '+version+' / '+now['id'])
        results.append(dict(version=version,positive_supported=metrics['correct_supported'],
                            positive_total=metrics['answerable_total'],negative_refusals=metrics['correct_refusals'],
                            negative_total=metrics['negative_total'],wrong_returns=metrics['wrong_returns'],
                            ambiguities=metrics['ambiguous']))
    return dict(role='Authored development replay; not independent validation or external fact certification',
                evaluated_source_revision=run['source_revision'],versions=results,
                current_engine_matches_recorded=manifest['engine_code_sha256']==C.code_pins())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=verify();payload=json.dumps(result,indent=2)+'\n'
    if args.output:
        if args.output.exists():parser.error('Choose a new output path; do not overwrite earlier reports')
        args.output.write_text(payload,encoding='utf-8')
    print(payload,end='')
