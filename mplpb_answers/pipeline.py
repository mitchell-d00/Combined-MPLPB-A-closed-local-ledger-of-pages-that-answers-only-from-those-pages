"""One response policy for strict compatibility and opt-in model-assisted reading."""
import copy
import re
from pathlib import Path
from .body_text import body_text
from dataclasses import dataclass, field
from mplpb_combined.reader import PROFILES, DEFAULT_PROFILE
from .support import supported_answer, code_pins
from .frames import parse
from . import literal_evidence, practical_evidence, policy_evidence, operational_evidence, relation_graph, procedures
from .evidence_contract import (VERSION, ReaderError, pin, canonical, shape, text,
                                validate_proposal, validate_review, PROPOSAL_SCHEMA, REVIEW_SCHEMA, PLAN_SCHEMA)
from .passages import PassageIndex
from mplpb_combined import provenance_gate as G

DIAGNOSTICS = {
    'exact_field_missing': 'Inspect the exact record and supply an explicit source body field; an identifier alone is not field support.',
    'contradictory_passages_pruned': 'Increase the evidence budget to display all competing passages; no selected subset licenses an answer.',
    'event_identity_unresolved': 'Supply an explicit source-declared event or occurrence key; similar subjects do not establish identity.',
    'correction_scope_unclear': 'Name the corrected field and, when needed, an ISO as-of time.',
    'stacked_field_paragraph': 'Revise the page so each "Field: value" line is its own paragraph (blank line between); mplpb_work.classing does this.',
}


# Additive categories preserve the detailed legacy codes and answer contract.
def refusal_category(code, kind):
    if code == 'source_changed':
        return 'source_state_changed'
    if code in {'contradictory_passages_pruned', 'conflicting_or_multiple_owners', 'conflicting_field_values', 'documentary_statement_conflict'}:
        return 'known_source_conflict'
    if 'budget' in code or code in {'index_exhausted', 'context_exhausted'}:
        return 'index_exhaustion'
    if code in {'no_eligible_sources', 'restricted_or_unavailable'}:
        return 'absent_eligible_source'
    if code == 'interpretation_unsupported':
        return 'unsupported_question_grammar'
    if code in {'retrieval_ambiguous', 'event_identity_unresolved', 'needs_clarification', 'correction_scope_unclear', 'documentary_scope_ambiguous', 'field_alias_ambiguous'}:
        return 'clarification_required'
    if kind == 'supported_answer':
        return 'source_support_established'
    if code == 'reader_reported_conflict':
        return 'unverified_reported_conflict'
    if code == 'reader_unavailable' or code.startswith('model_') or code.startswith('reader_'):
        return 'reader_unavailable_or_failed'
    return 'insufficient_evidence'


SOURCE_NOTICE = ('Source support establishes what eligible ledger pages state. '
                 'Outside-world confirmation is required before treating those statements as historical truth. '
                 'MPLPB cannot detect a coherent false original without contrary evidence, authenticate arbitrary testimony, '
                 'or establish general historical reconstruction from source integrity alone.')


def source_assurance(contract, gate):
    """Inspection of fresh declared lineage, never an independence/truth test.

    Count only output sources, not unrelated eligible pages. Unknown roots remain
    unknown. Even distinct declared roots do not establish independent witnesses.
    """
    pins = {(s['id'], s['hash']) for s in contract['sources']}
    sources = [s for s in gate.get('sources', []) if (s['id'], s['hash']) in pins]
    roots = set()
    for source in sources:
        for node in [source] + source.get('ancestry', []):
            if not node.get('derived_from') and not node.get('supersedes'):
                roots.add((node['id'], node['hash']))
    complete = bool(pins) and len(sources) == len(pins) and bool(roots)
    count = len(roots) if complete else None
    return {'basis': 'source_attributed_only',
            'outside_world_confirmation_required': True,
            'outside_world_truth': 'not_established',
            'authorship_authenticated': False, 'independence_verified': False,
            'declared_evidence_root_count': count,
            'single_declared_root': count == 1 if count is not None else None,
            'notice': SOURCE_NOTICE}


def _state(gate):
    return pin({'snapshot': gate.corpus_snapshot, 'policy': gate.policy,
                'sources': [(s['id'], s['hash']) for s in gate.sources], 'excluded': gate.excluded})


def _next_steps(code):
    if code in DIAGNOSTICS:
        return [DIAGNOSTICS[code]]
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
        if self.contract['kind']=='supported_answer' and self.strict.kind!='return':
            data.update(kind='return',text=self.contract['text'],reason=self.contract['diagnostic']['message'],
                        citation='; '.join(s['id']+'@'+s['hash'] for s in self.contract['sources']),candidates=[])
        if self.contract['kind'] != 'supported_answer' and (self.contract['mode'] == 'assisted' or self.strict.kind == 'return'):
            data.update(kind=self.contract['kind'] if self.contract['mode'] == 'assisted' else 'not_in_corpus', text=self.contract['text'],
                        reason=self.contract['diagnostic']['message'], citation='', candidates=[])
        if self.contract['diagnostic'].get('code') in {'partial_procedure_evidence', 'procedure_selection_needed', 'partial_documentary_evidence'}:
            data.update(text=self.contract['text'], reason=self.contract['diagnostic']['message'])
        return data


def _known_grammar(question):
    return any((procedures.request(question), literal_evidence.parse(question), practical_evidence.parse(question), policy_evidence.parse(question), operational_evidence.parse(question), relation_graph.parse(question), parse(question)))


def answer_query(root, question, profile=None, *, mode='strict', reader=None, min_confidence=0.8,
                 max_passages=12, max_chars=8000, record_id=None, field=None, exact_value=None,
                 as_of=None, relation_hops=None, source_hints=None):
    if not isinstance(question,str) or not question.strip() or len(question)>4000:
        raise ValueError('Question must contain 1–4000 characters')
    if type(max_passages) is not int or not 1<=max_passages<=64 or type(max_chars) is not int or not 1000<=max_chars<=64000:
        raise ValueError('Invalid passage admission budget')
    from mplpb_combined.ledger import serving_view
    request = relation_graph.exact_request(question,record_id,field,exact_value)
    if field is None and exact_value is None:
        from .field_aliases import resolve
        request = resolve(root,question,profile,request,as_of)
    from .passage_admission import source_suggestions
    with serving_view(as_of,request['field']),source_suggestions(source_hints):
        return _answer_query(root,question,profile,mode=mode,reader=reader,min_confidence=min_confidence,
                             max_passages=max_passages,max_chars=max_chars,exact=request,relation_hops=relation_hops)


def _answer_query(root, question, profile=None, *, mode, reader, min_confidence,
                  max_passages, max_chars, exact, relation_hops):
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
    if 'question_normalization' in exact:
        contract['question_normalization'] = copy.deepcopy(exact['question_normalization'])

    def finish(kind, code, message, stage):
        try:
            fresh = G.gather(root, question, profile)
            unchanged = _state(fresh) == initial_state and Path(strict.root).resolve() == initial_gate_root
            if unchanged and exact.get('alias_resolution'):
                from .field_aliases import unchanged as aliases_unchanged
                unchanged = aliases_unchanged(root,question,profile,exact['alias_resolution'])
        except (OSError, ValueError):
            unchanged = False
        if not unchanged or code == 'source_changed':
            kind, code, stage = 'abstain', 'source_changed', 'state_recheck'
            message = 'Source eligibility or serving policy changed during this query; no old evidence was accepted. Ask again against current sources.'
            contract.update(text='', claims=[], sources=[], missing=[], clarification='',
                            retrieval={'passages': [], 'sources': [], 'discarded': 'source_state_changed'},
                            verification={'structural': False, 'semantic': 'discarded_due_to_source_change', 'truth_verified': False, 'independence_verified': False})
            if exact.get('alias_resolution'):
                contract['question_normalization'] = {'version':'source-field-alias-v1',
                    'status':'discarded_due_to_source_change','normalization_is_evidence':False}
            strict.kind, strict.record, strict.candidates = 'not_in_corpus', None, []
            strict.support = {'status': 'unsupported', 'spans': [], 'reason': message}
            result.gate = {'sources': [], 'excluded': [], 'corpus_snapshot': '', 'notice': message}
            if 'exploration' in contract:
                contract['exploration']={'status':'source_changed','edges':[],'answer_supported':False,'content_truth_verified':False}
            if 'documentary_support' in contract:
                contract['documentary_support']={'status':'discarded_due_to_source_change','source_support_claims':0}
        else:
            result.gate = fresh.to_dict()
            from .passage_admission import output_budget
            if output_budget(contract,max_passages,max_chars):
                kind='conflict' if kind=='conflict' else 'partial_answer' if contract['claims'] else 'abstain'
                code='contradictory_passages_pruned' if kind=='conflict' else 'reader_budget_exceeded'
                stage='passage_admission'
                message='Required source witnesses do not fit the unchanged passage budget; completion was withheld.'
        if kind != 'supported_answer':
            contract['answer_supported'] = False
        if (mode=='assisted' and kind=='supported_answer'
                and contract['verification']['semantic']=='bounded_deterministic_grammar'):
            # Preserve the existing strict-first path without labelling its
            # deterministic source proof as assisted output.
            contract['mode']='strict'
        if contract['mode']=='assisted' or relation_hops is not None:
            contract['answer_supported']=False
            if kind=='supported_answer':
                kind='model_assisted_answer' if mode=='assisted' else 'partial_answer'
                code='candidate_source_evidence'
                message='Bounded source evidence is retained for inspection; this optional mode does not promote candidates to supported answers.'
        category = refusal_category(code, kind)
        if code == 'exact_field_missing' and contract['retrieval'].get('eligible_pages') == 0:
            category = 'absent_eligible_source'
        contract.update(kind=kind, diagnostic={'code': code, 'stage': stage, 'message': message,
                                             'category': category,
                                             'corpus_answerability': 'not_established', 'next_steps': _next_steps(code)})
        contract['source_assurance'] = source_assurance(contract, result.gate)
        return result

    initial_gate_root = Path(root).resolve()
    if exact.get('alias_resolution',{}).get('status') in {'blocked','ambiguous'}:
        resolution = exact['alias_resolution']
        code = resolution['code']
        if resolution['status']=='ambiguous':
            contract['clarification'] = 'More than one eligible source field matches this expression. Specify the literal field label.'
            contract['question_normalization'] = {'version':'source-field-alias-v1',
                'status':'ambiguous','requested_field':resolution['requested_field'],
                'candidate_fields':resolution.get('candidate_fields',[]),'normalization_is_evidence':False}
        return finish('clarify' if resolution['status']=='ambiguous' else 'abstain',code,
                      'Source-field normalization is unresolved; no alias proposal establishes support.','field_normalization')

    if (strict.kind!='return' and not exact['field']
            and any(s['reason']=='correction scope unclear' for s in initial_gate.excluded)):
        return finish('abstain','correction_scope_unclear','Name the field before using a field-scoped correction.','interpretation')

    if relation_hops is not None:
        contract['exploration'] = relation_graph.explore(root,question,relation_hops,profile)
    # Exact routes are established only after the ordinary full eligibility gate.
    index = None
    exact_requested = bool(exact['record_id'] or exact['field'] or exact['exact_value']
        or re.search(r'\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b',question) or any(
        re.search(r'(?<![\w-])'+re.escape(source['id'])+r'(?![\w-])',question) for source in initial_gate.sources))
    if exact_requested:
        try:
            index = PassageIndex(strict.root,question,profile,exact=exact)
        except ReaderError as exc:
            return finish('abstain',exc.code,str(exc),'eligibility')
        if exact['field'] and not index.exact_status:
            return finish('clarify','needs_clarification','Supply a record identifier or a unique source field/value selector.','retrieval')
        if index.exact_status:
            pack=index.retrieve([question],max_passages,max_chars)
            contract.update(retrieval=pack,sources=copy.deepcopy(pack['sources']))
            if index.exact_status=='ambiguous_value':
                return finish('clarify','retrieval_ambiguous','The supplied field value is not unique among eligible pages.','retrieval')
            if not index.exact_paths:
                return finish('abstain','event_identity_unresolved' if exact['field'] in {'event id','occurrence id'} else 'exact_field_missing',
                              'No unique eligible exact route supplies the requested field.','retrieval')
            if exact['field']:
                rows=[f for r in index.records if r.path in index.exact_paths
                      for f in relation_graph.declared_fields(r) if f['field']==exact['field']]
                if not rows:
                    return finish('abstain','exact_field_missing','The exact eligible record has no explicit body evidence for the requested field.','strict')
                if any(r.get('stacked_field_suspected') for r in rows):
                    contract['claims']=[{'text':r['quote'],'qualifiers':['Field value boundary unknown; not accepted as support.'],'citations':[r]} for r in rows[:max_passages]]
                    return finish('abstain','stacked_field_paragraph',
                                  'The field shares one paragraph with other "Label: value" lines, so its value boundary is unknown. Put each field in its own paragraph.','strict')
                contexts=[f for r in index.records if r.path in index.exact_paths
                          for f in relation_graph.field_contexts(r,exact['field'])]
                rows+=contexts
                values={r['value'] for r in rows}
                conflict=len(values)>1
                # Never erase a competing field with a ranking or page-diversity discount.
                shown=[];size=0
                for row in rows:
                    if len(shown)>=max_passages or size+len(row['quote'])>max_chars:continue
                    shown.append(row);size+=len(row['quote'])
                contract['claims']=[{'text':r['quote'],'qualifiers':['Source-declared field; source truth is unverified.'],'citations':[r]} for r in shown]
                contract['retrieval'].update(field_passages=shown,omitted_field_passages=len(rows)-len(shown))
                if len(shown)!=len(rows):
                    return finish('conflict' if conflict else 'abstain','contradictory_passages_pruned' if conflict else 'retrieval_budget_exceeded',
                                  'The budget cannot display all matching field passages; no selection is accepted as support.','retrieval')
                if conflict:
                    return finish('conflict','conflicting_or_multiple_owners','All competing eligible field passages remain visible.','strict')
                if contexts:
                    return finish('abstain','unresolved_evidence','Additional field mentions outside the declared header require source-context review.','strict')
                contract.update(text='\n'.join(dict.fromkeys(r['quote'] for r in rows)),answer_supported=mode=='strict')
                contract['verification'].update(structural=True,semantic='bounded_explicit_field')
                return finish('supported_answer' if mode=='strict' else 'model_assisted_answer',
                              'supported' if mode=='strict' else 'candidate_source_evidence','Exact source body field evidence; no inference from record identity.','strict')
            if strict.kind!='return' or strict.record.path not in index.exact_paths:
                return finish('abstain','exact_field_missing','The exact route does not establish the requested field under a bounded grammar.','strict')

    procedure = strict.support.get('procedure', {})
    if procedure.get('clarification'):
        contract['clarification'] = procedure['clarification']
        contract['text'] = procedure['clarification']
        return finish('clarify', 'procedure_selection_needed', procedure['clarification'], 'interpretation')
    if procedure.get('partial'):
        from mplpb_combined.ledger import Ledger
        records = {r.path:r for r in Ledger(strict.root).servable()}
        allowed = {s['path'] for s in initial_gate.sources}
        citations = []
        for source in procedure['partial_sources']:
            rec = records.get(source['path'])
            if not rec or rec.path not in allowed or rec.hash != source['hash']:
                return finish('abstain', 'source_changed', 'Partial procedure evidence is unavailable.', 'eligibility')
            body = body_text(rec.body_html)
            start = body.find(source['quote'])
            if start < 0:
                return finish('abstain', 'invalid_citation', 'Partial procedure excerpt cannot be located.', 'strict')
            citations.append(dict(source_id=rec.id,path=rec.path,hash=rec.hash,quote=source['quote'],
                                  start=start,end=start+len(source['quote']),body_start=start,body_end=start+len(source['quote'])))
        contract.update(text=procedures.render_partial(procedure), missing=procedure['gaps'],
                        claims=[{'text':s['quote'],'qualifiers':['Incomplete source procedure; not ready-to-execute guidance.'],
                                 'citations':[citation]} for s,citation in zip(procedure['partial_sources'],citations)],
                        sources=[{k:s[k] for k in ('id','path','hash')} for s in procedure['partial_sources']])
        contract['verification'].update(structural=True, semantic='bounded_source_excerpt_not_complete_procedure')
        return finish('partial_answer', 'partial_procedure_evidence',
                      'Source procedure evidence is incomplete; missing constraints are listed explicitly.', 'strict')
    if strict.kind == 'return' and strict.record.fields.get('corrects-field') and not exact['field']:
        return finish('abstain','correction_scope_unclear','Name the explicit field before applying a field-scoped correction.','interpretation')
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
        index = PassageIndex(strict.root, question, profile, exact=exact)
        result.gate = index.gate.to_dict()
        # Strict abstentions do not pay for model ranking or expose unrelated
        # passage bodies. Build the bounded retrieval pack only on explicit opt-in.
        contract['retrieval'] = {'eligible_pages': len(index.sources), 'total_passages': len(index.passages),
                                 'passages': [], 'sources': [], 'search_complete': False,
                                 'corpus_snapshot': index.gate.corpus_snapshot, 'ranking': 'not_run'}
        if not index.sources:
            code = 'restricted_or_unavailable' if index.gate.excluded else 'no_eligible_sources'
            return finish('abstain', code, 'No eligible body passages are available under this question and profile; corpus absence is not established.', 'eligibility')
        if any(r.fields.get('corrects-field') and r.path in {s['path'] for s in index.gate.sources} for r in index.records) and not exact['field']:
            return finish('abstain','correction_scope_unclear','Name the explicit field before applying a field-scoped correction.','interpretation')
        if re.search(r'\b(?:same event|event identity|same occurrence)\b',question,re.I):
            return finish('abstain','event_identity_unresolved','No explicit source key establishes the requested event identity.','interpretation')
        if mode == 'strict':
            from .documentary import compose
            stage='documentary_verification'
            documentary=compose(index,max_passages,max_chars)
            if documentary is not None:
                kind=documentary.pop('kind');code=documentary.pop('code')
                contract.update(documentary)
                if kind=='clarify':contract['clarification']='Specify the intended documentary appearance, actor or temporal scope.'
                return finish(kind,code,
                    'Checked source-attributed assertions only; unresolved question obligations remain explicit and historical truth is unverified.',stage)
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
