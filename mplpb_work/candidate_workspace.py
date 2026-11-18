"""Opt-in, offline processed-document review beside current eligible originals.

Neither a match nor the workspace changes a ledger or certifies a processed
statement. Ownership and strict proof remain independent of exploration.
"""
import argparse
import copy
import json
from pathlib import Path
import re

from . import sorter as core
from .sorter_suggestions import NOTICE, suggestions
from mplpb_answers.body_text import body_text
from mplpb_answers.evidence_contract import ReaderError
from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query
from mplpb_answers import documentary_verify as kernel
from mplpb_combined import reader
from mplpb_combined.ledger import serving_view

VERSION = 'candidate-review-workspace-v2'
EXPLORATORY = 'Exploratory · outside MPLPB-approved evidence.'
ELIGIBLE = 'Eligible MPLPB original under the current profile; source truth is not verified.'


def _status():
    return {'status':'candidate for review','evidence_status':EXPLORATORY,'approval_status':'outside_approved_evidence',
            'answer_supported':False,'content_truth_verified':False,
            'approval_transferred':False,'ownership_changed':False}


def _bounded(value, low, high, name):
    if type(value) is not int or not low <= value <= high:
        raise core.SortError('Invalid '+name+' budget')
    return value


def _original(index, passage, cache):
    """Reverse a canonical body span to actual native-original UTF-8 bytes."""
    # Reuse the existing reversible projection; do not invent byte coordinates
    # by searching normalized text in raw HTML.
    from tools.source_roundtrip import projection_offsets
    from mplpb_combined.record import _BODY, parse_page
    path=passage['path']
    if path not in cache:
        raw=(Path(index.root)/path).read_bytes();text=raw.decode('utf-8')
        record=next(r for r in index.records if r.path==path)
        fresh=parse_page(text,path)
        if fresh.hash_actual!=record.hash_actual or fresh.hash!=fresh.hash_actual:
            raise core.SortError('Original changed during byte mapping')
        match=_BODY.search(text)
        if not match:raise core.SortError('Original body envelope missing')
        canonical,starts,ends=projection_offsets(match[1],True)
        if canonical!=body_text(record.body_html):raise core.SortError('Original projection mismatch')
        cache[path]=(raw,text,match.start(1),canonical,starts,ends)
    raw,text,offset,canonical,starts,ends=cache[path]
    a=passage['body_start'];b=a+len(passage['text'])
    if canonical[a:b]!=passage['text']:raise core.SortError('Original passage changed')
    positions=[i for i in range(a,b) if starts[i]>=0 and ends[i]>=0]
    if not positions:raise core.SortError('No reversible original span')
    ca=offset+min(starts[i] for i in positions);cb=offset+max(ends[i] for i in positions)
    ba=len(text[:ca].encode('utf-8'));bb=len(text[:cb].encode('utf-8'))
    return {'source_id':passage['source_id'],'path':path,'hash':passage['hash'],
            'body_start':a,'body_end':b,'quote':passage['text'],
            'native_original_sha256':core.sha(raw),'byte_start':ba,'byte_end':bb,
            'raw_excerpt':raw[ba:bb].decode('utf-8'),'raw_excerpt_sha256':core.sha(raw[ba:bb]),
            'byte_coordinate_basis':'Native original page UTF-8; external acquisition mapping, if any, remains separate.',
            'evidence_status':ELIGIBLE,'approval_status':'eligible_original','profile':index.profile.name,'answer_supported':False,
            'content_truth_verified':False,'round_trip_quote_fidelity':True}


def _processed(node):
    return dict(_status(),node_id=node['id'],occurrence_id=node['occurrence'],
                span=copy.deepcopy(node['span']),review_annotation=copy.deepcopy(node['assessment']))


def _match(node, passage, features):
    text=node['span']['text'];original=passage['text'];results=[]
    if text in original:
        results.append(('exact_match','The complete processed wording occurs literally in this eligible original; approval does not transfer.'))
    left=kernel.action_assertion(text);right=kernel.action_assertion(original)
    if left and right and all(left[k]==right[k] for k in ['actor_text','action','object_text','temporal_qualification_text']) and left['negative']!=right['negative']:
        results.append(('conflicting_wording','Existing finite action grammar finds opposing polarity for the same literal actor/action/object. Event identity and truth remain unresolved.'))
    for f in features:
        if f['kind']=='reference_mention' and f['value'].strip('<>').rstrip(':.,')==passage['source_id']:
            kind=('quoted_or_qualified_reference_review' if f.get('scope')!='unqualified_text' else
                  'possible_correction' if core.CORRECTION.search(f['reference_wording']) else 'possible_reference')
            results.append((kind,'Literal source reference names this original record. The shown target is document context; the referenced claim, correction scope and effective time remain unresolved.'))
    if not results:
        # Reuse the sorter's literal four-word observations. A bag of topic
        # words or synonym neighbors is not a connection between documents.
        keys={f['value'] for f in features if f['kind']=='repeated_phrase'}
        shared=sorted(keys & passage.get('_phrase_keys',set()))
        if shared:
            results.append(('shared_wording_review','Existing sorter four-word phrase evidence: '+repr(shared[:4])+'. Lexical tokens only; identity, chronology, causation and correction are unresolved.'))
    return list(dict.fromkeys(results))


def build(graph, processed_directory, originals, *, question=None, topic=None, profile=None,
          max_passages=24, max_chars=16000, strict_passages=12, strict_chars=8000,
          scan_passages=256, pair_checks=4096, as_of=None):
    query=question if question is not None else topic
    if not isinstance(query,str) or not query.strip() or len(query)>4000:
        raise core.SortError('Supply a question or topic of1–4000 characters')
    topic=topic if topic is not None else query
    if not isinstance(topic,str) or not topic.strip() or len(topic)>4000:raise core.SortError('Invalid exploration topic')
    for v,lo,hi,n in [(max_passages,1,64,'exploration passages'),(max_chars,1,64000,'exploration characters'),
                       (strict_passages,1,64,'strict passages'),(strict_chars,1000,64000,'strict characters'),
                       (scan_passages,1,1024,'scan passages'),(pair_checks,1,16384,'comparison checks')]:_bounded(v,lo,hi,n)
    profile=profile or reader.PROFILES[reader.DEFAULT_PROFILE]
    if profile not in reader.PROFILES.values():raise core.SortError('Use a configured current profile')
    core.verify_graph(graph,processed_directory)
    from mplpb_answers.relation_graph import exact_request
    with serving_view(as_of,exact_request(query)['field']):
        owner_index=PassageIndex(originals,query,profile)
        index=owner_index if topic==query else PassageIndex(originals,topic,profile)
        # Gate exclusions, depth, supersession and permissions determine this
        # set. Neither candidate links nor synonym terms participate.
        route=reader.answer(originals,query,profile,_eligible_paths={r.path for r in owner_index.records}) if question is not None else None
        count=len(route.candidates) if route else None
        ownership={'status':'not_requested','eligible_owner_count':None,'strict_answer':None,'page':None,'competing_sources':[]}
        if route:
            ownership.update(status='one_eligible_owner' if route.kind==reader.RETURN else 'multiple_eligible_owners' if route.kind==reader.AMBIGUOUS else 'no_eligible_owner',
                eligible_owner_count=count,native_kind=route.kind,reason=route.reason,
                competing_sources=[{'id':r.id,'path':r.path,'hash':r.hash_actual,'title':r.title,'evidence_status':ELIGIBLE} for r,_ in route.candidates])
            if route.kind==reader.RETURN:
                r=route.record
                ownership['page']={'id':r.id,'path':r.path,'hash':r.hash_actual,'title':r.title,'text':body_text(r.body_html),'evidence_status':ELIGIBLE}
                # No hints or exploration allocations enter this call.
                ownership['strict_answer']=answer_query(originals,query,profile,max_passages=strict_passages,max_chars=strict_chars,as_of=as_of).contract
            else:
                ownership['message']='Disambiguate the eligible owners; strict answer withheld.' if route.kind==reader.AMBIGUOUS else 'No MPLPB-supported answer is returned by this ownership route. Labeled exploration remains available.'
        review=suggestions(graph,processed_directory,topic,synonym_ranker=True,candidate_relater=False)
        by_id={n['id']:n for n in graph['nodes']};features={}
        for n in graph['nodes']:
            if n.get('statement'):features.setdefault(n['statement'],[]).append(n)
        selected=review['ranked_hits'][:scan_passages]
        # Reuse bounded native discovery on eligible originals. This pool is
        # independent of strict-proof admission and does not affect ownership.
        discovery_chars=min(64000,max(1000,max_chars*4))
        discovered=index.retrieve([topic],min(scan_passages,64),discovery_chars)
        originals_to_scan=[]
        for passage in discovered['passages']:
            words=[m[0].casefold() for m in core.WORD.finditer(passage['text'])]
            phrases={' '.join(words[i:i+4]) for i in range(max(0,len(words)-3))}
            originals_to_scan.append(dict(passage,_phrase_keys=phrases))
        proposals=[];checks=0;scan_cut=len(review['ranked_hits'])>len(selected) or len(index.passages)>len(originals_to_scan)
        for hit in selected:
            node=by_id[hit['node_id']]
            for p in originals_to_scan:
                if checks>=pair_checks:scan_cut=True;break
                checks+=1
                for kind,why in _match(node,p,features.get(node['id'],[])):
                    proposals.append((kind,node,p,why))
            if checks>=pair_checks:break
        priorities={'conflicting_wording':0,'exact_match':1,'possible_correction':2,'possible_reference':3,'quoted_or_qualified_reference_review':4,'shared_wording_review':5}
        proposals.sort(key=lambda row:(priorities[row[0]],row[1]['span']['path'],row[1]['span']['char_start'],row[2]['path'],row[2]['body_start']))
        admitted={};characters=0;omitted=0;cache={};candidates=[];documents={};matched=set()
        def admit(endpoints):
            nonlocal characters,omitted
            fresh={}
            for key,text in endpoints:
                if key not in admitted:fresh[key]=text
            size=sum(len(t) for t in fresh.values())
            if len(admitted)+len(fresh)>max_passages or characters+size>max_chars:
                omitted+=1;return False
            admitted.update(fresh);characters+=size;return True
        def pk(node):
            s=node['span'];return ('processed',s['path'],s['source_sha256'],s['byte_start'],s['byte_end'])
        def show(node):
            if node['id'] not in documents:documents[node['id']]=dict(_processed(node),original_match_status='unmatched_or_unresolved_within_search_limits')
        for kind,node,p,why in proposals:
            ok=('original',p['path'],p['hash'],p['body_start'],p['body_start']+len(p['text']))
            if not admit([(pk(node),node['span']['text']),(ok,p['text'])]):continue
            show(node);matched.add(node['id']);documents[node['id']]['original_match_status']='candidate_links_for_review'
            candidates.append(dict(_status(),id=core.digest([kind,node['id'],ok]),kind=kind,
                processed=_processed(node),original=_original(index,p,cache),why=why,
                identity='unresolved',chronology='unresolved',causation='unresolved',correction_status='unresolved'))
        for hit in selected:
            node=by_id[hit['node_id']]
            if node['id'] not in documents and admit([(pk(node),node['span']['text'])]):show(node)
        # Cross-processed disagreements remain exploratory and use the same
        # already admitted source spans, never an approved-original label.
        disagreements=[];doc_nodes=[by_id[k] for k in documents];processed_checks=0
        for i,a in enumerate(doc_nodes):
            for b in doc_nodes[i+1:]:
                if processed_checks>=pair_checks:scan_cut=True;break
                processed_checks+=1
                if a['occurrence']==b['occurrence']:continue
                for kind,why in _match(a,{'text':b['span']['text'],'source_id':''},[]):
                    if kind=='conflicting_wording':disagreements.append(dict(_status(),kind=kind,left=_processed(a),right=_processed(b),why=why))
        for path,(raw,*_) in cache.items():
            if (Path(index.root)/path).read_bytes()!=raw:raise core.SortError('Original byte span changed during review')
        if not index.unchanged() or not owner_index.unchanged():raise core.SortError('Original eligibility/source state changed; rebuild workspace')
        core.verify_graph(graph,processed_directory)
        unresolved=[]
        for node in doc_nodes:
            for f in features.get(node['id'],[]):
                if f['kind']!='reference_mention':continue
                unresolved.append(dict(_status(),processed=_processed(node),reference_span=copy.deepcopy(f['span']),
                    target_key=f['value'],target_claim_status='unresolved',
                    eligible_document_identified=f['value'].strip('<>').rstrip(':.,') in {r.id for r in index.records},
                    reason='Document reference only; exact target claim, quoted/conditional scope and correction applicability need review.'))
        output={'schema':VERSION,'label':NOTICE,'status':'candidate for review','evidence_status':EXPLORATORY,'approval_status':'outside_approved_evidence',
            'answer_supported':False,'content_truth_verified':False,'approval_transferred':False,
            'graph_sha256':graph['graph_sha256'],'implementation_sha256':core.sha(Path(__file__).read_bytes()),
            'configuration':{'question':question,'topic':topic,'profile':profile.name,'max_passages':max_passages,'max_chars':max_chars,
                'strict_passages':strict_passages,'strict_chars':strict_chars,'scan_passages':scan_passages,'pair_checks':pair_checks,'as_of':as_of},
            'original_corpus_snapshot':index.gate.corpus_snapshot,'original_policy':index.gate.policy,
            'reader_implementation_sha256':core.sha(Path(reader.__file__).read_bytes()),
            'verifier_implementation_sha256':core.sha(Path(kernel.__file__).read_bytes()),
            'mplpb_decision':ownership,'processed_passages':list(documents.values()),'candidates':candidates,
            'processed_disagreements':disagreements,'unresolved_references':unresolved,'unmatched_passages':[d for k,d in documents.items() if k not in matched],
            'exploration_budget':{'max_passages':max_passages,'max_characters':max_chars,'unique_spans':len(admitted),'characters':characters,
                'omitted_items':omitted,'display_truncated':bool(omitted),'search_truncated':scan_cut or not graph['complete'],
                'original_discovery_passage_limit':min(scan_passages,64),'original_discovery_character_limit':discovery_chars,
                'original_passages_considered':len(originals_to_scan),'processed_passages_considered':len(selected),
                'original_pairs_examined':checks,'processed_pairs_examined':processed_checks,'strict_slots_consumed':0},
            'strict_budget':{'max_passages':strict_passages,'max_characters':strict_chars,
                'truncated':bool(ownership['strict_answer'] and (ownership['strict_answer'].get('passage_budget',{}).get('blocked_atomic_claims') or any('budget' in x.lower() for x in ownership['strict_answer'].get('missing',[]))))},
            'limits_notice':'Unshown/unmatched items remain in the separately pinned sorter graph. No missing match or silence proves absence.',
            'source_authority_changed':False,'ownership_changed':False}
        output['workspace_sha256']=core.digest(output)
        if len(json.dumps(output,ensure_ascii=False).encode())>33554432:raise core.SortError('Workspace exceeds32MiB output limit')
        return output


def verify_workspace(result,graph,processed_directory,originals):
    if result.get('schema')!=VERSION or result.get('workspace_sha256')!=core.digest({k:v for k,v in result.items() if k!='workspace_sha256'}):
        raise core.SortError('Workspace integrity/schema mismatch')
    config=dict(result['configuration']);config['profile']=reader.PROFILES[config['profile']]
    if build(graph,processed_directory,originals,**config)!=result:
        raise core.SortError('Workspace source, eligibility, implementation or decisions changed; rebuild before review')
    return {'status':'fresh_source_and_decision_replay','label':NOTICE,'answer_supported':False,'semantic_links_verified':False}


def main(argv=None):
    p=argparse.ArgumentParser(description=NOTICE+' '+EXPLORATORY)
    p.add_argument('command',choices=['build','peruse']);p.add_argument('graph',type=Path)
    p.add_argument('--processed',required=True,type=Path);p.add_argument('--originals',required=True,type=Path)
    p.add_argument('--question');p.add_argument('--topic');p.add_argument('--profile',choices=reader.PROFILES,default=reader.DEFAULT_PROFILE)
    p.add_argument('--exploration-passages',type=int,default=24);p.add_argument('--exploration-chars',type=int,default=16000)
    p.add_argument('--strict-passages',type=int,default=12);p.add_argument('--strict-chars',type=int,default=8000)
    p.add_argument('--scan-passages',type=int,default=256);p.add_argument('--pair-checks',type=int,default=4096)
    p.add_argument('--as-of');p.add_argument('--output',type=Path);p.add_argument('--workspace',type=Path);a=p.parse_args(argv)
    try:
        graph=core._load(a.graph)
        if a.command=='peruse':
            if not a.workspace:p.error('--workspace required for peruse')
            result=core._load(a.workspace);verify_workspace(result,graph,a.processed,a.originals)
            print(json.dumps(result,ensure_ascii=False,indent=2));return 0
        if not a.output:p.error('--output required for build')
        if a.output.resolve().is_relative_to(a.originals.resolve()):raise core.SortError('Workspace output must be outside original ledger')
        result=build(graph,a.processed,a.originals,question=a.question,topic=a.topic,profile=reader.PROFILES[a.profile],
            max_passages=a.exploration_passages,max_chars=a.exploration_chars,strict_passages=a.strict_passages,strict_chars=a.strict_chars,
            scan_passages=a.scan_passages,pair_checks=a.pair_checks,as_of=a.as_of)
        core._save(a.output,result,a.processed)
        print(json.dumps({'label':NOTICE,'evidence_status':EXPLORATORY,'status':'candidate for review',
            'mplpb_decision':result['mplpb_decision'],'exploration_budget':result['exploration_budget'],'output':str(a.output)},ensure_ascii=False));return 0
    except (OSError,ValueError,KeyError,TypeError,RecursionError) as exc:
        print(json.dumps({'label':NOTICE,'status':'refused','error':str(exc),'answer_supported':False}));return 2


if __name__=='__main__':raise SystemExit(main())
