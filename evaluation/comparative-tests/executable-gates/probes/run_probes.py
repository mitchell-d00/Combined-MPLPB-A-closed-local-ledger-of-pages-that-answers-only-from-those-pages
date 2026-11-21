"""Seven paired work-boundary probes against the MPLPB specialist-continuity executor.

Each pair runs a supported control and an unsupported/unauthorized variant on a
fresh store. The host adapter writes a marker file; the event store is counted
directly in SQLite before and after the execute call.
"""
import json, sqlite3, sys, tempfile, subprocess
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(REPO))

from mplpb_work import WorkStore, WorkError, Denied, Conflict
from mplpb_work.store import digest
from mplpb_work.model import OPERATIONS
from mplpb_combined.ledger import write, Ledger

ROLES = ['finder', 'critic', 'builder', 'reviewer']


class Fixture:
    def __init__(self, base):
        self.base = Path(base)
        self.now = [1000.0]
        self.corpus = self.base / 'corpus'
        write(self.corpus, doc_id='SRC-0001', title='Supplier', scope='supplier availability',
              body='Configuration AX-14 is discontinued. Component X remains available.')
        self.source = Ledger(self.corpus).by_id['SRC-0001'][0]
        self.store, self.host = WorkStore.create(self.base / 'work', {'research': self.corpus}, clock=lambda: self.now[0])
        self.marker = self.base / 'marker.txt'
        self.calls = 0
        self.store.executors['fixture.run.v1'] = self.adapter
        self.tokens = {}
        for r in ROLES:
            self.assign(r, r + '-1')
        self.put('finder', 'T1', 'task', {'goal': 'Test component availability', 'criteria': ['test passes'],
                                          'review_budget': 4, 'state': 'open', 'acceptance': {}})

    def adapter(self, request):
        self.calls += 1
        self.marker.write_text(request['idempotency_key'])
        return {'result': 'passed', 'validation': {'test passes': True}, 'artifact': 'marker written'}

    def assign(self, seat, instance, tools=None, predecessor=None):
        contract = {'operations': sorted(OPERATIONS), 'tools': ['fixture.run.v1'] if tools is None else tools,
                    'scopes': ['T1', 'T2'], 'share_with': ROLES, 'profile': 'internal', 'expires_at': 10000.0}
        res = self.store.assign(self.host, seat=seat, instance=instance,
                                model={'name': 'same-model', 'provider': 'fixture', 'version': '1',
                                       'context_policy_hash': digest({'policy': 'fixture'})},
                                contract=contract, continues_work_of=predecessor,
                                expected_head=self.store.head(self.host)['hash'])
        self.tokens[seat] = res['credential']

    def evidence(self, quote='Configuration AX-14 is discontinued.'):
        return {'task': 'T1', 'corpus': 'research', 'source_id': self.source.id, 'source_hash': self.source.hash,
                'quote': quote, 'query': 'supplier availability'}

    def claim(self, **ch):
        p = {'task': 'T1', 'proposition': 'Configuration AX-14 is discontinued', 'basis': 'inference',
             'assessment': 'supported_under_scope', 'assumptions': [],
             'alternatives': ['Other configurations may remain'], 'revisit_when': 'Check component catalog'}
        p.update(ch); return p

    def action(self):
        return {'task': 'T1', 'task_revision': 1, 'operation': 'fixture.run.v1', 'arguments': {'case': 'availability'},
                'side_effect': 'local', 'executor_seat': 'builder', 'state': 'proposed', 'retry_of': {}, 'retry_reason': ''}

    def put(self, seat, id, kind, payload, deps=None, revision=0):
        return self.store.put(self.tokens[seat], id=id, kind=kind, payload=payload, dependencies=deps or {},
                              visibility=list(ROLES), expected_revision=revision,
                              expected_head=self.store.snapshot(self.tokens[seat])['head'])

    def events(self):
        db = sqlite3.connect(str(self.base / 'work' / 'work.sqlite3'))
        try: return db.execute('SELECT count(*) FROM events').fetchone()[0]
        finally: db.close()

    def status(self):
        try:
            rows = {r['id']: r for r in self.store.snapshot(self.tokens['builder'])['records']}
        except Denied:
            return None, 'credential rejected'
        claim = next((rows[k]['effective_status'] for k in ('C2', 'C1') if k in rows), None)
        return claim, rows['A1']['permission']

    def execute(self):
        head = self.store.head(self.host)['hash']
        try:
            head = self.store.snapshot(self.tokens['builder'])['head']
        except Denied:
            pass
        try:
            r = self.store.execute(self.tokens['builder'], id='A1', expected_revision=1, expected_head=head)
            return 'dispatched; receipt ' + r['receipt']['status']
        except (Denied, Conflict, WorkError) as e:
            return type(e).__name__ + ': ' + str(e)


def standard(f, quote=None, **claim):
    f.put('finder', 'E1', 'evidence', f.evidence(quote) if quote else f.evidence())
    f.put('finder', 'C1', 'claim', f.claim(**claim), {'E1': 1})
    f.put('builder', 'A1', 'action', f.action(), {'C1': 1})


def chain(f):
    f.put('finder', 'E1', 'evidence', f.evidence())
    f.put('finder', 'C1', 'claim', f.claim(), {'E1': 1})
    f.put('finder', 'C2', 'claim', f.claim(), {'C1': 1})
    f.put('builder', 'A1', 'action', f.action(), {'C2': 1})


def change_source(f):
    page = f.corpus / f.source.path
    page.write_text(page.read_text().replace('is discontinued', 'is available'))


def revoke(f):
    f.store.revoke(f.host, 'builder', f.store.head(f.host)['hash'])


def no_tool(f):
    f.assign('builder', 'builder-2', tools=[], predecessor='builder-1')


PROBES = [
    ('P1', 'Contradicted proposition',
     'Claim matches a full quoted source sentence',
     'Claim says "Component X is discontinued"; cited page says it remains available',
     lambda f: standard(f), None,
     lambda f: standard(f, proposition='Component X is discontinued'), None),
    ('P2', 'Partial quotation',
     'Evidence quotes the complete source sentence',
     'Evidence quotes a fragment ("AX-14 is discontinued.")',
     lambda f: standard(f), None,
     lambda f: standard(f, quote='AX-14 is discontinued.'), None),
    ('P3', 'Unstated assumption',
     'Claim carries no assumptions',
     'Claim adds "Assume source applies"',
     lambda f: standard(f), None,
     lambda f: standard(f, assumptions=['Assume source applies']), None),
    ('P4', 'Claim-only chain',
     'Action depends on a claim pinned to evidence',
     'Action depends on a claim that cites only another claim',
     lambda f: standard(f), None,
     chain, None),
    ('P5', 'Source changed after planning',
     'Source bytes unchanged at dispatch',
     'Cited page edited after the action was proposed',
     lambda f: standard(f), None,
     lambda f: standard(f), change_source),
    ('P6', 'Revoked seat',
     'Executor seat holds a live grant',
     'Host revokes the executor seat before dispatch',
     lambda f: standard(f), None,
     lambda f: standard(f), revoke),
    ('P7', 'Tool not granted',
     'Seat contract lists fixture.run.v1',
     'Successor seat contract lists no tools',
     lambda f: standard(f), None,
     lambda f: standard(f), no_tool),
]


def run(setup, mutate):
    with tempfile.TemporaryDirectory() as d:
        f = Fixture(d)
        setup(f)
        if mutate: mutate(f)
        claim, perm = f.status()
        before = f.events()
        outcome = f.execute()
        after = f.events()
        return {'claim_status': claim, 'permission': perm, 'outcome': outcome,
                'marker_written': f.marker.exists(), 'adapter_calls': f.calls,
                'events_before': before, 'events_after': after, 'events_added': after - before}


results = []
for pid, name, cdesc, vdesc, cset, cmut, vset, vmut in PROBES:
    results.append({'probe': pid, 'name': name,
                    'control': dict(run(cset, cmut), description=cdesc),
                    'variant': dict(run(vset, vmut), description=vdesc)})

rev = subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
OUT.write_text(json.dumps({'repository_revision': rev, 'python': sys.version.split()[0], 'probes': results}, indent=2))
for r in results:
    c, v = r['control'], r['variant']
    print(r['probe'], r['name'], '|', c['claim_status'], c['permission'], c['marker_written'], c['events_added'], c['outcome'],
          '||', v['claim_status'], v['permission'], v['marker_written'], v['events_added'], v['outcome'])
