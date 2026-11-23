"""Host-side proposal gate for one local, source-cited report operation."""
import argparse
import json
from pathlib import Path
import re
import time

from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import Ledger, write
from mplpb_combined.reader import PROFILES
from mplpb_work import Conflict, Denied, WorkError, WorkStore
from mplpb_work.store import canonical, digest

OPERATION = 'save-cited-report.v1'


class CitedReportGate:
    """The host owns this object, its approval state, credential, and output directory."""

    def __init__(self, root, corpus, source_id, field):
        self.corpus = Path(corpus)
        self.output = Path(root) / 'reports'
        self.output.mkdir(parents=True)
        self.store, self.host = WorkStore.create(Path(root) / 'work', {'demo': self.corpus})
        self.store.executors[OPERATION] = {'run': self._write_report, 'side_effect': 'local'}
        self.field = field
        self.source, = [record for record in Ledger(corpus).servable() if record.id == source_id]
        self.approvals = set()
        assigned = self.store.assign(
            self.host, seat='reporter', instance='local-reporter',
            model={'name': 'report host', 'provider': 'local', 'version': '1',
                   'context_policy_hash': digest(OPERATION)},
            contract={'operations': ['create:task', 'create:evidence', 'create:action', 'execute'],
                      'scopes': ['REPORT'], 'tools': [OPERATION], 'share_with': [],
                      'profile': 'internal', 'expires_at': time.time() + 3600},
            expected_head=self.store.head(self.host)['hash'])
        self.credential = assigned['credential']
        self._put('REPORT', 'task', {'goal': 'Save a source-cited report',
                                   'criteria': ['readback matches report'],
                                   'state': 'open', 'acceptance': {}, 'review_budget': 1})
        initial = self._strict_answer()
        self._put('SOURCE', 'evidence', {'task': 'REPORT', 'corpus': 'demo',
                  'source_id': source_id, 'source_hash': self.source.hash_actual,
                  'quote': initial['claims'][0]['citations'][0]['quote'], 'query': field})

    def _put(self, key, kind, payload, dependencies=None):
        view = self.store.snapshot(self.credential)
        return self.store.put(self.credential, id=key, kind=kind, payload=payload,
                              dependencies=dependencies or {}, visibility=['reporter'],
                              expected_revision=0, expected_head=view['head'])

    def _strict_answer(self):
        contract = answer_query(self.corpus, f'What is the {self.field}?', profile=PROFILES['internal'],
                                record_id=self.source.id, field=self.field).contract
        if not contract['answer_supported'] or not contract['claims'] or any(
            not claim['citations'] or any(
                cite['source_id'] != self.source.id or cite['hash'] != self.source.hash_actual
                for cite in claim['citations'])
            for claim in contract['claims']
        ):
            raise Denied('Pinned source answer is unavailable')
        return contract

    def proposal(self, target):
        return {'operation': OPERATION, 'target': target, 'source_id': self.source.id,
                'source_hash': self.source.hash_actual, 'field': self.field}

    def _pin(self, proposal):
        if not isinstance(proposal, dict) or set(proposal) != {
            'operation', 'target', 'source_id', 'source_hash', 'field'
        }:
            raise Denied('invalid_proposal')
        target = proposal['target']
        if (not isinstance(target, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,39}\.json', target)
                or proposal != self.proposal(target)):
            raise Denied('operation_or_arguments_outside_policy')
        return digest({'policy': OPERATION, 'task_revision': 1,
                       'evidence_revision': 1, 'proposal': proposal})

    def approve(self, proposal):
        """Trusted host entry point. Keep approvals out of the proposal input."""
        self._strict_answer()
        self.approvals.add(self._pin(proposal))

    def submit(self, proposal):
        # Take a snapshot of untrusted input so the approved arguments are the
        # same ones handed to WorkStore, even if the caller retains its dict.
        if isinstance(proposal, dict):
            proposal = proposal.copy()
        try:
            pin = self._pin(proposal)
        except Denied as error:
            return {'status': 'denied', 'reason': str(error)}
        if pin not in self.approvals:
            return {'status': 'denied', 'reason': 'approval_required'}
        action = 'report:' + pin.split(':', 1)[1]
        try:
            view = self._put(action, 'action', {'task': 'REPORT', 'task_revision': 1,
                             'operation': OPERATION, 'arguments': proposal, 'side_effect': 'local',
                             'executor_seat': 'reporter', 'state': 'proposed',
                             'retry_of': {}, 'retry_reason': ''}, {'SOURCE': 1})
            receipt = self.store.execute(self.credential, id=action, expected_revision=1,
                                         expected_head=view['head'])['receipt']
        except Conflict:
            return {'status': 'denied', 'reason': 'duplicate_or_stale_proposal'}
        except Denied:
            return {'status': 'denied', 'reason': 'authority_or_evidence_unavailable'}
        result = {'status': receipt['status'], 'receipt_id': receipt['id']}
        if receipt['status'] == 'passed':
            path = self.output / proposal['target']
            try:
                report = path.read_text(encoding='utf-8')
            except (OSError, UnicodeError):
                report = None
            if (receipt['validation'].get('readback matches report') is not True
                    or report is None or digest(report) != receipt['artifact_hash']):
                return {**result, 'status': 'indeterminate'}
            result.update(status='verified', target=path.name, artifact_hash=receipt['artifact_hash'])
        return result

    def _write_report(self, request):
        proposal = request['action']['payload']['arguments']
        if self._pin(proposal) not in self.approvals:
            raise Denied('Approval unavailable at dispatch')
        contract = self._strict_answer()
        report = canonical({'claims': contract['claims'], 'historical_truth_verified': False,
                            'receipt_id': request['idempotency_key']}) + '\n'
        path = self.output / proposal['target']
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(report)
        if path.read_text(encoding='utf-8') != report:
            raise OSError('Report readback differs')
        return {'result': 'passed', 'validation': {'readback matches report': True}, 'artifact': report}


def demo(root):
    corpus = root / 'corpus'
    write(corpus, doc_id='DEMO-1', title='Museum register', scope='Public hours',
          body='Opening time: 09:00.')
    gate = CitedReportGate(root, corpus, 'DEMO-1', 'Opening time')
    proposal = gate.proposal('museum-hours.json')
    gate.approve(proposal)
    result = gate.submit(proposal)
    print(json.dumps(result, indent=2))
    return result['status'] == 'verified'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True)
    return 0 if demo(args.output) else 1


if __name__ == '__main__':
    raise SystemExit(main())
