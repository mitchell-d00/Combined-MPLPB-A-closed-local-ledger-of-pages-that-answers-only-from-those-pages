"""Deterministic local lead-text renderer; no network or template expansion.

This deliberately renders only source prose before the first section heading.
Templates, tables, references, file/category links and comments are omitted.
It is a bounded stripper, not MediaWiki's visual rendering or TextExtracts.
"""
import html
import re

VERSION = 'wikitext-lead-stripper-v1'


def strip_balanced(text, opening, closing):
    out = []
    depth = 0
    i = 0
    while i < len(text):
        if text.startswith(opening, i):
            depth += 1
            i += len(opening)
        elif depth and text.startswith(closing, i):
            depth -= 1
            i += len(closing)
        else:
            if not depth:
                out.append(text[i])
            i += 1
    return ''.join(out)


def render(wikitext):
    text = re.sub(r'<!--.*?-->', '', wikitext, flags=re.S)
    text = re.split(r'(?m)^={2,6}[^=\n].*?={2,6}\s*$', text, maxsplit=1)[0]
    text = re.sub(r'<ref\b[^>]*(?:/>|>.*?</ref\s*>)', '', text, flags=re.I | re.S)
    text = strip_balanced(text, '{{', '}}')
    text = strip_balanced(text, '{|', '|}')
    text = re.sub(r'\[\[(?:File|Image|Category):.*?\]\]', '', text, flags=re.I | re.S)
    # Process innermost wiki links first; labels are literal local source text.
    while re.search(r'\[\[[^\[\]]*\]\]', text):
        text = re.sub(r'\[\[([^\[\]]*)\]\]',
                      lambda m: m.group(1).split('|')[-1].split('#')[0], text)
    text = re.sub(r'\[(?:https?://|//)\S+(?:\s+([^\]]*))?\]',
                  lambda m: m.group(1) or '', text)
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r"'{2,5}", '', text)
    text = re.sub(r'(?m)^\s*[*#:;]+\s*', '', text)
    text = html.unescape(text)
    lines = [' '.join(line.split()) for line in text.splitlines()]
    return '\n'.join(line for line in lines if line).strip()
