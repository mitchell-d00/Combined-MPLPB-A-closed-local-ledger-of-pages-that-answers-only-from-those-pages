"""Freeze a tracked revision and retain reproducible closed-ledger checks.

Author-written regression evidence only, never independent semantic review.
No original documents or expected answers are rewritten. Output must be new.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import zipfile


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--revision', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--suite', choices=('boundary', 'full'), default='full')
    args = p.parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(['git', 'rev-parse', '--verify', args.revision+'^{commit}'], cwd=repo, text=True).strip()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    archive = output/'source.zip'
    subprocess.run(['git', 'archive', '--format=zip', '--output='+str(archive), revision], cwd=repo, check=True)
    extracted = output/'source'
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad:raise ValueError('Archive CRC failure: '+bad)
        z.extractall(extracted)
    commands = [[sys.executable, '-m', 'unittest', 'tests.test_answer_boundaries',
                 'tests.test_scoped_extensions', 'tests.test_supersession_policy', '-q']]
    if args.suite == 'full':
        commands += [[sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-q'],
                     [sys.executable, '-m', 'tools.evaluate_public_evidence', '--require-capabilities',
                      '--output', str(output/'public-evidence.json')]]
    report = {'schema': 'closed-ledger-reproduction-v1', 'revision': revision,
              'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'environment': {'python': sys.version, 'platform': platform.platform(),
                              'machine': platform.machine(), 'cpu_count': os.cpu_count()},
              'commands': [], 'independent_review': 'NOT RUN',
              'legacy_887_suite_reproduced': False,
              'legacy_887_note': 'No exact legacy 887-case suite or revision established by this runner.',
              'metrics': {'source_bytes_read': None, 'source_count_coverage': None,
                          'false_bridge_rate': None, 'human_labeling_seconds': None},
              'scope': 'Author-written software regression; no independent semantic accuracy measurement.'}
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    failed = False
    for i, command in enumerate(commands):
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        start = time.perf_counter()
        with (output/f'check-{i}.log').open('w') as log:
            try:
                completed = subprocess.run(command, cwd=extracted, env=env, stdout=log,
                                           stderr=subprocess.STDOUT, timeout=1200)
                code, timed_out = completed.returncode, False
            except subprocess.TimeoutExpired:
                code, timed_out = None, True
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        report['commands'].append({'command': command, 'exit_code': code, 'timed_out': timed_out,
            'wall_seconds': time.perf_counter()-start,
            'cpu_seconds': (after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime),
            'log': f'check-{i}.log'})
        failed |= code != 0
        # Preserve partial and failed results after every completed or timed-out check.
        # RUSAGE_CHILDREN is cumulative maximum child RSS, including git/archive.
        report['peak_child_rss_bytes'] = after.ru_maxrss * (1 if sys.platform == 'darwin' else 1024)
        report['peak_memory_scope'] = 'Process-lifetime maximum child RSS, not aggregate process-tree memory.'
        (output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'revision': revision, 'report': str(output/'report.json'), 'passed': not failed}))
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
