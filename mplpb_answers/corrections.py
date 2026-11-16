"""Explicit, uniquely scoped source corrections; never automatic fact rewriting."""
import json
import html
from datetime import datetime
from .body_text import body_text
from mplpb_combined.ledger import Ledger, revise
from mplpb_combined.provenance_gate import gather
from mplpb_combined.reader import PROFILES, DEFAULT_PROFILE


def correct_claim(root,source_id,old_quote,new_quote,*,effective_at='',profile=None):
    """Author an explicit successor replacing one exact, unique source span.

    Unchanged source text and the complete predecessor remain inspectable. The
    effective date is a source-author declaration, not an inferred event date.
    This API requires an explicit write call; experts never invoke it implicitly.
    """
    profile=profile or PROFILES[DEFAULT_PROFILE]
    if profile.name not in PROFILES or profile!=PROFILES[profile.name]:raise ValueError('Choose a known delivery profile')
    for text in (source_id,old_quote,new_quote):
        if not isinstance(text,str) or not text.strip() or len(text)>4000:raise ValueError('Expected bounded nonempty text')
    if not isinstance(effective_at,str) or len(effective_at)>100:raise ValueError('Invalid declared effective date')
    if effective_at:
        try:datetime.fromisoformat(effective_at.replace('Z','+00:00'))
        except ValueError as exc:raise ValueError('Invalid declared effective date') from exc
    ledger=Ledger(root)
    matches=[r for r in ledger.servable() if r.id==source_id and r.kind not in {'pointer','index'}]
    if len(matches)!=1:raise ValueError('Choose one current eligible source')
    record=matches[0]
    gate=gather(root,record.scope,profile)
    if record.path in {s['path'] for s in gate.excluded}:raise ValueError('Source is unavailable under this profile')
    body=body_text(record.body_html)
    start=body.find(old_quote)
    if start<0 or body.find(old_quote,start+1)>=0:raise ValueError('Correction requires one unique exact source span')
    correction={'kind':'scoped_source_correction','predecessor_id':record.id,
                'predecessor_hash':record.hash_actual,'start':start,'end':start+len(old_quote),
                'old_quote':old_quote,'new_quote':new_quote,'effective_at':effective_at,
                'time_basis':'author_declared','historical_truth_verified':False}
    corrected_body=body[:start]+new_quote+body[start+len(old_quote):]
    successor=revise(root,record.id,body_html='<pre>'+html.escape(corrected_body)+'</pre>',
                     note=json.dumps(correction,sort_keys=True),_event='scoped-correction')
    return {'source':{'id':successor.id,'path':successor.path,'hash':successor.hash_actual},
            'correction':correction,'answer_supported':False,'truth_verified':False}
