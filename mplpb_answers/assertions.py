"""Shared comparison of bounded assertions, never lexical entailment.

Values and qualifications are compared literally after existing normalization.
Different owners remain ambiguous even when their assertions are compatible.
"""
from dataclasses import dataclass, asdict

VERSION = 'bounded-assertions-v1'


@dataclass(frozen=True)
class Assertion:
    subject: str
    relation: str
    value: str
    polarity: str
    qualification: str
    source_id: str
    source_hash: str
    path: str
    quote: str

    def to_dict(self):
        return asdict(self)


def attach(check, frame, record):
    assertions = []
    for polarity, spans in (('positive', check.get('spans', [])),
                            ('negative', check.get('negative_spans', []))):
        for span in spans:
            assertions.append(Assertion(frame.entity, frame.relation,
                span['value'], polarity, span.get('qualification', ''),
                record.id, record.hash, record.path, span['quote']).to_dict())
    check['assertions'] = assertions
    return check


def conflicts(checks):
    """A denial opposes only the same value and exact qualification.

    Legacy extractors without qualified negative spans retain their own explicit
    conflict/denial contracts. No conditions, units or dates are discarded here.
    """
    assertions = [a for _, c in checks for a in c.get('assertions', [])]
    key = lambda a: (a['subject'], a['relation'], a['value'], a['qualification'])
    positive = {key(a) for a in assertions if a['polarity'] == 'positive'}
    negative = {key(a) for a in assertions if a['polarity'] == 'negative'}
    supported = [c for _, c in checks if c['status'] == 'supported']
    values = {s['value'] for c in supported for s in c['spans']}
    legacy_negative = {v for _, c in checks for v in c.get('negative_values', [])
                       if not c.get('negative_spans')}
    return (any(c['status'] == 'conflict' for _, c in checks)
            or bool(positive & negative) or bool(values & legacy_negative)
            or (bool(supported) and any(c.get('policy_denial') for _, c in checks)))
