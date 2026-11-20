"""Bounded documentary observations for historical specialist work.

These observations describe what a source header explicitly declares. They do
not establish authorship, publication priority, historical truth or causation.
Offsets refer to the supplied canonical body projection, without rewriting it.
"""
import re
from datetime import date, datetime

VERSION = 'historical-documentary-observations-v1'
KINDS = frozenset({'document_identity', 'declared_date', 'related',
                   'supersedes', 'not_superseded'})
FIELDS = frozenset({'kind', 'value', 'start', 'end', 'quote',
                    'target_id', 'target_version'})
MAX_BODY = 1000000
MAX_HEADER = 20000
MAX_BLOCK = 8000
ID = r'[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+'
DATE = r'\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2}))?'
FIELD = re.compile(r'^\s*(?:\|\s*)?(?:\*\*)?'
                   r'(?P<field>Document[ -]ID|Last[ -]Updated|Updated|Related(?: documents)?|Supersedes)'
                   r'(?:\*\*)?(?:\s*\|\s*|\s*[:.]\s*(?:\*\*)?\s*|[ \t]{2,})'
                   r'(?P<value>.*?)\s*$', re.I)
PLAIN_FIELD = re.compile(r'^\s*(?P<field>Document[ -]ID|Last[ -]Updated|Updated)'
                         r'[ \t]+(?P<value>\S.*?)\s*$', re.I)
NEGATIVE = re.compile(r'\b(?:nothing|none)\b|\b(?:does|do) not supersede\b|'
                      r'\bnot superseded\b|\bno\b[^.;\n]{0,180}\bsuperseded\b', re.I)
RELATED_NEGATIVE = re.compile(r'\b(?:not related|unrelated|does not|do not)\b|\bnot\s+'+ID, re.I)


def _blocks(body):
    """Yield complete recognized early-header fields, excluding fenced samples."""
    lines = body.splitlines(keepends=True)
    offset, fenced, seen_field = 0, None, False
    found, active_related = [], None
    related_list, related_closing_link = False, False
    for line_index, line in enumerate(lines[:100]):
        raw = line.rstrip('\r\n')
        if offset+len(raw) > MAX_HEADER:
            break
        stripped = raw.strip()
        fence = re.match(r'^\s{0,3}(`{3,}|~{3,})', raw)
        if fence:
            marker = fence.group(1)[0]
            if fenced is None:
                fenced = marker
            elif fenced == marker:
                fenced = None
            offset += len(line)
            continue
        if fenced:
            offset += len(line)
            continue
        # Headings before the header are titles/subtitles. After actual fields,
        # they start the paper proper; embedded demonstrations are not headers.
        if ((seen_field and re.match(r'^\s*#{1,6}\s+', raw))
                or re.match(r'^\s*(?:#{1,6}\s*)?(?:Abstract|Introduction)\s*$', raw, re.I)
                or re.match(r'^\s*(?:Example|Sample|Appendix|Body)\s*[:.]', raw, re.I)):
            break
        match = FIELD.match(raw) or PLAIN_FIELD.match(raw)
        if match:
            if len(raw) > MAX_BLOCK:
                offset += len(line)
                active_related = None
                continue
            seen_field = True
            found.append({'field': match['field'].lower().replace('-', ' '),
                          'start': offset, 'end': offset+len(raw),
                          'value': match['value'].rstrip(' |')})
            active_related = found[-1] if found[-1]['field'].startswith('related') else None
            related_list = active_related is not None and not active_related['value'].strip()
            related_closing_link = False
            if related_list:
                # Canonical body projection removes indentation and blank lines.
                # An explicit closing Back-to field still bounds a wrapped list.
                for upcoming in lines[line_index+1:100]:
                    if re.match(r'^\s*(?:\*\*)?Back to\b', upcoming, re.I):
                        related_closing_link = True
                        break
                    if (re.match(r'^\s*#{1,6}\s+', upcoming)
                            or re.fullmatch(r'\s*[-=_]{3,}\s*', upcoming)):
                        break
        elif active_related is not None:
            # Related lists may contain wrapped text, blank separators and bullets.
            # A different bold prose field, back-link or rule terminates the list.
            if (re.match(r'^\s*(?:\*\*)?(?:Back to|Implementation|What changed|Classing source (?:file|SHA-256|bytes))\b', raw, re.I)
                    or re.fullmatch(r'\s*[-=_]{3,}\s*', raw)):
                break
            if not stripped:
                if not related_list:
                    active_related = None
            elif related_list and not related_closing_link and not re.match(r'^\s*(?:[-*+]\s|\d+[.)]\s)|^\s{2,}\S', raw):
                active_related = None
            else:
                if offset+len(raw)-active_related['start'] > MAX_BLOCK:
                    found.remove(active_related)
                    active_related = None
                else:
                    active_related['end'] = offset+len(raw)
        offset += len(line)
    return found


def _targets(value):
    """Read explicit IDs and their adjacent versions; never guess by title."""
    for match in re.finditer(r'(?<![A-Za-z0-9_-])(?P<id>'+ID+r')(?![A-Za-z0-9_-])', value):
        tail = value[match.end():]
        first = re.match(r'\s+(v\d+)\b', tail, re.I)
        if not first:
            yield match['id'], ''
            continue
        yield match['id'], first[1]
        cursor = first.end()
        # Compact declarations can share an ID: DOC-101 v3 (date), v2 (date).
        while True:
            nxt = re.match(r'\s*(?:\([^()\n]{0,160}\))?\s*,\s*(v\d+)\b', tail[cursor:], re.I)
            if not nxt:
                break
            yield match['id'], nxt[1]
            cursor += nxt.end()


def _declared_date(value):
    match = re.match(r'\s*('+DATE+r')(?![\dA-Za-z:+-])(?:[ \t]+(v\d+)\b)?', value, re.I)
    if not match:
        return None
    raw = match[1]
    try:
        if 'T' in raw:
            datetime.fromisoformat(raw.replace('Z', '+00:00'))
        else:
            date.fromisoformat(raw)
    except ValueError:
        return None
    return raw, match[2] or ''


def extract(body, max_observations=64):
    """Extract closed, literal header observations from a canonical source body.

    Every result has exactly FIELDS. A blank target_id records a declaration
    whose target cannot safely be resolved. Reaching the caller's cap is not a
    completeness guarantee. Source eligibility and hashes are checked separately.
    """
    if not isinstance(body, str) or len(body) > MAX_BODY:
        raise ValueError('Historical body must be bounded text')
    if type(max_observations) is not int or not 1 <= max_observations <= 256:
        raise ValueError('Observation budget must be 1–256')
    blocks = _blocks(body)
    observations, seen = [], set()
    versions = {declared[1] for block in blocks
                if block['field'] in {'updated', 'last updated'}
                for declared in [_declared_date(block['value'])] if declared and declared[1]}
    header_version = next(iter(versions)) if len(versions) == 1 else ''

    def add(kind, value, block, target_id='', target_version=''):
        marker = (kind, value, block['start'], block['end'], target_id, target_version)
        if marker in seen or len(observations) >= max_observations:
            return
        seen.add(marker)
        observations.append({'kind':kind, 'value':value, 'start':block['start'],
                             'end':block['end'], 'quote':body[block['start']:block['end']],
                             'target_id':target_id, 'target_version':target_version})

    for block in blocks:
        field, value = block['field'], block['value']
        if field == 'document id':
            # The first ID names the document. Parenthetical mentioned IDs are
            # retained in the quotation but cannot become extra identities.
            identity = re.match(r'\s*('+ID+r')(?![A-Za-z0-9_-])', value)
            if identity:
                add('document_identity', identity[1], block, identity[1], header_version)
        elif field in {'updated', 'last updated'}:
            declared = _declared_date(value)
            if declared:
                # Keep the date's stated precision: a day is not a timestamp.
                add('declared_date', declared[0], block, target_version=declared[1])
        elif field.startswith('related'):
            whole_value = body[block['start']:block['end']]
            uncertain=RELATED_NEGATIVE.search(whole_value) or re.search(r'\b(?:if|unless|except|might|may|proposed|draft|never|no)\b',whole_value,re.I)
            targets = [] if uncertain else list(_targets(whole_value))
            if targets:
                for target, version in targets:
                    add('related', target, block, target, version)
            else:
                add('related', whole_value, block)
        elif field == 'supersedes':
            negative = NEGATIVE.search(value)
            positive = value[:negative.start()] if negative else value
            if negative:
                add('not_superseded', body[block['start']:block['end']], block)
            targets = list(_targets(positive))
            if re.search(r'\b(?:if|unless|except|might|may|proposed|draft)\b',positive,re.I):
                targets=[]
            for target, version in targets:
                add('supersedes', target, block, target, version)
            if not targets and not negative and value.strip() not in {'', '—', '-'}:
                add('supersedes', body[block['start']:block['end']], block)
    return observations


def inspect_document(body, max_observations=64):
    """Descriptive alias for callers that expose the documentary expert."""
    return extract(body, max_observations)
