"""Finite request slots shared across chat modes. Context selects; sources prove."""
import copy
import re
from tools import question_frames as F, conversation_memory as CM
from tools import self_knowledge as SK, deterministic_mind as M, dialogue_rules as DR

VERSION = 'structured-requests-v1'
FOLLOWUPS = {'tell me more', 'explain that', 'what does that mean', 'what is it',
             'what is that', 'what is this', 'what about it', 'more', 'continue'}


def parse(message, session):
    text=F.normalize(message).strip(' .?!'); key=CM.key(text)
    base={'version':VERSION,'action':None,'subject':None,'requested_attribute':None,
          'qualifiers':[],'context_reference':None,'original':message}
    # Split only a recognized introduction followed by a complete self-question.
    parts=re.split(r'[,;.!?]*\s+(?=(?:how long|for how long|what|who|how|will you|do you)\b)',text,maxsplit=1,flags=re.I)
    if len(parts)==2 and CM.introduction(parts[0]) and SK.recognize(parts[1]):
        return dict(base,action='introduce_and_explain',subject=CM.introduction(parts[0]),
                    requested_attribute=SK.recognize(parts[1])['topic'],clauses=parts)
    if len(parts)==2 and CM.introduction(parts[0]):
        return dict(base,action='unresolved_compound',subject=CM.introduction(parts[0]),clauses=parts)
    if SK.recognize(text):return dict(base,action='self',requested_attribute=SK.recognize(text)['topic'])
    # Activity selection is distinct from an expression or a statement about maths.
    if re.fullmatch(r'(?:(?:let us|lets|let\'s|i want to|i would like to|i\'d like to) )?(?:(?:work through|do|try|start|help me with) )?(?:a |some )?(?:small |simple |basic )?(?:calculation|arithmetic|math)',key):
        return dict(base,action='select_activity',subject='calculation')
    lexical=session.get('mind',{}).get('lexical_discussion')
    if lexical:
        pick=re.fullmatch(r'(?:sense |meaning |the )?(\d+|first|second|third)(?: one| sense| meaning)?',key)
        if pick:
            num={'first':1,'second':2,'third':3}.get(pick[1])
            return dict(base,action='select_sense',subject=lexical['word'],sense_number=num or int(pick[1]),context_reference='lexical_discussion')
        if key in FOLLOWUPS or re.fullmatch(r'(?:why|how|where|when|what|which)\b.*\b(?:it|that|this|they|its|their)\b.*',key):
            return dict(base,action='lexical_followup',subject=lexical['word'],
                        context_reference='lexical_discussion',requested_attribute='definition' if key in FOLLOWUPS else 'unsupported')
    subject=F.overview_subject(text) or F.definition_subject(text)
    generic=bool(re.search(r'^(?:what is|what are|tell (?:me|us) about|explain|describe) (?:a|an) [\w -]+$',key))
    if subject:
        return dict(base,action='dictionary_overview' if generic else 'overview',subject=re.sub(r'^(?:a|an|the)\s+','',subject,flags=re.I),
                    qualifiers=re.findall(r"\b(?:not|never|without|no)\b",key))
    if session.get('mind',{}).get('pending_activity')=='calculation' and not re.match(r'^(?:what|who|why|how|where|when|tell|explain|describe|search|import|find|load|change|hi|hello)\b',key):
        return dict(base,action='calculation_input',subject=text,context_reference='pending_activity')
    return base


def handles(message, session):
    return parse(message,session)['action'] in {'introduce_and_explain','self','select_activity','select_sense','lexical_followup','dictionary_overview','calculation_input','unresolved_compound'}


def handle(message, session, collections=None):
    frame=parse(message,session);action=frame['action'];result=None
    if action=='unresolved_compound':
        result=M.reply('clarify','I recognized your introduction, but cannot resolve the rest of that request confidently. Could you ask the question separately?',session.get('context'),'COMPOSE-CLARIFY',authority='conversation_structure')
    elif action=='self':result=SK.handle(message,session,collections)
    elif action=='introduce_and_explain':
        intro,question=frame['clauses']
        explanation=SK.handle(question,session,collections)
        result=copy.deepcopy(explanation)
        result['message']='Hi, '+frame['subject']+'!\n\n'+explanation['message']
        result['authority']='separate_conversation_claims'
        result['claim_units']=[{'text':'Hi, '+frame['subject']+'!','authority':'user_declaration','sources':[]},
                               {'text':explanation['message'],'authority':'system_description','sources':[]}]
    elif action=='select_activity':
        session.setdefault('mind',{})['pending_activity']='calculation'
        result=M.reply('conversation','What expression would you like to calculate? I can use numbers, +, −, ×, ÷ and parentheses.',session.get('context'),
                       'ACTIVITY-SELECTION',authority='conversation_structure',suggestions=['12 times 7'],
                       response_structure={'intent':'select_calculation','factual_claims':False,'mplpb_supported':False})
    elif action=='calculation_input':
        result=DR.handle(frame['subject'],session)
        if result is None:
            result=M.reply('clarify','Please enter a numeric expression using +, −, ×, ÷ and parentheses, or choose another activity.',session.get('context'),'CALCULATION-INPUT',authority='conversation_structure')
        else:session['mind'].pop('pending_activity',None)
    elif action in {'select_sense','lexical_followup','dictionary_overview'}:
        result=lexical(message,session,frame)
        if result is None:
            result=M.reply('reference_missing','No supported dictionary explanation for that complete request. Please specify a headword or an eligible source.',session.get('context'),'LEXICAL-MISSING',authority='lexical_reference')
    if result:
        result['structured_request']=frame
        if action not in {'select_activity','calculation_input'}:session.setdefault('mind',{}).pop('pending_activity',None)
    return result


def render_lexical(word, senses, selected, archive):
    displayed=[s for s in senses if s['id']==selected] if selected else senses[:12]
    lines=['Open English WordNet 2025 · '+word]
    for sense in displayed:
        number=next(i+1 for i,s in enumerate(senses) if s['id']==sense['id'])
        lines.append(str(number)+'. '+sense['id']+' ('+sense['part_of_speech']+') — '+'; '.join(sense['definitions']))
    if not selected and len(senses)>12:lines.append('Showing the first 12 of '+str(len(senses))+' senses. Use “define '+word+'” and dictionary pagination to inspect all senses.')
    if not selected and len(senses)>1:lines.append('Which sense do you mean? Choose a numbered sense; these meanings are not combined.')
    else:lines.append('This explanation quotes the selected definition. It does not establish additional facts about the topic.')
    lines.append('Source: '+archive['url']+'\nLicense: CC-BY-4.0 · Open English WordNet Community, derived from Princeton WordNet.')
    return '\n\n'.join(lines)


def lexical(message, session, frame=None):
    from tools import reference_resources as R
    frame=frame or parse(message,session)
    if frame['action'] not in {'overview','dictionary_overview','select_sense','lexical_followup'} or frame['qualifiers']:return None
    word=frame['subject']
    if not word or word.casefold() in {'it','this','that','you','yourself'}:return None
    # Whole headwords only; never discard entity modifiers or negation to find a hit.
    headword,senses,manifest=R.lookup_forms(word)
    if not senses:return None
    old=session.setdefault('mind',{}).get('lexical_discussion',{})
    selected=old.get('sense') if frame['context_reference'] else None
    if frame['action']=='select_sense':
        number=frame['sense_number']
        if not 1<=number<=len(senses):
            return M.reply('clarify','Choose a sense number from 1 to '+str(len(senses))+'.',session.get('context'),'LEXICAL-CHOICE',authority='conversation_structure')
        selected=senses[number-1]['id']
    if len(senses)==1:selected=senses[0]['id']
    if frame['requested_attribute']=='unsupported':
        return M.reply('unsupported','The selected dictionary definition does not establish that requested detail. Please ask a definition question or select a source with the required evidence.',session.get('context'),'LEXICAL-LIMIT',authority='unsupported')
    archive=manifest['resources'][0]
    body=render_lexical(headword,senses,selected,archive)
    session['mind']['lexical_discussion']={'word':headword,'sense':selected}
    proof={'word':headword,'sense':selected,'sense_ids':[s['id'] for s in senses],'archive_hash':archive['sha256']}
    result=M.reply('reference',body,session.get('context'),'LEXICAL-DISCUSSION',authority='lexical_reference',
        sources=[{'id':'OEWN-2025','hash':archive['sha256'],'path':'resources/'+archive['path'],'url':archive['url'],'license':'CC-BY-4.0'}],
        suggestions=['sense '+str(i+1) for i in range(min(len(senses),4))] if not selected else ['Explain that'],
        response_structure={'intent':'lexical_topic','subject':headword,'factual_claims':True,'mplpb_supported':False},
        lexical_proof=proof,headword=headword,senses=senses,source_scope='dictionary_reference',structured_request=frame)
    return result


def revalidate_lexical(result):
    from tools import reference_resources as R
    proof=result['lexical_proof'];senses,manifest=R.lookup(proof['word']);archive=manifest['resources'][0]
    return (proof['archive_hash']==archive['sha256'] and proof['sense_ids']==[s['id'] for s in senses]
            and (proof['sense'] is None or proof['sense'] in proof['sense_ids'])
            and result['message']==render_lexical(proof['word'],senses,proof['sense'],archive))
