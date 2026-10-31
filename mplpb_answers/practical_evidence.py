"""Finite practical relations with verbatim evidence, separate from frozen core.

No page titles, scope declarations, diagnosis, step execution, or open-ended
procedure completion. Unknown subjects/modifiers do not parse.
"""
import re
from dataclasses import dataclass
from .frames import normalize
from .literal_evidence import LiteralRequest
from mplpb_combined.record import text_of

VERSION = 'practical-evidence-v1'


@dataclass(frozen=True)
class PracticalRequest(LiteralRequest):
    def to_dict(self):
        return dict(super().to_dict(), version=VERSION)


# Every accepted surface binds an action/object and requested attribute.
QUESTIONS = (
    ('candle_duration', r'how long (?:do i|should i) candle (?:the )?burners'),
    ('resistance_interval', r'how often should i measure resistance with a multimeter'),
    ('sieve_mesh', r'what mesh sieve should i use'),
    ('shelf_posts', r'how many posts per shelf'),
    ('slurry_depth', r'how deep should i spread slurry on (?:the |a )?plaster batt'),
    ('sculpture_material', r'which clay is (?:for|suitable for) sculpture'),
    ('cone_material', r'which clay (?:is )?for cone (?P<entity>[0-9]{1,2})'),
)

NUMBER = r'(?:[0-9]+(?:\.[0-9]+)?|a|an|one|two|three|four|five|six|ten|twelve|twenty)'
PATTERNS = {
    'candle_duration': rf'light both burners on low and candle for (?P<value>{NUMBER} (?:minutes?|hours?))',
    'resistance_interval': rf'measure each circuit with a multimeter (?P<value>(?:once|twice|{NUMBER} times) a (?:year|month|week)) and replace the set when resistance has risen by {NUMBER} percent',
    'sieve_mesh': rf'pass (?:once|twice) through an? (?P<value>[0-9]+) mesh sieve',
    'shelf_posts': rf'(?P<value>{NUMBER}) posts per shelf(?:, aligned|, set in the same positions on every layer so the load carries straight down)?',
    'slurry_depth': rf'spread the slurry (?P<value>{NUMBER} (?:fingers?|cm|mm)) deep on a plaster batt and turn it when the underside peels away clean',
    'sculpture_material': r'(?P<value>[a-z]+(?: [a-z]+){0,3}), [a-z]{1,5}, is for sculpture and large slab work and tolerates uneven drying',
}


def parse(question):
    q = normalize(question)
    for relation, pattern in QUESTIONS:
        match = re.fullmatch(pattern, q)
        if match:
            return PracticalRequest(relation, match.groupdict().get('entity') or relation.replace('_', ' '), q)
    return None


def statement_support(frame, record):
    body = re.sub(r'<h[1-6]\b[^>]*>.*?</h[1-6]>', '\n', record.body_html, flags=re.I | re.S)
    text = text_of(body)
    # Reject instruction/hypothesis contexts page-wide, including quoted claims.
    if re.search(r'\b(?:imagine|suppose|assume|pretend|ignore)\b|["“”]', text, re.I):
        return {'status': 'unsupported', 'spans': []}
    pattern = PATTERNS.get(frame.relation)
    if frame.relation == 'cone_material':
        pattern = (r'(?P<value>[a-z]+(?: [a-z]+){0,3}), bag code [a-z]{1,5}, matures at cone '
                   + re.escape(frame.entity) + r' and shrinks ' + NUMBER + r' percent')
    spans, negative = [], []
    for sentence in re.split(r'(?<=[.!?])\s+|\n+', text):
        raw = sentence.strip()
        line = normalize(raw)
        if re.search(r'\b(?:perhaps|possibly|maybe|probably|allegedly|reportedly|might|could|would|should|unknown|if|unless|example|hypothetical|formerly|previously|currently|now)\b', line) or re.match(r'^(?:say|write|claim)\b', line):
            continue
        match = re.fullmatch(pattern, line)
        if match and not re.search(r'\b(?:not|never|no)\b', line):
            spans.append({'quote': raw, 'value': match['value']})
        # A recognized explicit denial blocks an affirmative return; never use
        # a denial as positive evidence. Unknown denials remain unsupported.
        denied = re.sub(r'\b(?:do not|does not|must not|never) ', '', line)
        denied = re.sub(r'\bis not for\b', 'is for', denied)
        m = re.fullmatch(pattern, denied) if denied != line else None
        if m:
            negative.append(m['value'])
    values = {s['value'] for s in spans}
    status = 'conflict' if len(values) > 1 or (spans and negative) else 'supported' if spans else 'unsupported'
    return {'status': status, 'spans': spans, 'negative_values': negative,
            'reason': 'Verbatim practical relation under a finite grammar; instructions are source declarations, not verified execution or general advice.'}
