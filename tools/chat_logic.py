"""Bounded contextual chat; explicit source facts and auditable inference rules."""
import hashlib
import json
from pathlib import Path
import re
from datetime import datetime, timezone
from mplpb_combined import ledger as L, reader as R, provenance_gate as G
from mplpb_combined.delivery import external_restriction
from mplpb_combined.record import text_of

VERSION = 'explicit-chat-rules-v1'
RULES = {
    'CTX-1': 'Replace explicit it/its/this topic/that topic with the selected topic, after rechecking its page pin.',
    'CTX-2': 'Literal more/continue/show-source follow-ups request the selected page verbatim; they add no facts.',
    'REL-1': 'Only the explicit relate arrow and is-X-a-Y / is-X-related-to-Y grammars select a structured relation query.',
    'FACT-1': 'Read a literal Fact: subject | predicate | object line from an eligible sealed page. This is a source assertion.',
    'TYPE-1': 'A subclass_of B and B subclass_of C imply A subclass_of C.',
    'TYPE-2': 'A instance_of B and B subclass_of C imply A instance_of C.',
    'REFUSE-1': 'No supported fact path means unknown, not false; source co-presence does not establish a relationship.',
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def eligible(root, profile):
    ledger = L.Ledger(root)
    p = R.PROFILES[profile]
    return [r for r in ledger.servable() if not external_restriction(r, p)
            and (p.max_depth is None or ledger.depth(r) <= p.max_depth)]


def context_for(root, title, profile):
    matches = [r for r in eligible(root, profile) if r.title.casefold() == title.casefold()]
    if len(matches) != 1:
        raise ValueError('Choose one exact eligible page title; absent or ambiguous topic')
    r = matches[0]
    if r.path not in {s['path'] for s in G.gather(root, title, R.PROFILES[profile]).sources}:
        raise ValueError('Topic is excluded by the provenance gate')
    return {'title': r.title, 'id': r.id, 'path': r.path, 'hash': r.hash}


def facts(root, profile, question=''):
    out = []
    allowed = {s['path'] for s in G.gather(root, 'Fact', R.PROFILES[profile]).sources}
    for r in eligible(root, profile):
        if r.path not in allowed or (R.PROFILES[profile].not_for and R.terms(question) & R.not_for_terms(r)):
            continue
        for line in text_of(r.body_html).splitlines():
            match = re.fullmatch(r'Fact: ([^|\n]{1,160}) \| (instance_of|subclass_of|related_to) \| ([^|\n]{1,160})', line.strip())
            if match:
                subject, predicate, obj = match.groups()
                out.append({'subject': subject.strip(), 'predicate': predicate, 'object': obj.strip(),
                            'premises': [{'id': r.id, 'hash': r.hash, 'path': r.path, 'quote': line.strip()}],
                            'rules': ['FACT-1'], 'status': 'source_assertion'})
    if len(out) > 200:
        raise ValueError('Structured fact limit exceeded')
    return out


def relations(root, profile, subject, obj):
    direct = facts(root, profile, subject + ' ' + obj)
    known = {}
    for fact in direct:
        key = (fact['subject'].casefold(), fact['predicate'], fact['object'].casefold())
        if key in known:
            known[key]['premises'] += fact['premises']
        else:
            known[key] = dict(fact, premises=list(fact['premises']))
    for _ in range(6):
        added = []
        for a in list(known.values()):
            for b in direct:
                if a['object'].casefold() != b['subject'].casefold() or b['predicate'] != 'subclass_of':
                    continue
                rule = {'subclass_of': 'TYPE-1', 'instance_of': 'TYPE-2'}.get(a['predicate'])
                if not rule or a['subject'].casefold() == b['object'].casefold():
                    continue
                key = (a['subject'].casefold(), a['predicate'], b['object'].casefold())
                if key in known:
                    continue
                premises = list({(p['id'], p['hash'], p['quote']): p for p in a['premises'] + b['premises']}.values())
                added.append((key, {'subject': a['subject'], 'predicate': a['predicate'], 'object': b['object'],
                                    'premises': premises, 'rules': list(dict.fromkeys(a['rules'] + b['rules'] + [rule])),
                                    'status': 'rule_inference'}))
        if not added:
            break
        for key, fact in added:
            known.setdefault(key, fact)
        if len(known) > 1000:
            raise ValueError('Inference limit exceeded; narrow the corpus')
    return [f for f in known.values() if f['subject'].casefold() == subject.casefold()
            and f['object'].casefold() == obj.casefold()]


def turn(app, corpus, root, profile, message, context):
    reasoning = []
    if context:
        try:
            fresh = context_for(root, context['title'], profile)
            if fresh != context:
                raise ValueError('Topic changed')
        except ValueError:
            return {'kind': 'clarify', 'message': 'The selected topic changed or is withheld. Choose it again before a follow-up.',
                    'context': None, 'reasoning': ['Context page pin no longer matches.'], 'sources': []}
    if message.lower().startswith('topic '):
        context = context_for(root, message[6:].strip(), profile)
        return {'kind': 'topic', 'message': 'Topic selected: ' + context['title'], 'context': context,
                'reasoning': ['Exact eligible title selected; page hash pinned.'], 'sources': [context]}
    referential = bool(re.search(r'\b(it|its|this topic|that topic)\b', message, re.I))
    expanded = message
    if referential:
        if not context:
            return {'kind': 'clarify', 'message': 'Which topic do you mean? Use “topic Exact title” or select a page.',
                    'context': None, 'reasoning': ['No selected topic for this follow-up.'], 'sources': []}
        expanded = re.sub(r'\b(this topic|that topic|its|it)\b', lambda _: context['title'], message, flags=re.I)
        reasoning.append({'rule': 'CTX-1', 'expanded_question': expanded, 'context_pin': context})
    if message.lower().strip(' ?.!') in {'tell me more', 'more', 'continue', 'show source', 'show page'}:
        if not context:
            return {'kind': 'clarify', 'message': 'Select a topic first.', 'context': None,
                    'reasoning': ['CTX-2 needs a selected topic.'], 'sources': []}
        expanded = context['title']
        reasoning.append({'rule': 'CTX-2', 'expanded_question': expanded, 'context_pin': context})
    # Deliberate command grammar, not semantic extraction from arbitrary prose.
    relation = re.fullmatch(r'relate (.{1,160}?)\s*->\s*(.{1,160})', expanded, re.I)
    if not relation:
        relation = re.fullmatch(r'is (.{1,160}?) (?:a|an|related to) (.{1,160})', expanded.rstrip('?.!'), re.I)
    if relation:
        reasoning.append({'rule': 'REL-1', 'expanded_question': expanded})
        subject, obj = (v.strip() for v in relation.groups())
        results = relations(root, profile, subject, obj)
        if not results:
            bundle = G.gather(root, subject + ' ' + obj, R.PROFILES[profile]).to_dict()
            return {'kind': 'unknown_relation', 'message': 'No supported structured relationship is encoded for these subjects. Unknown, not false.',
                    'context': context, 'reasoning': reasoning + [{'rule': 'REFUSE-1'}], 'relations': [], 'gate': bundle, 'sources': bundle['sources']}
        return {'kind': 'relations', 'message': 'Supported by the source assertions and rules below; source truth is not authenticated.',
                'context': context, 'reasoning': reasoning, 'relations': results,
                'sources': list({(p['id'], p['hash']): p for f in results for p in f['premises']}.values())}
    result = app.query({'corpus': corpus, 'profile': profile, 'question': expanded})
    reader = result['reader']
    if reader['kind'] == 'return':
        message_out = reader['text']
        context = context_for(root, reader['title'], profile)
    elif reader['kind'] == 'ambiguous':
        message_out = 'Several eligible pages match. Choose a topic; I cannot select one as the answer.'
    else:
        message_out = 'No eligible page owns this question. I cannot answer it from this corpus.'
    return {'kind': reader['kind'], 'message': message_out, 'context': context,
            'reasoning': reasoning + [{'rule': 'MPLPB reader', 'matched_on': reader['matched_on'], 'reason': reader['reason']}],
            'reader': reader, 'gate': result['gate'], 'sources': result['gate']['sources']}


def log_turn(log, payload):
    entry = {'index': len(log) + 1, 'at': datetime.now(timezone.utc).isoformat(),
             'previous_sha256': log[-1]['sha256'] if log else None, 'payload': payload,
             'logic_version': VERSION, 'logic_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    entry['sha256'] = digest(entry)
    log.append(entry)
    return entry


def verify_log(log):
    previous = None
    for index, entry in enumerate(log, 1):
        content = {k: v for k, v in entry.items() if k != 'sha256'}
        if entry.get('index') != index or entry.get('previous_sha256') != previous or digest(content) != entry.get('sha256'):
            return False
        previous = entry['sha256']
    return True
