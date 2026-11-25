"""Opt-in inspection of source-linked proposals against native report proofs.

Tags never rewrite a question, establish permissions, or supply answer facts.
The ordinary reader must first verify the complete source-scoped claim. This
experimental API is not connected to the answering or delivery path.
"""
import hashlib
import html
import json

from .body_text import body_text
from .passages import PassageIndex
from .pipeline import answer_query
from .source_units import statement_units

VERSION = 'source-linked-proposals-v1'
FIELDS = {'reporter','author','inner_action','object','inner_negative','outer_negative',
          'conditions','content_asserted_by_reporter','actual_authorship_established',
          'source_writer_or_unknown','relation','source_voice','reporting_layer',
          'completion_established','historical_truth_independently_verified'}


def _same(a, b):
    # JSON equality retains the distinction between booleans and integer labels.
    return json.dumps(a, sort_keys=True, ensure_ascii=False) == json.dumps(b, sort_keys=True, ensure_ascii=False)


def _validate(index, record, packet, answer):
    if set(packet) != {'schema','source','nodes','relations'} or packet['schema'] != VERSION:
        raise ValueError('unsupported_schema_or_policy_fields')
    source = packet['source']
    expected = {'id':record.id,'path':record.path,'hash':record.hash_actual,
                'body_html_sha256':hashlib.sha256(record.body_html.encode()).hexdigest()}
    if not _same(source, expected):raise ValueError('source_pin_or_schema_mismatch')
    if record.kind != 'page' or record.derived_from:raise ValueError('original_source_required')
    nodes, relations = packet['nodes'], packet['relations']
    if (type(nodes) is not list or not 1 <= len(nodes) <= 64
            or type(relations) is not list or not 1 <= len(relations) <= 12):
        raise ValueError('proposal_budget_exceeded')
    body=body_text(record.body_html);raw=record.body_html.encode();by_id={}
    for node in nodes:
        if type(node) is not dict:raise ValueError('invalid_node')
        ident=node.get('id')
        if type(ident) is not str or not 1 <= len(ident) <= 80 or ident in by_id:
            raise ValueError('duplicate_or_invalid_node_id')
        base={'id','kind','parent','body_start','body_end'}
        document=node.get('kind')=='document'
        if set(node) != base | (set() if document else {'quote','original_start_byte','original_end_byte'}):
            raise ValueError('unsupported_node_fields')
        if node['kind'] not in {'document','paragraph','quotation','statement','person','object'}:
            raise ValueError('unsupported_node_kind')
        a,b=node['body_start'],node['body_end']
        if type(a) is not int or type(b) is not int or not 0 <= a < b <= len(body):
            raise ValueError('invalid_canonical_coordinates')
        if document:
            if node['parent'] is not None or (a,b)!=(0,len(body)):
                raise ValueError('invalid_document_root')
        else:
            if type(node['parent']) is not str or body[a:b] != node['quote']:
                raise ValueError('canonical_witness_mismatch')
            lo,hi=node['original_start_byte'],node['original_end_byte']
            if (type(lo) is not int or type(hi) is not int or not 0 <= lo < hi <= len(raw)
                    or html.unescape(raw[lo:hi].decode()) != node['quote']):
                raise ValueError('original_witness_mismatch')
        by_id[ident]=node
    if sum(n['kind']=='document' for n in nodes)!=1:raise ValueError('one_document_root_required')
    for node in nodes:
        seen={node['id']};current=node
        while current['parent'] is not None:
            parent=by_id.get(current['parent'])
            if parent is None or parent['id'] in seen:raise ValueError('invalid_containment_tree')
            if not parent['body_start'] <= current['body_start'] < current['body_end'] <= parent['body_end']:
                raise ValueError('containment_span_mismatch')
            if parent['kind']!='document' and not (parent['original_start_byte'] <= current['original_start_byte'] < current['original_end_byte'] <= parent['original_end_byte']):
                raise ValueError('original_containment_span_mismatch')
            seen.add(parent['id']);current=parent
    verified=[];seen_relations=set()
    for relation in relations:
        if type(relation) is not dict or set(relation)!={'witness','subject','reported_by','object','proposition'}:
            raise ValueError('invalid_relation_schema')
        proposition=relation['proposition']
        if type(proposition) is not dict or set(proposition)!=FIELDS:
            raise ValueError('unsupported_or_incomplete_claim')
        signature=json.dumps(proposition,sort_keys=True,ensure_ascii=False)
        if signature in seen_relations:raise ValueError('duplicate_relation')
        seen_relations.add(signature)
        witness=by_id.get(relation['witness'])
        if not witness or witness['kind']!='statement':raise ValueError('complete_statement_required')
        for role, field, kind in [('subject','author','person'),('reported_by','reporter','person'),('object','object','object')]:
            node=by_id.get(relation[role])
            if (not node or node['kind']!=kind or node['quote']!=proposition[field]
                    or not witness['body_start'] <= node['body_start'] < node['body_end'] <= witness['body_end']):
                raise ValueError('role_witness_mismatch')
        matches=[]
        for claim in answer['claims']:
            actual=claim.get('proposition',{})
            if not all(k in actual and _same(actual[k],v) for k,v in proposition.items()):continue
            for c in claim['citations']:
                if ((c['source_id'],c['path'],c['hash'])==(record.id,record.path,record.hash_actual)
                        and (c.get('body_start'),c.get('body_end'),c['quote'])==
                            (witness['body_start'],witness['body_end'],witness['quote'])
                        and c.get('original_witness',{}).get('start_byte')==witness['original_start_byte']
                        and c.get('original_witness',{}).get('end_byte')==witness['original_end_byte']):
                    matches.append(claim)
        if len(matches)!=1:raise ValueError('no_unique_native_complete_claim')
        verified.append({'proposition':matches[0]['proposition'],'citations':matches[0]['citations']})
    return verified


def verify_proposals(root, question, packet, profile=None):
    """Return inspection certificates; never change the ordinary answer contract."""
    base={'schema':VERSION,'original_coordinate_space':'admitted_record_body_html_utf8','authoritative':False,'changes_host_access':False,
          'node_classifications_authoritative':False,'historical_truth_independently_verified':False,
          'verified_relations':[]}
    try:
        if type(packet) is not dict or len(json.dumps(packet,ensure_ascii=False))>64000:
            raise ValueError('proposal_budget_exceeded')
        index=PassageIndex(root,question,profile)
        if len(index.records)>8:raise ValueError('record_budget_exceeded')
        bodies=[body_text(r.body_html) for r in index.records]
        if sum(map(len,bodies))>200000 or sum(sum(1 for _ in statement_units(b)) for b in bodies)>1000:
            raise ValueError('scan_budget_exceeded')
        source=packet.get('source',{})
        if type(source) is not dict:raise ValueError('invalid_source_schema')
        records=[r for r in index.records if (r.id,r.path,r.hash_actual)==
                 (source.get('id'),source.get('path'),source.get('hash'))]
        if len(records)!=1:raise ValueError('no_unique_current_eligible_source')
        # Full native query preserves question obligations, counterevidence and
        # all qualifications. A tag cannot make an unrecognized question pass.
        answer=answer_query(root,question,profile,max_passages=12,max_chars=8000).contract
        if answer['kind']!='supported_answer' or not answer['answer_supported']:
            raise ValueError('no_complete_native_answer')
        verified=_validate(index,records[0],packet,answer)
        if not index.unchanged():raise ValueError('source_changed')
        return dict(base,status='accepted',native_source_check='matched',verified_relations=verified,
                    question=question,source_snapshot=index.gate.corpus_snapshot,
                    policy_settings_hash=index.gate.policy.get('settings_hash'))
    except (ValueError,TypeError,KeyError,UnicodeError,RecursionError) as error:
        return dict(base,status='rejected',reason=str(error),native_source_check='withheld')
