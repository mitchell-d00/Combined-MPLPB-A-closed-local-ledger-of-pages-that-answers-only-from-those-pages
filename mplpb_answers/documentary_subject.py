"""Verify a literal memorandum subject reference against one eligible original."""

from datetime import date
import re

from .body_text import body_text
from .documentary_response import (
    _DAY, _FULL_NAME, _MAX_CHARS, _MAX_LINES, _NAME,
    _citations, _document, _verified_lines,
)
from .documentary_verify import _date_value, source_question
from .passage_admission import Budget


_REQUESTS = tuple(re.compile(form, re.I) for form in (
    rf"Which memorandum does (?P<writer>{_NAME})[’']s subject line identify as the paper submitted to the President\?",
    rf"What memorandum is identified by the subject line of (?P<writer>{_NAME})[’']s memorandum\?",
    rf"Which memorandum is named in (?P<writer>{_NAME})[’']s subject line\?",
))
_TOPIC = r"[A-Za-z][A-Za-z0-9 ,’'()\-]{1,150}"
_REFERENCE = re.compile(
    rf'(?P<topic>{_TOPIC}) Memorandum submitted to (?P<addressee>the President) '
    rf'(?P<date>{_DAY}) by (?P<writer>{_FULL_NAME})'
)
_SUBJECT_MARKER = re.compile(r'SUBJECT(?::.*)?', re.I)
_PROSE_BOUNDARY = re.compile(r'(?:I|We|Our|This|The) [^\n]+[.!?]')
_CORRESPONDENCE_PROSE = re.compile(
    r'(?:Memoranda|Letters|Reports|Notes) from [A-Za-z ,’]+? '
    r'(?:arrived|crossed|reached|were|came) [^\n]+[.!?]'
)
_RECIPIENT = re.compile(rf'President {_NAME}')
_WITNESS_ROLE = 'exact_documentary_subject_witnesses'


def request(question):
    original = source_question(question)
    for pattern in _REQUESTS:
        if match := pattern.fullmatch(original):
            return match['writer']
    return None


def _declares_writer(label, requested):
    name = label.partition(' of the ')[0]
    if not re.fullmatch(_FULL_NAME, name):
        return False
    return (name.casefold() == requested.casefold()
            or name.split()[-1].casefold() == requested.casefold())


def _subject_lines(document):
    lines = document['lines']
    if (len(lines) >= 2 and lines[0][0] == 'SUBJECT'
            and sum(bool(_SUBJECT_MARKER.fullmatch(line[0])) for line in lines) == 1):
        return lines
    return []


def _reference_boundary(document, following):
    # Canonical text drops blank lines and indentation. A continuation such
    # as a suffix cannot be discarded just because the first line parses.
    # The FRUS projection can split opening prose around editorial notes.
    prose = [line for line in following[:5] if not line[0].startswith('Editorial note: ')]
    if not prose:
        return False
    if _PROSE_BOUNDARY.fullmatch(prose[0][0]):
        return _verified_lines(document['record'], document['body'], prose[:1], document['ranges'])
    joined = ' '.join(line[0] for line in prose)
    return (len(joined) <= 1200 and bool(_CORRESPONDENCE_PROSE.fullmatch(joined))
            and _verified_lines(document['record'], document['body'], prose, document['ranges']))


def _reference(document):
    lines = _subject_lines(document)
    if not lines:
        return None
    field = lines[:2]
    match = _REFERENCE.fullmatch(lines[1][0])
    if match is None and len(lines) >= 3:
        field = lines[:3]
        match = _REFERENCE.fullmatch(' '.join(line[0] for line in field[1:]))
    if (match is None or not _verified_lines(document['record'], document['body'], field, document['ranges'])
            or not _reference_boundary(document, lines[len(field):])):
        return None
    written = _date_value(match['date'])
    if not written or not written['year']:
        return None
    return match, date(**written), field


def _target_fields(document, reference, written):
    if date(**document['date']) != written or not _RECIPIENT.fullmatch(document['header']['recipient']):
        return None
    lines = _subject_lines(document)
    if (len(lines) < 3 or lines[1][0].casefold() != reference['topic'].casefold()
            or not _PROSE_BOUNDARY.fullmatch(lines[2][0])):
        return None
    subject = lines[:2]
    label = document['header']['writer']
    author = reference['writer']
    signature = []
    if label.casefold() != author.casefold():
        if not label.endswith(' (' + author.split()[-1] + ')'):
            return None
        # An office heading needs a full-name signature. Look at the end of
        # the original body before any editorial description and postscript.
        end = len(lines)
        while end > 3 and lines[end-1][0].startswith(('Editorial note: ', 'P.S. ')):
            end -= 1
        signature = lines[end-1:end]
        if signature[0][0].casefold() != author.casefold():
            return None
    if not _verified_lines(document['record'], document['body'], subject + signature, document['ranges']):
        return None
    return [subject, signature]


def verify(index, max_passages, max_chars):
    writer = request(index.question)
    if writer is None:
        return None
    support = {'scope':'documentary_subject_target', 'original_question':index.question,
               'requested_reference_writer':writer, 'source_support_claims':0,
               'subject_stage':'reference_verification'}
    result = {'documentary_support':support}
    bodies = [(record, body_text(record.body_html)) for record in index.records]
    characters = sum(len(body) for _, body in bodies)
    lines = sum(body.count('\n') + 1 for _, body in bodies)
    support['scan'] = {'characters':characters, 'lines':lines,
                       'max_characters':_MAX_CHARS, 'max_lines':_MAX_LINES}
    if characters > _MAX_CHARS or lines > _MAX_LINES:
        support['subject_stage'] = 'scan_budget'
        return 'abstain', 'reference_scan_budget', result
    documents = [doc for record, body in bodies if (doc := _document(record, body)) and doc['date']['year']]
    references = [doc for doc in documents if _declares_writer(doc['header']['writer'], writer)]
    support['eligible_reference_count'] = len(references)
    if len(references) != 1 or (parsed := _reference(references[0])) is None:
        return 'abstain', 'documentary_subject_reference_unverified', result
    source = references[0]
    reference, written, field = parsed
    support['target_constraints'] = {'writer':reference['writer'], 'date':written.isoformat(),
                                     'addressee':reference['addressee'], 'topic':reference['topic']}
    targets = [(doc, witnesses) for doc in documents
               if doc['record'].path != source['record'].path
               and written < date(**source['date'])
               and (witnesses := _target_fields(doc, reference, written))]
    support.update(subject_stage='target_verification', eligible_target_count=len(targets))
    if len(targets) != 1:
        return 'abstain', 'documentary_subject_target_unverified', result
    target, witnesses = targets[0]
    spans = (_citations(source, [[line] for line in source['head']] + [field])
             + _citations(target, [[line] for line in target['head']] + witnesses))
    budget = Budget(index, max_passages, max_chars)
    admitted = budget.offer(spans, _WITNESS_ROLE)
    support['admission'] = budget.report()
    if not admitted:
        support['subject_stage'] = 'display_budget'
        return 'abstain', 'reader_budget_exceeded', result
    if not index.unchanged():
        return 'abstain', 'source_changed', {}
    support.update(subject_stage='proved', source_support_claims=1, final_source_state='unchanged')
    proposition = {
        'relation':'documentary_subject_target',
        'reference_source_id':source['record'].id,
        'target_source_id':target['record'].id,
        'target_date':written.isoformat(),
        'target_writer_as_named':reference['writer'],
        'target_addressee':reference['addressee'],
        'target_subject':reference['topic'],
        'historical_truth_independently_verified':False,
    }
    text = (f"The subject line identifies the memorandum by {reference['writer']} to "
            f"{reference['addressee']} dated {written.isoformat()} on {reference['topic']}.")
    qualifier = 'Actual submission, receipt, reading, agreement and execution remain unverified.'
    result.update(answer_supported=True, text=text, missing=[],
                  claims=[{'proposition':proposition, 'citations':spans, 'text':text,
                           'source_support_established':True, 'qualifiers':[qualifier]}],
                  sources=[record for record in index.sources
                           if record['path'] in {source['record'].path, target['record'].path}],
                  verification={'structural':True, 'semantic':'bounded_documentary_subject_reference',
                                'truth_verified':False, 'independence_verified':False})
    return 'supported_answer', 'supported_documentary_assertion', result
