"""Frozen fictional researcher journeys against the real native application.

Scripted users, no simulated answer engine. HTTP, CLI, disk saves and fresh-process
recovery run for real. Fixture backup is not a product backup feature. Neither
workflow checks nor literal gold matching establish human usability or general
semantic accuracy. Run: python -m tools.evaluate_researcher_pilot --output NEW.json
"""
import argparse
from contextlib import contextmanager
import hashlib
import http.client
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from threading import Thread
import time

from mplpb_answers.body_text import body_text
from mplpb_answers.evidence_contract import loads, pin
from mplpb_answers.passages import PassageIndex
from mplpb_combined.ledger import Ledger
from mplpb_combined.reader import PROFILES
from mplpb_work import WorkStore, Denied
from tools.ledger_ui import App, handler

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUITE = ROOT/'evaluation/researcher-pilot/journeys.json'
RETURNED = {'supported_answer', 'model_assisted_answer', 'partial_answer'}


def load_suite(path):
    path = Path(path)
    raw = path.read_bytes()
    if len(raw) > 1000000 or hashlib.sha256(raw).hexdigest() != path.with_suffix(path.suffix+'.sha256').read_text().split()[0]:
        raise ValueError('Pilot fixture differs from its frozen SHA-256 or exceeds budget')
    suite = loads(raw.decode('utf-8'))
    if suite.get('schema') != 'mplpb-researcher-pilot-suite-v1' or suite.get('role') != 'development':
        raise ValueError('Only explicitly synthetic development journeys are accepted')
    journeys = suite.get('journeys')
    if not isinstance(journeys, list) or not 1 <= len(journeys) <= 20:
        raise ValueError('Pilot requires 1–20 journeys')
    ids = set()
    for journey in journeys:
        if not isinstance(journey.get('id'), str) or journey['id'] in ids:
            raise ValueError('Journey IDs must be unique')
        ids.add(journey['id'])
        if not isinstance(journey.get('documents'), list) or not 1 <= len(journey['documents']) <= 10:
            raise ValueError('Journey needs inline source documents')
        for doc in journey['documents']+[journey['conflict']]:
            allowed = {'title', 'url', 'text', 'question', 'gold_quotes'}
            if set(doc)-allowed or any(not isinstance(doc.get(k), str) or not doc[k].strip() for k in ('title', 'url', 'text')):
                raise ValueError('Sources must be inline text, never filesystem paths')
        questions = journey.get('questions')
        if not isinstance(questions, list) or not 1 <= len(questions) <= 20:
            raise ValueError('Journey needs questions')
        qids = set()
        for q in questions:
            if q.get('id') in qids or q.get('answerability') not in {'answerable', 'unanswerable', 'ambiguous'}:
                raise ValueError('Questions need unique IDs and declared answerability')
            qids.add(q.get('id'))
            if not isinstance(q.get('gold_quotes'), list) or any(not isinstance(s, str) or not s for s in q['gold_quotes']):
                raise ValueError('Gold quotations must be explicit text')
            if q['answerability'] == 'answerable' and not q['gold_quotes']:
                raise ValueError('Answerable questions need gold body quotations')
    return suite, hashlib.sha256(raw).hexdigest()


@contextmanager
def native_api(app):
    class QuietHandler(handler(app)):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    def post(route, data):
        conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=30)
        try:
            conn.request('POST', route, json.dumps(data), {'Content-Type': 'application/json'})
            response = conn.getresponse()
            value = loads(response.read().decode())
            if response.status != 200:
                raise ValueError(value.get('error', 'Native API failed'))
            return value
        finally:
            conn.close()
    try:
        yield post
    finally:
        server.shutdown(); server.server_close(); worker.join(timeout=5)


def citation_check(app, corpus, contract):
    citations = [c for claim in contract['claims'] for c in claim['citations']]
    valid = 0
    for cite in citations:
        # Open through the same source-inspection service used by the UI, then
        # independently check offsets against canonical eligible body text.
        page = app.page(corpus, cite['path'], 'internal')
        recs = [r for r in Ledger(app.root(corpus)).servable() if r.path == cite['path']]
        if len(recs) != 1:
            continue
        rec = recs[0]; body = body_text(rec.body_html)
        if (page['hash'] == rec.hash_actual == cite['hash'] and rec.id == cite['source_id']
                and body[cite['body_start']:cite['body_end']] == cite['quote']
                and cite['quote'] in page['text']):
            valid += 1
    return {'citations': len(citations), 'valid': valid,
            'complete': bool(citations) and valid == len(citations),
            'inspection': 'native source service; actual browser clicks measured separately'}


def score_question(question, contract, citations, retrieval):
    returned = contract['kind'] in RETURNED
    # Deliberately literal development oracle, never an entailment classifier.
    quotes = [c['quote'] for claim in contract['claims'] for c in claim['citations']]
    gold = question['gold_quotes']
    exact_gold = bool(gold) and all(any(g in q for q in quotes) for g in gold)
    ungraded = returned and contract['kind'] != 'supported_answer'
    correct = (returned and not ungraded and question['answerability'] == 'answerable'
               and exact_gold and citations['complete'] and contract['text'] == ' '.join(gold))
    found = sum(any(g in p['text'] for p in retrieval['passages']) for g in gold)
    return {'returned': returned, 'literal_gold_supported': correct,
            'requires_human_semantic_review': ungraded,
            'wrong_return_under_literal_oracle': returned and not ungraded and not correct,
            'unnecessary_refusal': question['answerability'] == 'answerable' and not returned,
            'safe_nonreturn': question['answerability'] != 'answerable' and not returned,
            'gold_passages': len(gold), 'gold_passages_retrieved': found,
            'retrieval_recall': found/len(gold) if gold else None,
            'oracle': 'developer-authored exact-quote regression; not human semantic grading'}


def recover(request):
    """Called in a fresh interpreter; credentials arrive via stdin, not argv."""
    app = App(topic_base=Path(request['app'])/'topics')
    saved = app.resume_chat({'session': request['session']})
    exported = app.export_chat({'session': request['session']})
    answer = app.query({'corpus': request['corpus'], 'question': request['question']})['reader']['answer_contract']
    result = {'saved': saved, 'export': exported, 'answer': answer}
    if 'work' in request:
        store = WorkStore(request['work'], executors={'pilot.inspect.v1': lambda r: {}})
        result['handoff'] = store.handoff(request['credential'])
    return result


def fresh_process(request):
    code = 'import json,sys; from tools.evaluate_researcher_pilot import recover; print(json.dumps(recover(json.load(sys.stdin))))'
    process = subprocess.run([sys.executable, '-c', code], input=json.dumps(request), text=True,
                             capture_output=True, cwd=str(ROOT), timeout=60)
    if process.returncode:
        raise RuntimeError('Fresh-process recovery failed: '+process.stderr[-1000:])
    return loads(process.stdout)


def work_handoff(base, root, journey, initial, conflict_source):
    store, authority = WorkStore.create(base, {'research': root})
    operations = ['create:'+k for k in ('task', 'evidence', 'claim', 'attempt', 'decision', 'review', 'action')]+['execute']
    contract = {'operations': operations, 'tools': ['pilot.inspect.v1'], 'scopes': ['T1'],
                'share_with': ['researcher'], 'profile': 'internal', 'expires_at': time.time()+3600}
    def assign(instance, previous=None):
        return store.assign(authority, seat='researcher', instance=instance,
                            model={'name': 'scripted-npc', 'provider': 'none', 'version': '1', 'context_policy_hash': pin({'fixture': 'researcher-pilot'})},
                            contract=contract, continues_work_of=previous,
                            expected_head=store.head(authority)['hash'])['credential']
    token = assign('day-one')
    def put(id, kind, payload, deps=None):
        store.put(token, id=id, kind=kind, payload=payload, dependencies=deps or {},
                  visibility=['researcher'], expected_revision=0, expected_head=store.snapshot(token)['head'])
    put('T1', 'task', {'goal': journey['goal'], 'criteria': ['Reconcile conflicting source years'], 'review_budget': 3, 'state': 'open', 'acceptance': {}})
    cite = initial['claims'][0]['citations'][0]
    for id, source_id, source_hash, quote in [('E1', cite['source_id'], cite['hash'], cite['quote']),
                                            ('E2', conflict_source.id, conflict_source.hash_actual, journey['conflict']['text'])]:
        put(id, 'evidence', {'task': 'T1', 'corpus': 'research', 'source_id': source_id, 'source_hash': source_hash, 'quote': quote, 'query': journey['conflict']['question']})
    put('C1', 'claim', {'task': 'T1', 'proposition': 'A single uncontested opening year is established', 'basis': 'inference',
                      'assessment': 'supported_under_scope', 'assumptions': ['The first bulletin is sufficient'],
                      'alternatives': ['The bulletins conflict'], 'revisit_when': 'A competing source appears'}, {'E1': 1})
    put('F1', 'attempt', {'task': 'T1', 'method': 'Determine a single year from disputed bulletins', 'result': 'failed',
                         'failure': 'Actual strict conflict query could not establish a unique year',
                         'retry_when': 'The conflict has been resolved against reviewed sources', 'artifact': 'import_disagreement event in pilot report'})
    put('R1', 'review', {'task': 'T1', 'target': {'C1': 1}, 'target_variable': 'opening year', 'regime': 'synthetic bulletins',
                       'finding': 'Second bulletin states a different year', 'outcome': 'challenge', 'resolution': ''}, {'E2': 1})
    put('D1', 'decision', {'task': 'T1', 'choice': 'Inspect both bulletins before publishing', 'alternatives': ['Publish the first year'],
                         'reason': 'Unresolved conflicting evidence', 'assessment': 'proposed', 'recheck_when': 'Conflict is resolved', 'failed_attempts': {'F1': 1}})
    action = {'task': 'T1', 'task_revision': 1, 'operation': 'pilot.inspect.v1', 'arguments': {'purpose': 'inspect sources'},
              'side_effect': 'local', 'executor_seat': 'researcher', 'state': 'proposed', 'retry_of': {}, 'retry_reason': ''}
    put('INSPECT', 'action', action, {'E1': 1, 'E2': 1})
    put('PUBLISH', 'action', dict(action, arguments={'purpose': 'publish single year'}), {'C1': 1})
    store.end(token, store.snapshot(token)['head'])
    successor = assign('day-two', 'day-one')
    try:
        store.snapshot(token)
        old_rejected = False
    except Denied:
        old_rejected = True
    return successor, old_rejected


def _journey(journey, base, reader=None):
    journey_started = time.monotonic()
    app_dir = base/'app'
    app = App(topic_base=app_dir/'topics', local_reader=reader)
    checks, events, rows = [], [], []
    def check(name, passed, detail):
        checks.append({'name': name, 'passed': bool(passed), 'detail': detail})
    def event(action, **data):
        events.append({'step': len(events)+1, 'action': action, **data})
    with native_api(app) as post:
        corpus = post('/api/collections/create', {'name': journey['persona']['name']+' investigation'})['corpus']
        event('create_collection', label=journey['persona']['name']+' investigation')
        for doc in journey['documents']:
            imported = post('/api/source/import', dict(doc, corpus=corpus))
            check('import_'+doc['title'], imported['capture']['transport'] == 'user-pasted-text'
                  and imported['capture']['authorship'] == 'unknown', 'User-supplied text, no fetched/authorship claim')
            event('import_document', title=doc['title'], source_id=imported['id'])
        root = app.root(corpus)
        for question in journey['questions']:
            # Only the actual question and mode reach the reader. Gold and
            # expected outcomes remain entirely in this scoring layer.
            started = time.monotonic()
            result = post('/api/query', {'corpus': corpus, 'question': question['question'], 'mode': 'assisted' if reader else 'supported'})
            answer = result['reader']['answer_contract']
            elapsed = round((time.monotonic()-started)*1000, 3)
            pack = PassageIndex(root, question['question'], PROFILES['internal']).retrieve([question['question']], 12, 8000)
            cites = citation_check(app, corpus, answer)
            scored = score_question(question, answer, cites, pack)
            # Strict expected abstentions are contract baselines, not success
            # targets imposed on an optional live assisted reader.
            if reader is None:
                check('question_'+question['id'], answer['kind'] in question['expected_kinds'], 'Frozen strict contract; coverage is scored separately')
            if scored['returned']:
                check('citations_'+question['id'], cites['complete'], 'Opened current page and checked source hash/body offsets')
            rows.append({'id': question['id'], 'question': question['question'], 'answerability': question['answerability'],
                         'answer': answer, 'citation_inspection': cites, 'score': scored, 'latency_ms': elapsed,
                         'retrieval': {'passages': [{'source_id': p['source_id'], 'quote': p['text'], 'score': p['retrieval_score']} for p in pack['passages']],
                                       'search_complete': pack['search_complete'], 'ranking': pack['ranking']}})
            event('ask_and_inspect', question=question['question'], kind=answer['kind'], diagnostic=answer['diagnostic'])
        primary = rows[1]['answer']
        # Keep CLI parity strict even when an explicitly configured live reader
        # is under evaluation; no second unrecorded model call.
        cli = subprocess.run([sys.executable, '-m', 'mplpb_answers', 'ask', str(root), journey['questions'][1]['question'], '--json'],
                             cwd=str(ROOT), capture_output=True, text=True, timeout=30)
        cli_answer = loads(cli.stdout)['answer_contract']
        strict_again = app.query({'corpus': corpus, 'question': journey['questions'][1]['question']})['reader']['answer_contract']
        check('cli_http_parity', cli.returncode == 0 and cli_answer == strict_again, 'Real CLI subprocess and native HTTP share strict payload')
        conflict_doc = {k: v for k, v in journey['conflict'].items() if k in {'title', 'url', 'text'}}
        disputed = post('/api/source/import', dict(conflict_doc, corpus=corpus))
        conflict = post('/api/query', {'corpus': corpus, 'question': journey['conflict']['question']})['reader']['answer_contract']
        check('conflicting_sources_stop', conflict['kind'] == 'conflict' and not conflict['answer_supported'], 'No ranked winner or blended year')
        event('import_disagreement', answer=conflict)
        chat = post('/api/chat', {'corpus': corpus, 'message': 'remember '+journey['note']})
        sid = chat['session']
        before = post('/api/chat/export', {'session': sid})
        check('notes_are_not_evidence', not chat['response']['sources'], 'Working note remains conversation state')
        event('save_investigation_note', note=journey['note'], turn_sha256=chat['turn_sha256'])
    source = Ledger(root).by_id[disputed['id']][0]
    token, fenced = work_handoff(base/'work', root, journey, primary, source)
    event('end_first_instance', replacement='fresh interpreter and new specialist instance')
    request = {'app': str(app_dir), 'session': sid, 'corpus': corpus, 'question': journey['conflict']['question'],
               'work': str(base/'work'), 'credential': token}
    resume_started = time.monotonic()
    recovered = fresh_process(request)
    resume_ms = round((time.monotonic()-resume_started)*1000, 3)
    handoff = recovered.pop('handoff'); records = {r['id']: r for r in handoff['records']}
    check('fresh_process_resume', recovered['saved']['chain_intact'] and journey['note'] in recovered['saved']['notes']
          and recovered['export'] == before, 'Same saved notes and exact transcript chain after interpreter replacement')
    check('fresh_conflict_recheck', recovered['answer']['kind'] == 'conflict', 'Resume performs a fresh source query, not historical-answer reuse')
    check('ended_writer_fenced', fenced, 'Day-one capability cannot write as day two')
    check('structured_handoff', records['C1']['effective_status'] == 'contested'
          and records['F1']['payload']['result'] == 'failed' and records['R1']['payload']['outcome'] == 'challenge'
          and 'INSPECT' in handoff['next_actions'] and 'PUBLISH' not in handoff['next_actions'],
          'Findings, disagreement, failed route and fresh next-action permissions survive')
    event('resume_next_day', notes=recovered['saved']['notes'], handoff={k: handoff[k] for k in ('authority', 'answer_supported', 'content_truth_verified', 'next_actions')},
          work=[{'id': r['id'], 'kind': r['kind'], 'status': r['effective_status'], 'payload': r['payload']} for r in handoff['records']])
    # Quiescent whole-app directory copy is harness infrastructure, NOT an
    # implemented end-user backup/export/import feature or portable work DB.
    shutil.copytree(app_dir, base/'fixture-backup')
    shutil.copytree(base/'fixture-backup', base/'fixture-restored')
    restore_request = {k: v for k, v in request.items() if k not in {'work', 'credential'}}
    restore_request['app'] = str(base/'fixture-restored')
    restored = fresh_process(restore_request)
    check('fixture_directory_restore', restored['export'] == before and restored['answer']['kind'] == 'conflict',
          'Test-only quiescent directory copy; not product backup UI, portable specialist restore, or schema upgrade')
    save = app.session_store.path; original = save.read_bytes()
    save.write_text('{}')
    try:
        App(topic_base=app_dir/'topics')
        blocked = False
    except ValueError as exc:
        blocked = 'integrity' in str(exc).lower() and save.read_text() == '{}'
    check('damaged_save_not_overwritten', blocked, 'Readable recovery error; damaged bytes retained')
    save.write_bytes(original)
    captures = app.collections.entries()[corpus]['captures']
    raw_path = app.collections.path(corpus)/'captures'/captures[0]['id']/'source.bin'
    original = raw_path.read_bytes(); raw_path.write_bytes(b'changed after interruption')
    try:
        app.query({'corpus': corpus, 'question': journey['conflict']['question']})
        blocked = False
    except ValueError as exc:
        blocked = 'source bytes differ' in str(exc)
    check('source_change_blocks_resume_answer', blocked, 'Pinned source drift cannot become a fresh answer')
    raw_path.write_bytes(original)
    event('fault_and_restore_checks', source_drift_rejected=blocked,
          backup_scope='harness directory copy only')
    return {'id': journey['id'], 'persona': journey['persona'], 'domain': journey['domain'],
            'checks': checks, 'events': events, 'questions': rows,
            'workflow_passed': all(c['passed'] for c in checks),
            'resume_ms': resume_ms, 'workflow_elapsed_ms': round((time.monotonic()-journey_started)*1000, 3),
            'actual_human_participant': False, 'simulated_elapsed_day': 'fresh-process interruption, no claim of elapsed calendar day'}


def summarize(journeys):
    rows = [r for j in journeys for r in j['questions']]
    answerable = [r for r in rows if r['answerability'] == 'answerable']
    returned = [r for r in rows if r['score']['returned']]
    gold = sum(r['score']['gold_passages'] for r in answerable)
    return {'journeys': len(journeys), 'workflow_passes': sum(j['workflow_passed'] for j in journeys),
            'checks': sum(len(j['checks']) for j in journeys), 'failed_checks': sum(not c['passed'] for j in journeys for c in j['checks']),
            'questions': len(rows), 'answerable': len(answerable), 'returned': len(returned),
            'unexecuted_questions': sum(bool(r.get('execution_error')) for r in rows),
            'literal_gold_supported': sum(r['score']['literal_gold_supported'] for r in rows),
            'wrong_returns_under_literal_oracle': sum(r['score']['wrong_return_under_literal_oracle'] for r in rows),
            'ungraded_model_returns': sum(r['score']['requires_human_semantic_review'] for r in rows),
            'unnecessary_refusals': sum(r['score']['unnecessary_refusal'] for r in rows),
            'complete_answerable_coverage': sum(r['score']['literal_gold_supported'] and r['answer']['kind'] != 'partial_answer' for r in answerable)/len(answerable) if answerable else None,
            'retrieval_gold_recall': sum(r['score']['gold_passages_retrieved'] for r in answerable)/gold if gold else None,
            'valid_citations': sum(r['citation_inspection']['valid'] for r in returned),
            'citations': sum(r['citation_inspection']['citations'] for r in returned),
            'latency_ms_total': round(sum(r['latency_ms'] for r in rows), 3),
            'resume_ms_total': round(sum(j.get('resume_ms', 0) for j in journeys), 3),
            'semantic_accuracy_independently_measured': False, 'human_usability_measured': False}


def run(suite_path=DEFAULT_SUITE, reader=None):
    suite, suite_sha = load_suite(suite_path)
    journeys = []
    for journey in suite['journeys']:
        with tempfile.TemporaryDirectory(prefix='mplpb-npc-') as temp:
            try:
                journeys.append(_journey(journey, Path(temp), reader))
            except Exception as exc:
                # A broken journey remains in the denominator. Continue the
                # other NPCs, retain the failure, and exit nonzero after reporting.
                rows = []
                for q in journey['questions']:
                    answer = {'kind': 'abstain', 'text': '', 'claims': []}
                    citations = {'citations': 0, 'valid': 0, 'complete': False}
                    rows.append({'id': q['id'], 'question': q['question'], 'answerability': q['answerability'],
                                 'answer': answer, 'citation_inspection': citations,
                                 'score': score_question(q, answer, citations, {'passages': []}),
                                 'latency_ms': 0, 'execution_error': True})
                journeys.append({'id': journey['id'], 'persona': journey['persona'], 'domain': journey['domain'],
                                 'workflow_passed': False, 'actual_human_participant': False, 'questions': rows,
                                 'events': [], 'checks': [{'name': 'journey_execution', 'passed': False,
                                 'detail': type(exc).__name__+'; journey incomplete, no success or accuracy credit'}]})
    report = {'schema': 'mplpb-researcher-pilot-run-v1', 'suite_sha256': suite_sha, 'provenance': suite['provenance'],
              'status': 'synthetic_development_workflow_only', 'independence_verified': False,
              'reader': reader.describe() if reader else {'adapter': 'strict', 'live_inference': False},
              'implementation_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(set([Path(__file__)]+list((ROOT/'mplpb_answers').glob('*.py'))+list((ROOT/'mplpb_work').glob('*.py'))
                  +[ROOT/'tools'/n for n in ('ledger_ui.py', 'exploration_store.py', 'mind_session.py', 'conversation_engine.py', 'conversation_router.py', 'deterministic_mind.py')]))},
              'summary': summarize(journeys), 'journeys': journeys,
              'product_readiness': {'status': 'not_certified', 'gaps': [
                  'Real participants and independently authored questions are absent',
                  'Browser click results are a separate Chromium gate, not native API evidence',
                  'No live-model quality inference without an explicitly configured reader and human grading',
                  'Dedicated investigation overview UI is not implemented',
                  'Portable user backup/restore and specialist-store relocation are not established by fixture copies',
                  'Schema upgrade/migration, long-duration storage and installation usability remain unmeasured',
                  'Unknown grammar is not reliably distinguished from absent evidence; actionable uncertainty needs product work']}}
    report['run_sha256'] = pin(report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', type=Path, default=DEFAULT_SUITE)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reader-model')
    parser.add_argument('--reviewer-model')
    args = parser.parse_args(argv)
    if args.output.exists():
        raise FileExistsError('Choose a new report path; pilot history is never overwritten')
    reader = None
    if args.reader_model:
        from mplpb_answers.local_reader import OllamaLocalReader
        reader = OllamaLocalReader(args.reader_model, reviewer_model=args.reviewer_model)
    report = run(args.suite, reader)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'status': report['status'], 'summary': report['summary'], 'report': str(args.output)}))
    return 1 if report['summary']['failed_checks'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
