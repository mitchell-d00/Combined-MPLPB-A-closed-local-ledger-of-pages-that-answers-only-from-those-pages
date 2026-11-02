"""Build/check a content-pinned repository handoff from the last update record."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

GENERATED = {'HANDOFF.md', 'handoff/manifest.json'}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def safe(root, name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts or '.git' in path.parts:
        raise ValueError('Unsafe handoff inventory path')
    target = root / path
    target.resolve().relative_to(root.resolve())
    if not target.is_file():
        raise ValueError('Missing inventory file: '+name+'; stage intentional deletions first')
    return target


def tracked(root, previous=None):
    if (root / '.git').exists():
        raw = subprocess.check_output(['git','ls-files','-z'], cwd=root)
        return sorted(set(raw.decode().split('\0')) - {''} - GENERATED)
    if previous is None:
        raise ValueError('An extracted source ZIP needs its handoff manifest')
    return sorted(previous['files'])


def inventory(root, names):
    return {name:digest(safe(root, name)) for name in names}


def update_record(root):
    record = json.loads((root/'handoff/update.json').read_text())
    if set(record) != {'instruction','scope','validation','limitations','next_steps'}:
        raise ValueError('Update record needs instruction, scope, validation, limitations, next_steps')
    if not isinstance(record['instruction'],str) or not record['instruction'].strip():
        raise ValueError('Record the latest user instruction')
    for field in ('scope','validation','limitations','next_steps'):
        if not isinstance(record[field], list) or not all(isinstance(s,str) and s.strip() for s in record[field]):
            raise ValueError('Invalid update field: '+field)
    return record


def render(record, manifest):
    rows=['# Repository handoff', '',
          'Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.', '',
          'Base commit: `'+manifest['base_revision']+'` (ancestry, not the final self-containing commit).',
          'Source inventory SHA-256: `'+manifest['inventory_sha256']+'`.', '',
          '## Latest user update instructions', '', record['instruction'], '']
    for field,title in (('scope','Implemented scope'),('validation','Validation recorded'),
                        ('limitations','Limitations and blocked checks'),('next_steps','Next steps')):
        rows += ['## '+title, '']+[ '- '+s for s in record[field]]+['']
    rows += ['## Use this ZIP in your repository', '',
             'Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. '
             'Copy the source into your existing checkout while preserving its `.git` directory and personal saves. '
             'Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. '
             'The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.', '',
             'For the next change, update `handoff/update.json` from the latest instruction, stage intended files, '
             'run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.', '']
    return '\n'.join(rows)


def build(root):
    root=Path(root)
    old=json.loads((root/'handoff/manifest.json').read_text()) if (root/'handoff/manifest.json').exists() else None
    record=update_record(root)
    files=inventory(root,tracked(root,old))
    if 'handoff/update.json' not in files or 'AGENTS.md' not in files:
        raise ValueError('Stage AGENTS.md and handoff/update.json before building')
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip() if (root/'.git').exists() else old['base_revision']
    manifest={'schema':'repository-handoff-v1','base_revision':revision,
              'inventory_sha256':hashlib.sha256(canonical(files).encode()).hexdigest(),'files':files}
    (root/'handoff/manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    (root/'HANDOFF.md').write_text(render(record,manifest))
    return manifest


def check(root):
    root=Path(root)
    manifest=json.loads((root/'handoff/manifest.json').read_text())
    actual=inventory(root,tracked(root,manifest))
    if actual != manifest['files'] or hashlib.sha256(canonical(actual).encode()).hexdigest()!=manifest['inventory_sha256']:
        raise ValueError('Handoff is stale: update handoff/update.json, stage intended files, and rebuild')
    if (root/'HANDOFF.md').read_text()!=render(update_record(root),manifest):
        raise ValueError('HANDOFF.md does not match the recorded latest update')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args=parser.parse_args()
    try:
        manifest=(check if args.check else build)(Path(__file__).resolve().parents[1])
    except (ValueError,OSError,KeyError) as exc:
        parser.exit(1,str(exc)+'\n')
    print(('PASS current handoff: ' if args.check else 'Built handoff: ')+manifest['inventory_sha256'])
