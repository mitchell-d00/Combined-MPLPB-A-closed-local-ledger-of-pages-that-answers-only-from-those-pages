"""Generate and verify an exact-candidate CI evidence manifest.

This is a manifest of checks completed by a trusted CI job, not a signature,
a factual-truth certificate, or proof that a candidate was deployed.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

GATES = (
    'Python attack and full regression: PASS',
    'JavaScript/API/crawler/bridge: PASS',
    'Pinned Python WebAssembly engine: PASS',
    'Chromium published-live baseline: PASS',
    'Chromium ZIP-built candidate: PASS',
)
SCHEMA = 'mplpb-candidate-release-evidence-v1'


def _sha256(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
        raise ValueError('Missing, empty, or symlinked release input: ' + str(path))
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _commit(path):
    value = path.read_text(encoding='ascii').strip()
    if not re.fullmatch(r'[0-9a-f]{40}', value):
        raise ValueError('Invalid full Git SHA in ' + str(path))
    return value


def inspect(archive_dir, expected_commit):
    directory = Path(archive_dir)
    commit = _commit(directory / 'commit.sha')
    if commit != expected_commit:
        raise ValueError('Packaged commit does not match the exact candidate head')
    tree = _commit(directory / 'tree.sha')
    source = directory / 'mplpb-repository.zip'
    source_digest = _sha256(source)
    checksum = (directory / 'mplpb-repository.zip.sha256').read_text(encoding='ascii').strip()
    if checksum != source_digest + '  mplpb-repository.zip' and checksum != source_digest + ' mplpb-repository.zip':
        raise ValueError('Source ZIP checksum does not match the pinned archive')
    preview = directory / 'mplpb-candidate-preview.html'
    preview_digest = _sha256(preview)
    report = directory / 'validation-report.txt'
    report_digest = _sha256(report)
    report_text = report.read_text(encoding='utf-8')
    if any(report_text.count(gate) != 1 for gate in GATES):
        raise ValueError('Validation report is missing a required passed gate')
    if 'Git commit packaged: ' + commit not in report_text or 'ZIP SHA-256: ' + source_digest not in report_text:
        raise ValueError('Validation report does not identify this exact source ZIP')
    return {
        'schema': SCHEMA,
        'status': 'candidate_checks_passed_not_deployed',
        'commit_sha': commit,
        'tree_sha': tree,
        'source_zip': {'file': source.name, 'bytes': source.stat().st_size, 'sha256': source_digest},
        'browser_preview': {'file': preview.name, 'bytes': preview.stat().st_size, 'sha256': preview_digest},
        'validation_report_sha256': report_digest,
        'passed_gate_labels': list(GATES),
        'limitations': 'CI candidate evidence only; deployment and post-deployment browser verification are separate.',
    }


def create(archive_dir, expected_commit):
    evidence = inspect(archive_dir, expected_commit)
    target = Path(archive_dir) / 'release-evidence.json'
    target.write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return evidence


def verify(archive_dir, expected_commit):
    target = Path(archive_dir) / 'release-evidence.json'
    actual = json.loads(target.read_text(encoding='utf-8'))
    expected = inspect(archive_dir, expected_commit)
    if actual != expected:
        raise ValueError('Release evidence manifest differs from verified inputs')
    return expected


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('create', 'verify'))
    parser.add_argument('--archive-dir', required=True, type=Path)
    parser.add_argument('--expected-commit', required=True)
    args = parser.parse_args(argv)
    action = create if args.operation == 'create' else verify
    print(json.dumps(action(args.archive_dir, args.expected_commit), sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
