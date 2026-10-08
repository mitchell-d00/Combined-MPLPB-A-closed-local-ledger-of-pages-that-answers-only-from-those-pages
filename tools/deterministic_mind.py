"""Finite conversational intents over sealed pages and declared working notes."""
import re
from mplpb_combined.record import text_of
from tools import chat_logic as C

VERSION = 'deterministic-mind-v1'

# Interface instructions, not corpus facts. Matching is finite and explicit.
HELP = {
 'start': ('Start here', 'Choose Chat. Select Simple English Wikipedia for exploration without an API key. Send “search dinosaurs” to build a new collection, then “what is it?” or “summarize it”. For pages already loaded, use “topic Exact title”. Ask “how do I search?”, “how do I save?” or “how do I reset?” for one step at a time.'),
 'search': ('Search and build', 'Choose Simple English Wikipedia or English Wikipedia in the menu beside Send, then type “search dinosaurs”. This builds a separate saved MPLPB from up to five pinned pages. General Web mode needs a deployed crawler URL and access token in crawler settings. Wikipedia mode needs neither. “find dinosaurs” lists Wikipedia titles for manual import.'),
 'ask': ('Ask about pages', 'After a search build, ask “what is it?”, “summarize it” or “show source”. To change focus within the collection, send “topic Exact page title”, using a title from Explore. Ordinary questions use literal word matching. I may refuse a paraphrase or stop when several pages match. I do not guess missing facts.'),
 'save': ('Save your work', 'The hosted browser app saves sources and chat in this browser after each successful operation. Refresh to resume; no Save command is needed. Use Export transcript for a copy of your chat and pins. That export is not a full source-store backup. Clearing browser storage or storage eviction can erase saves. The crawler access token is not saved and must be entered again after reload.'),
 'reset': ('Restart or reset', 'Restart MPLPB clears the selected chat and working notes, while retaining its source pages. Open “Build and search your MPLPB collections”, then “Clear saved MPLPBs”. Tick one or several collections and choose “Clear selected MPLPBs”, or choose “Clear all my collections”. Confirm the named list to remove those collections and chats from active state. Prior sources and chats stay in local archives; this does not purge storage. Bundled examples stay. “forget notes” only clears working notes.'),
 'sources': ('Sources and revisions', 'Open Explore for the collection’s page titles. “show source” reads the selected page. Revision tree shows retained captures and history. “Crawl and build record” shows the search, limits, links and failures. Pins check recorded bytes, not truth or authorship. A changed or invalid pin stops serving; previous files are retained.'),
 'refusal': ('Why I stopped', 'One eligible lexical owner returns a page; several matches stop as ambiguous; none refuses. Paraphrases can miss. Try an exact page title with “topic Exact title”, then “what is it?”. A blocked capture needs reimport or restoration, not a made-up answer. “why?” shows the previous decision’s historical rule trace.'),
 'memory': ('Working notes', 'Send “remember I am studying fossils” to save a working note, “memory” to list notes, or “forget notes” to clear them. Notes are your declarations, not verified source facts. Each collection has its own saved chat; a new search build starts a separate chat.'),
 'limits': ('What I can do', 'I can build bounded source collections, select exact topics, quote or summarize source text, keep working notes, and apply named rules to explicit structured facts. I am deterministic and use no language model. I do not understand every phrasing or invent facts. Wikipedia exploration works directly; general web exploration requires the separate crawler backend.'),
}
HELP_ALIASES = {
 'start': {'help','help me','can you help','can you help me','how do i use this','how do i use you','how to use mplpb','how do i use mplpb','how does this work','how do i start','get started','what can i say','teach me how to use this','i am new','i am confused'},
 'search': {'how do i search','how can i search','how to search','how do i search a topic','can you search the web','how do i build a collection','how do i build an mplpb','how do i build a mplpb','do i need an api key','is search free','where are crawler settings'},
 'ask': {'how do i ask a question','what should i ask','what do i do next','how do i chat','how do i change topic','how do i select a topic','how do i summarize','how do i ask about a page'},
 'save': {'how do i save','how do i save my chat','will you remember this','does it save','is my chat saved','where is my data saved','how do i export','how do i export my chat','will this survive refresh'},
 'reset': {'how do i reset','how do i restart','how do i delete a collection','what does reset do','what does restart do','how do i clear my chat','how do i clear collections','how do i clear all','how do i delete mplpb','clear mplpb','delete mplpb'},
 'sources': {'where are the sources','how do i see sources','how do i see revisions','what is a pin','what are pins','what is provenance','where is the revision tree'},
 'refusal': {'why did you refuse','why can you not answer','why did you stop','what does ambiguous mean','why is my page blocked','what does blocked mean'},
 'memory': {'how do i remember something','how do i add a note','how do i use memory','how do i clear notes','what are working notes'},
 'limits': {'what can you do','what are your limits','are you ai','are you a language model','can you answer anything','are you deterministic'},
}

def help_reply(message, context):
    key = re.sub(r'\s+', ' ', re.sub(r"[?!.,]", '', message.casefold().replace('’', "'"))).strip()
    key = re.sub(r"\bi'm\b", 'i am', key)
    key = re.sub(r"\bcan't\b", 'can not', key)
    key = re.sub(r'^(?:please |explain |tell me )', '', key)
    if key in {'hello','hi','hey','good morning','good afternoon','good evening'}:
        return reply('help', 'Hi! I can help you explore your local pages. Ask “how do I use this?” for a quick start, or “how do I search?” to build a topic collection.', context, 'HELP-GREETING')
    if key in {'thanks','thank you','thank you so much','ok','okay','got it'}:
        return reply('help', 'You’re welcome. Ask “what do I do next?” if you need another step.', context, 'HELP-ACK')
    if key in {'how are you','how are you doing'}:
        return reply('help', 'Ready to help with your pages. I do not have feelings. What would you like to explore? Ask “how do I search?” to get started.', context, 'HELP-GREETING')
    search_help = re.fullmatch(r'how (?:do|can) i (?:search for|search|learn about|explore) (.{1,160})', key)
    if search_help:
        return reply('help', 'Choose a Wikipedia mode beside Send, then send “search '+search_help[1]+'”. That builds a new local collection. After it finishes, ask “what is it?” or “summarize it”. Web mode instead needs the hosted crawler setup. This reply has not made a network request.', context, 'HELP-SEARCH', authority='interface_instructions')
    for topic, aliases in HELP_ALIASES.items():
        if key in aliases:
            title, body = HELP[topic]
            return reply('help', title + '\n\n' + body, context, 'HELP-' + topic.upper(), authority='interface_instructions')
    return None

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
    guide = help_reply(message, context)
    if guide is not None: return guide
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
