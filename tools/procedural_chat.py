"""Procedure chat shares MPLPB support checks. Saved step position is not completion."""
from mplpb_answers import procedures as P
from mplpb_combined.reader import PROFILES

FOLLOWUPS = {'next','next step','continue','go on','what next','what is next','tell me more'}


def handle(app, session, message, corpus, profile):
    query = P.request(message)
    previous = session['mind'].get('procedure_selector')
    following = message.casefold().strip(' .?!') in FOLLOWUPS and previous is not None
    if not query and not following: return None
    keys = session.get('environment', {}).get('corpora', [corpus])
    if following:
        query = {'procedure':previous['procedure'], 'step':previous['step']+1}
        keys = [previous['corpus']] if previous['corpus'] in keys else []
    checks = [(key, *P.check(app.root(key), query, PROFILES[profile])) for key in keys]
    valid = [(k,c,r) for k,c,r in checks if c['status']=='supported']
    conflicts = any(c['status']=='conflict' for _,c,_ in checks)
    result = {'kind':'clarify','message':'No eligible, complete procedure matches. Choose a loaded collection and a source-authored procedure identifier.',
              'context':session.get('context'),'sources':[], 'authority':'unsupported',
              'procedure_request':query,'procedure_checks':[dict(c,corpus=k) for k,c,_ in checks],
              'response_structure':{'intent':'procedural','mplpb_supported':False,'factual_claims':False}}
    if len(valid)>1 or conflicts:
        result.update(kind='conflict',message='Conflicting or multiple eligible procedure definitions. No continuation selected.')
    elif len(valid)==1:
        key, checked, rec = valid[0]
        result['sources'] = [dict(checked['source'],corpus=key)]
        if following and (previous['source'] != checked['source'] or previous['profile'] != profile):
            result['message'] = 'The procedure source or profile changed. Select it again; saved context is not evidence.'
        elif following and previous['step']==0:
            result['message']='Choose an explicit step to inspect. Reading the whole plan does not establish a current execution step.'
        elif following:
            step = checked['steps'][query['step']-1]
            result['message'] = ('Step '+str(query['step'])+' requires verification of prerequisite steps '+
                ', '.join(map(str,step['prerequisites']))+'. Showing an earlier step does not prove completion. '+
                'Provide eligible evidence of completion and applicable conditions, or ask to inspect “step '+str(query['step'])+' of procedure '+query['procedure']+'”.')
            result['procedure_constraints'] = step
        else:
            result.update(kind='return',message=P.render(checked),authority='source_assertion',procedure=checked,source_corpus=key)
            result['response_structure'].update(mplpb_supported=True,factual_claims=True)
            session['mind']['procedure_selector'] = dict(procedure=query['procedure'],step=query['step'] or 0,
                                                       corpus=key,profile=profile,source=checked['source'])
    elif checks:
        result['message'] = 'No supported procedure. '+' '.join(g for _,c,_ in checks for g in c['gaps'])
    return result


def revalidate(app, result, profile):
    """Run again after wording; reject altered tags, omitted warnings or stale bytes."""
    if not result.get('procedure'): return True
    old = result['procedure']; key=result['source_corpus']
    checked, rec = P.check(app.root(key), result['procedure_request'], PROFILES[profile])
    return bool(rec) and checked==old and result['message']==P.render(checked)
