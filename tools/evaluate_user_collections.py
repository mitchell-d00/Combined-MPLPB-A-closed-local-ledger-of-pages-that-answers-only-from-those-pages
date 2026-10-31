"""Frozen, source-built collection workflows; literal developer oracle, not human validation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from tools.ledger_ui import App
from tools.evaluate_researcher_pilot import native_api, citation_check, fresh_process
from mplpb_answers.evidence_contract import loads, pin
from mplpb_answers.passages import PassageIndex
from mplpb_answers.support import code_pins
from mplpb_combined.ledger import Ledger

ROOT = Path(__file__).resolve().parents[1]


def run(path):
    path = Path(path); raw = path.read_bytes()
    suite_sha = hashlib.sha256(raw).hexdigest()
    if len(raw) > 1000000 or suite_sha != path.with_suffix(path.suffix+'.sha256').read_text().split()[0]:
        raise ValueError('Collection study input differs from frozen bytes')
    suite = loads(raw.decode())
    if suite['schema'] != 'mplpb-user-collection-study-v1' or suite['role'] not in {'development', 'evaluation'}:
        raise ValueError('Unknown collection study')
    rows, journeys = [], []
    for case in suite['cases']:
        if not re.fullmatch(r'[a-z][a-z0-9_-]{0,50}', case['id']):
            raise ValueError('Invalid case ID')
        with tempfile.TemporaryDirectory(prefix='mplpb-collection-study-') as temp:
            base = Path(temp); app = App(topic_base=base/'topics')
            checks = []; events = []
            def check(name, passed):
                checks.append({'name': name, 'passed': bool(passed)})
            with native_api(app) as post:
                key = post('/api/collections/create', {'name': case['task']})['corpus']
                doc = case['source']
                imported = post('/api/source/import', dict(doc, corpus=key))
                check('pasted_origin_honest', imported['capture']['transport'] == 'user-pasted-text' and imported['capture']['authorship'] == 'unknown')
                first_record = next(r for r in Ledger(app.root(key)).servable() if r.id == imported['id'])
                for q in case['questions']:
                    started = time.monotonic()
                    # Gold/acceptance fields never enter a reader request.
                    answer = post('/api/query', {'corpus': key, 'question': q['question']})['reader']['answer_contract']
                    elapsed = (time.monotonic()-started)*1000
                    pack = PassageIndex(app.root(key), q['question']).retrieve([q['question']], 12, 8000)
                    cited = citation_check(app, key, answer)
                    returned = answer['kind'] in {'supported_answer', 'partial_answer', 'model_assisted_answer'}
                    correct = (answer['kind'] == 'supported_answer' and q['answerable']
                               and answer['text'] == q['gold'] and cited['complete'])
                    rows.append({'case': case['id'], 'id': q['id'], 'question': q['question'], 'answerable': q['answerable'],
                                 'answer': answer, 'returned': returned, 'correct_literal_return': correct,
                                 'wrong_return': returned and not correct,
                                 'unnecessary_refusal': q['answerable'] and not returned,
                                 'gold_retrieved': any(q['gold'] in p['text'] for p in pack['passages']) if q['gold'] else None,
                                 'citation': cited, 'latency_ms': round(elapsed, 3),
                                 'retrieval_chars': sum(len(p['text']) for p in pack['passages'])})
                revised = post('/api/source/import', dict(doc, corpus=key, text=case['revision']['text']))
                answer = post('/api/query', {'corpus': key, 'question': case['questions'][1]['question']})['reader']['answer_contract']
                records = Ledger(app.root(key))
                successor = records.by_id[revised['id']][0]
                check('revision_retains_pinned_predecessor', successor.id != first_record.id and
                      any(r.id == first_record.id and r.hash == first_record.hash_actual for r in successor.supersedes)
                      and records.effective_status(records.by_id[first_record.id][0]) == 'retired')
                check('updated_policy_answer', answer['kind'] == 'supported_answer' and answer['text'] == case['revision']['gold']
                      and citation_check(app, key, answer)['complete'])
                try:
                    app.page(key, first_record.path, 'internal'); blocked = False
                except ValueError:
                    blocked = True
                check('old_citation_not_fresh_evidence', blocked)
                saved = post('/api/chat', {'corpus': key, 'message': 'remember Compare the revised policy. Keep the earlier source history.'})
                exported = post('/api/chat/export', {'session': saved['session']})
            recovered = fresh_process({'app': str(base.parent/base.name), 'session': saved['session'], 'corpus': key,
                                       'question': case['questions'][1]['question']})
            check('fresh_process_notes_and_transcript', recovered['export'] == exported and recovered['saved']['chain_intact']
                  and recovered['saved']['notes'] == ['Compare the revised policy. Keep the earlier source history.'])
            check('fresh_process_current_answer', recovered['answer']['text'] == answer['text'] and recovered['answer']['kind'] == answer['kind'])
            competing = app.import_source(dict(case['conflict'], corpus=key))
            conflict = app.query({'corpus': key, 'question': case['questions'][1]['question']})['reader']['answer_contract']
            check('body_conflict_explicit', conflict['kind'] == 'conflict' and conflict['diagnostic']['code'] == 'conflicting_or_multiple_owners')
            check('external_sources_withheld', not app.query({'corpus': key, 'profile': 'external', 'question': case['questions'][1]['question']})['reader']['answer_supported'])
            with tempfile.TemporaryDirectory(prefix='mplpb-restore-study-') as destination:
                restored = Path(destination)/'workspace'
                shutil.copytree(base, restored)
                restored_result = fresh_process({'app': str(restored), 'session': saved['session'], 'corpus': key,
                                                 'question': case['questions'][1]['question']})
                check('quiescent_copy_retains_sources_history_and_notes', restored_result['export'] == exported
                      and restored_result['saved']['notes'] == recovered['saved']['notes']
                      and restored_result['answer']['kind'] == conflict['kind'])
            raw_source = app.collections.path(key)/'captures'/app.collections.entries()[key]['captures'][0]['id']/'source.bin'
            source_bytes = raw_source.read_bytes(); raw_source.write_bytes(b'deliberately damaged study capture')
            try:
                app.query({'corpus': key, 'question': case['questions'][1]['question']}); rejected = False
            except ValueError as exc:
                rejected = 'source bytes differ' in str(exc)
            finally:
                raw_source.write_bytes(source_bytes)
            check('capture_damage_is_an_error_not_an_answer', rejected)
            events.extend([{'operation': 'revision', 'answer': answer}, {'operation': 'conflict', 'answer': conflict}])
            journeys.append({'id': case['id'], 'checks': checks, 'events': events,
                             'workflow_complete': all(c['passed'] for c in checks),
                             'saved_bytes': sum(p.stat().st_size for p in base.rglob('*') if p.is_file()),
                             'acquisition': 'explicit pasted sources; no network source requests',
                             'backup_assessment': 'Quiescent complete-directory copy restored these source/lineage/note fixtures. Transcript export omits sources. A portable, versioned, validated user backup/restore interface is not implemented.'})
    answerable = [r for r in rows if r['answerable']]
    returns = [r for r in rows if r['returned']]
    metrics = {'questions': len(rows), 'answerable': len(answerable), 'returned': len(returns),
               'correct_literal_returns': sum(r['correct_literal_return'] for r in rows),
               'wrong_returns': sum(r['wrong_return'] for r in rows),
               'return_precision': sum(r['correct_literal_return'] for r in returns)/len(returns) if returns else None,
               'answerable_coverage': sum(r['correct_literal_return'] for r in answerable)/len(answerable),
               'unnecessary_refusals': sum(r['unnecessary_refusal'] for r in rows),
               'ambiguities_or_conflicts': sum(r['answer']['kind'] == 'conflict' for r in rows),
               'retrieval_misses': sum(not r['gold_retrieved'] for r in answerable),
               'citation_accuracy_and_completeness': sum(r['citation']['complete'] for r in returns)/len(returns) if returns else None,
               'completed_journeys': sum(j['workflow_complete'] for j in journeys), 'journeys': len(journeys),
               'failed_workflow_checks': sum(not c['passed'] for j in journeys for c in j['checks']),
               'query_latency_ms': round(sum(r['latency_ms'] for r in rows), 3),
               'retrieval_chars': sum(r['retrieval_chars'] for r in rows),
               'source_network_requests': 0, 'model_calls': 0}
    for row in rows:
        code = row['answer']['diagnostic']['code']
        row['failure_class'] = ('none' if row['correct_literal_return'] else 'wrong_return' if row['wrong_return']
            else 'missing_answer_in_frozen_sources' if not row['answerable']
            else 'ineligible_sources' if code == 'restricted_or_unavailable'
            else 'retrieval_miss' if not row['gold_retrieved']
            else 'conflicting_evidence' if code == 'conflicting_or_multiple_owners'
            else 'unsupported_wording' if code == 'interpretation_unsupported' else 'unresolved_evidence')
    metrics['failure_classes'] = {name: sum(r['failure_class'] == name for r in rows) for name in sorted({r['failure_class'] for r in rows})}
    metrics['injected_capture_errors_rejected'] = sum(c['passed'] for j in journeys for c in j['checks'] if c['name'] == 'capture_damage_is_an_error_not_an_answer')
    acceptance = suite['acceptance']
    passed = (metrics['wrong_returns'] <= acceptance['max_wrong_returns'] and metrics['answerable_coverage'] >= acceptance['min_answerable_coverage']
              and metrics['citation_accuracy_and_completeness'] == acceptance['citation_completeness'] and metrics['failed_workflow_checks'] == 0)
    report = {'schema': 'mplpb-user-collection-report-v1', 'suite_sha256': suite_sha, 'role': suite['role'],
              'authorship': suite['authorship'], 'independence_verified': False, 'human_usability_measured': False,
              'acceptance': acceptance, 'acceptance_sha256': pin(acceptance), 'acceptance_passed': passed,
              'baseline_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'reader_code_sha256': code_pins(), 'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'application_sha256': {n: hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ('tools/ledger_ui.py', 'tools/exploration_store.py')},
              'metrics': metrics, 'rows': rows, 'journeys': journeys,
              'limitations': 'Developer-authored frozen lexical controls, not independent semantic accuracy. Workflow checks do not count as correct answers. Backup/upgrade and real participants remain outstanding.'}
    report['run_sha256'] = pin(report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('suite', type=Path); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Evaluation history is never overwritten')
    report = run(args.suite)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as f:
        f.write(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'metrics': report['metrics'], 'acceptance_passed': report['acceptance_passed']}))


if __name__ == '__main__':
    main()
