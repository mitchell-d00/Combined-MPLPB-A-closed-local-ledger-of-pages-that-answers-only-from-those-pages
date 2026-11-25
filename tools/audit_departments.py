"""Audit navigation ownership without moving implementations or evidence."""
import argparse
from collections import Counter
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEPARTMENTS={'reader','ledger','intake-research','work-coordination','applications',
             'testing-evaluation','delivery-operations'}

def department_for(path, mapping):
    if path in mapping['exact_overrides']:return mapping['exact_overrides'][path]
    parts=Path(path).parts
    if any(p.lower() in {'tests','test_tools','evaluation','killtest'} for p in parts):
        return 'testing-evaluation'
    if parts[0]=='tools':
        for prefix,department in mapping['tool_name_prefix_overrides'].items():
            if parts[-1].startswith(prefix):return department
    return mapping['root_components'][parts[0]]

def audit(root=ROOT):
    root=Path(root);mapping=json.loads((root/'docs/departments/components.json').read_text())
    # The handoff inventory works identically in a checkout and extracted ZIP.
    files=json.loads((root/'handoff/manifest.json').read_text())['files']
    paths=set(files)|{'HANDOFF.md','handoff/manifest.json'}
    counts=Counter()
    for path in paths:
        department=department_for(path,mapping)
        if department not in DEPARTMENTS:raise ValueError('Unknown department: '+department)
        counts[department]+=1
    if {Path(p).parts[0] for p in paths}!=set(mapping['root_components']):
        raise ValueError('Root component map is incomplete or contains a removed component')
    for path in mapping['exact_overrides']:
        if path not in paths:raise ValueError('Broken exact component path: '+path)
    for name in DEPARTMENTS:
        page=root/'docs/departments'/(name+'.md')
        text=page.read_text()
        for required in ['Implementation:','Protecting checks:','Measured status:','Open work:']:
            if required not in text:raise ValueError('Incomplete department entry: '+name)
    index=json.loads((root/'docs/results.json').read_text())
    for family in index['families']:
        if family.get('responsible_department') not in DEPARTMENTS:
            raise ValueError('Evaluation family lacks responsible department: '+family['family'])
    return {'mapped_paths':len(paths),'departments':dict(sorted(counts.items())),
            'unmapped_paths':0,'file_moves':0,
            'meaning':'Navigation/path coverage, not runtime or semantic accuracy'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args();result=audit()
    if a.output:
        with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
