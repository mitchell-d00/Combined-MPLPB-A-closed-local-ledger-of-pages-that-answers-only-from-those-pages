"""Replay claim-boundary regressions; not a new runtime authority framework.

The optional baseline comparison runs the *new* development tests against an
archived old implementation. It is not a rerun of a historical published suite.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    'A_answer': ['tests.test_answer_reliability', 'tests.test_answer_support', 'tests.test_page_retrieval', 'tests.test_release_answer_contract'],
    'B_C_artifact_release': ['tests.test_release_evidence', 'tests.test_handoff'],
    'D_work': ['tests.test_specialist_continuity'],
}
TARGETS = [
    'test_completion_cannot_drop_unmet_criterion_in_same_write',
    'test_completion_cannot_replace_goal_using_old_receipt',
    'test_completion_cannot_replace_task_inputs_using_old_receipt',
    'test_completion_allows_reordered_identical_criteria',
    'test_completion_accepts_fresh_execution_after_explicit_contract_revision',
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def replay(root, tests):
    # Separate process imports the implementation under test, not this runner's
    # already-imported modules. Startup/setup time is included in elapsed time.
    command = [sys.executable, '-m', 'unittest', *tests, '-v']
    env = dict(os.environ, PYTHONPATH=str(root))
    start = time.perf_counter()
    process = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True)
    output = process.stdout + process.stderr
    return {'command': command, 'exit_code': process.returncode,
            'elapsed_seconds_including_setup': time.perf_counter()-start,
            'reported_test_count': int(re.search(r'Ran (\d+) tests?', output)[1]) if re.search(r'Ran (\d+) tests?', output) else None,
            'cases': [{'test': name, 'outcome': result} for name, result in
                      re.findall(r'^(test_\w+) .*? \.\.\. (ok|FAIL|ERROR|skipped[^\n]*)$', output, re.M)],
            'output': output}


def artifact_boundary():
    """A coherent manifest is not an arbitrary semantic acceptance oracle."""
    sys.path.insert(0, str(ROOT))
    from tools.release_evidence import GATES, create, verify
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory); commit = 'a'*40
        expected = b'EXPECTED: measured outcome'
        unrelated = b'UNRELATED: draft'
        with zipfile.ZipFile(path/'mplpb-repository.zip', 'w') as archive:
            archive.writestr('requested-result.txt', unrelated)
        digest = sha(path/'mplpb-repository.zip')
        (path/'commit.sha').write_text(commit+'\n')
        (path/'tree.sha').write_text('b'*40+'\n')
        (path/'mplpb-repository.zip.sha256').write_text(digest+'  mplpb-repository.zip\n')
        (path/'mplpb-candidate-preview.html').write_bytes(unrelated)
        # These labels are authored fixture input, NOT executed CI evidence.
        (path/'validation-report.txt').write_text('\n'.join(['Git commit packaged: '+commit, 'ZIP SHA-256: '+digest, *GATES])+'\n')
        create(path, commit); result = verify(path, commit)
        with zipfile.ZipFile(path/'mplpb-repository.zip') as archive:
            archive_readable = archive.testzip() is None
            actual = archive.read('requested-result.txt')
        assert archive_readable and actual != expected
        return {'role': 'Authored trust/semantic boundary control; not an uncovered verifier bug',
                'gate_labels_are_fixture_data_not_executed_ci_results': True,
                'commit_and_tree_are_example_identifiers': True,
                'requested_bytes_hex': expected.hex(), 'actual_bytes_hex': actual.hex(),
                'zip_readable': archive_readable, 'manifest_verified': True,
                'native_status': result['status'], 'requested_semantic_content_satisfied': actual == expected,
                'conclusion': 'Manifest verification is scoped to coherent inputs from trusted CI; it does not validate arbitrary requested content or certify a public deployment.'}


def baseline_comparison(ref):
    if not re.fullmatch(r'[0-9a-f]{40}', ref):
        raise ValueError('Use a full baseline commit SHA')
    names = ['tests.test_specialist_continuity.ContinuityTests.'+name for name in TARGETS]
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        packed = subprocess.check_output(['git', 'archive', ref], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(packed)) as archive:
            archive.extractall(root, filter='data')
        old_hash = sha(root/'mplpb_work/store.py')
        shutil.copyfile(ROOT/'tests/test_specialist_continuity.py', root/'tests/test_specialist_continuity.py')
        old = replay(root, names)
    new = replay(ROOT, names)
    return {'role': 'Same five frozen author-inspected tests, interpreter and fixtures; old implementation plus new tests versus patched implementation. Not independent observations or a four-domain randomized comparison.',
            'baseline_commit': ref, 'baseline_store_sha256': old_hash,
            'candidate_store_sha256': sha(ROOT/'mplpb_work/store.py'),
            'tests_sha256': sha(ROOT/'tests/test_specialist_continuity.py'),
            'baseline': old, 'candidate': new,
            'latency_interpretation': 'Single suite durations include setup and are not an estimate of added gate computation or population latency.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline-ref', help='Requires Git history; compares new tests against this archived implementation')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Use a new output path; preserve earlier measurements')
    report = {'schema': 'nup-contract-audit-v1',
              'scope': 'Deterministic developer-authored contract replay and one semantic/trust boundary control. Test counts are not unsupported-promotion population rates, independent validation, or deployment evidence.',
              'code_sha256': {name: sha(ROOT/name) for name in ['mplpb_answers/support.py', 'mplpb_answers/pipeline.py', 'mplpb_combined/retrieval.py', 'tools/release_evidence.py', 'mplpb_work/store.py', 'tests/test_specialist_continuity.py', 'tools/audit_unverified_promotion.py']},
              'case_freeze_sha256': sha(ROOT/'evaluation/no-unverified-promotion/development-cases.json'),
              'regressions': {name: replay(ROOT, tests) for name, tests in GROUPS.items()},
              'artifact_boundary': artifact_boundary(),
              'not_measured': ['independent held-out performance', 'four-domain controlled promotion rates', 'human correction burden', 'inter-rater reliability', 'added gate latency/compute', 'new deployment behavior']}
    if args.baseline_ref:
        report['targeted_comparison'] = baseline_comparison(args.baseline_ref)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    passed = all(value['exit_code'] == 0 for value in report['regressions'].values())
    if 'targeted_comparison' in report:
        comparison = report['targeted_comparison']
        expected_failures = set(TARGETS[:3])
        observed_failures = {case['test'] for case in comparison['baseline']['cases'] if case['outcome'] == 'FAIL'}
        passed = passed and observed_failures == expected_failures and comparison['candidate']['exit_code'] == 0
    print(json.dumps({'passed': passed, 'test_counts': {key: value['reported_test_count'] for key, value in report['regressions'].items()}, 'output': str(args.output)}, indent=2))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
