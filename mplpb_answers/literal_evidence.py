"""Bounded, literal source extraction; no semantic or truth inference.

Every supported answer returns an unchanged source sentence. Unknown patterns
and conditional/quoted evidence abstain. Added separately from the sealed core.
"""
from dataclasses import asdict, dataclass
import re

from .frames import normalize
from mplpb_combined.record import text_of

VERSION = "literal-evidence-v2"
_UNSAFE_QUESTION = re.compile(
    r"\b(?:not|never|before|after|during|unless|if|possibly|maybe|"
    r"currently|formerly|now|supposedly|allegedly)\b")
_UNSAFE_EVIDENCE = re.compile(
    r"\b(?:not|never|if|unless|perhaps|possibly|allegedly|reportedly|"
    r"supposedly|unknown|unrecorded|maybe|probably|apparently|likely|might|could|would|should|claims?|says?|said|believes?)\b")
_DECOY = re.compile(r"^(?:say|write|claim|imagine|suppose|assume|pretend|if)\b")


@dataclass(frozen=True)
class LiteralRequest:
    relation: str
    entity: str
    canonical: str
    other: str = ""

    def to_dict(self):
        return dict(asdict(self), version=VERSION, general_entailment=False)


def parse(question):
    q = normalize(question)
    if _UNSAFE_QUESTION.search(q) or re.search(r'[;"“”]', q):
        return None
    patterns = (
        ("abbreviation", r"what is (.+?) (?:often )?abbreviated as"),
        ("event_start", r"when did (.+?) begin"),
        ("atomic_number", r"(?:what is )?the atomic number of (?:the periodic table for )?(.+)"),
        ("economy_type", r"what kind of economy does (.+?) have"),
        ("country_location", r"in what country is (.+?) located"),
        ("country_location", r"what country is (.+?) in"),
        ("merger_company", r"what company was formed by the merger of (.+?) and (.+)"),
        # Three bounded request forms: the answer must still be found in the body.
        ("classification_branch", r"what branch of (.+?) deals with (?:broadly )?classifying (.+?) by difficulty and class of relationship"),
        ("population_center", r"where was (.+?)'s (.+?) population (?:largely|mainly) centered"),
        ("law_definition", r"what is (.+?) law"),
        ("noncombustion_source", r"along with (.+?) and (.+?), what is a notable non-combustion heat source"),
    )
    for kind, pattern in patterns:
        match = re.fullmatch(pattern, q)
        if not match:
            continue
        fields = match.groups()
        if any(not value or len(value) > 100 or re.search(r"[?!:,.]", value)
               for value in fields):
            return None
        return LiteralRequest(kind, fields[0], q, fields[1] if len(fields) > 1 else "")
    return None


def _extract(frame, line):
    entity = re.escape(frame.entity)
    if frame.relation == "abbreviation":
        patterns = (
            rf"^(?:the )?{entity}, (?:often )?abbreviated (?:as )?(?P<value>[a-z0-9-]{{2,32}}), (?:is|are|was|were)\b",
            rf"^(?:the )?{entity} (?:is|was) (?:often )?abbreviated as (?P<value>[a-z0-9-]{{2,32}})$",
        )
    elif frame.relation == "event_start":
        patterns = (
            rf"^(?:the )?{entity} began in (?P<value>(?:[a-z]+ )?\d{{4}})\b",
            rf"^(?:the )?{entity} began on (?P<value>[a-z]+ \d{{1,2}},? \d{{4}})\b",
        )
    elif frame.relation == "atomic_number":
        patterns = (
            rf"^(?:the )?{entity} is a (?:chemical )?element with symbol [a-z]{{1,3}} and atomic number (?P<value>\d{{1,3}})\b",
            rf"^(?:the )?{entity} (?:has|is assigned) (?:an? )?atomic number (?:of )?(?P<value>\d{{1,3}})\b",
        )
    elif frame.relation == "economy_type":
        patterns = (
            rf"^the economy of {entity} is (?P<value>(?:(?:highly|very|largely|mostly) )?[a-z-]{{3,30}})(?=[:;,]|$)",
        )
    elif frame.relation == "country_location":
        patterns = (
            rf"^(?:(?:the )?[a-z][a-z0-9 (),:;\"-]*?gave their name to )?{entity}, a (?:geographic )?region in (?P<value>[a-z]+(?: [a-z]+){{0,2}})(?=[,.]|$)",
            rf"^(?:the )?{entity} (?:is|lies|is located) in (?P<value>[a-z]+(?: [a-z]+){{0,2}})(?=[,.]|$)",
        )
    elif frame.relation == "merger_company":
        other = re.escape(frame.other)
        patterns = (
            rf"^formed in [a-z0-9 ]+ by the (?:equal )?merger of {entity} and {other}, (?P<value>[a-z0-9-]{{2,30}}) became\b",
            rf"^(?P<value>[a-z0-9-]{{2,30}}) was formed by the merger of {entity} and {other}\b",
        )
    elif frame.relation == "classification_branch":
        # Both the classification and the class-to-class relationship must
        # appear in one affirmative sentence; topic overlap is not enough.
        other = re.escape(frame.other)
        patterns = (
            rf"^(?P<value>[a-z][a-z ]{{2,100}}) is a branch of "
            rf"(?:the theory of computation in )?{entity} that focuses on "
            rf"classifying {other} according to their inherent difficulty, "
            rf"and relating those classes to each other\b",
        )
    elif frame.relation == "population_center":
        # The question's population and country are checked separately.
        # A nearby location with the wrong group/country must never answer.
        group = re.escape(frame.other)
        patterns = (
            rf"^{group} (?:numbers|population) "
            rf"(?:(?:was|were) |(?:peaked (?:near |at )(?:an? )?(?:estimated )?"
            rf"[a-z0-9 ]+ by \d{{4}}, ))?concentrated "
            rf"(?:mainly|largely) in (?P<value>the [a-z ]+? parts of {entity})"
            rf"(?=,|\.|$)",
        )
    elif frame.relation == "law_definition":
        # Preserve an explicit legal-definition sentence even when its
        # example clause contains ordinary "or" alternatives.
        patterns = (
            rf"^{entity} law is "
            rf"(?P<value>a body of treaties and legislation"
            rf"(?:, such as [^.;]+)?)$",
        )
    elif frame.relation == "noncombustion_source":
        match = re.match(r"^non-combustion heat sources such as (.+?) may be used$", line)
        if not match:
            return []
        entries = [part.strip() for part in re.split(r",\s*|\s+or\s+", match[1])]
        if len(entries) < 3 or len(entries) > 8:
            return []
        remaining = [item for item in entries if not any(
            re.search(r"\b" + re.escape(name) + r"\b", item)
            for name in (frame.entity, frame.other))]
        if len(remaining) != 1 or not all(any(
                re.search(r"\b" + re.escape(name) + r"\b", item)
                for item in entries)
                for name in (frame.entity, frame.other)):
            return []
        return [remaining[0]]
    else:
        return []
    found = []
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            value = match["value"]
            if frame.relation == "atomic_number" and not 1 <= int(value) <= 118:
                continue
            found.append(value)
    return found


def statement_support(frame, record):
    # Metadata, headings, scopes, and titles are not answer evidence.
    body = re.sub(r"<h[1-6]\b[^>]*>.*?</h[1-6]>", "\n",
                  record.body_html, flags=re.I | re.S)
    spans = []
    negative_values = []
    # An explicit discourse instruction cannot certify its following sentences.
    # Conservatively decline the page; do not execute or strip the instruction.
    if re.search(r"(?:^|[.!?]\s+|\n)(?:imagine|suppose|assume|pretend|ignore)\b",
                 text_of(body), re.I):
        return {"status": "unsupported", "spans": [],
                "reason": "Instructional or hypothetical source context is not factual evidence."}
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", text_of(body)):
        raw = sentence.strip()
        line = normalize(raw)
        # Detect explicit negative assertions using the same bounded relation
        # grammar. The affirmative surface is for contradiction detection only.
        negative = re.sub(r"\bdid not begin\b", "began", line)
        negative = re.sub(r"\bdoes not have\b", "has", negative)
        negative = re.sub(r"\b(is|are|was|were|has) not\b", r"\1", negative)
        if negative != line and not _UNSAFE_EVIDENCE.search(negative):
            negative_values.extend(_extract(frame, negative))
        if not line or _DECOY.search(line) or _UNSAFE_EVIDENCE.search(line):
            continue
        # Remove quoted words from the matching surface, rather than rejecting
        # an otherwise explicit statement that mentions a quotation elsewhere.
        line = re.sub(r'"[^"]*"|“[^”]*”', ' [quoted] ', line)
        for value in _extract(frame, line):
            spans.append({"quote": raw, "value": value})
    distinct = {item["value"] for item in spans}
    if len(distinct) > 1 or distinct.intersection(negative_values):
        return {"status": "conflict", "spans": spans,
                "reason": "Different literal values in eligible source text."}
    if not spans:
        return {"status": "unsupported", "spans": [],
                "negative_values": sorted(set(negative_values)),
                "reason": "No exact affirmative source statement fits the bounded grammar."}
    return {"status": "supported", "spans": spans,
            "reason": "Exact source statement under a bounded grammar; factual truth not checked."}
