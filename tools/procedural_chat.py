"""Source procedure inspection and recoverable selectors; never execution proof."""
import copy
import re
from mplpb_answers import procedures as P
from mplpb_combined.reader import PROFILES

FOLLOWUPS = {'next','next step','continue','go on','what next','what is next','tell me more'}
INSPECT_NEXT = {'inspect next step','show the next step','show me the next step'}
SOCIAL = {'thanks','thank you','hello','hi','show source'}


def handle(app, session, message, corpus, profile):
    memory = session['mind']
    previous = memory.get('procedure_selector')
    pending = memory.get('procedure_pending')
    key = message.casefold().strip(' .?!')
    keys = session.get('environment', {}).get('corpora', [corpus])
    # Pending selections are conversational context only and bound to scope.
    if pending and (pending['corpus'] != corpus or pending['profile'] != profile):
        memory.pop('procedure_pending', None)
        pending = None
    correction = re.fullmatch(r'(?:actually,? |no,? )?(?:i meant |i mean )?(?:show )?step ([1-9][0-9]{0,2})', key)
    named_correction = re.fullmatch(r'(?:actually,? |no,? )i meant (procedure .+)', key)
    query = P.request(named_correction[1] if named_correction else message)
    following = key in FOLLOWUPS and previous is not None
    inspecting = key in INSPECT_NEXT and previous is not None
    focus = re.fullmatch(r'(?:show |what are )?(?:the )?(prerequisites|conditions|warnings)(?: for (?:that|this) step)?', key)
    if correction and previous:
        query = {'procedure':previous['procedure'], 'step':int(correction[1])}
    elif pending and pending.get('choices') and key in pending['choices']:
        query = {'procedure':key, 'step':None}
    elif (following or inspecting or focus) and previous:
        keys = [previous['corpus']] if previous['corpus'] in keys else []
        if inspecting and previous['step'] == 0 or focus and previous['step'] == 0:
            memory['procedure_pending'] = {'corpus':corpus,'profile':profile,'field':focus[1] if focus else None}
            return _clarify(session, 'Which step would you like to inspect? You can say “step 1”.', previous)
        query = {'procedure':previous['procedure'],
                 'step': previous['step']+1 if following or inspecting else previous['step']}
    if not query:
        if key not in SOCIAL:
            memory.pop('procedure_selector', None)
            memory.pop('procedure_pending', None)
        return None
    if correction and previous:
        keys = [previous['corpus']] if previous['corpus'] in keys else []
    inherited_request = following or inspecting or focus is not None or (correction is not None and previous is not None)
    if not inherited_request:
        memory.pop('procedure_selector',None)
        memory.pop('procedure_pending',None)
    checks = [(k, *P.check(app.root(k), query, PROFILES[profile])) for k in keys]
    if query.get('interpretation') and not any(c['identified'] for _,c,_ in checks):
        memory.pop('procedure_selector', None)
        memory.pop('procedure_pending', None)
        return None  # Do not steal existing question/help routes on a wording match.
    valid = [(k,c,r) for k,c,r in checks if c['status']=='supported']
    conflicts = any(c['status']=='conflict' for _,c,_ in checks)
    result = _clarify(session, 'No eligible, complete procedure matches. Choose a loaded collection and a source-authored procedure identifier.', query)
    result.update(procedure_request=query, procedure_checks=[dict(c,corpus=k) for k,c,_ in checks])
    choices = sorted({choice for _,c,_ in checks for choice in c['choices']})
    if query['procedure'] is None and len(choices)>1:
        memory['procedure_pending'] = dict(corpus=corpus,profile=profile,choices=choices)
        result['message']='Which procedure would you like to inspect? '+', '.join(choices)
        result['suggestions']=['procedure '+choice for choice in choices[:8]]
    elif len(valid)>1 or conflicts:
        result.update(kind='conflict',message='Conflicting or multiple eligible procedure definitions. No continuation selected.')
        memory.pop('procedure_selector',None)
    elif len(valid)==1:
        k, checked, rec = valid[0]
        result['sources'] = [dict(checked['source'],corpus=k)]
        inherited = following or inspecting or focus is not None or (correction is not None and previous is not None)
        if inherited and (previous['source'] != checked['source'] or previous['profile'] != profile):
            result['message'] = 'The procedure source or profile changed. Select it again; saved context is not evidence.'
            memory.pop('procedure_selector',None)
            memory.pop('procedure_pending',None)
        elif following and previous['step']==0:
            result['message']='Choose an explicit step to inspect. Reading the whole plan does not establish a current execution step. You can say “step 1”.'
        elif following:
            step = checked['steps'][query['step']-1]
            result['message'] = ('Step '+str(query['step'])+' requires verification of prerequisite steps '+
                ', '.join(map(str,step['prerequisites']))+'. Showing an earlier step does not prove completion. '+
                'To read the next instruction without claiming completion, say “inspect next step”.')
            result['procedure_constraints'] = step
        else:
            result.update(kind='return',message=P.render(checked),authority='source_assertion',procedure=checked,source_corpus=k)
            result['response_structure'].update(mplpb_supported=True,factual_claims=True)
            if focus or pending and pending.get('field'):
                result['requested_constraint'] = focus[1] if focus else pending['field']
            memory['procedure_selector'] = dict(procedure=checked['procedure'],step=query['step'] or 0,
                                                corpus=k,profile=profile,source=checked['source'])
            memory.pop('procedure_pending',None)
    elif len(checks)==1 and checks[0][1].get('partial'):
        k, checked, _ = checks[0]
        result.update(kind='partial',message=P.render_partial(checked),authority='source_excerpt',
                      procedure_partial=checked,source_corpus=k,
                      sources=[dict(s,corpus=k) for s in checked['partial_sources']])
        result['response_structure']['factual_claims']=True
        memory.pop('procedure_pending',None)
        memory.pop('procedure_selector',None)
    elif checks:
        result['message'] = next((c['clarification'] for _,c,_ in checks if c.get('clarification')),None) or 'No supported procedure. '+' '.join(g for _,c,_ in checks for g in c['gaps'])
        if following or inspecting:
            result['message'] += ' No continuation was invented.'
    return result


def _clarify(session, message, query):
    return {'kind':'clarify','message':message,'context':session.get('context'),'sources':[],
            'authority':'unsupported','procedure_request':copy.deepcopy(query),
            'response_structure':{'intent':'procedural','mplpb_supported':False,'factual_claims':False}}


def revalidate(app, result, profile):
    """Reject stale sources, missing qualifications or modified partial excerpts."""
    old = result.get('procedure') or result.get('procedure_partial')
    if not old: return True
    checked, rec = P.check(app.root(result['source_corpus']), result['procedure_request'], PROFILES[profile])
    if result.get('procedure_partial'):
        return checked==old and checked.get('partial') and result['message']==P.render_partial(checked)
    return bool(rec) and checked==old and result['message']==P.render(checked)
