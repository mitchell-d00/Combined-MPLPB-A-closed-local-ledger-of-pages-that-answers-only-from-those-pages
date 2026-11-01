"""Finite, conservative statement support. Not general entailment or truth checking.

Scope/title metadata never supplies an answer. Unsupported grammar abstains.
"""
import re
from mplpb_combined.record import text_of

VERSION = 'statement-support-v4'


from .frames import normalize, parse


def statement_support(question, record):
    frame = parse(question)
    if frame is None:
        return {'status':'unsupported','reason':'Question is outside the supported statement grammar.','spans':[]}
    subject = frame.entity if frame.relation == 'description' else ''
    patterns = [frame.statement]
    negative = False
    spans=[]
    # Only body sentences, never declared scope or when-to-use. Whole sentence
    # matches reject quoted instructions, hypothetical prefixes and other subjects.
    body=re.sub(r'<h[1-6]\b[^>]*>.*?</h[1-6]>','\n',record.body_html,flags=re.I|re.S)
    if re.search(r'(?:^|[.!?]\s+|\n)(?:imagine|suppose|assume|pretend|ignore)\b',
                 text_of(body), re.I):
        return {'status': 'unsupported', 'spans': [],
                'reason': 'Instructional or hypothetical source context is not factual evidence.'}
    for sentence in re.split(r'(?<=[.!?])\s+|\n+',text_of(body)):
        raw=sentence.strip();line=normalize(raw)
        if re.match(r'^(?:say|write|claim|imagine|suppose|assume|pretend|if|perhaps|possibly|maybe)\b', line):
            continue
        if frame.negative_statement and re.fullmatch(frame.negative_statement,line):
            negative = True
            continue
        fact=re.fullmatch(r'fact: (.+?) \| (instance_of|subclass_of) \| (.+)',line)
        if fact and subject and fact[1]==subject:
            spans.append({'quote':raw,'value':fact[3]})
        for pattern in patterns:
            m=re.fullmatch(pattern,line)
            if not m:continue
            value=m['value']
            if frame.relation in {'owner','chosen_colour'} and (re.search(r'[,;\d]|\b(?:says|said|believes|claims|formerly|currently|previously|now|then)\b', value) or len(value.split())>6):
                continue
            if re.search(r'\bnot\b',value):negative=True
            if frame.relation == 'socket' or re.search(r'\b(?:port|socket)$',subject):
                if not re.fullmatch(r'\d{1,5}',value) or not 0<int(value)<65536:continue
            if re.search(r'\b(not|unknown|unrecorded|unspecified|unavailable|missing|maybe|perhaps|possibly|probably|apparently|reportedly|allegedly|likely|may|if|unless|might|could|should|would|either|or)\b',value):continue
            # Avoid presenting a future/conditional statement as an unconditional fact.
            if any(c in value for c in ['"','“','”',';']):continue
            spans.append({'quote':raw,'value':value})
    values={s['value'] for s in spans}
    if len(values)>1 or (spans and negative):return {'status':'conflict','reason':'Conflicting matching statements in the candidate page.','spans':spans,'frame':frame.to_dict()}
    if not spans:return {'status':'unsupported','reason':'No affirmative statement answers the complete requested subject.','spans':[],'negative_match':negative}
    return {'status':'supported','reason':'Exact affirmative statement under a finite grammar; source truth is not verified.','spans':spans,'frame':frame.to_dict()}


from dataclasses import dataclass, field
from mplpb_combined.reader import Answer, RETURN

@dataclass
class SupportedAnswer(Answer):
    support: dict = field(default_factory=dict)

    @property
    def text(self):
        if self.kind != RETURN or not self.record:return ''
        if self.support.get('procedure'):
            from .procedures import render
            return render(self.support['procedure'])
        if self.support.get('status')=='supported':
            return '\n'.join(s['quote'] for s in self.support['spans'])
        return ''

    def to_dict(self):
        result=super().to_dict();result['answer_support']=dict(self.support, code_sha256=code_pins())
        return result

def supported_answer(root, question, profile=None):
    """Body support across eligible lexical candidates; never answer from scope.

    The pinned legacy reader remains available for reproducing retrieval results.
    Pointer routing is retained only after it resolves to one corpus. No facts
    are combined across pages and no ambiguous hub route is silently resolved.
    """
    from mplpb_combined.reader import answer, RETURN, AMBIGUOUS, NOT_IN_CORPUS
    from mplpb_combined.provenance_gate import gather
    from mplpb_combined.ledger import Ledger
    from . import procedures
    procedural = procedures.request(question)
    if procedural:
        selected = answer(root, question, profile)
        out = SupportedAnswer(**selected.__dict__)
        checked, rec = procedures.check(out.root, procedural, out.profile)
        out.record = rec
        out.kind = RETURN if rec else AMBIGUOUS if checked['status']=='conflict' else NOT_IN_CORPUS
        out.support = {'status':checked['status'],'version':VERSION,'spans':[], 'procedure':checked}
        out.reason = 'Source-authored procedure constraints; execution is not verified.' if rec else ' '.join(checked['gaps'])
        out.matched_on = 'body procedure constraints' if rec else ''
        if rec: out.depth = Ledger(out.root).depth(rec)
        return out
    # The literal extension is a separate, conservative grammar. It may only
    # return directly evidenced sentences from eligible pages, never metadata.
    from . import literal_evidence as LE
    literal = LE.parse(question)
    practical = False
    if literal is None:
        from . import practical_evidence as PE
        literal = PE.parse(question)
        if literal is not None:
            LE = PE
            practical = True
    if literal is None:
        from . import policy_evidence as PO
        literal = PO.parse(question)
        if literal is not None:
            LE = PO
            practical = True  # Gate the complete original question and exclusions.
    if literal is None:
        from . import operational_evidence as OP
        literal = OP.parse(question)
        if literal is not None:
            LE = OP
            practical = True  # Full question remains authoritative for exclusions.
    if literal:
        selected = answer(root, question, profile)
        out = SupportedAnswer(**selected.__dict__)
        out.question = question
        out.record = None
        out.support = {'status': 'unsupported', 'version': LE.VERSION,
                       'frame': literal.to_dict(), 'spans': [],
                       'candidate_checks': []}
        ledger = Ledger(out.root)
        if any(r.kind == 'pointer' for r in ledger.servable()):
            out.kind = AMBIGUOUS if selected.kind == AMBIGUOUS else NOT_IN_CORPUS
            out.reason = 'Literal extraction requires a directly resolved corpus.'
            return out
        bundle = gather(out.root, question if practical else ' '.join((literal.entity, literal.other)).strip(), out.profile)
        # The sealed lexical gate may list a record rejected by current
        # ledger status/lineage checks. Intersect; never trust or index it blindly.
        by_path = {r.path: r for r in ledger.servable()}
        checks = [(by_path[s['path']], LE.statement_support(literal, by_path[s['path']]))
                  for s in bundle.sources if s['path'] in by_path]
        # Candidate diagnostics stay in answer_support.candidate_checks.
        # Unrelated pages with zero matched answer spans are not answer owners.
        out.candidates = []
        out.support['candidate_checks'] = [dict(id=rec.id, hash=rec.hash,
                                               status=check['status'], spans=check['spans'])
                                           for rec, check in checks]
        supported = [(rec, check) for rec, check in checks if check['status'] == 'supported']
        positive_values = {span['value'] for _, check in supported for span in check['spans']}
        negative_values = {value for _, check in checks for value in check.get('negative_values', [])}
        conflict = (any(check['status'] == 'conflict' for _, check in checks)
                    or bool(positive_values.intersection(negative_values))
                    or (bool(supported) and any(check.get('policy_denial') for _, check in checks)))
        unresolved = any(check.get('unresolved') for _, check in checks)
        out.support['unresolved'] = unresolved
        if len(supported) == 1 and not conflict and not unresolved:
            rec, check = supported[0]
            out.record, out.depth, out.kind = rec, ledger.depth(rec), RETURN
            out.support.update(check)
            out.matched_on = 'literal body statement'
            out.reason = check['reason']
        else:
            out.kind = AMBIGUOUS if conflict or len(supported) > 1 else NOT_IN_CORPUS
            out.support['status'] = 'conflict' if out.kind == AMBIGUOUS else 'unsupported'
            out.reason = ('Conflicting or multiple eligible supporting source statements.'
                          if out.kind == AMBIGUOUS else
                          'Relevant policy evidence has unresolved wording or inherited conditions.' if unresolved else
                          'No eligible body statement supports the complete literal question.')
            out.support['reason'] = out.reason
        return out
    frame = parse(question)
    canonical = frame.canonical if frame else question
    selected = answer(root, canonical, profile)
    out = SupportedAnswer(**selected.__dict__)
    out.question = question
    out.support = {'status':'unsupported','version':VERSION,'spans':[],
                   'frame':frame.to_dict() if frame else None,
                   'reason':'Question is outside the supported statement grammar.'}
    if frame is None:
        # Lexical ambiguity can still be reported, explicitly without a support claim.
        out.kind = AMBIGUOUS if selected.kind == AMBIGUOUS else NOT_IN_CORPUS
        out.record = None
        out.reason = out.support['reason']
        return out
    ledger = Ledger(out.root)
    if any(r.kind == 'pointer' for r in ledger.servable()):
        out.kind = AMBIGUOUS if selected.kind == AMBIGUOUS else NOT_IN_CORPUS
        out.record = None
        out.reason = 'A unique local evidence corpus was not resolved; pointers are not answers.'
        return out
    gate = gather(out.root, canonical, out.profile)
    by_path = {r.path:r for r in ledger.servable()}
    checks = [(by_path[s['path']], statement_support(question, by_path[s['path']]))
              for s in gate.sources if s['path'] in by_path]
    # Keep lexical inspection separate from verified answer evidence.
    out.candidates = []
    out.support['candidate_checks'] = [dict(id=rec.id, path=rec.path, hash=rec.hash,
                                          status=check['status'], spans=check['spans'])
                                       for rec,check in checks]
    supported = [(rec,check) for rec,check in checks if check['status']=='supported']
    conflict = any(check['status']=='conflict' for _,check in checks) or (bool(supported) and any(check.get('negative_match') for _,check in checks))
    if len(supported)==1 and not conflict:
        rec,check = supported[0]
        out.record, out.depth, out.kind = rec, ledger.depth(rec), RETURN
        out.support.update(check)
        out.reason = check['reason']
        out.matched_on = 'body statement'
    else:
        out.record = None
        out.kind = AMBIGUOUS if conflict or len(supported)>1 else NOT_IN_CORPUS
        out.support['status'] = 'conflict' if out.kind==AMBIGUOUS else 'unsupported'
        out.reason = ('Multiple eligible supporting pages or conflicting statements; no winner chosen.'
                      if out.kind==AMBIGUOUS else 'No eligible body statement supports the complete question.')
        out.support['reason'] = out.reason
    return out


def candidate_answer(root, question, profile=None):
    """Explicit page inspection. Never call this to answer a factual question."""
    from mplpb_combined.reader import answer
    result = answer(root, question, profile)
    data = result.to_dict()
    data['answer_support'] = {'status':'candidate_only','version':VERSION,'spans':[],
                             'reason':'Explicit source inspection, not a supported answer.'}
    data['mode'] = 'candidate_retrieval'
    return result, data


def code_pins():
    import hashlib
    from pathlib import Path
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(__file__).parent.glob('*.py'))}
