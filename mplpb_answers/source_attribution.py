"""Finite source-voice bindings; eligibility and final state remain reader-owned."""
import re

from .body_text import body_text
from .documentary_verify import META, citation, context_ranges, quoted_context, named_actor, metadata_values

NAME = r'(?-i:[A-Z][a-z]+(?: [A-Z][a-z]+){0,3})'
FULL_NAME = r'(?-i:[A-Z][a-z]+(?: (?:[A-Z][a-z]+|[A-Z]\.)){0,3} [A-Z][a-z]+)'
_TITLE = r'(?:(?:Ambassador|Director|Secretary|Minister|Dr\.|Mr\.|Ms\.|Mrs\.) )?'
_SALUTATION = re.compile(rf'^Dear (?P<addressee>{_TITLE}(?P<recipient>{NAME})):[ \t]*$', re.M)
_SIGNATURE = re.compile(
    rf'^(?:Sincerely|Respectfully|Yours sincerely|Yours truly),\n(?P<signer>{FULL_NAME})[ \t]*(?=\n|$)', re.M)


def printed_writer_label(body, *, require_person=False):
    """A scoped printed label, never authenticated authorship or identity expansion."""
    patterns = [r'^From: (?P<writer>[^\n]+)(?=\n|$)',
                r'^(?P<writer>[^\n]{2,100}?) TO [^\n]{2,120}?\. [^\n]+',
                r'^(?:Report\.\n)?Written by (?P<writer>[^.\n]+)\.?',
                r'^Meeting minutes\.\s*(?:Recorder:|Recorded by) (?P<writer>[^.\n]+)\.?']
    for pattern in patterns:
        match = re.match(pattern, body)
        if match and (not require_person or named_actor(match['writer'])):
            return match['writer'], match.span()
    return None, None


def writer_declarations(record, body):
    """Scoped printed labels and whole-letter signature markers, not identity proof.

    Opaque initials stay opaque. These declarations constrain reference links;
    they do not establish that two historical people are the same individual.
    """
    labels=[]
    name,span=printed_writer_label(body)
    if span and unqualified_span(record,body,*span):labels.append(name)
    greetings=list(_SALUTATION.finditer(body))
    signature=re.search(r'^(?:Sincerely|Respectfully|Yours sincerely|Yours truly),\n(?P<label>[^\n]{1,120})[ \t]*\Z',body,re.M)
    if len(greetings)==1 and signature:
        greeting=greetings[0];prefix=body[:greeting.start()]
        if ((not prefix or metadata_values(prefix) is not None)
                and all(unqualified_span(record,body,*m.span()) for m in (greeting,signature))):
            labels.append(signature['label'].strip())
    return labels


def same_name(requested, declared):
    requested, declared = requested.casefold(), declared.casefold()
    return requested == declared or (' ' not in requested and requested == declared.rsplit(' ', 1)[-1])


def unqualified_span(record, body, start, end):
    """Recheck canonical bytes and documentary governors for a complete witness."""
    return (body_text(record.body_html) == body and 0 <= start < end <= len(body)
            and not any(a < end and b > start for a, b in context_ranges(record))
            and not quoted_context(body[:start]) and not META.search(body[:start]))


def signed_letter(record, author, recipient):
    """Bind printed salutation and full signature in one original letter.

    Call only with a record independently reread by the native checker. This
    proves source voice, not authenticated authorship or an answered question.
    A caller must still resolve competing letters and verify the asserted claim.
    """
    if record.kind != 'page' or record.derived_from or record.fields.get('corrects-field'):
        return None
    body = body_text(record.body_html)
    greetings, signatures = list(_SALUTATION.finditer(body)), list(_SIGNATURE.finditer(body))
    if len(greetings) != 1 or len(signatures) != 1:
        return None
    greeting, signature = greetings[0], signatures[0]
    if (greeting.end() >= signature.start() or not same_name(author, signature['signer'])
            or not same_name(recipient, greeting['recipient'])
            or not all(unqualified_span(record, body, *span.span()) for span in (greeting, signature))):
        return None
    return body, {
        'actor': signature['signer'], 'addressee': greeting['addressee'],
        'source_voice': 'signed_letter_first_person',
        'letter_start': greeting.start(), 'content_start': greeting.end(), 'content_end': signature.start(),
        'witnesses': [citation(record, body, *greeting.span()), citation(record, body, *signature.span())],
    }


def source_frame(record, form):
    """Derive documentary writer and layer from eligible body witnesses.

    Titles and caller labels never supply voice. Quoted speech is subsequently
    bound by its own complete predicate, not inherited from the writer.
    """
    if record.kind != 'page' or record.derived_from or record.fields.get('corrects-field'):
        return None
    body = body_text(record.body_html)
    if form == 'letter':
        greetings, signatures = list(_SALUTATION.finditer(body)), list(_SIGNATURE.finditer(body))
        if len(greetings) != 1 or len(signatures) != 1:
            return None
        greeting, signature = greetings[0], signatures[0]
        binding = signed_letter(record, signature['signer'], greeting['recipient'])
        if not binding or greeting.start() != 0 or signature.end() != len(body):
            return None
        _, voice = binding
        return body, dict(form=form, writer=voice['actor'], start=voice['content_start'],
                          end=voice['content_end'], witnesses=voice['witnesses'])
    labels = {'minutes': ('Meeting minutes.', 'Recorded by'), 'report': ('Report.', 'Written by')}
    if form not in labels:
        return None
    label, byline = labels[form]
    header = re.match(rf'^{re.escape(label)}\n{byline} (?P<writer>{FULL_NAME})\.\n', body)
    if not header or not unqualified_span(record, body, 0, header.end()):
        return None
    return body, dict(form=form, writer=header['writer'], start=header.end(), end=len(body),
                      witnesses=[citation(record, body, 0, header.end()-1)])


_RECIPIENT = r'the [a-z]+(?:[ -][a-z]+){0,7}'
_TASK_TEXT = r'[^.!?;:“”"\n]{3,600}'
_ROLE = rf'(?:I|{FULL_NAME})'
_INSTRUCTION_PATTERNS = [
    rf'(?P<actor>{_ROLE}) (?P<verb>instruct|order|instructed|ordered) (?P<recipient>{_RECIPIENT}) to (?P<task>{_TASK_TEXT})\.',
    rf'(?P<actor>{_ROLE}) (?P<verb>instruct|order|instructed|ordered) (?P<recipient>{_RECIPIENT}): “(?P<task>{_TASK_TEXT})\.”',
    rf'My instruction to (?P<recipient>{_RECIPIENT}) is to (?P<task>{_TASK_TEXT})\.',
    rf'The instruction from (?P<actor>{FULL_NAME}) to (?P<recipient>{_RECIPIENT}) was to (?P<task>{_TASK_TEXT})\.',
    rf'The instruction from (?P<actor>{FULL_NAME}) to (?P<recipient>{_RECIPIENT}) was: “(?P<task>{_TASK_TEXT})\.”',
    rf'To (?P<recipient>{_RECIPIENT}), I give this instruction: “(?P<task>{_TASK_TEXT})\.”',
    rf'(?P<actor>{FULL_NAME}) gave (?P<recipient>{_RECIPIENT}) this instruction: “(?P<task>{_TASK_TEXT})\.”',
    rf'(?P<recipient>{_RECIPIENT}) (?P<copula>is|was) instructed by (?P<actor>me|{FULL_NAME}) to (?P<task>{_TASK_TEXT})\.',
    rf'(?P<recipient>{_RECIPIENT}) received this instruction from (?P<actor>{FULL_NAME}): “(?P<task>{_TASK_TEXT})\.”',
    rf'“(?P<task>{_TASK_TEXT}),” is my instruction to (?P<recipient>{_RECIPIENT})\.',
    rf'“(?P<task>{_TASK_TEXT}),” (?P<actor>{FULL_NAME}) directed (?P<recipient>{_RECIPIENT})\.',
    rf'For (?P<recipient>{_RECIPIENT}), my instruction is to (?P<task>{_TASK_TEXT})\.',
    rf'For (?P<recipient>{_RECIPIENT}), the instruction from (?P<actor>{FULL_NAME}) was to (?P<task>{_TASK_TEXT})\.',
    rf'For (?P<recipient>{_RECIPIENT}), the instruction from (?P<actor>{FULL_NAME}) was: “(?P<task>{_TASK_TEXT})\.”',
    rf'My instruction is for (?P<recipient>{_RECIPIENT}) to (?P<task>{_TASK_TEXT})\.',
    rf"(?P<actor>{FULL_NAME})'s instruction was for (?P<recipient>{_RECIPIENT}) to (?P<task>{_TASK_TEXT})\.",
    rf"(?P<actor>{FULL_NAME})'s instruction for (?P<recipient>{_RECIPIENT}) was “(?P<task>{_TASK_TEXT})\.”",
]
_INSTRUCTION_PATTERNS = [re.compile(p, re.I) for p in _INSTRUCTION_PATTERNS]
_UNRESOLVED_TASK = re.compile(
    r'\b(?:not|never|if|unless|provided|assuming|might|may|could|would|should|denied|'
    r'allegedly|hypothetical|example|supposed|purported|either|neither|instead|only|'
    r'he|she|they|it|this|that|these|those|them|him|her|their|its|my|your|me|we|I)\b', re.I)


def instruction_roles(text):
    """One complete affirmative instruction; no writer or question inference.

    Active, nominal, passive and explicit quotation constructions reduce to the
    same roles. First-person roles require a separately checked signed letter.
    An attribution predicate is retained as reporting, never event/execution.
    """
    matches = [m for pattern in _INSTRUCTION_PATTERNS if (m := pattern.fullmatch(text))]
    if len(matches) != 1:
        return None
    values = matches[0].groupdict()
    actor = values.get('actor') or 'I'
    if actor.casefold() in {'i', 'me'}:
        actor = 'I' if actor.casefold() == 'i' else 'me'
    verb = (values.get('verb') or '').lower()
    if verb and ((actor == 'I') != (verb in {'instruct', 'order'})):
        return None
    task = values['task']
    if (len(values['recipient']) > 180 or _UNRESOLVED_TASK.search(task)
            or not re.fullmatch(r'[A-Za-z][A-Za-z ,\-0-9]*', task)
            or len(task.split()) > 80):
        return None
    return {'speaker': actor, 'first_person': actor in {'I', 'me'},
            'recipient': values['recipient'].lower(), 'task': task[0].lower()+task[1:],
            'quotation': '“' in text, 'modality': 'instruction_only'}
