"""Explicit library commands and scope-only conversational continuity."""
import re
from mplpb_answers.library import Library


def catalog(app):
    return Library(app.roots(),app.library_manifest,resolve=app.root)


def handle(app, message, session, profile):
    text=message.strip(); mind=session.setdefault('mind',{})
    if text.casefold() in {'browse library','main index','library'}:
        mind.pop('library_pending',None)
        return catalog(app).browse(profile=profile)
    browse=re.fullmatch(r'library browse (.+?)(?: page ([1-9][0-9]{0,4}))?',text,re.I)
    if browse:
        mind.pop('library_pending',None)
        return catalog(app).browse(browse[1],profile,int(browse[2] or 1))
    more=re.fullmatch(r'library choices ([a-zA-Z0-9_-]+) page ([1-9][0-9]{0,4})',text,re.I)
    if more and mind.get('library_pending'):
        return catalog(app).answer(mind['library_pending']['question'],more[1],profile,int(more[2]))
    choose=re.fullmatch(r'library choose (.+)',text,re.I)
    if choose:
        pending=mind.get('library_pending')
        if not pending:return catalog(app).browse(choose[1],profile)
        # State selects the query/scope; all source checks run again.
        result=catalog(app).answer(pending['question'],choose[1],profile)
    else:
        ask=re.fullmatch(r'library ask(?: in ([^:]+))?:\s*(.+)',text,re.I)
        if not ask:
            if text.casefold().startswith('library '):
                result=catalog(app).browse(profile=profile)
                result['kind']='clarify'
                result['message']='Use library browse SHELF or library ask in SHELF: QUESTION.\n\n'+result['message']
                return result
            return None
        result=catalog(app).answer(ask[2],ask[1],profile)
    if result['kind']=='clarify':mind['library_pending']={'question':result['library_proof']['question']}
    else:mind.pop('library_pending',None)
    return result


def revalidate(app,result,profile):
    proof=result['library_proof']
    lib=catalog(app)
    if proof.get('version')!='library-routing-v1' or proof.get('catalog_sha256')!=lib.digest or proof.get('profile')!=profile:return False
    fresh=lib.answer(proof['question'],proof['shelf'],profile,proof.get('page',1))
    return all(fresh.get(k)==result.get(k) for k in ('kind','message','sources','library_route'))
