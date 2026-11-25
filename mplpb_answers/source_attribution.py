"""Finite source-voice bindings; eligibility and final state remain reader-owned."""
import re

from .body_text import body_text
from .documentary_verify import META, citation, context_ranges, quoted_context

NAME = r'(?-i:[A-Z][a-z]+(?: [A-Z][a-z]+){0,3})'
FULL_NAME = r'(?-i:[A-Z][a-z]+(?: (?:[A-Z][a-z]+|[A-Z]\.)){0,3} [A-Z][a-z]+)'
_TITLE = r'(?:(?:Ambassador|Director|Secretary|Minister|Dr\.|Mr\.|Ms\.|Mrs\.) )?'
_SALUTATION = re.compile(rf'^Dear (?P<addressee>{_TITLE}(?P<recipient>{NAME})):[ \t]*$', re.M)
_SIGNATURE = re.compile(
    rf'^(?:Sincerely|Respectfully|Yours sincerely|Yours truly),\n(?P<signer>{FULL_NAME})[ \t]*(?=\n|$)', re.M)


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
