"""Presentation-only removal of obvious Wiki navigation/template debris.

This never changes a captured page, its hash, source pin, or eligibility.
Only complete source lines that look like rendered template parameters are hidden;
remaining lines are returned unchanged. Absence of clean lines is not evidence.
"""
import re

VERSION = "source-preview-v1"

# Navbox/infobox parameter fragments left by some complex Wiki templates.
_FIELDS = re.compile(r"(?:^|[|}\s])(?:above(?:style)?|list\d+(?:name|title|style|titlestyle)?|group\d+(?:name|style)?|bodyclass|titlestyle)\s*=", re.I)
_CSS = re.compile(r"(?:padding|background-color|border-top|display)\s*:\s*[^;\n]{0,80}", re.I)


def navigation_debris(line):
    text = line.strip()
    if not text:
        return False
    # Require distinctive template/CSS syntax, not ordinary encyclopedic prose.
    return bool(_FIELDS.search(text) and
                (_CSS.search(text) or len(_FIELDS.findall(text)) >= 2
                 or re.match(r"^[}|\s]+", text)))


def readable_lines(source):
    """Keep original literal lines; do not reconstruct or paraphrase facts."""
    return [line.strip() for line in source.splitlines()
            if line.strip() and not navigation_debris(line)]


def preview(source):
    return "\n".join(readable_lines(source))
