"""Typed conversational acts around freshly resolved local content.

Conversation framing is separate from evidence. Context selects a subject; it
never supplies a fact or authorizes reading a ledger in off-the-record mode.
"""
import copy
import re
from tools import question_frames as F, deterministic_mind as M
from tools import response_construction as N

VERSION = 'topic-dialogue-v1'
ACTS = {
    'discuss': {"let's talk about it", 'lets talk about it', 'can we talk about this',
                'can we chat about it', 'talk to me about this', "let's discuss it",
                'lets discuss it', 'can we discuss that', 'talk more about that'},
    'interest': {'that is interesting', "that's interesting", 'thats interesting',
                 'interesting', 'sounds interesting', 'i like this topic'},
    'clarify': {'i am confused', "i'm confused", "i don't understand", 'i dont understand',
                'that is confusing', 'help me understand', 'can you explain that part'},
    'perspective': {'what do you think', 'what is your opinion', 'do you like this topic'},
}
CATALOG = re.compile(r"(?:what (?:content|topics|pages) (?:do you have|can we (?:discuss|talk about))|(?:tell me about|discuss|talk about|show me) (?:your content|your pages|the loaded content|what is in (?:your|my|the) mplpb)|what can we (?:discuss|talk about) (?:from|in) (?:the |my |your )?(?:loaded )?(?:mplpb|pages|collections))")


def subject(session):
    mind = session.get('mind', {})
    # The last substantive reply selects which context is being discussed.
    for turn in reversed(session.get('log', [])[-12:]):
        response = turn.get('payload', {}).get('response', {})
        if response.get('self_knowledge'):
            return None
        name = response.get('response_structure', {}).get('subject')
        if name:
            return name
        if (response.get('context') or {}).get('title'):
            return response['context']['title']
    return (session.get('context') or {}).get('title') or mind.get('idea_chat', {}).get('subject') or mind.get('general_reference_topic')


def recognize(message, session):
    key = F.normalize(message).casefold().strip(' .!?')
    if CATALOG.fullmatch(key):return 'catalog'
    # Legacy direct-reader workflows retain their existing navigation controls.
    if not session.get('environment'):return None
    act = next((a for a, forms in ACTS.items() if key in {F.normalize(form).casefold().strip(' .!?') for form in forms}), None)
    return act if act and subject(session) else None


def catalog(app, session, profile):
    from tools import chat_environment as E, general_reference as G
    env = session.get('environment', {})
    roots = app.roots()
    keys = env.get('corpora', []) if env.get('mode') == 'focus' else sorted(roots)
    if env.get('mode') == 'free':keys = []
    entries, blocked = E.pages(app, keys, profile)
    lines = []
    for key in keys:
        titles = [p['title'] for k, p in entries if k == key]
        lines.append(roots[key][0]+': '+(', '.join(titles[:6]) or 'no eligible pages')+
                     ('; '+str(len(titles)-6)+' more pages' if len(titles)>6 else ''))
    label = 'loaded collections' if env.get('mode') == 'focus' else 'saved collections'
    body = ('We can talk about these '+label+':\n\n'+'\n'.join(lines) if lines else
            'There are no eligible '+label+' available in this mode.')
    body += '\n\nI also have short seed notes about '+', '.join(r['topic'] for r in G.records())+'. '
    body += 'We can discuss an idea, explore a page, or look closely at a word’s meaning and synonyms. Which interests you?'
    if env.get('mode') == 'free':body += ' Free chat uses bundled references and conversation only; leave this mode to read ledger collections.'
    return M.reply('conversation', body, session.get('context'), 'CONTENT-CATALOG',
        authority='system_description', blocked_collections=blocked,
        suggestions=['Tell me about '+p['title'] for _,p in entries[:3]]+['general topics'],
        response_structure={'intent':'content_catalog','factual_claims':False,'mplpb_supported':False},
        content_catalog={'collections':keys,'eligible_pages':len(entries),'metadata_is_evidence':False})


def handle(app, data, session, message, corpus, profile):
    act = recognize(message, session)
    if not act:return None
    if act == 'catalog':return catalog(app, session, profile)
    name = subject(session)
    from tools import chat_environment as E, general_reference as G, structured_requests as SR
    shadow = copy.deepcopy(session)
    result = None
    lexical = shadow['mind'].get('lexical_discussion', {})
    if lexical.get('word') == name:
        # Its proof requires an exact renderer. Keep the dictionary payload
        # intact; it offers sense-specific wording as a separate request.
        result = SR.lexical('explain that', shadow)
        if result:
            result['suggestions']=['Other words for that meaning','Tell me about '+name]
            session.clear();session.update(shadow)
            return result
    if session.get('environment', {}).get('mode') != 'free':
        request = 'tell me more' if act=='interest' and shadow['mind'].get('idea_chat',{}).get('sourced') else 'Tell me about '+name
        result = E.retrieve(app, data, shadow, request, corpus, profile,
                            outside=session.get('environment',{}).get('mode')=='focus')
    if result is None:
        request = 'tell me more' if act=='interest' and shadow['mind'].get('general_reference_topic')==name else 'Tell me about '+name
        result = G.handle(request, shadow, allow_all_modes=True)
    turn = len(session.get('log', []))+1
    opener, trace = N.discussion(name, act, turn)
    if result:
        # Keep the source result and all pins available for final revalidation.
        # Framing is never inserted inside a source quotation or lexical proof.
        child = copy.deepcopy(result)
        result['message'] = opener+'\n\n'+result['message']
        result['discussion_payload'] = child
        result['discussion_frame'] = {'subject':name,'act':act,'turn':turn,'construction':trace}
        result['claim_units'] = [
            {'text':opener,'authority':'conversation_structure','sources':[]},
            {'text':child['message'],'authority':child.get('authority'),'sources':copy.deepcopy(child.get('sources',[]))}]
        # Preserve source inspection, scope and all existing evidence markers.
        session.clear();session.update(shadow)
    else:
        result = M.reply('conversation',opener+' What aspect would you like to explore?',
            session.get('context'),'TOPIC-DISCUSSION',authority='conversation_structure',
            suggestions=['Brainstorm '+name,'Tell me about '+name],
            response_structure={'intent':'casual_topic_discussion','subject':name,
                                'factual_claims':False,'mplpb_supported':False,'construction':trace})
    result['topic_dialogue']={'version':VERSION,'act':act,'subject':name,'context_is_evidence':False}
    return result
