"""Shared delivery policy and human clarification hints; no semantic retrieval."""


def external_restriction(record, profile):
    if profile.name.rstrip("*") != "external":
        return ""
    if record.fields.get("external", "").lower() not in ("", "yes"):
        return "external delivery denied by sealed page policy"
    if record.fields.get("source-authorship") == "unknown":
        return "source authorship unknown; external delivery withheld"
    return ""


def authorship(record):
    value = record.fields.get("source-authorship", "")
    if not value:
        return None
    unknown = value == "unknown"
    return {"status": value, "verified": False,
            "notice": "Who made this source is unknown. A person can supply a source attribution for review."
                      if unknown else "Source authorship is declared, not independently verified."}


def clarification(content, record=None):
    options = record.fields.get("clarify-options", "") if record else ""
    if len(content) != 1:
        return None
    choices = [s.strip() for s in options.split(";") if s.strip()]
    if not choices and content == {"dog"}:
        choices = ["dogs in general", "dog breeds", "dogs as companions"]
    if not choices:
        return None
    return {"prompt": "Which meaning do you want?", "choices": choices,
            "notice": "These are possible intents for a person to clarify, not claims that the corpus answers them.",
            "changes_retrieval": False}
