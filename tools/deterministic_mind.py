"""Finite conversational intents over sealed pages and declared working notes."""
import re
from mplpb_combined.record import text_of
from tools import chat_logic as C

VERSION = 'deterministic-mind-v1'

def reply(kind, message, context, rule, sources=None, **extra):
    return dict(kind=kind, message=message, context=context,
                reasoning=[{'rule': rule}], sources=sources or [], **extra)

def selected(root, profile, context):
    if not context or C.context_for(root, context['title'], profile) != context:
        raise ValueError('Choose an exact eligible topic again; the selected source is missing, changed or withheld.')
    return context

def excerpt(root, profile, pin):
    selected(root, profile, pin)
    record = next(r for r in C.eligible(root, profile) if r.path == pin['path'])
    paragraphs = [p.strip() for p in text_of(record.body_html).splitlines() if p.strip()]
    # Verbatim source fragments, bounded; never assemble new factual sentences.
    return '\n\n'.join(paragraphs[:3])[:1600]

def handle(root, profile, message, context, memory):
    """Return None for intents delegated to the original reader/chat rules."""
    key = message.casefold().strip(' ?.!')
    notes = memory.setdefault('notes', [])
    if key in {'hello', 'hi', 'hey', 'help', 'what can i say'}:
        return reply('help', 'Select a page with “topic Exact title”. Use “summarize it”, “compare Title A vs Title B”, “remember NOTE”, “memory”, “forget notes”, or “why?”. Search/import are explicit network commands. Restart clears this session, not the source ledger.', context, 'INTENT-1')
    if message.casefold().startswith('remember '):
        note = message[9:].strip()
        if not note or len(note) > 600 or len(notes) >= 20:
            raise ValueError('Notes need 1–600 characters; at most 20. Forget notes to free space.')
        if note not in notes:
            notes.append(note)
        return reply('memory', 'Saved as your declaration, not verified source evidence: ' + note, context, 'NOTE-1')
    if key in {'memory', 'what do you remember', 'show memory'}:
        return reply('memory', '\n'.join(notes) if notes else 'No working notes saved.', context, 'NOTE-1', notes=list(notes), authority='user_declaration')
    if key in {'forget notes', 'forget memory'}:
        notes.clear()
        return reply('memory', 'Working notes cleared. Historical turns remain in the transcript until restart.', context, 'NOTE-2')
    if key in {'forget topic', 'clear topic'}:
        return reply('topic', 'Selected topic cleared. Notes and transcript retained.', None, 'CTX-3')
    if key in {'why', 'why did you say that', 'explain your decision'}:
        previous = memory.get('last')
        if not previous:
            return reply('clarify', 'There is no earlier decision to explain.', context, 'WHY-1')
        # Old explanations are historical, never evidence for a new answer.
        return reply('explanation', 'Historical decision trace:\n' + '\n'.join(str(r) for r in previous['reasoning']), context, 'WHY-1', historical=True, decision=previous)
    summary = re.fullmatch(r'(?:summarize|explain|tell me about) (.+)', message.strip(), re.I)
    if summary:
        title = summary[1].strip().rstrip('?.!')
        try:
            pin = selected(root, profile, context) if title.casefold() in {'it', 'this topic', 'that topic'} else C.context_for(root, title, profile)
            return reply('summary', excerpt(root, profile, pin), pin, 'QUOTE-1', [pin], extractive=True)
        except ValueError as exc:
            return reply('clarify', str(exc), None, 'QUOTE-1')
    comparison = re.fullmatch(r'compare (.{1,160}?) vs (.{1,160})', message.strip().rstrip('?.!'), re.I)
    if comparison:
        try:
            pins = [C.context_for(root, t.strip(), profile) for t in comparison.groups()]
            rows = [{'title': p['title'], 'quote': excerpt(root, profile, p), 'source': p} for p in pins]
            return reply('comparison', '\n\n'.join(r['title'] + ':\n' + r['quote'] for r in rows), context, 'COMPARE-1', pins, comparison=rows,
                         notice='Separate source excerpts. Co-presence establishes no relationship.')
        except ValueError as exc:
            return reply('clarify', str(exc), context, 'COMPARE-1')
    return None

def record(memory, result):
    if result['kind'] != 'explanation':
        memory['last'] = {'kind': result['kind'], 'reasoning': result.get('reasoning', []),
                          'source_pins': [{k: s[k] for k in ('id', 'hash', 'path') if k in s} for s in result.get('sources', [])]}
