"""Check a quoted presentation inside a continuous, named editorial report."""
from datetime import date
import re

from .documentary_verify import DATE, META, _date_value, citation, context_ranges


_PERSON = r'[A-Z][a-z]+(?: [A-Z][a-z]+){0,5}'
_TITLE = r'(?:(?:Mr\.|Ms\.|Mrs\.|Dr\.|Director|Minister|President|Secretary(?: of [A-Z][a-z]+)?) )?'
_DATE = DATE.pattern
_DATELINE = re.compile(rf'^{_PERSON}, (?P<date>{_DATE})\.(?=\n)')
_LEAD = re.compile(
    rf'^On (?P<date>{_DATE}), {_TITLE}(?P<speaker>{_PERSON}) reported to (?P<addressee>{_TITLE}{_PERSON}) '
    r'on the results of a mission (?P<pronoun>he|she|they) had just led [^.!?\n“”]{1,300}\. '
    rf'(?P<reporter>{_PERSON}) reported the trip (?P<assessment>[^.!?\n“”]{{1,420}})\. '
    r'(?P<continuation>He|She|They) also reported positive reactions to '
    r'(?P<possessive>his|her|their) emphasis on (?P<framework>[^.:!?\n“”]{3,100}?) '
    r'as the basis for dealing with [^.:!?\n“”]{3,160}:\n'
)
_QUOTE = re.compile(
    r'“In my (?P<setting>[^,.:!?\n“”]{3,130}), I (?:expressed|presented) '
    r'(?P<approach>[^.:!?\n“”]{3,200}?) in terms of (?P<framework>[^.:!?\n“”]{3,100}) '
    r'expressed as ideals:\n'
    r'(?P<items>(?:“[1-6]\. [^.:!?\n“”]{2,100}\n){2,6})'
    r'“[^.!?\n“”]{3,150}\.” '
)
_MEMO = re.compile(
    rf'\(Memorandum from {_TITLE}(?P<speaker>{_PERSON}) to (?P<addressee>{_TITLE}{_PERSON}), '
    rf'(?P<date>{_DATE}); [^()\n“”]{{1,400}}\)(?=$|\n)'
)
_POSSESSIVES = {'he': 'his', 'she': 'her', 'they': 'their'}
_COUNTS = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}
_UNCERTAIN = re.compile(r'\b(?:not|never|denied|allegedly|possibly|might|unless|if|'
                        r'whether|reportedly|instead|claimed|supposed)\b', re.I)
_SWITCH = re.compile(r'\b(?:according to|said|stated|added|quoted|replied|reported|told|explained)\b', re.I)


def _day(text):
    parsed = _date_value(text)
    return date(parsed['year'], parsed['month'], parsed['day']) if parsed else None


def _surname(text):
    return text.rsplit(' ', 1)[-1]


def _parse(body, speaker, pronoun):
    lead = _LEAD.match(body)
    quote = _QUOTE.match(body, lead.end()) if lead else None
    memo = _MEMO.match(body, quote.end()) if quote else None
    if not memo or META.search(body[:memo.end()]) or _UNCERTAIN.search(body[:memo.end()]):
        return None
    if (lead['pronoun'] != pronoun or lead['continuation'].lower() != pronoun
            or lead['possessive'] != _POSSESSIVES[pronoun]
            or speaker not in {lead['speaker'], _surname(lead['speaker'])}
            or lead['reporter'] != _surname(lead['speaker'])
            or memo['speaker'] not in {lead['speaker'], _surname(lead['speaker'])}
            or _SWITCH.search(lead['assessment'])
            or memo['addressee'] != lead['addressee']
            or _day(memo['date']) != _day(lead['date'])):
        return None
    if not re.search(r'\bmeetings\b', quote['setting']) or quote['framework'] != lead['framework']:
        return None
    lines = quote['items'].splitlines()
    if (_COUNTS.get(quote['framework'].split()[0]) != len(lines)
            or not all(line.startswith(f'“{i}. ') for i, line in enumerate(lines, 1))):
        return None
    return lead, quote, memo, [line[4:] for line in lines]


def verify(originals, advice_record, advice_body, speaker, pronoun):
    dateline = _DATELINE.match(advice_body)
    before = _day(dateline['date']) if dateline else None
    if before is None or any(lo < dateline.end() and hi > 0 for lo, hi in context_ranges(advice_record)):
        return 'advice_dateline_unresolved', None
    if len(originals) < 2:
        return 'presentation_original_missing', None
    matches = []
    for record, body in originals:
        if record.path == advice_record.path:
            continue
        match = _parse(body, speaker, pronoun)
        if match and not any(lo < match[2].end() and hi > 0 for lo, hi in context_ranges(record)):
            matches.append((record, body, match))
    if len(matches) != 1:
        return ('presentation_ambiguous' if matches else 'presentation_attribution_unresolved'), None
    record, body, (lead, quote, memo, items) = matches[0]
    after = _day(lead['date'])
    if not after or after <= before:
        return 'report_chronology_unresolved', None
    text = f"{speaker} said the framework was {quote['framework']}: " + '; '.join(items) + '.'
    claim = {'text': text, 'proposition': {'relation': 'source_quoted_presentation_report',
        'speaker': speaker, 'addressee': lead['addressee'], 'framework': quote['framework'],
        'framework_items': items, 'modality': 'quoted_self_report',
        'reporting_layer': 'editorial_account_quoting_attributed_memorandum',
        'advice_record_date': before.isoformat(), 'report_date': after.isoformat()},
        'citations': [citation(advice_record, advice_body, *dateline.span()),
                      citation(record, body, lead.start(), memo.end())],
        'source_support_established': True,
        'qualifiers': ['The editorial account attributes the quoted report to the speaker. '
                       'The dates establish record order. Event identity and implementation remain unresolved.']}
    return 'supported', claim
