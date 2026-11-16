"""Independent verification of bounded documentary observations.

The verifier reloads current eligible source bytes and parses documentary
headers itself. It does not invoke the extraction specialist or certify factual
truth, publication priority, causation, or arbitrary historical synthesis.
"""
import copy
from datetime import datetime
from pathlib import Path
import re

from mplpb_answers.body_text import body_text
from mplpb_combined import provenance_gate as G
from mplpb_combined.ledger import Ledger
from mplpb_combined.reader import PROFILES, DEFAULT_PROFILE

VERSION = 'historical-observation-verifier-v1'
FIELDS = {'source_id', 'path', 'hash', 'start', 'end', 'quote',
          'kind', 'value', 'target_id', 'target_version'}
KINDS = {'document_identity', 'declared_date', 'related', 'supersedes', 'not_superseded'}
IDENTIFIER = r'[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+'
DATE = re.compile(r'(?<![\w-])\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?(?![\w:-])')


def _profile(profile):
    return PROFILES[profile] if isinstance(profile, str) else profile or PROFILES[DEFAULT_PROFILE]


def _snapshot(root, question, profile, gate):
    return {'root': str(Path(root).resolve()), 'question': question,
            'profile': profile.name, 'policy': copy.deepcopy(gate.policy),
            'corpus_snapshot': gate.corpus_snapshot}


def verification_snapshot(root, question, profile=None):
    """Pin the original question, serving policy, corpus state and root."""
    profile = _profile(profile)
    return _snapshot(root, question, profile, G.gather(root, question, profile))


def _field(line):
    # Markdown styling belongs to the original body, not active ledger metadata.
    clean = line.replace('**', '').strip()
    if clean.startswith('|'):
        parts = clean.strip('|').split('|')
        if len(parts) != 2:
            return None
        key, value = (part.strip() for part in parts)
    else:
        match = re.fullmatch(r'(Document ID|Document-ID|Last Updated|Updated|Related documents|Related|Supersedes)'
                             r'(?:\s*[:.]\s*|\s{2,})(.*)', clean, re.I)
        if not match:
            # The canonical body projection collapses plain-text table padding.
            # Only identity/date fields permit this separator, never prose such
            # as "Related pages may ...".
            match = re.fullmatch(r'(Document ID|Document-ID|Last Updated|Updated)\s+(.*)', clean, re.I)
        if not match:
            return None
        key, value = match.groups()
    key = key.lower().replace('-', ' ')
    if key not in {'document id', 'last updated', 'updated', 'related documents', 'related', 'supersedes'}:
        return None
    return key, value


def _headers(body):
    """Recognize genuine early header fields, never later examples or sections."""
    lines, offset = [], 0
    fenced, seen_field = False, False
    for raw in body.splitlines(keepends=True):
        line = raw.rstrip('\r\n')
        clean = line.replace('**', '').strip()
        if len(lines) >= 120 or offset > 12000:
            break
        if re.match(r'^(```|~~~)', clean):
            fenced = not fenced
        if not fenced and (re.match(r'^(?:#{1,6}\s*)?(?:Abstract|Introduction)\s*$', clean, re.I)
                           or re.match(r'^(?:#{1,6}\s*)?\d+[.)]\s', clean)
                           or re.match(r'^(?:Example|Sample|Appendix|Body)\s*[:.]', clean, re.I)
                           or (seen_field and re.match(r'^#{1,6}\s+', clean))
                           or re.match(r'^Back to[.:]', clean, re.I)):
            break
        field = None if fenced else _field(line)
        seen_field = seen_field or bool(field)
        lines.append((offset, line, field))
        offset += len(raw)
    blocks = []
    for i, (start, line, field) in enumerate(lines):
        if not field:
            continue
        key, value = field
        end = start + len(line)
        if key in {'related', 'related documents'}:
            # Related prose can wrap; a marker with no inline value introduces
            # a list, whose intervening blank lines are retained.
            for nxt_start, nxt_line, nxt_field in lines[i+1:]:
                clean = nxt_line.replace('**','').strip()
                if (nxt_field or (value and not nxt_line.strip())
                        or re.match(r'^(?:Back to|Implementation|What changed)\b',clean,re.I)
                        or re.fullmatch(r'[-=_]{3,}',clean)):
                    break
                end = nxt_start + len(nxt_line)
        begin = start + len(line)-len(line.lstrip())
        while end > begin and body[end-1].isspace():
            end -= 1
        blocks.append({'key':key, 'value':value, 'start':begin, 'end':end,
                       'quote':body[begin:end]})
    return blocks


def _declarations(blocks):
    identities, dates, versions = set(), set(), set()
    for block in blocks:
        if block['key'] == 'document id':
            match = re.match(IDENTIFIER+r'(?![A-Z0-9_-])', block['value'])
            if match:
                identities.add(match[0])
        if block['key'] in {'updated', 'last updated'}:
            header = re.fullmatch(r'('+DATE.pattern+r')(?:\s+(v\d+))?', block['value'])
            for match in [header] if header else []:
                try:
                    datetime.fromisoformat(match[1].replace('Z', '+00:00'))
                except ValueError:
                    continue
                dates.add(match[1])
            versions.update(re.findall(r'\bv\d+\b', block['value']))
    return identities, dates, versions


def _negative(value):
    text = ' '.join(value.replace('**', '').split())
    return bool(_negative_at(text))


def _negative_at(value):
    return re.search(r'\b(?:nothing|none)\b|\b(?:does|do) not supersede\b|'
                     r'\bnot superseded\b|\bno\b[^.;\n]{0,180}\bsuperseded\b', value, re.I)


def _pairs(value):
    pairs = set()
    matches = list(re.finditer(r'(?<![A-Z0-9_-])'+IDENTIFIER+r'(?![A-Z0-9_-])', value))
    for index, match in enumerate(matches):
        tail = value[match.end():matches[index+1].start() if index+1<len(matches) else len(value)]
        first = re.match(r'\s+(v\d+)\b', tail)
        if not first:
            pairs.add((match[0], ''))
            continue
        pairs.add((match[0], first[1]))
        rest = tail[first.end():]
        while True:
            nxt = re.match(r'\s*(?:\([^()\n]{0,160}\))?\s*,\s*(v\d+)\b', rest)
            if not nxt:
                break
            pairs.add((match[0], nxt[1]))
            rest = rest[nxt.end():]
    return pairs


def _semantic(observation, body):
    blocks = _headers(body)
    identities, dates, versions = _declarations(blocks)
    if len(identities) != 1:
        return False
    matching = [block for block in blocks if block['start'] == observation['start']
                and block['end'] == observation['end'] and block['quote'] == observation['quote']]
    if len(matching) != 1:
        return False
    block = matching[0]
    kind = observation['kind']
    value, target, version = (observation[key] for key in ('value', 'target_id', 'target_version'))
    if kind == 'document_identity':
        return (block['key'] == 'document id' and value in identities and target == value
                and (version in versions if len(versions) == 1 else not version and not versions))
    if kind == 'declared_date':
        return (block['key'] in {'updated', 'last updated'} and len(dates) == 1 and value in dates and not target
                and (version in versions if len(versions) == 1 else not version and not versions))
    if kind == 'not_superseded':
        return (block['key'] == 'supersedes' and not target and not version
                and value == block['quote'] and _negative(value))
    required = {'related': {'related', 'related documents'}, 'supersedes': {'supersedes'}}
    if kind not in required or block['key'] not in required[kind]:
        return False
    if not target:
        return bool(not version and value == block['quote'])
    if value != target or not re.fullmatch(IDENTIFIER, target):
        return False
    positive = block['quote']
    if kind == 'related' and re.search(r'\b(?:not related|unrelated|do not|does not)\b|\bnot\s+'+IDENTIFIER,positive,re.I):
        return False
    if kind == 'supersedes':
        negative = _negative_at(positive)
        if negative:
            positive = positive[:negative.start()]
    if re.search(r'\b(?:if|unless|except|might|may|proposed|draft)\b',positive,re.I):
        return False
    if kind=='related' and re.search(r'\b(?:not|never|no|unrelated)\b',positive,re.I):
        return False
    return (target, version) in _pairs(positive)


def _result(code, current, verified=None, rejected=None):
    return {'version': VERSION, 'code': code, 'source_state_current': current,
            'verified': verified or [], 'rejected': rejected or [],
            'answer_supported': False, 'truth_verified': False,
            'authority': 'verified_bounded_documentary_observations',
            'notice': 'Exact source declarations only; no historical truth, causation, priority or unrestricted synthesis is certified.'}


def verify_observations(root, question, profile, observations, expected_snapshot):
    """Reload evidence and independently check the extractor's proposed facts.

    A changed snapshot discards every proposed quote and trace. Invalid individual
    observations are rejected without echoing their untrusted field values.
    """
    if (not isinstance(question, str) or not question.strip() or len(question) > 4000
            or not isinstance(observations, list) or len(observations) > 256
            or not isinstance(expected_snapshot, dict)):
        return _result('invalid_verification_request', False)
    try:
        profile = _profile(profile)
        initial = G.gather(root, question, profile)
        if _snapshot(root, question, profile, initial) != expected_snapshot or not initial.query_terms:
            return _result('source_changed', False)
        excluded = {source['path'] for source in initial.excluded}
        lexical = {source['path'] for source in initial.sources}
        ledger = Ledger(root)
        records = {(record.id, record.path, record.hash_actual):record for record in ledger.servable()
                   if record.kind not in {'pointer', 'index'} and record.path not in excluded
                   and (profile.prose or record.path in lexical)}
        verified, rejected, quote_size = [], [], 0
        for index, observation in enumerate(observations):
            reason = 'invalid_observation'
            if isinstance(observation, dict) and set(observation) == FIELDS:
                strings = FIELDS-{'start','end'}
                valid = all(isinstance(observation[key],str) and len(observation[key]) <= 16000 for key in strings)
                valid = valid and type(observation['start']) is int and type(observation['end']) is int
                if valid and observation['kind'] in KINDS:
                    quote_size += len(observation['quote'])
                    if quote_size > 262144:
                        return _result('verification_budget_exceeded', False)
                    record = records.get(tuple(observation[key] for key in ('source_id','path','hash')))
                    if record is None:
                        reason = 'source_unavailable'
                    else:
                        body = body_text(record.body_html)
                        start, end = observation['start'], observation['end']
                        if not 0 <= start < end <= len(body) or body[start:end] != observation['quote']:
                            reason = 'invalid_citation'
                        elif not _semantic(observation, body):
                            reason = 'unverified_declaration'
                        else:
                            verified.append(copy.deepcopy(observation))
                            continue
            rejected.append({'index':index, 'reason':reason})
        fresh = G.gather(root, question, profile)
        if _snapshot(root, question, profile, fresh) != expected_snapshot:
            return _result('source_changed', False)
        return _result('verified' if not rejected else 'partially_verified', True, verified, rejected)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return _result('source_unavailable', False)
