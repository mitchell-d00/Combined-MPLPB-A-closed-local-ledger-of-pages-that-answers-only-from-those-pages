"""Evaluate a frozen cross-domain suite and export separately pinned human review.

No gold labels are passed to the reader. Correctness requires human judgments.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
import tempfile
import time
from mplpb_combined.ledger import write
from mplpb_answers.pipeline import answer_query
from mplpb_answers.evidence_contract import loads, pin
from mplpb_answers.evaluation import seal_report, review_template, score, DEFAULT_POLICY


def run(suite_path, reader=None, mode='strict', threshold=0.8, policy=None):
    policy = dict(DEFAULT_POLICY if policy is None else policy)
    path = Path(suite_path)
    raw = path.read_bytes()
    expected = path.with_suffix(path.suffix+'.sha256').read_text().split()[0]
    if len(raw) > 20000000:
        raise ValueError('Evaluation suite exceeds 20 MB')
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise ValueError('Evaluation question bytes differ from their frozen SHA-256')
    suite = loads(raw.decode())
    if suite.get('schema') != 'mplpb-general-evaluation-v1' or suite.get('role') not in {'development', 'calibration', 'test'}:
        raise ValueError('Unknown evaluation suite schema or role')
    if not isinstance(suite.get('cases'), list) or not 1 <= len(suite['cases']) <= 10000:
        raise ValueError('Evaluation requires cases')
    ids = set(); rows = []
    identity = reader.describe() if reader is not None and mode == 'assisted' else {'adapter': 'strict', 'live_inference': False}
    for case in suite['cases']:
        if not isinstance(case.get('id'), str) or case['id'] in ids or case.get('answerability') not in {'answerable', 'unanswerable', 'ambiguous'} or not isinstance(case.get('domain'), str):
            raise ValueError('Cases need unique IDs, domains and declared answerability')
        ids.add(case['id'])
        if not isinstance(case.get('documents'), list) or not 1 <= len(case['documents']) <= 100:
            raise ValueError('Each case needs 1–100 inline source documents')
        allowed = {'doc_id', 'title', 'scope', 'body', 'body_html', 'not_for', 'origin', 'source_authorship', 'external', 'derived_from', 'supersedes'}
        for document in case['documents']:
            if (not isinstance(document, dict) or set(document)-allowed
                    or not isinstance(document.get('doc_id'), str)
                    or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,79}', document['doc_id'])):
                raise ValueError('Fixture documents require safe IDs and explicit source fields; filesystem paths are not allowed')
        with tempfile.TemporaryDirectory() as temp:
            for document in case['documents']:
                write(temp, when='2026-01-01T00:00Z', **document)
            started = time.monotonic()
            answer = answer_query(temp, case['question'], mode=mode, reader=reader, min_confidence=threshold).contract
            elapsed = round((time.monotonic()-started)*1000, 3)
            gold = case.get('gold_passages', [])
            passages = answer.get('retrieval', {}).get('passages', [])
            recall = (sum(any(p['source_id'] == g['source_id'] and g['quote'] in p['text'] for p in passages) for g in gold)/len(gold)) if gold and passages else None
            rows.append({'id': case['id'], 'domain': case['domain'], 'question': case['question'],
                         'answerability': case['answerability'], 'answer': answer,
                         'retrieval_recall': recall, 'elapsed_ms': elapsed})
    return seal_report({'schema': 'mplpb-general-evaluation-run-v1', 'suite_sha256': actual,
                        'role': suite['role'], 'provenance': suite.get('provenance', {}),
                        'reader': identity, 'mode': mode, 'threshold': threshold, 'rows': rows,
                        'release_policy': policy, 'release_policy_sha256': pin(policy),
                        'calibration_run_sha256': suite.get('calibration_run_sha256'),
                        'independence_verified': False})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    execute = commands.add_parser('run')
    execute.add_argument('suite'); execute.add_argument('--output', required=True)
    execute.add_argument('--mode', choices=['strict', 'assisted'], default='strict')
    execute.add_argument('--reader-model'); execute.add_argument('--reviewer-model')
    execute.add_argument('--reader-endpoint', default='http://127.0.0.1:11434')
    execute.add_argument('--reader-digest'); execute.add_argument('--reviewer-digest')
    execute.add_argument('--threshold', type=float, default=0.8)
    execute.add_argument('--policy', help='Explicit release-policy JSON frozen into the run')
    grade = commands.add_parser('score')
    grade.add_argument('report'); grade.add_argument('judgments'); grade.add_argument('--output', required=True)
    args = parser.parse_args(argv)
    output = Path(args.output)
    review_path = output.with_suffix('.review.json')
    if output.exists() or (args.command == 'run' and review_path.exists()):
        raise FileExistsError('Choose a new output path; evaluation history and human judgments are never overwritten')
    if args.command == 'run':
        reader = None
        if args.reader_model:
            from mplpb_answers.local_reader import OllamaLocalReader
            reader = OllamaLocalReader(args.reader_model, args.reader_endpoint, args.reviewer_model,
                                       model_digest=args.reader_digest, reviewer_digest=args.reviewer_digest)
        report = run(args.suite, reader, args.mode, args.threshold, loads(Path(args.policy).read_text()) if args.policy else None)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x') as stream:
            stream.write(json.dumps(report, indent=2)+'\n')
        with review_path.open('x') as stream:
            stream.write(json.dumps(review_template(report), indent=2)+'\n')
        print(json.dumps({'run_sha256': report['run_sha256'], 'questions': len(report['rows']),
                          'semantic_correctness': 'unscored; complete the pinned human review template'}))
    else:
        result = score(loads(Path(args.report).read_text()), loads(Path(args.judgments).read_text()))
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
        print(json.dumps({'release_assessment': result['release_assessment'], 'blockers': result['blockers']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
