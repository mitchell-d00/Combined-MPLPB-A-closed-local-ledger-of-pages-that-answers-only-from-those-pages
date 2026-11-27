"""Recompare consumed public cases against the recorded Thoth contracts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

from tools.bubble_wrap_trial import normal


THOTH = Path('evaluation/egyptian-gods/thoth')
WAMPUS = Path('evaluation/cryptid/wampus-cat')
BUNYIP = Path('evaluation/cryptid/bunyip/round2/replacement')
ARMS = [
    (THOTH / 'development', 12, 'development-thoth', 'development'),
    (THOTH / 'fresh', 12, 'fresh-thoth', 'fresh'),
    (WAMPUS / 'development', 12, 'wampus-development-thoth', 'development'),
    (WAMPUS / 'fresh', 10, 'wampus-fresh-thoth', 'development'),
    (BUNYIP / 'development', 10, 'bunyip-development-thoth', 'development'),
    (BUNYIP / 'R', 20, 'bunyip-R-thoth', 'development'),
    (BUNYIP / 'X', 20, 'bunyip-X-thoth', 'development'),
]


def run(args):
    results = []
    for directory, count, prefix, evidence in ARMS:
        registry = directory / 'registry.json'
        rows = json.loads(registry.read_bytes())['cases']
        assert len(rows) == count
        archive = THOTH / f'{evidence}-evidence.zip'
        output = args.output / prefix
        command = [sys.executable, '-m', 'tools.cryptid_trial_v5', '--registry',
                   str(registry), '--implementation', str(args.implementation),
                   '--source-commit', args.commit, '--output', str(output)]
        code = subprocess.run(command, check=False).returncode
        with zipfile.ZipFile(archive) as reference:
            run_record = json.loads(reference.read(f'{prefix}/run.json'))
            assert run_record['registry_sha256'] == hashlib.sha256(registry.read_bytes()).hexdigest()
            for row in rows:
                case = row['id']
                before = json.loads(reference.read(f'{prefix}/{case}/result.json'))['answer']
                result_path = output / case / 'result.json'
                after = json.loads(result_path.read_bytes())['answer'] if result_path.exists() else None
                results.append({'case': case, 'arm': prefix, 'runner_exit': code,
                                'executed': after is not None,
                                'same_contract': after is not None and normal(before) == normal(after)})
    receipt = {'candidate_commit': args.commit, 'planned': len(results),
               'executed': sum(row['executed'] for row in results),
               'same_contract': sum(row['same_contract'] for row in results),
               'rows': results}
    (args.output / 'comparison.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'rows'}), flush=True)
    return any(not row['same_contract'] or row['runner_exit'] for row in results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--implementation', type=Path, required=True)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    raise SystemExit(run(parser.parse_args()))
