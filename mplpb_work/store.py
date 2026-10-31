"""Transactional capability-gated work history. No model, shell or network runner.

SQLite serializes validation and append. Projections are rebuilt from the verified
chain; only a trusted host can issue capabilities or register execution adapters.
"""
import copy
from contextlib import contextmanager
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import re
import secrets
import sqlite3
import time
import uuid

from . import model as M
from .errors import WorkError, Conflict, Denied, IntegrityError

SCHEMA = 'mplpb-work-v1'
ZERO = 'sha256:' + '0' * 64


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(value):
    return 'sha256:' + hashlib.sha256(canonical(value).encode()).hexdigest()


def implementation_pins():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))}


def token_hash(token):
    if not isinstance(token, str) or len(token) < 32:
        raise Denied('Credential rejected')
    return hashlib.sha256(token.encode()).hexdigest()


def _empty():
    return {'head': ZERO, 'seq': 0, 'records': {}, 'history': {}, 'seats': {},
            'instances': {}, 'transfers': {}, 'receipts': {}}


def _apply(state, event):
    p, kind = event['payload'], event['type']
    if kind == 'initialize':
        state['authority_hash'], state['corpora'] = p['authority_hash'], p['corpora']
    elif kind == 'assign':
        old = state['seats'].get(p['seat'])
        if old and state['instances'][old['instance']]['ended_at'] is None:
            state['instances'][old['instance']]['ended_at'] = event['time']
        state['seats'][p['seat']] = p['grant']
        state['instances'][p['instance']['id']] = p['instance']
    elif kind in {'revoke', 'end'}:
        grant = state['seats'][p['seat']]
        grant['revoked'] = True
        if state['instances'][grant['instance']]['ended_at'] is None:
            state['instances'][grant['instance']]['ended_at'] = event['time']
    elif kind in {'put', 'transfer'}:
        record = p['record']
        state['records'][record['id']] = record
        state['history'].setdefault(record['id'], []).append(record)
        if kind == 'transfer':
            state['transfers'].setdefault(record['id'], set()).update(p['to'])
    elif kind == 'start':
        state['receipts'][p['receipt']['id']] = p['receipt']
    elif kind == 'finish':
        receipt = state['receipts'][p['receipt']['id']]
        receipt.update(p['receipt'])
        for record in p['records']:
            state['records'][record['id']] = record
            state['history'].setdefault(record['id'], []).append(record)
    else:
        raise IntegrityError('Unknown event type')
    state['seq'], state['head'] = event['seq'], digest(event)


class WorkStore:
    def __init__(self, directory, executors=None, clock=None):
        self.directory = Path(directory).resolve()
        self.path = self.directory / 'work.sqlite3'
        self.executors = dict(executors or {})
        for operation, adapter in self.executors.items():
            M.identifier(operation)
            if not (callable(adapter) or (isinstance(adapter, dict) and set(adapter) == {'run', 'side_effect'} and callable(adapter['run']) and adapter['side_effect'] in {'local', 'external'})):
                raise WorkError('Host adapters need a callable and an explicit effect class')
        self.clock = clock or time.time
        if not self.path.is_file():
            raise WorkError('Work store has not been initialized')

    @classmethod
    def create(cls, directory, corpora=None, clock=None):
        """Trusted local host bootstrap. Returns authority credential exactly once."""
        directory = Path(directory).resolve()
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        path = directory / 'work.sqlite3'
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        db = sqlite3.connect(str(path), isolation_level=None)
        try:
            db.execute('PRAGMA synchronous=FULL')
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE events (seq INTEGER PRIMARY KEY, body TEXT NOT NULL, hash TEXT NOT NULL)')
            db.execute('CREATE TABLE head (id INTEGER PRIMARY KEY CHECK(id=1), seq INTEGER NOT NULL, hash TEXT NOT NULL)')
            db.execute('INSERT INTO head VALUES (1,0,?)', (ZERO,))
            state = _empty()
            secret = secrets.token_urlsafe(48)
            roots = {}
            for name, root in (corpora or {}).items():
                M.identifier(name)
                root = Path(root).resolve()
                if not root.is_dir():
                    raise WorkError('Registered corpus must exist')
                roots[name] = str(root)
            store = cls(directory, clock=clock)
            store._append(db, state, 'initialize', {'authority_hash': token_hash(secret), 'corpora': roots}, 'host')
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()
        return store, secret

    @contextmanager
    def _transaction(self):
        # mode=rw never creates a missing/truncated store on read.
        db = sqlite3.connect(self.path.as_uri()+'?mode=rw', uri=True, timeout=15, isolation_level=None)
        try:
            db.execute('PRAGMA synchronous=FULL')
            db.execute('BEGIN IMMEDIATE')
            yield db, self._read(db)
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def _read(self, db):
        state = _empty()
        try:
            for seq, body, pin in db.execute('SELECT seq,body,hash FROM events ORDER BY seq'):
                event = json.loads(body)
                if (seq != state['seq']+1 or event['seq'] != seq or event['prev'] != state['head']
                        or event['schema'] != SCHEMA or digest(event) != pin):
                    raise IntegrityError('Event chain verification failed')
                _apply(state, event)
            row = db.execute('SELECT seq,hash FROM head WHERE id=1').fetchone()
            if row != (state['seq'], state['head']) or state['seq'] == 0:
                raise IntegrityError('Ledger head mismatch or truncated history')
        except (KeyError, TypeError, json.JSONDecodeError, sqlite3.DatabaseError) as exc:
            raise IntegrityError('Invalid work ledger') from exc
        return state

    def _append(self, db, state, kind, payload, actor):
        event = {'schema': SCHEMA, 'seq': state['seq']+1, 'prev': state['head'],
                 'id': uuid.uuid4().hex, 'time': self.clock(), 'type': kind,
                 'actor': actor, 'implementation_sha256': implementation_pins(), 'payload': copy.deepcopy(payload)}
        pin = digest(event)
        db.execute('INSERT INTO events VALUES (?,?,?)', (event['seq'], canonical(event), pin))
        db.execute('UPDATE head SET seq=?,hash=? WHERE id=1', (event['seq'], pin))
        _apply(state, event)
        return pin

    def _host(self, state, credential):
        if not hmac.compare_digest(token_hash(credential), state['authority_hash']):
            raise Denied('Credential rejected')

    def _actor(self, state, credential):
        hashed = token_hash(credential)
        for seat, grant in state['seats'].items():
            if hmac.compare_digest(hashed, grant['token_hash']):
                if grant['revoked'] or self.clock() >= grant['expires_at']:
                    break
                return dict(grant, seat=seat)
        raise Denied('Credential rejected, revoked, expired or fenced out')

    def head(self, authority):
        with self._transaction() as (_, state):
            self._host(state, authority)
            return {'seq': state['seq'], 'hash': state['head']}

    @staticmethod
    def _expect(actual, expected):
        if not isinstance(expected, str) or not hmac.compare_digest(actual, expected):
            raise Conflict('Stale work view; reload and reconcile')

    def assign(self, authority, *, seat, instance, model, contract, expected_head, continues_work_of=None):
        """Host-issued scoped capability; a new occupant fences the previous one."""
        M.identifier(seat); M.identifier(instance)
        if not isinstance(model, dict) or set(model) != {'name', 'provider', 'version', 'context_policy_hash'}:
            raise WorkError('Model metadata requires name, provider, version and context_policy_hash')
        for v in model.values():
            M.words(v, 500)
        if model['context_policy_hash'] != 'unknown' and not re.fullmatch(r'sha256:[0-9a-f]{64}', model['context_policy_hash']):
            raise WorkError('Context policy needs a SHA-256 pin or explicit unknown')
        required = {'operations', 'tools', 'scopes', 'share_with', 'profile', 'expires_at'}
        if not isinstance(contract, dict) or set(contract) != required:
            raise WorkError('Incomplete seat contract')
        for field in ('operations', 'tools', 'scopes', 'share_with'):
            M.strings(contract[field])
        from mplpb_combined.reader import PROFILES
        if (not set(contract['operations']) <= M.OPERATIONS or contract['profile'] not in PROFILES
                or type(contract['expires_at']) not in (int, float) or not math.isfinite(contract['expires_at'])
                or contract['expires_at'] <= self.clock()):
            raise WorkError('Invalid rights, profile or expiry')
        for name in contract['tools']+contract['share_with']:
            M.identifier(name)
        for scope in contract['scopes']:
            if scope != '*':
                M.identifier(scope)
        with self._transaction() as (db, state):
            self._host(state, authority); self._expect(state['head'], expected_head)
            if instance in state['instances']:
                raise Conflict('Instance IDs are never reused')
            if continues_work_of and continues_work_of not in state['instances']:
                raise WorkError('Unknown predecessor instance')
            secret = secrets.token_urlsafe(48)
            previous = state['seats'].get(seat)
            fence = previous['fence']+1 if previous else 1
            grant = dict(copy.deepcopy(contract), instance=instance, fence=fence,
                         revoked=False, token_hash=token_hash(secret))
            identity = {'id': instance, 'seat': seat, 'model': model,
                        'started_at': self.clock(), 'ended_at': None, 'continues_work_of': continues_work_of}
            self._append(db, state, 'assign', {'seat': seat, 'grant': grant, 'instance': identity}, 'host')
            return {'credential': secret, 'instance': identity, 'fence': fence, 'head': state['head']}

    def revoke(self, authority, seat, expected_head):
        with self._transaction() as (db, state):
            self._host(state, authority); self._expect(state['head'], expected_head)
            if seat not in state['seats']:
                raise WorkError('Unknown seat')
            self._append(db, state, 'revoke', {'seat': seat}, 'host')
            return {'head': state['head']}

    def end(self, credential, expected_head):
        with self._transaction() as (db, state):
            actor = self._actor(state, credential)
            self._expect(self._view(state, actor)['head'], expected_head)
            self._append(db, state, 'end', {'seat': actor['seat']}, actor['instance'])
            return {'ended': True}

    def _adapter(self, operation):
        adapter = self.executors.get(operation)
        if callable(adapter):
            return adapter, 'local'
        if isinstance(adapter, dict) and set(adapter) == {'run', 'side_effect'} and callable(adapter['run']) and adapter['side_effect'] in {'local', 'external'}:
            return adapter['run'], adapter['side_effect']
        return None, None

    @staticmethod
    def _scope(record):
        return record['id'] if record['kind'] == 'task' else record['payload']['task']

    @staticmethod
    def _allowed(actor, operation, task):
        return operation in actor['operations'] and ('*' in actor['scopes'] or task in actor['scopes'])

    def _source(self, state, payload, profile, cache):
        from mplpb_combined.provenance_gate import gather
        from mplpb_combined.reader import PROFILES
        from mplpb_combined.ledger import Ledger
        from mplpb_combined.record import text_of
        from mplpb_combined.delivery import external_restriction
        key = (payload['corpus'], payload['query'], profile)
        try:
            root = state['corpora'][payload['corpus']]
            if key not in cache:
                cache[key] = gather(root, payload['query'], PROFILES[profile]).sources
            matches = [s for s in cache[key] if s['id'] == payload['source_id'] and s['hash'] == payload['source_hash']]
            if len(matches) != 1:
                return None
            source = matches[0]
            records = [r for r in Ledger(root).servable() if r.path == source['path'] and r.hash_actual == payload['source_hash']]
            if len(records) != 1:
                return None
            rec = records[0]
            body = text_of(re.sub(r'<h[1-6]\b[^>]*>.*?</h[1-6]>', '\n', rec.body_html, flags=re.I | re.S))
            if payload['quote'] not in body:
                return None
            nodes = [source]+source['ancestry']
            roots = sorted({n['id']+'@'+n['hash'] for n in nodes if not n['derived_from'] and not n['supersedes']})
            return {'roots': roots, 'depth': source['origin_depth'], 'external_allowed': not bool(external_restriction(rec, PROFILES['external']))}
        except (OSError, ValueError, KeyError):
            return None

    def _can_read(self, state, actor, record):
        readers = set(record['visibility']) | state['transfers'].get(record['id'], set())
        if actor['seat'] not in readers or not ('*' in actor['scopes'] or self._scope(record) in actor['scopes']):
            return False
        if record['kind'] == 'evidence':
            from mplpb_combined.reader import PROFILES
            profile = PROFILES[actor['profile']]
            if profile.max_depth is not None and record['source']['depth'] > profile.max_depth:
                return False
            if actor['profile'] == 'external' and (not record['source']['external_allowed'] or not self._source(state, record['payload'], actor['profile'], {})):
                return False
        return True

    def _readable_version(self, state, actor, record, trail=None):
        if not self._can_read(state, actor, record):
            return False
        trail = set(trail or ())
        marker = (record['id'], record['revision'])
        if marker in trail:
            return True
        trail.add(marker)
        for key, revision in M.references(record).items():
            ref = state['records'][key] if revision is None else state['history'][key][revision-1]
            if not self._readable_version(state, actor, ref, trail):
                return False
        return True

    def _visible(self, state, actor):
        return {key for key, record in state['records'].items() if self._readable_version(state, actor, record)}

    def _effective(self, state, record, profile, cache, trail=None):
        trail = set(trail or ())
        if record['id'] in trail:
            return 'needs_recheck'
        trail.add(record['id'])
        kind, p = record['kind'], record['payload']
        if kind == 'evidence':
            return 'eligible' if self._source(state, p, profile, cache) else 'needs_recheck'
        refs = dict(record['dependencies'])
        if kind == 'task':
            refs.update(p['acceptance'])
        for key, revision in refs.items():
            dep = state['records'][key]
            if dep['revision'] != revision or self._effective(state, dep, profile, cache, trail) not in {'eligible', 'supported_under_scope', 'passed', 'accepted', 'done', 'completed'}:
                return 'needs_recheck'
        if kind == 'claim':
            if any(r['kind'] == 'review' and record['id'] in r['payload']['target']
                   and (r['payload']['outcome'] == 'challenge' or (r['payload']['outcome'] == 'resolved' and self._effective(state, r, profile, cache, trail) != 'resolved'))
                   for r in state['records'].values()):
                return 'contested'
            return p['assessment']
        if kind == 'action':
            if any(r['action'] == record['id'] and r['status'] == 'started' for r in state['receipts'].values()):
                return 'indeterminate'
            return p['state']
        if kind == 'attempt':
            return p['result']
        if kind == 'decision':
            for key, revision in p['failed_attempts'].items():
                failed = state['records'][key]
                if failed['revision'] != revision or self._effective(state, failed, profile, cache, trail) not in {'failed', 'inconclusive', 'indeterminate'}:
                    return 'needs_recheck'
            return p['assessment']
        if kind == 'review':
            return p['outcome']
        return p['state']

    def _permission(self, state, actor, action, visible, cache):
        p = action['payload']
        if (not self._allowed(actor, 'execute', p['task']) or p['executor_seat'] != actor['seat']
                or p['operation'] not in actor['tools']):
            return 'requires_authorization'
        adapter, effect = self._adapter(p['operation'])
        if adapter is None or effect != p['side_effect']:
            return 'blocked'
        if action['id'] not in visible or self._effective(state, action, actor['profile'], cache) != 'proposed':
            return 'blocked'
        failures = [r for r in state['receipts'].values() if r['status'] in {'failed', 'inconclusive'}
                    and r['task'] == p['task'] and state['history'][r['action']][r['action_revision']-1]['payload']['operation'] == p['operation']]
        latest_failure = failures[-1]['id'] if failures else None
        for receipt in state['receipts'].values():
            prior = state['history'][receipt['action']][receipt['action_revision']-1]
            if receipt['action'] == action['id'] or prior['payload']['task'] != p['task'] or prior['payload']['operation'] != p['operation']:
                continue
            if receipt['status'] in {'started', 'indeterminate'}:
                return 'blocked'
            if receipt['status'] in {'failed', 'inconclusive'}:
                retries = [state['records'][key] for key in p['retry_of']]
                if receipt['id'] == latest_failure and not any(r.get('receipt') == receipt['id'] for r in retries):
                    return 'blocked'
                if prior['payload']['arguments'] == p['arguments'] and prior['payload']['task_revision'] == p['task_revision'] and prior['dependencies'] == action['dependencies']:
                    return 'blocked'
        task = state['records'][p['task']]
        if task['revision'] != p['task_revision'] or task['payload']['state'] != 'open' or self._effective(state, task, actor['profile'], cache) != 'open':
            return 'blocked'
        return 'allowed'

    def _view(self, state, actor):
        visible, cache = self._visible(state, actor), {}
        records = []
        for key in sorted(visible):
            record = copy.deepcopy(state['records'][key])
            record['effective_status'] = self._effective(state, record, actor['profile'], cache)
            record['history'] = [copy.deepcopy(r) for r in state['history'][key] if self._readable_version(state, actor, r)]
            if record['kind'] == 'action':
                record['permission'] = self._permission(state, actor, record, visible, cache)
            records.append(record)
        own_instances = [copy.deepcopy(i) for i in state['instances'].values() if i['seat'] == actor['seat']]
        contract = {k: copy.deepcopy(actor[k]) for k in ('seat', 'instance', 'fence', 'operations', 'tools', 'scopes', 'share_with', 'profile', 'expires_at')}
        result = {'schema': SCHEMA, 'implementation_sha256': implementation_pins(),
                  'authority': 'revisable_work_state', 'answer_supported': False,
                  'content_truth_verified': False, 'identity_basis': 'Host-issued bearer capability; model metadata is declared, not provider-attested.',
                  'instance': copy.deepcopy(state['instances'][actor['instance']]), 'instances': own_instances,
                  'contract': contract, 'records': records}
        # Seat view head excludes private events, counts, credentials and global sequence.
        result['head'] = digest(result)
        result['next_actions'] = [r['id'] for r in records if r['kind'] == 'action' and r['permission'] == 'allowed']
        return result

    def snapshot(self, credential):
        with self._transaction() as (_, state):
            return self._view(state, self._actor(state, credential))

    def handoff(self, credential):
        # Always reconstructed under the current successor grant, never a raw tail.
        return self.snapshot(credential)

    def _validate_record(self, state, actor, record, old):
        kind, p = record['kind'], record['payload']
        M.validate(kind, p); M.pins(record['dependencies'])
        scope = self._scope(record)
        if not self._allowed(actor, ('revise:' if old else 'create:')+kind, scope):
            raise Denied('Operation is outside this seat contract')
        visibility = record['visibility']
        M.strings(visibility, empty=False)
        if (actor['seat'] not in visibility or not set(visibility) <= set(state['seats'])
                or (not old and not set(visibility) <= {actor['seat']} | set(actor['share_with']))):
            raise Denied('Invalid explicit visibility')
        if old:
            if kind != old['kind'] or scope != self._scope(old) or visibility != old['visibility']:
                raise Denied('Kind, task and visibility require explicit transfer, not revision')
            if kind in {'evidence', 'attempt'}:
                raise Denied('Evidence and attempts are immutable; record a new object')
        visible = self._visible(state, actor)
        if old and old['id'] not in visible:
            raise Denied('Record unavailable')
        if kind != 'task':
            task = state['records'].get(scope)
            if not task or task['kind'] != 'task':
                raise WorkError('Record needs an existing task')
        for key, revision in M.references(record).items():
            if key not in visible:
                raise Denied('Referenced record unavailable')
            ref = state['records'][key]
            historical_target = kind == 'review' and key in p['target']
            if revision is not None and (revision > ref['revision'] or (not historical_target and ref['revision'] != revision)):
                raise Conflict('A referenced revision changed')
            if historical_target:
                ref = state['history'][key][revision-1]
            readers = set(ref['visibility']) | state['transfers'].get(key, set())
            if not set(visibility) <= readers:
                raise Denied('A reference cannot widen its source visibility')
        # Prerequisites are a DAG; task containment and review targets are typed links.
        def visit(key, trail):
            if key in trail:
                raise WorkError('Cyclic prerequisite relationship')
            target = record if key == record['id'] else state['records'][key]
            for child in target['dependencies']:
                visit(child, trail | {key})
        visit(record['id'], set())
        if kind == 'claim' and p['assessment'] == 'supported_under_scope':
            if not record['dependencies'] or any(state['records'][key]['kind'] not in {'evidence', 'claim'} for key in record['dependencies']):
                raise WorkError('Working support needs pinned evidence or claim dependencies')
        if kind == 'evidence':
            source = self._source(state, p, actor['profile'], {})
            if not source:
                raise WorkError('No eligible exact body span at the pinned source revision')
            record['source'] = source
        if kind == 'review':
            if old and p['target'] != old['payload']['target']:
                raise Denied('Review targets are immutable')
            target = state['records'][next(iter(p['target']))]
            if target['kind'] != 'claim' or set(visibility) != set(target['visibility']):
                raise Denied('A challenge must have the same visibility as its claim')
            rounds = {r['review_round'] for versions in state['history'].values() for r in versions
                      if r['kind'] == 'review' and r['payload']['task'] == scope}
            resolving = old and old['payload']['outcome'] == 'challenge' and p['outcome'] == 'resolved'
            if not resolving and len(rounds) >= state['records'][scope]['payload']['review_budget']:
                raise WorkError('Declared review budget exhausted')
            record['review_round'] = old['review_round'] if resolving else max(rounds, default=0)+1
            if p['outcome'] == 'resolved':
                if not old or old['payload']['outcome'] != 'challenge' or 'resolve_review' not in actor['operations'] or not record['dependencies']:
                    raise Denied('Challenge resolution requires separate rights and pinned evidence')
                if any(state['records'][key]['kind'] != 'evidence' or self._effective(state, state['records'][key], actor['profile'], {}) != 'eligible' for key in record['dependencies']):
                    raise WorkError('Challenge resolution requires current source evidence')
            elif old and old['payload']['outcome'] == 'challenge':
                raise Denied('A live challenge needs explicit resolution')
            roots = self._roots(state, record['dependencies'])
            previous, previous_spans = set(), set()
            for r in state['records'].values():
                if (r['kind'] == 'review' and r['payload']['target'] == p['target']
                        and r['payload']['target_variable'] == p['target_variable'] and r['payload']['regime'] == p['regime']):
                    previous.update(r.get('evidence_roots', []))
                    previous_spans.update(r.get('evidence_spans', []))
            spans = self._evidence_spans(state, record['dependencies'])
            record.update(evidence_roots=sorted(roots), new_evidence_roots=sorted(roots-previous),
                          evidence_spans=sorted(spans), new_evidence_spans=sorted(spans-previous_spans), discrimination='unmeasured')
        failure_refs = p['failed_attempts'] if kind == 'decision' else p['retry_of'] if kind == 'action' else {}
        for key in failure_refs:
            failed = state['records'][key]
            if failed['kind'] != 'attempt' or failed['payload']['result'] not in {'failed', 'inconclusive', 'indeterminate'}:
                raise WorkError('Failed-route links require an unsuccessful attempt')
        if kind == 'action':
            if p['task_revision'] != state['records'][scope]['revision']:
                raise Conflict('Task constraints changed; refresh the action')
            if p['executor_seat'] not in state['seats']:
                raise WorkError('Unknown execution seat')
            if old and any(r['action'] == record['id'] for r in state['receipts'].values()):
                raise Denied('Dispatched actions are immutable; propose a new action')
        if kind == 'task':
            if p['state'] == 'done':
                receipts = []
                for ref in p['acceptance']:
                    attempt = state['records'][ref]
                    if attempt['kind'] != 'attempt' or attempt['payload']['task'] != record['id'] or 'receipt' not in attempt:
                        raise WorkError('Completion requires host execution receipts')
                    receipt = state['receipts'][attempt['receipt']]
                    if receipt['task_revision'] != (old['revision'] if old else 0):
                        raise WorkError('Acceptance criteria changed after execution')
                    if receipt['status'] != 'passed' or self._effective(state, attempt, actor['profile'], {}) != 'passed':
                        raise WorkError('Completion evidence is stale or unsuccessful')
                    receipts.append(receipt)
                passed = {criterion for receipt in receipts for criterion, ok in receipt['validation'].items() if ok is True}
                if not set(p['criteria']) <= passed:
                    raise WorkError('Each acceptance criterion needs a passing host result')
            elif p['acceptance']:
                raise WorkError('Only completed tasks can declare acceptance evidence')

    @staticmethod
    def _roots(state, refs, trail=None):
        result, trail = set(), set(trail or ())
        for key in refs:
            if key in trail:
                continue
            record = state['records'][key]
            if record['kind'] == 'evidence':
                result.update(record['source']['roots'])
            else:
                result.update(WorkStore._roots(state, record['dependencies'], trail | {key}))
        return result

    @staticmethod
    def _evidence_spans(state, refs, trail=None):
        result, trail = set(), set(trail or ())
        for key in refs:
            if key in trail:
                continue
            record = state['records'][key]
            if record['kind'] == 'evidence':
                result.add(digest({k: record['payload'][k] for k in ('corpus', 'source_id', 'source_hash', 'quote')}))
            else:
                result.update(WorkStore._evidence_spans(state, record['dependencies'], trail | {key}))
        return result

    def put(self, credential, *, id, kind, payload, dependencies, visibility, expected_revision, expected_head):
        M.identifier(id)
        if id.startswith('attempt:'):
            raise Denied('Execution attempt identifiers are reserved for the host')
        with self._transaction() as (db, state):
            actor = self._actor(state, credential)
            self._expect(self._view(state, actor)['head'], expected_head)
            old = state['records'].get(id)
            if type(expected_revision) is not int or expected_revision != (old['revision'] if old else 0):
                raise Conflict('Stale record revision')
            if old is None and any(r['id'] == id for values in state['history'].values() for r in values):
                raise Conflict('Record identifiers are never reused')
            record = {'id': id, 'kind': kind, 'revision': expected_revision+1,
                      'payload': copy.deepcopy(payload), 'dependencies': copy.deepcopy(dependencies),
                      'visibility': copy.deepcopy(visibility),
                      'created_by': old['created_by'] if old else actor['instance'],
                      'revised_by': actor['instance'], 'created_at': old['created_at'] if old else self.clock(),
                      'revised_at': self.clock()}
            self._validate_record(state, actor, record, old)
            self._append(db, state, 'put', {'record': record, 'seat': actor['seat'], 'fence': actor['fence']}, actor['instance'])
            return self._view(state, actor)

    def transfer(self, credential, *, id, to, include_history, expected_revision, expected_head):
        M.strings(to, empty=False)
        if include_history is not True:
            raise WorkError('Transfers explicitly include the entire record history')
        with self._transaction() as (db, state):
            actor = self._actor(state, credential)
            self._expect(self._view(state, actor)['head'], expected_head)
            if id not in self._visible(state, actor):
                raise Denied('Record unavailable')
            old = state['records'][id]
            if not self._allowed(actor, 'transfer', self._scope(old)) or not set(to) <= set(actor['share_with']) or not set(to) <= set(state['seats']):
                raise Denied('Transfer is outside this seat contract')
            if old['revision'] != expected_revision:
                raise Conflict('Stale record revision')
            if old['kind'] == 'action' and any(r['action'] == id for r in state['receipts'].values()):
                raise Denied('Dispatched actions cannot be transferred')
            readers = set(old['visibility']) | set(to)
            for version in state['history'][id]:
                for key in M.references(version):
                    source = state['records'][key]
                    if not readers <= set(source['visibility']) | state['transfers'].get(key, set()):
                        raise Denied('Transfer dependencies first; no private-reference laundering')
            record = copy.deepcopy(old)
            record.update(visibility=sorted(readers), revision=old['revision']+1, revised_by=actor['instance'], revised_at=self.clock())
            self._append(db, state, 'transfer', {'record': record, 'to': to, 'include_history': True}, actor['instance'])
            return self._view(state, actor)

    def execute(self, credential, *, id, expected_revision, expected_head):
        """Dispatch once through a host-registered adapter, after a fresh gate.

        A crash after the durable start stays indeterminate. No automatic retry.
        Adapters receive a durable idempotency key and exact pinned inputs.
        """
        with self._transaction() as (db, state):
            actor = self._actor(state, credential)
            view = self._view(state, actor)
            self._expect(view['head'], expected_head)
            if id not in self._visible(state, actor):
                raise Denied('Action unavailable')
            action = state['records'][id]
            if action['kind'] != 'action' or action['revision'] != expected_revision:
                raise Conflict('Stale action revision')
            if self._permission(state, actor, action, self._visible(state, actor), {}) != 'allowed':
                raise Denied('Action is not currently permissible')
            operation = action['payload']['operation']
            if operation not in self.executors:
                raise Denied('No host adapter registered for this operation')
            receipt = {'id': uuid.uuid4().hex, 'action': id, 'action_revision': expected_revision,
                       'instance': actor['instance'], 'seat': actor['seat'], 'fence': actor['fence'],
                       'status': 'started', 'validation': {}, 'artifact_hash': None,
                       'task': action['payload']['task'], 'task_revision': action['payload']['task_revision'],
                       'input_pins': dict(state['records'][action['payload']['task']]['dependencies'], **action['dependencies'])}
            self._append(db, state, 'start', {'receipt': receipt}, actor['instance'])
        # Recheck authority and source bytes immediately at the dispatch boundary.
        try:
            with self._transaction() as (_, state):
                current = self._actor(state, credential)
                if current['fence'] != actor['fence']:
                    raise Denied('Writer fenced out')
                original = copy.deepcopy(state['records'][id])
                effective = self._effective(state, original, actor['profile'], {})
                # "indeterminate" is caused by our own durable reservation. Check
                # all dependencies directly as well, never treating it as permission.
                if original['revision'] != expected_revision or effective not in {'indeterminate', 'proposed'}:
                    raise Denied('Inputs changed before dispatch')
                task = state['records'][original['payload']['task']]
                if task['revision'] != original['payload']['task_revision'] or task['payload']['state'] != 'open' or self._effective(state, task, actor['profile'], {}) != 'open':
                    raise Denied('Task changed before dispatch')
                for key, revision in original['dependencies'].items():
                    dep = state['records'][key]
                    if dep['revision'] != revision or self._effective(state, dep, actor['profile'], {}) not in {'eligible', 'supported_under_scope', 'passed', 'accepted', 'done', 'completed'}:
                        raise Denied('Inputs changed before dispatch')
            adapter, effect = self._adapter(operation)
            if adapter is None or effect != action['payload']['side_effect']:
                raise Denied('Adapter changed before dispatch')
            outcome = adapter({'idempotency_key': receipt['id'], 'action': copy.deepcopy(action), 'context': view})
            if (not isinstance(outcome, dict) or set(outcome) != {'result', 'validation', 'artifact'}
                    or outcome['result'] not in {'passed', 'failed', 'inconclusive'}
                    or not isinstance(outcome['validation'], dict)
                    or any(type(v) is not bool for v in outcome['validation'].values())):
                raise WorkError('Host adapter returned an invalid result')
            M.words(outcome['artifact'], 16000)
            for key in outcome['validation']:
                M.words(key, 1000)
        except Exception as exc:
            # Exceptions may occur after a side effect. Do not label them a clean
            # failure or retry; the operator must reconcile external state.
            outcome = {'result': 'indeterminate', 'validation': {}, 'artifact': type(exc).__name__+': dispatch outcome requires host reconciliation'}
        return self._finish(receipt['id'], outcome)

    def reconcile(self, authority, *, receipt, result, validation, artifact, reason, expected_head):
        M.words(reason); M.words(artifact, 16000)
        if result not in {'passed', 'failed', 'inconclusive'} or not isinstance(validation, dict) or any(type(v) is not bool for v in validation.values()):
            raise WorkError('Reconciliation requires a declared host-verified outcome')
        for key in validation:
            M.words(key, 1000)
        return self._finish(receipt, {'result': result, 'validation': validation, 'artifact': artifact},
                            authority=authority, expected_head=expected_head, reason=reason)

    def _finish(self, receipt_id, outcome, authority=None, expected_head=None, reason=None):
        with self._transaction() as (db, state):
            if authority is not None:
                self._host(state, authority); self._expect(state['head'], expected_head)
            if receipt_id not in state['receipts']:
                raise WorkError('Unknown receipt')
            receipt = copy.deepcopy(state['receipts'][receipt_id])
            if receipt['status'] not in ({'started', 'indeterminate'} if authority is not None else {'started'}):
                raise Conflict('Execution has already been reconciled')
            if authority is not None:
                receipt.update(reconciled_by='host', reconciliation_reason=reason)
            receipt.update(status=outcome['result'], validation=outcome['validation'], artifact_hash=digest(outcome['artifact']))
            action = copy.deepcopy(state['records'][receipt['action']])
            if action['revision'] != receipt['action_revision']+(1 if 'attempt:'+receipt_id in state['records'] else 0):
                raise Conflict('Dispatched action was changed')
            action['revision'] += 1
            action['revised_at'] = self.clock()
            action['payload']['state'] = 'completed' if outcome['result'] == 'passed' else 'indeterminate' if outcome['result'] == 'indeterminate' else 'failed'
            attempt = {'id': 'attempt:'+receipt_id+(':reconciled' if 'attempt:'+receipt_id in state['records'] else ''), 'kind': 'attempt', 'revision': 1,
                       'created_by': receipt['instance'], 'revised_by': receipt['instance'], 'created_at': self.clock(), 'revised_at': self.clock(),
                       'visibility': list(action['visibility']), 'dependencies': dict(receipt['input_pins']),
                       'receipt': receipt_id, 'payload': {'task': action['payload']['task'],
                       'method': action['payload']['operation'], 'result': outcome['result'],
                       'failure': 'none' if outcome['result'] == 'passed' else outcome['artifact'],
                       'retry_when': 'A new authorized action and current input pins are required; never retry an indeterminate receipt automatically.',
                       'artifact': outcome['artifact']}}
            self._append(db, state, 'finish', {'receipt': receipt, 'records': [action, attempt]}, 'host-adapter')
            return {'receipt': receipt, 'attempt': attempt['id'], 'action': action['id']}

    def audit(self, authority, checkpoint=None):
        with self._transaction() as (db, state):
            self._host(state, authority)
            events = [json.loads(row[0]) for row in db.execute('SELECT body FROM events ORDER BY seq')]
            if checkpoint:
                n = checkpoint.get('seq')
                if type(n) is not int or n < 1 or n > len(events) or digest(events[n-1]) != checkpoint.get('hash'):
                    raise IntegrityError('Trusted checkpoint no longer matches this history')
            return {'schema': SCHEMA, 'head': {'seq': state['seq'], 'hash': state['head']}, 'events': events}
