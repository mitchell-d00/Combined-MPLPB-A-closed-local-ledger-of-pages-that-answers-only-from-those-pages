"""Source-declared event candidates, distinct from documentary occurrences.

Only an explicit Event-ID or a repeated explicit Event-Key groups occurrences. Shared subjects never establish
identity. Candidates and changed-body review flags are not historical truth.
"""
from collections import defaultdict
import hashlib
import re

from mplpb_answers.body_text import body_text
from mplpb_combined.ledger import Ledger
from mplpb_combined import provenance_gate as G
from mplpb_combined.reader import PROFILES, DEFAULT_PROFILE
from .historical_verifier import verification_snapshot

VERSION='documentary-event-candidates-v1'


def inspect_events(root,question,profile=None,source_ids=None,expected_snapshot=None):
    profile=profile or PROFILES[DEFAULT_PROFILE]
    if profile.name not in PROFILES or profile!=PROFILES[profile.name]:
        raise ValueError('Choose a known delivery profile')
    initial=verification_snapshot(root,question,profile)
    empty={'version':VERSION,'source_state_current':False,'candidates':[],
           'unassigned_occurrences':[],'answer_supported':False,'truth_verified':False}
    if expected_snapshot is not None and initial!=expected_snapshot:return empty
    gate=G.gather(root,question,profile)
    excluded={s['path'] for s in gate.excluded};lexical={s['path'] for s in gate.sources}
    requested=set(source_ids) if source_ids is not None else None
    groups=defaultdict(list);unassigned=[];count=0
    for record in Ledger(root).servable():
        if (record.kind in {'pointer','index'} or record.path in excluded
                or (not profile.prose and record.path not in lexical)
                or (requested is not None and record.id not in requested)):
            continue
        if count>=32:break
        count+=1
        body=body_text(record.body_html)
        if len(body)>1000000:continue
        fields={};offset=0;body_start=None;invalid=False
        for line in body.splitlines(keepends=True)[:100]:
            raw=line.rstrip('\r\n')
            if re.match(r'^\s*(?:```|~~~|#{1,6}\s|Example[:.]|Sample[:.])',raw,re.I):break
            match=re.fullmatch(r'(Event-ID|Event-Key|Occurrence-ID|Message-ID|Subject|Date|Body):\s*(.*)',raw,re.I)
            if match:
                key=match[1].lower()
                if key in fields:invalid=True;break
                fields[key]={'value':match[2],'source_id':record.id,'path':record.path,
                             'hash':record.hash_actual,'start':offset,'end':offset+len(raw),'quote':raw}
                if key=='body':body_start=offset+match.start(2);break
            offset+=len(line)
        for key in ('event-id','occurrence-id'):
            value=record.fields.get(key,'')
            if value:
                if key in fields and fields[key]['value']!=value:invalid=True
                fields.setdefault(key,{'value':value,'source_id':record.id,'path':record.path,
                                       'hash':record.hash_actual,'declaration_location':'sealed_metadata'})
        if invalid:continue
        if body_start is None:
            if not any(key in fields for key in ('event-id','occurrence-id')):continue
            body_start=0
        message=fields.get('message-id',{}).get('value',record.id)
        event=fields.get('event-id',{}).get('value','')
        declared_occurrence=fields.get('occurrence-id',{}).get('value','')
        if declared_occurrence and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:@/-]{0,99}',declared_occurrence):continue
        event_key=fields.get('event-key',{}).get('value','')
        if event_key and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:@/-]{0,99}',event_key):continue
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:@/-]{0,99}',message):continue
        if event and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:@/-]{0,99}',event):continue
        occurrence={'occurrence_id':record.id+'@'+record.hash_actual,
                    'event_key':event_key,
                    'declared_occurrence_id':fields.get('occurrence-id',{}).get('value',''),
                    'source_id':record.id,'path':record.path,'hash':record.hash_actual,
                    'message_id':message,'event_id':event,
                    'subject':fields.get('subject',{}).get('value',''),
                    'source_stated_date':fields.get('date',{}).get('value',''),
                    'body_sha256':hashlib.sha256(body[body_start:].encode()).hexdigest(),
                    'citations':list(fields.values()),'identity_basis':'explicit_source_identifiers',
                    'answer_supported':False,'content_truth_verified':False}
        if event:groups[('declared_event_id',event)].append(occurrence)
        else:unassigned.append(occurrence)
    # A new shared-key node requires two distinct source appearances. No title,
    # subject, date similarity or receipt is an identity key.
    shared=defaultdict(list)
    for occurrence in unassigned:
        key=occurrence['event_key']
        if key:shared[key].append(occurrence)
    assigned=set()
    for key,appearances in shared.items():
        if len(appearances)>=2:
            groups[('shared_event_key',key)].extend(appearances)
            assigned.update(a['occurrence_id'] for a in appearances)
    unassigned=[o for o in unassigned if o['occurrence_id'] not in assigned]
    candidates=[]
    for (namespace,key),occurrences in sorted(groups.items()):
        event=key if namespace=='declared_event_id' else 'source-key:'+key
        versions=defaultdict(set)
        for occurrence in occurrences:versions[occurrence['message_id']].add(occurrence['body_sha256'])
        review=any(len(values)>1 for values in versions.values())
        candidates.append({'event_id':event,'kind':'documentary_event_candidate',
                           'node_id':'event:'+hashlib.sha256((namespace+'\0'+key).encode()).hexdigest(),
                           'identity_namespace':namespace,'identity_key':key,
                           'answer_supported':False,'content_truth_verified':False,
                           'status':'needs_review' if review else 'candidate',
                           'changed_message_body':review,'occurrences':occurrences,
                           'historical_identity_confirmed':False})
    if verification_snapshot(root,question,profile)!=initial:return empty
    return dict(empty,source_state_current=True,candidates=candidates,unassigned_occurrences=unassigned,
                notice='Explicit source IDs group candidate occurrences; equal subjects do not prove identity and changed bodies require review.')
