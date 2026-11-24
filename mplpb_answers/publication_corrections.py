"""Strict, bounded links between Federal Register publications."""
from dataclasses import dataclass
from datetime import date
import re

from .body_text import body_text
from .documentary_verify import citation, context_ranges

_MONTHS = 'January February March April May June July August September October November December'.split()
_DATE = r'(?:' + '|'.join(_MONTHS) + r')\s+\d{1,2},\s+\d{4}'
_MONTH_DAY = r'(?:' + '|'.join(_MONTHS) + r')\s+\d{1,2}(?:,\s+\d{4})?'
_ID = r'[A-Z0-9][A-Z0-9-]{1,40}'
_CITY = r"[A-Za-z][A-Za-z .'’-]{1,50}"
_CITATION = r'(?P<volume>\d{1,3})\s+FR\s+(?P<page>\d{1,6})'
_HEADER = (rf'^\[Federal Register Volume (?P<volume>\d{{1,3}}), Number \d{{1,3}} '
           rf'\((?:[A-Za-z]+, )?(?P<date>{_DATE})\)\]\n'
           rf'(?:(?:\[[^\]\n]+\])\n)?\[Pages? (?P<page>\d{{1,6}})(?:-\d{{1,6}})?\]\n'
           rf'(?:From the Federal Register Online[^\n]*\n)?\[FR Doc No: (?P<doc>{_ID})\]')
_AGENCY = r'^AGENCY: (?P<agency>[^.\n]{3,160})\.$'
_EFFECTIVE = rf'^DATES: (?:This (?:final )?rule is effective|Effective) (?P<effective>{_DATE})\.'
_ACTION = r'^ACTION: [^\n.]{1,160}\bcorrection\.$'
_HOURS = r'(?P<hours>\d{1,2}(?::\d{2})? [ap]\.m\. to \d{1,2}(?::\d{2})? [ap]\.m\.)'
_VENUE_TARGET = (rf'^SUMMARY: (?:(?!^[A-Z ]{{4,}}:)[\s\S]){{0,1300}}?(?P<reference>(?:The )?notice,?\s+(?:which was\s+)?published in the Federal Register on\s+'
                 rf'(?P<date>{_DATE})\s+\({_CITATION}\), provided an incorrect location for the\s+'
                 rf'meeting to be held in (?P<place>{_CITY}, [A-Z]{{2}})\.)')
_INSTRUCTIONS_TARGET = (rf'^SUPPLEMENTARY INFORMATION: In FR Doc\. (?P<doc>{_ID}) appearing on page '
                        rf'(?P<page>\d{{1,6}})\s+in the Federal Register of (?:[A-Za-z]+, )?(?P<date>{_DATE}), '
                        rf'the following\s+corrections are made:')
_INSTRUCTION = r'\bcorrect instruction\s+(?P<number>\d{1,4}(?:\.[a-z]\.)?)(?=,|\s)'
_ORDER = r'(?:Order No\. (?P<order>\d{1,9}))'
_DOCKET = r'^\[Docket No\. (?P<docket>[A-Z0-9-]+)(?:; Order No\. (?P<order>\d{1,9}))?\]$'
_DEADLINE_TARGET = (rf'^On (?P<date>{_DATE}), notice of {_ORDER} was published in the\s+'
                    rf'Federal Register, {_CITATION}, providing that:')
_DEADLINE_BRIDGE = (rf'^On (?P<date>{_DATE}), a correction regarding the (?P<target_day>{_MONTH_DAY}) notice\s+'
                    rf'concerning {_ORDER} was published in the Federal Register, {_CITATION},\s+'
                    rf'stating that:')
_DEADLINE_FINAL = rf'^Notice is hereby given that the deadline to submit filings to\s+comply with {_ORDER} has been corrected and is (?P<replacement>{_DATE})\.'
_DEADLINE_REPLACEMENT = rf'[`\x27]{{1,3}}(?P<previous>{_DATE})[\x27]{{1,3}} should read [`\x27]{{1,3}}(?P<replacement>{_DATE})[\x27]{{1,3}}'
_DEADLINE_DOCUMENT = (rf'^In rule document (?P<doc>{_ID}) beginning on page (?P<page>\d{{1,6}}) in the issue of\s+'
                      rf'(?:[A-Za-z]+, )?(?P<date>{_DATE}), make the following correction:')
_DEADLINE_OLD = rf'^DATES: [^\n]*\. Each [^\n]{{1,90}} must file\s+the tariff changes needed to implement the requirements of this final\s+rule by (?P<previous>{_DATE})\.'

_MONTH = '(?:' + '|'.join(_MONTHS) + ')'
_ISSUER = r'^AGENCY: (?P<agency>(?:[^\n]{1,170}\n){1,3}?)(?=ACTION:)'
_CORRECTING_AMENDMENT = r'^ACTION: Correcting amendment\.$'
_PREVIOUS_RULE = (rf'^On (?P<date>{_DATE}), [^\n]{{1,180}}\s+published a final rule in the Federal Register at\s+'
                  rf'{_CITATION}\s+\(FR Doc\.\s+(?P<doc>{_ID})\)\.')
_PREVIOUS_CORRECTION = (rf'^On (?P<date>{_DATE}), (?P<issuer>[A-Z]{{2,8}}) published a correction to the final rule\s+'
                        rf'titled [\s\S]{{1,300}}?\.\s+{_CITATION}\.')
_SCOPE_REPORT = (
    r'The\s+correction included amendatory instruction (?P<instruction>\d{1,3}) in the first column of\s+'
    r'page (?P<page>\d{1,6})\. A typographical error in that instruction caused the Office\s+'
    r'of the Federal Register to replace the whole of paragraph (?P<paragraph>\([a-z0-9]{1,3}\))\s+'
    r'with the\s+text on page (?P=page)\. (?P<issuer>[A-Z]{2,8}) did not intend to do that\. Rather, (?P=issuer) intended\s+'
    r'to correct only the introductory text of paragraph (?P=paragraph)\.')
_APPLICABILITY = (
    rf'^This correction is applicable as if (?P<issuer>[A-Z]{{2,8}}) had included this change in\s+'
    rf'the final rule that published on (?P<original>{_DATE})\. That rule had an\s+'
    rf'effective date of (?P<described>{_DATE})\. Accordingly, the correction is\s+'
    rf'applicable as of (?P<applicable>{_DATE})(?=[,.])')
_UNSAFE = re.compile(r'\b(?:if|unless|allegedly|possibly|reported(?:ly)?|proposed|hypothetical|draft|not|never|except)\b', re.I)
_MAX_SCAN = 2 * 1024**2
_MAX_FILES = 64
_FORMS = {
    'reported_scope': (
        rf'What did the (?P<later>{_MONTH}) (?P<issuer>[A-Z]{{2,8}}) document say went wrong in the '
        rf'(?P<previous>{_MONTH}) correction, and what part of paragraph (?P<paragraph>\([a-z0-9]{{1,3}}\)) had (?P=issuer) intended to change\?',
    ),
    'reaffirmed_applicability': (
        rf'Across the (?P<earlier>{_MONTH}) rule, (?P<previous>{_MONTH}) correction and '
        rf'(?P<later>{_MONTH}) follow-up, what earlier applicability date is reaffirmed\?',
    ),
    'venue': (
        rf'What changed about the (?P<city>{_CITY}) meeting (?:venue|location), and what hours did the (?:published )?correction retain\?',
        rf'How did the (?P<city>{_CITY}) meeting venue change, and what meeting hours stayed the same\?',
    ),
    'deadline': (
        rf'Trace the original {_ORDER} (?:compliance|filing) deadline, its correction, and the date reaffirmed by the later notice\.',
        rf'What was the original {_ORDER} (?:compliance|filing) deadline, and what date did the correction and later notice give\?',
    ),
    'instructions': (
        rf'(?:Which|What) two instructions did the (?P<agency>[A-Z]{{2,8}}) correction amend, and did the (?:listed )?(?P<effective>{_MONTH_DAY}) effective date change\?',
    ),
}


def parse(question):
    for kind, forms in _FORMS.items():
        for form in forms:
            matched = re.fullmatch(form, question, re.I)
            if matched:
                return 'publication_correction', (), (kind, matched.groupdict())
    return None


def _date(text):
    normalized = ' '.join(text.split())
    name, day, year = re.fullmatch(r'(\w+) (\d{1,2}), (\d{4})', normalized).groups()
    try:
        month = [m.casefold() for m in _MONTHS].index(name.casefold()) + 1
        return date(int(year), month, int(day))
    except ValueError:
        return None


def _text(text):
    return ' '.join(text.split())


def _date_display(value):
    return f'{_MONTHS[value.month - 1]} {value.day}, {value.year}'


def _single(items):
    return items[0] if len(items) == 1 else None


@dataclass
class Publication:
    record: object
    body: str
    header: re.Match

    @property
    def date(self):
        return _date(self.header['date'])

    def match(self, pattern, limit=None):
        return _single(list(re.finditer(pattern, self.body if limit is None else self.body[:limit],
                                       re.I | re.M)))

    def cites(self, *matches):
        ranges = context_ranges(self.record)
        result = []
        for match in (self.header, *matches):
            a, b = match.span()
            if any(lo < b and hi > a for lo, hi in ranges):
                return None
            witness = citation(self.record, self.body, a, b)
            if witness not in result:
                result.append(witness)
        return result


def _reference(publications, ref, *, through=None):
    return _single([p for p in publications if p.header['page'] == ref['page']
                   and p.date == _date(ref['date'])
                   and all(p.header[k].casefold() == ref[k].casefold()
                           for k in ('doc', 'volume') if k in ref.re.groupindex)
                   and (through is None or p.date < through)])


def _same_agency(left, right):
    a, b = left.match(_AGENCY, 16000), right.match(_AGENCY, 16000)
    return a and b and a['agency'].casefold() == b['agency'].casefold()


def _combine(op, text, proposition, *groups):
    if any(group is None for group in groups):
        return None
    return {'text': text, 'proposition': {'relation': 'published_' + op + '_correction', **proposition},
            'citations': [c for group in groups for c in group], 'source_support_established': True,
            'qualifiers': ['The relationship concerns what these publications state.']}


def _venue(publications, request):
    city = request['city'].casefold()
    pair = _single([(p, ref) for p in publications if p.match(_ACTION, 16000)
                    and (ref := p.match(_VENUE_TARGET, 16000))
                    and ref['place'].split(',')[0].casefold() == city])
    if pair is None:
        return None
    newer, ref = pair
    earlier = _reference(publications, ref, through=newer.date)
    if not earlier or not _same_agency(earlier, newer):
        return None
    place = re.escape(ref['place'])
    old = earlier.match(rf'^(?:ADDRESSES: )?{place}: (?P<venue>[^,;\n]{{3,100}})(?=,)', 16000)
    new = newer.match(rf'^ADDRESSES: The {place}, public meeting will be held at the\s+(?P<venue>[^,;]{{3,100}})(?=,)', 16000)
    addresses = earlier.match(r'^ADDRESSES:', 16000)
    before = earlier.match(rf'^DATES: (?:(?!^[A-Z ]{{4,}}:)[\s\S]){{0,1400}}?'
                           rf'The (?:public )?meetings? will be held from {_HOURS}(?=,\s+local time\.|$)', 16000)
    after = newer.match(rf'^DATES: The {place}, (?:public )?meeting will be held '
                        rf'(?:on {_DATE},\s+)?from {_HOURS}(?=,\s+local time\.|$)', 16000)
    if (not all((old, new, before, after, addresses)) or old.start() < addresses.start()
            or re.search(r'^[A-Z ]{4,}:', earlier.body[addresses.end():old.start()], re.M)
            or _UNSAFE.search(before[0])
            or _UNSAFE.search(after[0]) or old['venue'].casefold() == _text(new['venue']).casefold()
            or before['hours'] != after['hours']):
        return None
    previous, replacement, hours = old['venue'], _text(new['venue']), before['hours']
    return _combine('venue', f'The published venue changed from {previous} to {replacement}. The announced hours remained {hours}.',
                    {'from_venue': previous, 'to_venue': replacement, 'retained_hours': hours},
                    earlier.cites(old, before), newer.cites(ref, new, after))


def _deadline(publications, request):
    order = request['order']
    later = _single([(p, final) for p in publications if (final := p.match(_DEADLINE_FINAL, 16000))
                     and final['order'] == order])
    if later is None:
        return None
    confirmation, final = later
    target = confirmation.match(_DEADLINE_TARGET, 16000)
    bridge = confirmation.match(_DEADLINE_BRIDGE, 16000)
    if (not target or not bridge or target['order'] != order or bridge['order'] != order
            or not _date(target['date'])
            or _text(bridge['target_day']) != _date_display(_date(target['date'])).rsplit(',', 1)[0]):
        return None
    original = _reference(publications, target, through=confirmation.date)
    correction = _reference(publications, bridge, through=confirmation.date)
    if not original or not correction or original.date >= correction.date:
        return None
    dockets = [p.match(_DOCKET, 16000) for p in (original, correction, confirmation)]
    if (not all(dockets) or len({m['docket'] for m in dockets}) != 1
            or any(m['order'] != order for m in dockets[:2])):
        return None
    destination = correction.match(_DEADLINE_DOCUMENT, 16000)
    correction_value = correction.match(_DEADLINE_REPLACEMENT, 16000)
    original_value = original.match(_DEADLINE_OLD, 16000)
    confirmed_value = confirmation.match(_DEADLINE_REPLACEMENT, 16000)
    if (not all((destination, correction_value, original_value, confirmed_value))
            or _reference(publications, destination, through=correction.date) is not original):
        return None
    previous = _date(original_value['previous'])
    updated = _date(final['replacement'])
    if (not previous or not updated or previous == updated or any(
            _date(change['previous']) != previous or _date(change['replacement']) != updated
            for change in (correction_value, confirmed_value))):
        return None
    old_date, new_date = map(_date_display, (previous, updated))
    return _combine('deadline', f'The original notice listed {old_date}. The published correction changed the deadline to {new_date}, and the later notice reaffirmed it.',
                    {'order': order, 'previous_date': old_date, 'replacement_date': new_date},
                    original.cites(original_value), correction.cites(destination, correction_value),
                    confirmation.cites(target, bridge, confirmed_value, final))


def _instructions(publications, request):
    def named(p):
        m = p.match(_AGENCY, 16000)
        return m and ''.join(part[0] for part in m['agency'].split()).casefold() == request['agency'].casefold()

    pair = _single([(p, ref) for p in publications if named(p) and p.match(_ACTION, 16000)
                    and (ref := p.match(_INSTRUCTIONS_TARGET, 16000))])
    if pair is None:
        return None
    newer, ref = pair
    earlier = _reference(publications, ref, through=newer.date)
    if not earlier or not _same_agency(earlier, newer):
        return None
    a, b = (p.match(_EFFECTIVE, 16000) for p in (earlier, newer))
    lines = list(re.finditer(_INSTRUCTION, newer.body, re.I))
    if not a or not b or len(lines) != 2 or len({m['number'] for m in lines}) != 2:
        return None
    old, new = _date(a['effective']), _date(b['effective'])
    if not old or not new or _text(request['effective']) not in {
            _date_display(old), _date_display(old).rsplit(',', 1)[0]}:
        return None
    numbers = [m['number'] for m in lines]
    effective = _date_display(new)
    text = (f'The correction identifies instructions {numbers[0]} and {numbers[1]} for amendment. '
            + (f'The listed effective date remained {effective}.' if old == new else
               f'The listed effective date changed from {_date_display(old)} to {effective}.'))
    return _combine('instruction', text, {'instructions': numbers, 'effective_date': effective,
                                          'effective_date_changed': old != new},
                    earlier.cites(a), newer.cites(ref, *lines, b))


def _successive(publications, request, kind):
    """Resolve two publication references before comparing the reported scopes."""
    selected = _single([(p, ref) for p in publications
                        if p.match(_CORRECTING_AMENDMENT, 16000)
                        and _MONTHS[p.date.month - 1].casefold() == request['later'].casefold()
                        and (ref := p.match(_PREVIOUS_CORRECTION, 16000))
                        and ('issuer' not in request or request['issuer'].casefold() == ref['issuer'].casefold())])
    if selected is None:
        return None
    later, ref = selected
    previous = _reference(publications, ref, through=later.date)
    if (not previous or not previous.match(_ACTION, 16000)
            or _MONTHS[previous.date.month - 1].casefold() != request['previous'].casefold()):
        return None
    prior = previous.match(_PREVIOUS_RULE, 16000)
    if not prior:
        return None
    earlier = _reference(publications, prior, through=previous.date)
    if not earlier:
        return None
    stamps = [p.match(_ISSUER, 16000) for p in (earlier, previous, later)]
    if not all(stamps):
        return None
    issuer = ref['issuer']
    abbreviation = r' \(' + re.escape(issuer) + r'\)(?=\.$)'
    agencies = [_text(m['agency']) for m in stamps]
    if not re.search(abbreviation, agencies[-1], re.I):
        return None
    if len({re.sub(abbreviation, '', name, flags=re.I).casefold() for name in agencies}) != 1:
        return None
    if kind == 'reported_scope':
        scope = later.match(_SCOPE_REPORT, 16000)
        if (not scope or scope.start() < ref.end() or later.body[ref.end():scope.start()].strip()
                or any(scope[k].casefold() != v.casefold()
                       for k, v in (('paragraph', request['paragraph']), ('issuer', issuer)))):
            return None
        paragraph = scope['paragraph']
        replaced, intended = f'whole of paragraph {paragraph}', f'introductory text of paragraph {paragraph}'
        return _combine(kind, f'The agency reported that a typographical error led to replacement of the {replaced}. '
                              f'It said it intended to correct only the {intended}.',
                        {'reported_replaced_scope': replaced, 'intended_scope': intended,
                         'instruction': scope['instruction']},
                        earlier.cites(stamps[0]), previous.cites(stamps[1], prior), later.cites(stamps[2], ref, scope))
    if _MONTHS[earlier.date.month - 1].casefold() != request['earlier'].casefold():
        return None
    application = later.match(_APPLICABILITY, 16000)
    values = [p.match(_EFFECTIVE, 16000) for p in (earlier, previous, later)]
    if not application or not all(values) or application['issuer'].casefold() != issuer.casefold():
        return None
    original_date, correction_date, later_date = [_date(m['effective']) for m in values]
    if (not original_date or not later_date or original_date != correction_date
            or original_date >= later_date or _date(application['original']) != earlier.date
            or any(_date(application[k]) != original_date for k in ('described', 'applicable'))):
        return None
    applicable, effective = (_date_display(d) for d in (original_date, later_date))
    return _combine(kind, f'The follow-up reaffirms {applicable} as the stated applicability date. '
                          f'Its own listed effective date is {effective}.',
                    {'applicability_date': applicable, 'later_effective_date': effective},
                    earlier.cites(stamps[0], values[0]), previous.cites(stamps[1], prior, values[1]),
                    later.cites(stamps[2], ref, application, values[2]))


def prove(index, request):
    if len(index.records) > _MAX_FILES or sum(len(r.body_html) for r in index.records) > _MAX_SCAN:
        return 'reference_scan_budget', None
    publications = []
    for record in index.records:
        body = body_text(record.body_html)
        header = re.match(_HEADER, body, re.I)
        if header and _date(header['date']):
            publications.append(Publication(record, body, header))
    kind, arguments = request
    handler = {'venue': _venue, 'deadline': _deadline, 'instructions': _instructions}.get(kind)
    claim = handler(publications, arguments) if handler else _successive(publications, arguments, kind)
    return 'supported_documentary_assertion' if claim else 'documentary_link_unverified', claim
