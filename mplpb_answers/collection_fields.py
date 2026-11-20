"""Bounded collection predicates over source-declared fields."""
import re

from mplpb_combined.ledger import Ledger, field_name

from .relation_graph import declared_fields, field_contexts

MAX_RECORDS = 4096
MAX_BODY_CHARS = 16000000
_LABEL = r"[A-Za-z][A-Za-z0-9 _-]{0,39}?"
_VALUE = r"[\w][\w .:\-]{0,99}"
_CONDITION = re.compile(rf"({_LABEL}) (is explicitly absent|is|contains)(?: ({_VALUE}))?", re.I)
_UNCERTAIN = re.compile(r"\b(?:unknown|unspecified|undetermined|optional|maybe|possibly|if|unless|except|or)\b", re.I)
_NUMBER = r"\d+(?:\.\d+)?"
_UNITS = r"(?:\s*(?:g|kg|mg|ml|l|oz|lb|cups?|tsp|tbsp))?"
_AMOUNT = _NUMBER + _UNITS
_ITEM = re.compile(rf"(?:(?:{_AMOUNT}) )?([\w-]+(?: [\w-]+)*)", re.I)
_NO_COOK = {"no cook", "no cooking", "no-cook"}


def parse(question):
    """Fully consume a bounded request. Aliases select fields, never evidence."""
    text = " ".join(question.strip().removesuffix("?").split())
    if len(text) > 420:
        return None
    match = re.fullmatch(r"(?:which|list) records (?:where|match) (.+)", text, re.I)
    if match:
        predicates = []
        for clause in re.split(r"\s+and\s+", match[1], flags=re.I):
            part = _CONDITION.fullmatch(clause)
            if not part:
                return None
            label, operator, value = part.groups()
            operator = operator.lower()
            if (operator != "is explicitly absent") != bool(value):
                return None
            # Additional unparsed logical operators cannot be hidden in a literal.
            if value and re.search(r"\b(?:or|except|unless|where|is|contains)\b", value, re.I):
                return None
            predicates.append((field_name(label), operator, value or ""))
        if 1 <= len(predicates) <= 4:
            return tuple(predicates)
        return None
    match = re.fullmatch(r"which recipes contain ([\w-]+)", text, re.I)
    if match:
        return (("ingredients", "contains", match[1]),)
    if re.fullmatch(r"which recipes use no water", text, re.I):
        return (("water", "is explicitly absent", ""),)
    match = re.fullmatch(r"which ([\w-]+) recipes for ([\w-]+) need no cook(?:ing)?", text, re.I)
    if match:
        occasion = match[2].casefold()
        if occasion.endswith("ies"):
            occasion = occasion[:-3] + "y"
        elif occasion.endswith("s") and not occasion.endswith(("ss", "us", "is")):
            occasion = occasion[:-1]
        return (("ingredients", "contains", match[1]), ("occasion", "is", occasion),
                ("preparation", "is", "no cook"))
    match = re.fullmatch(r"which ([\w-]+) spells are level (\d{1,2})", text, re.I)
    if match:
        return (("category", "is", "spell"), ("school", "is", match[1]), ("spell level", "is", match[2]))
    return None


def _match(label, operation, value, wanted):
    value, wanted = (" ".join(item.casefold().split()) for item in (value, wanted))
    if _UNCERTAIN.search(value):
        return None
    if operation == "is":
        if label == "preparation" and wanted in _NO_COOK:
            return value in _NO_COOK
        return value == wanted
    if operation == "contains":
        items = [_ITEM.fullmatch(item.strip()) for item in value.split(",")]
        if any(item is None for item in items):
            return None
        return any(item[1] == wanted for item in items)
    if value in {"none", "absent", "no", "not used"}:
        return True
    amount = re.fullmatch(rf"({_NUMBER}){_UNITS}", value)
    if amount:
        return not amount[1].strip("0.")
    return False if value in {"yes", "present", "used"} else None


def verify(root, gate, predicates):
    """Check all gated records. Missing or conflicting fields stay unknown."""
    if len(gate.sources) > MAX_RECORDS or sum(len(s["text"]) for s in gate.sources) > MAX_BODY_CHARS:
        return "collection_scan_budget", {}
    if any("correction scope unclear" == s["reason"] or
           "field-scoped source requires a field selector" == s["reason"] for s in gate.excluded):
        return "correction_scope_unclear", {}
    records = {r.path: r for r in Ledger(root).servable()}
    sources, claims, unresolved = [], [], 0
    for source in gate.sources:
        record = records.get(source["path"])
        if record is None or record.id != source["id"] or record.hash_actual != source["hash"]:
            return "source_changed", {}
        fields = declared_fields(record)
        citations, decisions = [], []
        for label, operator, wanted in predicates:
            rows = [row for row in fields if row["field"] == label]
            values = {row["value"] for row in rows}
            if not rows or len(values) != 1 or any(row["stacked_field_suspected"] for row in rows) or field_contexts(record, label):
                decisions.append(None)
                continue
            decisions.append(_match(label, operator, rows[0]["value"], wanted))
            citations.extend(rows)
        if False in decisions:
            continue
        if None in decisions:
            unresolved += 1
            continue
        sources.append({k: source[k] for k in ("id", "path", "hash")})
        claims.append({"text": f"{record.id} — " + "; ".join(dict.fromkeys(c["quote"] for c in citations)),
                       "qualifiers": ["Every condition is supported by explicit fields on this source."],
                       "citations": citations})
    complete = bool(gate.sources) and not unresolved
    details = {"evaluated_records": len(gate.sources), "verified_matches": len(claims),
               "unresolved_records": unresolved, "evaluation_complete": complete,
               "complete": complete and bool(claims),
               "predicates": [{"field": field, "operation": op, "value": value}
                              for field, op, value in predicates]}
    return "supported" if details["complete"] else "collection_evidence_incomplete", {
        "text": "\n".join(c["text"] for c in claims), "sources": sources, "claims": claims,
        "collection_filter": details, "answer_supported": details["complete"],
        "missing": ["Some records could not be decided from explicit fields."] if unresolved else [],
    }
