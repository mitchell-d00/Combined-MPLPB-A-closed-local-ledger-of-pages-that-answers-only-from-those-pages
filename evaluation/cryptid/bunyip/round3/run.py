"""Run the sealed synthetic diagnostic against its four pinned reader ZIPs."""
import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from tools.cryptid_trial_v5 import read, save, sha

ROOT = Path(__file__).resolve().parents[4]
STUDY = Path('evaluation/cryptid/bunyip/round3')
PACKAGES = ('mplpb_answers', 'mplpb_combined', 'mplpb_work')


def verify():
    home = ROOT/STUDY/'diagnostic'
    freeze = read(home/'freeze.json')
    registry_path = home/'registry.json'
    assert sha(registry_path) == freeze['registry_sha256'] and freeze['public_raw_output'] is True
    assert all(sha(ROOT/path) == digest for path, digest in freeze['harness'].items())
    cases = read(registry_path)['cases']
    assert len(cases) == 12 and len({c['id'] for c in cases}) == 12
    for entry in cases:
        ident = entry['id']
        assert re.fullmatch(r'BUNYIP-R3-D0[1-6]-[AB]', ident)
        packet = home/'inputs'/ident
        assert packet.relative_to(ROOT) == Path(entry['packet'])
        assert {p.name for p in packet.iterdir()} == {'case.json'}
        raw = packet/'case.json'
        assert raw.is_file() and not raw.is_symlink() and sha(raw) == entry['files']['case.json']
        case = read(raw)
        assert case['id'] == ident and case['adapter_mode'] == 'documentary' and case['profile'] == 'internal'
        assert 1 <= len(case['sources']) <= 2
        for src in case['sources']:
            assert src['origin'] == 'machine' and src['title'] == 'Synthetic documentary record'
            assert set(src) == {'title', 'origin', 'id', 'body_html', 'external', 'when'}
    return registry_path


def run(out, work):
    registry = verify()
    out.mkdir()
    work.mkdir()
    readers = read(ROOT/STUDY/'readers.json')
    outcomes = []
    for role, pin in readers.items():
        assert role in {'released', 'c3', 'wampus', 'thoth'}
        revision = pin['commit']
        assert re.fullmatch(r'[a-f0-9]{40}', revision)
        archive = out/f'{role}-runtime.zip'
        runtime = work/role
        runtime.mkdir()
        with (out/f'{role}.log').open('x') as log:
            subprocess.run(['git', 'fetch', '--no-tags', '--depth=1', 'origin', revision],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
            subprocess.run(['git', 'archive', '--format=zip','-0','-o', str(archive),
                            revision, *PACKAGES], check=True)
            assert sha(archive) == pin['runtime_zip_sha256']
            with zipfile.ZipFile(archive) as reader:
                reader.extractall(runtime)
            log.flush()
            result = subprocess.run(['sudo', 'env', f'PYTHONPATH={ROOT}', 'MPLPB_REQUIRE_SANDBOX=1',
                sys.executable, '-m', 'tools.cryptid_trial_v5', '--registry', str(registry),
                '--implementation', str(runtime), '--source-commit', revision, '--output', str(out/role)],
                stdout=log, stderr=subprocess.STDOUT)
        outcomes.append(dict(role=role, commit=revision, archive_sha256=sha(archive), exit_code=result.returncode))
        print(role, result.returncode, flush=True)
    save(out/'run-receipt.json', outcomes)
    return int(any(row['exit_code'] for row in outcomes))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--work', type=Path)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    if args.verify_only:
        verify()
    else:
        assert args.output and args.work
        raise SystemExit(run(args.output.resolve(), args.work.resolve()))
