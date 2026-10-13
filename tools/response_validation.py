"""Last local response gate. Context and source presence alone are not proofs."""
from mplpb_combined.reader import PROFILES
from mplpb_combined.provenance_gate import gather
from mplpb_answers.support import supported_answer
from tools import procedural_chat as PR

VERSION='final-response-validation-v1'


def validate_response(app, result, profile, corpus, approved_message):
    errors=[]; checks=[]
    if result.get('lexical_proof'):
        from tools.structured_requests import revalidate_lexical
        try:
            if not revalidate_lexical(result):errors.append('Dictionary sense or constrained wording changed.')
        except (ValueError,KeyError,OSError):errors.append('Dictionary evidence is unavailable.')
        checks.append('fresh dictionary sense and exact constrained rendering')
    if result.get('procedure'):
        if not PR.revalidate(app,result,profile): errors.append('Procedure constraints or generated wording changed.')
        checks.append('fresh procedure tags and exact constrained rendering')
    elif result.get('kind')=='return' and result.get('reader',{}).get('question'):
        reader=result['reader']; key=result.get('source_corpus',corpus)
        fresh=supported_answer(app.root(key),reader['question'],PROFILES[profile])
        if fresh.kind!='return' or fresh.text!=reader.get('text') or result.get('message')!=approved_message:
            errors.append('The supported answer failed fresh evidence or wording validation.')
        checks.append('fresh supported answer')
    elif result.get('kind')=='grounded_answer':
        from tools import grounded_chat as Q
        pin=result.get('context') or {}; key=result.get('source_corpus',corpus)
        try:
            page=app.page(key,pin['path'],profile)
            attr=result.get('response_structure',{}).get('intent')
            expected=Q.evidence(page['text'],pin['title'],attr)
            if page['hash']!=pin['hash'] or not expected or result.get('evidence')!=expected or result.get('message')!=approved_message:
                errors.append('Grounded answer changed or its evidence no longer matches.')
        except (ValueError,KeyError): errors.append('Grounded source is unavailable.')
        checks.append('fresh attribute statement grammar')
    elif result.get('kind')=='relations':
        from tools import chat_logic as C
        key=result.get('source_corpus',corpus)
        for relation in result.get('relations',[]):
            fresh=C.relations(app.root(key),profile,relation['subject'],relation['object'])
            if relation not in fresh: errors.append('Relation proof no longer follows from eligible sources.')
        if not result.get('relations') or result.get('message')!=approved_message: errors.append('Relation response changed or lacks a proof.')
        checks.append('fresh relation premises and permitted inference rules')
    elif result.get('kind')=='return':
        errors.append('A factual return needs a supported reader or procedure proof.')
    if result.get('scope_results'):
        for item in result['scope_results']:
            child=item['response']
            validated=validate_response(app,child,profile,item['corpus'],child.get('message',''))
            if validated['response_validation']['status']=='blocked':errors.append('A collection result failed its evidence checks.')
        checks.append('separate collection proof validation')
    # Page inspection/summaries retain their distinct extractive/reference contract.
    # Every local pin is checked against the current gate, including contextual ones.
    for source in result.get('sources',[]):
        if not all(k in source for k in ('path','id','hash')): continue
        if source['path'].startswith('resources/') and result.get('authority')=='lexical_reference':
            from tools import reference_resources as F
            try:
                manifest=F.verify()
                if not any('resources/'+r['path']==source['path'] and r['sha256']==source['hash'] for r in manifest['resources']):
                    errors.append('Reference pin differs from verified resource manifest.')
            except (ValueError,OSError): errors.append('Reference resource verification failed.')
            checks.append('separate pinned lexical reference manifest')
            continue
        key=source.get('corpus',result.get('source_corpus',corpus))
        try:
            page=app.page(key,source['path'],profile)
            fresh=gather(app.root(key),page['title'],PROFILES[profile])
            if not any(all(s.get(k)==source[k] for k in ('path','id','hash')) for s in fresh.sources):
                errors.append('Source pin is changed, withheld or no longer eligible.')
        except (ValueError,OSError):errors.append('Source collection unavailable.')
    if errors:
        result={'kind':'unsupported','message':'Response withheld: '+' '.join(dict.fromkeys(errors)),
                'context':None,'sources':[],'authority':'unsupported',
                'response_structure':{'factual_claims':False,'mplpb_supported':False}}
    result['response_validation']={'version':VERSION,'status':'blocked' if errors else 'checked',
        'checks':checks or ['existing non-answer/reference contract; current local pins checked'],
        'context_is_evidence':False,'source_presence_is_support':False,'errors':errors}
    return result
