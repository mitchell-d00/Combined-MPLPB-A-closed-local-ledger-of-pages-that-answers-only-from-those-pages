"""Replay the archived Executable Gates probes and check their observations."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
PIN = '6ba371ca07dd9269f28af762ed1971ad484fb6b5'


def verify(repo, output):
    git = ['git', '-C', str(repo)]
    revision = subprocess.check_output([*git, 'rev-parse', 'HEAD'], text=True).strip()
    if revision != PIN:
        raise ValueError(f'Expected MPLPB checkout {PIN}, got {revision}')
    dirty = subprocess.check_output(
        [*git, 'status', '--porcelain', '--', 'mplpb_work', 'mplpb_combined', 'mplpb_answers'],
        text=True,
    )
    if dirty:
        raise ValueError('The MPLPB executable packages must match the pinned checkout')
    output.mkdir()
    result = output / 'mplpb-results.json'
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'probes/run_probes.py'),
                    str(repo), str(result)], check=True)
    actual = json.loads(result.read_text(encoding='utf-8'))
    original = json.loads((HERE / 'probes/results.json').read_text(encoding='utf-8'))
    if actual['repository_revision'] != PIN or actual['probes'] != original['probes']:
        raise ValueError('The MPLPB replay differs from the archived probe outcomes')
    observed = subprocess.check_output(['sh', str(HERE / 'probes/git_probe.sh')], text=True)
    (output / 'git-results.txt').write_text(observed, encoding='utf-8')
    if observed != (HERE / 'reproduction/git-results.txt').read_text(encoding='utf-8'):
        raise ValueError('The Git replay differs from the retained server readbacks')
    print('PASS: all seven MPLPB pairs and both local Git fixtures matched')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mplpb', type=Path, help='Clean MPLPB checkout at the paper revision')
    parser.add_argument('output', type=Path, help='New directory for replay evidence')
    args = parser.parse_args()
    try:
        verify(args.mplpb.resolve(), args.output.resolve())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
