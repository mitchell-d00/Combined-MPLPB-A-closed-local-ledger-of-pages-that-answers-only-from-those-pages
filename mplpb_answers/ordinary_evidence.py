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
    ranges=context_ranges(record,literal_source=True)
    if any(a<end and b>start for a,b in ranges):return False
    if quoted_context(body[:start]):return False
    # A reporting caption can scope a following field block without explicit
    # quote marks. Do not turn its reported fields into the outer source voice.
    reported=re.search(r'(?:^|[.!?]\s+|\n)(?P<caption>[^.!?\n]*\b(?P<report_verb>said|stated|reported|quoted|testified|wrote)\b[^.!?\n]*:)\s*$',body[:start],re.I)
    if reported and not any(a<reported.end('report_verb') and b>reported.start('report_verb') for a,b in ranges):
        return False
    # Recognized restriction heads remain restrictions at any source length.
    # A quoted condition is a different reporting layer, not an outer governor.
    condition=re.search(r'(?:^|[.!?]\s+|\n)(?P<condition>(?:(?:Only\s+)?If|Unless|Provided(?:\s+that)?|Subject\s+to)\b[^.!?]+[.!?]?)\s*$',body[:start],re.I)
    if condition and not any(a<condition.end('condition') and b>condition.start('condition') for a,b in ranges):
        return False
    return True


def opening_fields(frame, record):
    if frame.relation != 'opening_time':
        return None
    return named_fields(frame, record, 'opening time')


def named_fields(frame, record, label, *, exact_offsets=False):
    """Check one named entity and one explicit, unqualified source field."""

    from .relation_graph import FIELD_LINE,STACKED_LABEL
    from mplpb_combined.ledger import field_name
    from .body_text import body_text
    body=body_text(record.body_html)
    if len(body)>200000:return None
    # Explicit body fields need not be the document's initial header. Inspect
    # every occurrence so a narrative prefix cannot hide competing evidence.
    # This does not grant later fields global record-identity/header authority.
    fields=[{'field':field_name(m[1]),'value':m[2].strip(),'quote':m[0],
             'body_start':m.start(),'body_end':m.end(),
             'stacked_field_suspected':bool(STACKED_LABEL.search(m[2]))}
            for m in FIELD_LINE.finditer(body)]
    names = [f for f in fields if f['field'] == 'name']
    values_for_field = [f for f in fields if f['field'] == label]
    matching=[f for f in names if normalize(f['value'])==frame.entity]
    # Relevance requires the exact named entity, requested time role and an
    # unqualified source layer. Other entities/roles and purely quoted or
    # conditional blocks do not become blanket counterevidence.
    if (not matching or not values_for_field
        or not any(unscoped(record,body,f['body_start'],f['body_end']) for f in matching)
        or not any(unscoped(record,body,f['body_start'],f['body_end']) for f in values_for_field)):return None
    chosen = names + values_for_field
    def unresolved_fields():
        return {'status':'unsupported','spans':[],'negative_spans':[],'unresolved':True,
                'unresolved_spans':[dict(f,source_id=record.id,path=record.path,hash=record.hash_actual) for f in chosen[:12]],
                'omitted_unresolved_locators':max(0,len(chosen)-12),'frame':frame.to_dict(),
                'reason': f'Relevant {label.replace("opening time", "opening-time")} fields have unresolved entity binding, scope or value.'}
    if ({normalize(f['value']) for f in names}!={frame.entity}
        or any(f.get('stacked_field_suspected') for f in chosen)
        or any(not unscoped(record,body,f['body_start'],f['body_end']) for f in chosen)):
        return unresolved_fields()
    values = {f['value'] for f in values_for_field}
    if len(values) != 1:
        return {'status': 'conflict', 'spans': [], 'reason': f'Competing explicit {label.replace("opening time", "opening-time")} fields.'}
    value=next(iter(values))
    if label == 'opening time':
        if not re.fullmatch(r'(?:[01]?\d|2[0-3]):[0-5]\d(?: ?(?:am|pm))?', value, re.I):
            return unresolved_fields()
        reason = 'Explicit body name and opening-time fields checked together; no closing time or timezone inferred.'
    else:
        if not re.fullmatch(r"[\w][\w ,.'’/-]{0,119}", value) or re.search(
                r'\b(?:if|unless|not|unknown|unspecified|unrecorded|formerly|either|or|maybe|reportedly)\b',
                value, re.I):
            return unresolved_fields()
        reason = 'Explicit body name and location checked together.'
    spans = [dict(f, value=value) if exact_offsets else {'quote': f['quote'], 'value': value}
             for f in chosen]
    return {'status': 'supported', 'spans': spans, 'negative_spans': [],
            'frame': frame.to_dict(), 'reason': reason}
