"""One response policy for strict compatibility and opt-in model-assisted reading."""
import copy
from pathlib import Path
from .body_text import body_text
from dataclasses import dataclass, field
from mplpb_combined.reader import PROFILES, DEFAULT_PROFILE
from .support import supported_answer, code_pins
from .frames import parse
from . import literal_evidence, practical_evidence, policy_evidence, procedures
from .evidence_contract import (VERSION, ReaderError, pin, canonical, shape, text,
                                validate_proposal, validate_review, PROPOSAL_SCHEMA, REVIEW_SCHEMA, PLAN_SCHEMA)
from .passages import PassageIndex
from mplpb_combined import provenance_gate as G


def _state(gate):
    return pin({'snapshot': gate.corpus_snapshot, 'policy': gate.policy,
                'sources': [(s['id'], s['hash']) for s in gate.sources], 'excluded': gate.excluded})


def _next_steps(code):
    if code in {'supported', 'model_assessed', 'partial_model_assessed'}:
        return ['Open the cited source and check its conditions and revision.']
    if 'conflict' in code or code == 'retrieval_ambiguous':
        return ['Inspect the competing sources; specify the intended subject or resolve the disagreement by a source revision.']
    if code in {'restricted_or_unavailable', 'source_changed'}:
        return ['Check source integrity and delivery restrictions; restore or revise the source through the normal workflow, then ask again.']
    if code == 'no_eligible_sources':
        return ['Import relevant source material or check the selected collection. No acquisition was started.']
    if code in {'interpretation_unsupported', 'unresolved_evidence', 'evidence_not_established'}:
        return ['Inspect the relevant source. Try a supported question form or explicitly select a configured assisted reader; do not treat this refusal as proof that the answer is absent.']
    if code == 'reader_unavailable':
        return ['Ask the native host operator to configure an installed local reader, or continue with strict source inspection.']
    return ['Review the diagnostic and source evidence before retrying.']


@dataclass
class QueryResult:
    contract: dict
    strict: object
    gate: dict = field(default_factory=dict)

    def legacy(self):
        """Preserve strict legacy kinds; model-assisted claims never become return."""
        data = self.strict.to_dict()
        data['answer_contract'] = copy.deepcopy(self.contract)
        data['answer_diagnostics'] = copy.deepcopy(self.contract['diagnostic'])
        data['answer_supported'] = self.contract['answer_supported']
        if self.contract['kind'] != 'supported_answer' and (self.contract['mode'] == 'assisted' or self.strict.kind == 'return'):
            data.update(kind=self.contract['kind'] if self.contract['mode'] == 'assisted' else 'not_in_corpus', text=self.contract['text'],
                        reason=self.contract['diagnostic']['message'], citation='', candidates=[])
        return data


def _known_grammar(question):
    return any((procedures.request(question), literal_evidence.parse(question), practical_evidence.parse(question), policy_evidence.parse(question), parse(question)))


def answer_query(root, question, profile=None, *, mode='strict', reader=None, min_confidence=0.8,
                 max_passages=12, max_chars=8000):
    if not isinstance(question, str) or not question.strip() or len(question) > 4000:
        raise ValueError('Question must contain 1–4000 characters')
    if mode not in {'strict', 'assisted'}:
        raise ValueError('Unknown answer mode')
    if type(min_confidence) not in (int, float) or not 0 <= min_confidence <= 1:
        raise ValueError('Confidence threshold must be between zero and one')
    if (type(max_passages) is not int or not 1 <= max_passages <= 64
            or type(max_chars) is not int or not 1000 <= max_chars <= 64000):
        raise ValueError('Invalid retrieval budget')
    profile = profile or PROFILES[DEFAULT_PROFILE]
    initial_gate = G.gather(root, question, profile)
    initial_state = _state(initial_gate)
    strict = supported_answer(root, question, profile)
    contract = {'schema': VERSION, 'mode': mode, 'question': question, 'kind': 'abstain',
                'answer_supported': False, 'text': '', 'claims': [], 'missing': [], 'clarification': '',
                'confidence': None, 'confidence_calibrated': False, 'sources': [], 'retrieval': {},
                'verification': {'structural': False, 'semantic': 'not_run', 'truth_verified': False, 'independence_verified': False},
                'reader': None, 'trace': [], 'diagnostic': {}, 'code_sha256': code_pins()}
    result = QueryResult(contract, strict, initial_gate.to_dict())

    def finish(kind, code, message, stage):
        try:
            fresh = G.gather(root, question, profile)
            unchanged = _state(fresh) == initial_state and Path(strict.root).resolve() == initial_gate_root
        except (OSError, ValueError):
            unchanged = False
        if not unchanged or code == 'source_changed':
            kind, code, stage = 'abstain', 'source_changed', 'state_recheck'
            message = 'Source eligibility or serving policy changed during this query; no old evidence was accepted. Ask again against current sources.'
            contract.update(text='', claims=[], sources=[], missing=[], clarification='',
                            retrieval={'passages': [], 'sources': [], 'discarded': 'source_state_changed'},
                            verification={'structural': False, 'semantic': 'discarded_due_to_source_change', 'truth_verified': False, 'independence_verified': False})
            strict.kind, strict.record, strict.candidates = 'not_in_corpus', None, []
            strict.support = {'status': 'unsupported', 'spans': [], 'reason': message}
            result.gate = {'sources': [], 'excluded': [], 'corpus_snapshot': '', 'notice': message}
        else:
            result.gate = fresh.to_dict()
        contract.update(kind=kind, diagnostic={'code': code, 'stage': stage, 'message': message,
                                             'corpus_answerability': 'not_established', 'next_steps': _next_steps(code)})
        return result

    initial_gate_root = Path(root).resolve()

    if strict.kind == 'return':
        body = body_text(strict.record.body_html)
        quotes = [span['quote'] for span in strict.support.get('spans', [])]
        if not quotes and strict.support.get('procedure', {}).get('steps'):
            quotes = list(dict.fromkeys(step['source']['quote'] for step in strict.support['procedure']['steps']))
        citations = []
        for quote in quotes:
            begin = body.find(quote)
            if begin < 0:
                return finish('abstain', 'invalid_citation', 'The bounded reader span could not be located in the canonical source body.', 'strict')
            citations.append({'passage': pin({'source': strict.record.path, 'hash': strict.record.hash_actual, 'start': 0, 'text': body}),
                              'start': begin, 'end': begin+len(quote), 'quote': quote,
                              'source_id': strict.record.id, 'path': strict.record.path, 'hash': strict.record.hash_actual,
                              'body_start': begin, 'body_end': begin+len(quote)})
        if not citations:
            return finish('abstain', 'missing_evidence', 'The bounded reader did not provide a source evidence span.', 'strict')
        contract.update(answer_supported=True, text=strict.text,
                        claims=[{'text': strict.text, 'qualifiers': [], 'citations': citations}])
        contract['sources'] = [{'id': strict.record.id, 'path': strict.record.path, 'hash': strict.record.hash_actual}]
        contract['verification'].update(structural=True, semantic='bounded_deterministic_grammar')
        return finish('supported_answer', 'supported', 'Explicit source statements satisfy the existing bounded grammar.', 'strict')
    if strict.kind == 'ambiguous' and strict.support.get('status') == 'conflict':
        return finish('conflict', 'conflicting_or_multiple_owners', strict.reason, 'strict')
    stage = 'eligibility'
    try:
        index = PassageIndex(strict.root, question, profile)
        result.gate = index.gate.to_dict()
        # Strict abstentions do not pay for model ranking or expose unrelated
        # passage bodies. Build the bounded retrieval pack only on explicit opt-in.
        contract['retrieval'] = {'eligible_pages': len(index.sources), 'total_passages': len(index.passages),
                                 'passages': [], 'sources': [], 'search_complete': False,
                                 'corpus_snapshot': index.gate.corpus_snapshot, 'ranking': 'not_run'}
        if not index.sources:
            code = 'restricted_or_unavailable' if index.gate.excluded else 'no_eligible_sources'
            return finish('abstain', code, 'No eligible body passages are available under this question and profile; corpus absence is not established.', 'eligibility')
        if mode == 'strict':
            if strict.kind == 'ambiguous':
                return finish('conflict', 'retrieval_ambiguous', 'Candidate ownership is ambiguous; this does not establish conflicting body evidence.', 'retrieval')
            code = 'unresolved_evidence' if strict.support.get('unresolved') else 'evidence_not_established' if _known_grammar(question) else 'interpretation_unsupported'
            return finish('abstain', code, 'Eligible passages exist, but the strict reader cannot establish an answer to this question.', 'strict')
        if reader is None:
            return finish('abstain', 'reader_unavailable', 'Assisted mode needs an explicitly configured local reader. No model request was made.', 'reader')
        stage = 'reader_setup'
        identity = reader.describe()
        contract['reader'] = copy.deepcopy(identity)

        def invoke(task, payload, schema):
            nonlocal stage
            stage = task
            contract['trace'].append({'stage': task, 'request_sha256': pin(payload)})
            response = reader.complete(task, copy.deepcopy(payload), copy.deepcopy(schema))
            if len(canonical(response)) > 100000:
                raise ReaderError('reader_budget_exceeded', 'Structured reader response exceeds the contract budget')
            contract['trace'][-1]['response_sha256'] = pin(response)
            return response

        plan = invoke('plan', {'question': question}, PLAN_SCHEMA)
        shape(plan, 'question queries')
        if plan['question'] != question or not isinstance(plan['queries'], list) or len(plan['queries']) > 3:
            raise ReaderError('question_changed', 'Retrieval plan must retain the original question')
        for q in plan['queries']:
            text(q, 200)
        pack = index.retrieve([question]+plan['queries'], max_passages, max_chars)
        contract['retrieval'], contract['sources'] = pack, copy.deepcopy(pack['sources'])
        if not pack['passages']:
            return finish('abstain', 'retrieval_budget_exceeded', 'No complete passage fits the configured retrieval budget.', 'retrieval')
        if not index.unchanged():
            raise ReaderError('source_changed', 'Corpus eligibility changed before model dispatch')
        proposal = invoke('read', {'question': question, 'passages': pack['passages'],
                                  'sources': pack['sources'], 'search_complete': pack['search_complete']}, PROPOSAL_SCHEMA)
        stage = 'evidence_validation'
        claims = validate_proposal(proposal, question, pack['passages'])
        if not index.unchanged():
            raise ReaderError('source_changed', 'Corpus state changed during reading; rerun against current evidence')
        contract['verification']['structural'] = True
        if proposal['outcome'] in {'clarify', 'abstain'}:
            if pin(reader.describe()) != pin(identity):
                raise ReaderError('model_changed', 'Reader weights changed during the query')
            contract.update(missing=proposal['missing'], clarification=proposal['clarification'])
            return finish('clarify' if proposal['outcome'] == 'clarify' else 'abstain',
                          'needs_clarification' if proposal['outcome'] == 'clarify' else 'evidence_not_established',
                          proposal['clarification'] or 'The local reader did not find a supported interpretation in the supplied passages.', 'reader')
        review = invoke('review', {'question': question, 'claims': proposal['claims'], 'passages': pack['passages'],
                                  'sources': pack['sources'], 'requested_outcome': proposal['outcome'], 'missing': proposal['missing'],
                                  'search_complete': pack['search_complete']}, REVIEW_SCHEMA)
        stage = 'verification'
        checks = validate_review(review, question, claims)
        contract['verification'].update(semantic='model_assessed_not_proved', checks=checks)
        if not index.unchanged():
            raise ReaderError('source_changed', 'Corpus state changed during verification; no answer was accepted')
        if pin(reader.describe()) != pin(identity):
            raise ReaderError('model_changed', 'Reader weights changed during the query')
        contract['confidence'] = min(proposal['confidence'], review['confidence'])
        if proposal['outcome'] == 'conflict' or review['verdict'] == 'conflict':
            contract['claims'] = claims
            return finish('conflict', 'reader_reported_conflict', 'The local reader reports competing evidence; inspect the exact cited passages.', 'review')
        if review['verdict'] == 'clarify':
            contract.update(missing=review['missing'], clarification='Clarify the unresolved subject, conditions or requested scope before answering.')
            return finish('clarify', 'needs_clarification', contract['clarification'], 'review')
        if contract['confidence'] < min_confidence:
            return finish('abstain', 'below_assisted_threshold', 'Model-assessed confidence is below the configured threshold; this score is not calibrated.', 'review')
        if review['verdict'] == 'reject':
            return finish('abstain', 'verification_failed', 'The separate review did not accept the proposed answer.', 'review')
        accepted = [claim for claim, check in zip(claims, checks) if all(check[k] for k in ('supported', 'subject_matches', 'relation_matches', 'constraints_preserved'))]
        if not accepted:
            return finish('abstain', 'verification_failed', 'No claim passed subject, relation, qualification and source-support review.', 'review')
        missing = list(dict.fromkeys(proposal['missing']+review['missing']))
        truncated = {p['id'] for p in pack['passages'] if p['context_truncated']}
        if any(cite['passage'] in truncated for claim in accepted for cite in claim['citations']):
            missing.append('A cited paragraph exceeds the supplied context window; inspect its complete conditions in the source.')
        partial = proposal['outcome'] == 'partial' or not review['complete'] or len(accepted) != len(claims) or bool(missing)
        if partial and not missing:
            raise ReaderError('invalid_review', 'An incomplete answer must identify what remains unresolved')
        contract.update(claims=accepted, missing=missing)
        rendered = []
        for claim in accepted:
            rendered.append(claim['text'])
            if claim['qualifiers']:
                rendered.append('Conditions: '+'; '.join(claim['qualifiers']))
        contract['text'] = '\n'.join(rendered)
        return finish('partial_answer' if partial else 'model_assisted_answer',
                      'partial_model_assessed' if partial else 'model_assessed',
                      'Exact citations and a separate model review passed. Semantic support is model-assessed; this is not a deterministic supported-answer guarantee.', 'review')
    except ReaderError as exc:
        contract.update(text='', claims=[], missing=[], clarification='')
        if exc.code == 'source_changed':
            # A source/profile may have become restricted while the model ran.
            # Do not leak its old body or model review text through diagnostics.
            contract['sources'] = []
            contract['retrieval'] = {'passages': [], 'sources': [], 'search_complete': False, 'discarded': 'source_state_changed'}
            contract['verification'] = {'structural': False, 'semantic': 'discarded_due_to_source_change', 'truth_verified': False, 'independence_verified': False}
        return finish('abstain', exc.code, str(exc), stage)
