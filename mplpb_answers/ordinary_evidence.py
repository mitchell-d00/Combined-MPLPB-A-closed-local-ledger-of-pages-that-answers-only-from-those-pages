"""Shared literal proof helpers; proposals never establish source support."""
import re
from .frames import normalize

def patterns(frame,negative=False):
    base=frame.negative_statement if negative else frame.statement
    result=[base] if base else []
    e=re.escape(frame.entity)
    if frame.relation=='owner':
        result.extend([rf'{e} is '+('not ' if negative else '')+r'owned by (?P<value>.+)',rf'{e} '+('does not belong' if negative else 'belongs')+r' to (?P<value>.+)'])
    return result

def unscoped(record,body,start,end):
    from .documentary_verify import context_ranges,quoted_context
    if any(a<end and b>start for a,b in context_ranges(record)):return False
    if quoted_context(body[:start]):return False
    # Recognized restriction heads remain restrictions at any source length.
    # A quoted condition is a different reporting layer, not an outer governor.
    condition=re.search(r'(?:^|[.!?]\s+|\n)(?P<condition>(?:(?:Only\s+)?If|Unless|Provided(?:\s+that)?|Subject\s+to)\b[^.!?]+[.!?]?)\s*$',body[:start],re.I)
    if condition and not any(a<condition.end('condition') and b>condition.start('condition') for a,b in context_ranges(record)):
        return False
    return True


def opening_fields(frame,record):
    from .relation_graph import declared_fields,field_contexts
    from .body_text import body_text
    if frame.relation!='opening_time':return None
    body=body_text(record.body_html)
    if len(body)>200000:return None
    fields=declared_fields(record);names=[f for f in fields if f['field']=='name'];times=[f for f in fields if f['field']=='opening time']
    if (not names or not times or {normalize(f['value']) for f in names}!={frame.entity}
        or any(f.get('stacked_field_suspected') for f in names+times)
        or any(field_contexts(record,label) for label in ['name','opening time'])):return None
    chosen=names+times
    if any(not unscoped(record,body,f['body_start'],f['body_end']) for f in chosen):return None
    values={f['value'] for f in times}
    if len(values)!=1:return {'status':'conflict','spans':[],'reason':'Competing explicit opening-time fields.'}
    value=next(iter(values))
    if not re.fullmatch(r'(?:[01]?\d|2[0-3]):[0-5]\d(?: ?(?:am|pm))?',value,re.I):return None
    return {'status':'supported','spans':[{'quote':f['quote'],'value':value} for f in chosen],'negative_spans':[],'frame':frame.to_dict(),'reason':'Explicit body name and opening-time fields checked together; no closing time or timezone inferred.'}
