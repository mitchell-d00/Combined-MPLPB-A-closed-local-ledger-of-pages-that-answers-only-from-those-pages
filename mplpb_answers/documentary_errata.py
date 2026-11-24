"""Bounded proof of a repository erratum and its earlier verification limit."""
from dataclasses import dataclass
import json
import re
from urllib.parse import urlsplit

from .body_text import body_text
from .documentary_verify import citation, context_ranges
from .relation_graph import _capture_evidence_text

_QUESTION = (r"According to the (?P<repo>[A-Za-z0-9][A-Za-z0-9-]{0,99}) erratum, "
             r"what attribution was withdrawn and what happened to the earlier benchmark scores\?")
_COORDINATE = re.compile(r'/([\w.-]+)/([\w.-]+)/([a-f0-9]{40})/([\w./-]+\.md)', re.ASCII)
_HASH = re.compile(r'[a-f0-9]{64}')
_HEADING = re.compile(r'^# (?P<title>[^\n#]{1,180})$')
_MARKDOWN_HEADING = re.compile(
    r'^[ \t]{0,3}(?:(?P<level>#{1,6})[ \t]+(?P<atx>[^\n]+)|'
    r'(?P<setext>[^#>\n][^\n]*)\n[ \t]{0,3}(?P<underline>=+|-+)[ \t]*)$', re.M)
_QUALIFIED_HEADING = re.compile(
    r'\b(?:hypothetical|conditional|sample|examples?|scenarios?|proposed|quotations?|quoted|mock)\b', re.I)
_CORRECTION_HEADING = re.compile(r'(?P<title>.+?) [—–] [^\n]{1,80} attribution correction', re.I)
_VERSION = r'[0-9]{1,6}(?:\.[0-9]{1,6}){1,3}'
_RELEASE = re.compile(rf'\bCorrected in version (?P<version>{_VERSION})\.', re.I)
_EARLIER = re.compile(rf'\bVersion (?P<version>{_VERSION})\b', re.I)
_WITHDRAWAL = re.compile(
    rf'\bVersion (?P<version>{_VERSION}) mistakenly referred to [“"](?P<wording>[^”"\n]{{3,150}})[”"]'
    r'\s+That attribution(?:\s+was introduced during (?:preparation|drafting) of this (?:review|report) and)?'
    r'\s+is withdrawn\.', re.I)
_SCORES = re.compile(
    r'\bNo benchmark scores(?:, underlying\s+source documents or prior experimental outputs)?'
    r'\s+change as a result of this erratum\.', re.I)
_LIMIT = re.compile(
    r'\b(?:The|This) (?:available )?(?:package|archive|evidence|record|material) does not '
    r'(?:establish|verify|demonstrate) that [^.!?\n]{3,350}\.', re.I)
_BOUNDARY = re.compile(r'(?:^|[.!?])\s*\Z')
_MARKER = '\nSource capture: '
_MAX_FILES = 64
_MAX_SCAN = 200_000


@dataclass
class Capture:
    record: object
    body: str
    repository: tuple
    source_path: str
    title: re.Match


def parse(question):
    match = re.fullmatch(_QUESTION, question, re.I)
    return ('erratum_report', (), match['repo'].casefold()) if match else None


def _capture(record, repository):
    if record.kind != 'page' or record.derived_from or record.fields.get('corrects-field'):
        return None
    body = _capture_evidence_text(record)
    projected, separator, raw = body_text(record.body_html).partition(_MARKER)
    if not body or not separator or projected != body:
        return None
    manifest = json.loads(raw)
    if not _HASH.fullmatch(manifest['source_sha256']):
        return None
    try:
        url = urlsplit(manifest['source_url'])
    except ValueError:
        return None
    if (url.scheme, url.netloc, url.query, url.fragment) != ('https', 'raw.githubusercontent.com', '', ''):
        return None
    coordinate = _COORDINATE.fullmatch(url.path)
    if not coordinate:
        return None
    owner, name, revision, path = coordinate.groups()
    if (name.casefold() != repository or owner in {'.', '..'}
            or any(segment in {'', '.', '..'} for segment in path.split('/'))):
        return None
    title = _HEADING.fullmatch(body.split('\n', 1)[0])
    if not title:
        return None
    return Capture(record, body, (owner.casefold(), name.casefold(), revision), path, title)


def _unique(pattern, text):
    matches = list(pattern.finditer(text))
    return matches[0] if len(matches) == 1 else None


def _markdown_scope(body, start):
    headings = {}
    for heading in _MARKDOWN_HEADING.finditer(body, 0, start):
        level = len(heading['level']) if heading['level'] else 1 + heading['underline'].startswith('-')
        headings = {depth: title for depth, title in headings.items() if depth < level}
        headings[level] = heading['atx'] or heading['setext']
    return headings.values()


def _unqualified(capture, matches):
    ranges = context_ranges(capture.record, document_draft=True)
    for match in matches:
        if any(start < match.end() and match.start() < end for start, end in ranges):
            return False
        if any(_QUALIFIED_HEADING.search(title) for title in _markdown_scope(capture.body, match.start())):
            return False
    return not _QUALIFIED_HEADING.search(capture.title['title'])


def _version_number(value):
    parts = tuple(int(part) for part in value.split('.'))
    return parts + (0,) * (4 - len(parts))


def prove(index, repository):
    if len(index.records) > _MAX_FILES or sum(len(row.body_html) for row in index.records) > _MAX_SCAN:
        return 'reference_scan_budget', None
    captures = [capture for row in index.records if (capture := _capture(row, repository))]
    notices = [(capture, title) for capture in captures
               if (title := _CORRECTION_HEADING.fullmatch(capture.title['title']))]
    if len(notices) != 1:
        return 'erratum_repository_unresolved', None
    notice, title = notices[0]
    release = _unique(_RELEASE, notice.body)
    withdrawn = _unique(_WITHDRAWAL, notice.body)
    scores = _unique(_SCORES, notice.body)
    if (not all((release, withdrawn, scores))
            or _version_number(release['version']) <= _version_number(withdrawn['version'])
            or not _unqualified(notice, (notice.title, release, withdrawn, scores))
            or not all(_BOUNDARY.search(notice.body[:m.start()]) for m in (release, withdrawn, scores))):
        return 'erratum_withdrawal_unverified', None
    earlier = [(capture, version) for capture in captures
               if capture.repository == notice.repository and capture.source_path != notice.source_path
               and capture.title['title'].casefold() == title['title'].casefold()
               and (version := _unique(_EARLIER, capture.body[:600]))
               and version['version'] == withdrawn['version']]
    if len(earlier) != 1:
        return 'erratum_earlier_source_unresolved', None
    old, version = earlier[0]
    wording = withdrawn['wording'].removesuffix('.')
    wording_pattern = re.compile(r'(?<!\w)' + re.escape(wording) + r'(?!\w)')
    wording_match = _unique(wording_pattern, old.body)
    limits = [match for match in _LIMIT.finditer(old.body)
              if wording_match and match.start() <= wording_match.start()
              and wording_match.end() < match.end() and _BOUNDARY.search(old.body[:match.start()])]
    if len(limits) != 1 or not _unqualified(old, (old.title, version, limits[0])):
        return 'erratum_prior_statement_unverified', None
    statement = limits[0].group()
    proposition = {'relation': 'reported_erratum_withdrawal', 'withdrawn_attribution': wording,
                   'earlier_version': version['version'], 'correction_version': release['version'],
                   'earlier_statement': statement, 'benchmark_scores': 'unchanged'}
    witnesses = [citation(source.record, source.body, match.start(), match.end())
                 for source, matches in ((notice, (notice.title, release, withdrawn, scores)),
                                         (old, (old.title, version, limits[0])))
                 for match in matches]
    return 'supported_documentary_assertion', {
        'text': (f'The erratum reports withdrawing the attribution “{wording}” and states that earlier '
                 f'benchmark scores are unchanged. The earlier version states: “{statement}”'),
        'proposition': proposition, 'citations': witnesses, 'source_support_established': True,
        'qualifiers': ['The citations establish what the two documents report. Private execution and '
                       'independent verification of score changes remain unverified.']}
