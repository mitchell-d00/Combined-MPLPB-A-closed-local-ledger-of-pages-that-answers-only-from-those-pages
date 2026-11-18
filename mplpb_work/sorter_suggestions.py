"""Optional lexical ranker and candidate relater beside the unchanged sorter.

Search neighbors are inspection aids, not semantic equivalences. No result in
this module establishes source eligibility, identity, chronology or correction.
"""
import argparse
from collections import defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

from . import sorter as core

NOTICE = 'Sorter suggestions for review. MPLPB has not verified these links or answers.'
VERSION = 'offline-sorter-suggestions-v3'
STOP = set('a an the who what which when where why how is are was were be been did does do can could would should have has had and or of to for from in on by with it its this that their they he she his her'.split())
BUILTIN = {'groups': [
    {'name':'dispatch-receipt-search', 'terms':['send','sent','sending','planned to send','dispatch','dispatched','mail','mailed','post','posted','receive','received'],
     'note':'Intention, request, dispatch and receipt have different meanings; this group is for discovery only.'},
    {'name':'request-search', 'terms':['arrange','arranged','request','requested','instruct','instructed','asked','told'],
     'note':'An arrangement or instruction is not execution.'},
    {'name':'publication-search', 'terms':['publish','published','publication','release','released','printed'],
     'note':'Printing and publication dates or occurrences are not interchangeable.'},
    {'name':'correction-search', 'terms':['correct','corrected','correction','revise','revised','reconsidered','retract','retracted','amend','amended','erratum'],
     'note':'Correction scope, target and effective time require original evidence.'},
    {'name':'earlier-search', 'terms':['before','earlier','prior','preceded'], 'note':'Temporal words do not verify chronology.'},
    {'name':'later-search', 'terms':['after','later','subsequently','following'], 'note':'Temporal words do not verify chronology.'},
    {'name':'cancellation-search', 'terms':['cancel','cancelled','canceled','called off','withdraw','withdrawn','aborted'],
     'note':'Cancellation, withdrawal and abort refer to different possible actions.'},
]}


def glossary(value=None):
    value=copy.deepcopy(value if value is not None else {'groups':[]})
    if not isinstance(value,dict) or set(value)!={'groups'} or not isinstance(value['groups'],list) or len(value['groups'])>200:
        raise core.SortError('Glossary must contain at most200 groups')
    names=set()
    for group in value['groups']:
        if not isinstance(group,dict) or set(group)-{'name','terms','note'} or not isinstance(group.get('name'),str) or not 1<=len(group['name'])<=80:
            raise core.SortError('Invalid glossary group')
        if group['name'] in names: raise core.SortError('Duplicate glossary group name')
        names.add(group['name']); values=group.get('terms')
        if not isinstance(values,list) or not 2<=len(values)<=16: raise core.SortError('Each glossary group needs2–16 terms')
        for term in values:
            if not isinstance(term,str) or not 1<=len(term)<=80 or not re.fullmatch(r'[^\W_]+(?:[ -][^\W_]+){0,5}',term,re.UNICODE):
                raise core.SortError('Glossary terms must be short literal words or phrases')
        if len({v.casefold() for v in values})!=len(values): raise core.SortError('Duplicate term within group')
        if not isinstance(group.get('note',''),str) or len(group.get('note',''))>500: raise core.SortError('Glossary note too long')
    return value


def _pattern(term):
    return re.compile(r'(?<!\w)'+r'\s+'.join(re.escape(w) for w in term.split())+r'(?!\w)',re.I)


def set_suggestion_class(node,query,graph,kind=None):
    """Reuse provisional status assignment; a class explains a suggestion only.

    An exact query word is not an exact quote, source selector or field proof.
    The reader independently decides relevance, eligibility and passage slots.
    """
    classification='synonym_or_shared_wording';why='Lexical search neighbors or shared wording; search/review only.'
    if kind in {'possible_reference','possible_correction','possible_partial_correction'}:
        classification='explicit_reference' if kind=='possible_reference' else 'possible_correction'
        why='Explicit source-declared reference/correction candidate; target and relevance require reader checking.'
    elif kind is not None:
        classification='shared_subject_review' if kind=='shared_subject_review' else 'shared_wording_review'
    else:
        text=node['span']['text']
        quoted=re.findall(r'["“]([^"”]{2,500})["”]',query)
        if any(q in text for q in quoted):
            classification='exact_quote_match';why='The question quotes this exact original wording; meaning and eligibility are not established.'
        for feature in graph['nodes']:
            if feature.get('statement')!=node['id']:continue
            if feature['kind']=='header_identifier' and _pattern(feature['value']).search(query):
                if feature.get('primary_identity_eligible') is True:
                    classification='exact_source_id_match';why='Literal requested source-declared identifier; the native source router must still resolve it.'
                else:classification='quoted_identifier_review';why='Identifier is embedded/quoted; it does not identify an eligible owner.'
            elif feature['kind']=='header' and feature.get('header_context')=='top_level_text':
                literal=feature.get('header_name','')+': '+feature.get('value','')
                if literal and literal.casefold() in query.casefold():
                    classification='exact_field_match';why='Literal source field/value mentioned in the question; field support remains unverified.'
    return {'suggestion_class':classification,'class_reason':why,'reader_assigns_passage_slot':True,
        'automatic_passage_slot':False,'automatic_relationship_traversal':False,
        'assessment':core.assign_status(node['kind'],scope=node.get('scope'))}


def _span(node,a,b,text):
    s=node['span'];prefix=text[:a];stop=text[:b]
    return dict(source_id=s['source_id'],source_sha256=s['source_sha256'],path=s['path'],
        char_start=s['char_start']+a,char_end=s['char_start']+b,
        byte_start=s['byte_start']+len(prefix.encode('utf-8')),byte_end=s['byte_start']+len(stop.encode('utf-8')),text=text[a:b])


def _endpoint(node,by_id):
    # Occurrences are not collapsed. Prefer their explicit anchored declaration
    # or first complete statement to displaying an entire source file as a quote.
    occurrence=node.get('occurrence',node['id'] if node['kind']=='source_occurrence' else None)
    if 'text' not in node['span']:
        eligible=[n for n in by_id.values() if n.get('occurrence')==occurrence and 'text' in n['span']]
        eligible.sort(key=lambda n:(n['kind']!='header_identifier',n['kind']!='statement',n['span']['char_start']))
        if not eligible:return None
        node=eligible[0]
    return {'node_id':node['id'],'occurrence_id':occurrence,'span':copy.deepcopy(node['span']),
            'review_annotation':copy.deepcopy(node['assessment']),'scope':node.get('scope'),
            'statement_node_id':node.get('statement'),
            'context_span':copy.deepcopy(by_id[node['statement']]['span']) if node.get('statement') in by_id else None,
            'header_context':node.get('header_context'),'primary_identity_eligible':node.get('primary_identity_eligible')}


def _links(graph,hits,neighbors):
    by_id={n['id']:n for n in graph['nodes']};links=[];unresolved=[];seen=set();checks=0;limited=False
    def add(kind,left,right,why,basis):
        nonlocal limited
        a=_endpoint(by_id[left],by_id);b=_endpoint(by_id[right],by_id)
        if not a or not b or a['occurrence_id']==b['occurrence_id']:return
        key=(kind,tuple(sorted([a['node_id'],b['node_id']])))
        if key in seen:return
        if len(links)>=256:limited=True;return
        seen.add(key)
        links.append({'id':'suggestion:'+core.digest(key)[7:],'kind':kind,'left':a,'right':b,'why':why,
            'basis':basis,'assessment':core.assessment('needs_review'),'identity':'unresolved','chronology':'unresolved',
            'causation':'unresolved','correction_status':'unresolved','applied':False,'confidence':None})
    for e in graph['edges']:
        if not e.get('comparison_only'):continue
        kind=e['kind']
        if kind=='unresolved_reference_review':
            unresolved.append({'source':_endpoint(by_id[e['from']],by_id),'target':None,
                'target_key':e.get('target_key'),'reason':e.get('reason'),'why':e['evidence_note'],
                'assessment':core.assessment('unresolved_missing_or_ambiguous_target')});continue
        if kind=='embedded_identifier_review':continue
        mapping={'explicit_reference_candidate':'possible_reference','possible_correction':'possible_correction',
                 'possible_partial_correction':'possible_partial_correction','shared_header_review':'shared_subject_review',
                 'repeated_phrase_review':'shared_wording_review'}
        if kind=='candidate_identity_cluster':
            members=e.get('members',[e['from'],e['to']])
            for a,b in zip(members,members[1:]):
                add('possible_conflicting_versions' if e.get('changed_bodies') else 'possible_duplicate_appearances',a,b,
                    e['evidence_note']+' Different bytes do not by themselves establish a semantic contradiction.',{'core_edge_id':e['id']})
        elif kind in mapping:
            evidence=[by_id[n] for n in e['evidence_nodes'] if n in by_id and 'text' in by_id[n]['span']]
            left=next((n['id'] for n in evidence if n.get('occurrence')==e['from']),e['from'])
            right=next((n['id'] for n in evidence if n.get('occurrence')==e['to']),e['to'])
            add(mapping[kind],left,right,e['evidence_note'],{'core_edge_id':e['id']})
    # Neighbor overlap locates inspection hits but cannot establish a documentary
    # relation. The v1 two-group heuristic linked different named objects merely
    # because both mentioned publication and dispatch. Preserve that failed trial;
    # only source-key/reference or literal-wording reviews produce edges here.
    return links,unresolved,{'comparisons':checks,'partial':limited,'max_links':256,'max_comparisons':20000}


def suggestions(graph,directory,query='',*,synonym_ranker=False,candidate_relater=False,user_glossary=None):
    core.verify_graph(graph,directory)
    if not synonym_ranker and not candidate_relater:return copy.deepcopy(graph)
    if not isinstance(query,str) or len(query)>4000:raise core.SortError('Query exceeds4000 characters')
    custom=glossary(user_glossary)
    if {g['name'] for g in custom['groups']}&{g['name'] for g in BUILTIN['groups']}:
        raise core.SortError('User glossary group names must not replace built-in groups')
    groups=glossary(BUILTIN)['groups']+custom['groups']
    tokens=sorted({m[0].casefold() for m in core.WORD.finditer(query)}-STOP)
    if len(tokens)>64:raise core.SortError('Use at most64 content query terms')
    wanted={term for group in groups for term in group['terms'] if _pattern(term).search(query)}
    exact=sorted(set(tokens)|wanted)
    expanded=defaultdict(list)
    if synonym_ranker:
        for group in groups:
            matched=[term for term in group['terms'] if _pattern(term).search(query)]
            for term in group['terms']:
                for original in matched:
                    if term.casefold()!=original.casefold():expanded[term].append((original,group['name'],group.get('note','')))
    patterns={term:_pattern(term) for term in set(exact)|set(expanded)};hits=[];signal_partial=False
    for node in graph['nodes']:
        if node['kind']!='statement':continue
        text=node['span']['text'];signals=[];exact_terms=set();neighbor_terms=set();neighbor_groups=set();omitted=0
        for term,pattern in sorted(patterns.items()):
            for match in pattern.finditer(text):
                bases=[('exact',term,None,'Literal query wording.')] if term in exact else []
                bases += [('synonym',original,name,note) for original,name,note in expanded.get(term,[])]
                for kind,original,name,note in bases:
                    if kind=='exact':exact_terms.add(original)
                    else:neighbor_terms.add(original);neighbor_groups.add(name)
                    if len(signals)>=128:omitted+=1;signal_partial=True;continue
                    signals.append({'kind':kind,'query_term':original,'matched_term':term,'original_phrase':match[0],
                        'span':_span(node,match.start(),match.end(),text),'vocabulary_group':name,
                        'why':note,'semantic_equivalence_established':False})
        if not signals:continue
        counts=defaultdict(set)
        for s in signals:counts[s['query_term']].add(s['vocabulary_group'])
        hits.append({'node_id':node['id'],'occurrence_id':node['occurrence'],'span':copy.deepcopy(node['span']),
            'scope':node.get('scope'),'review_annotation':copy.deepcopy(node['assessment']),
            'rank_score':2*len(exact_terms)+len(neighbor_terms-exact_terms),
            'exact_query_terms':sorted(exact_terms),'synonym_query_terms':sorted(neighbor_terms),
            'neighbor_groups':sorted(neighbor_groups),'signals':signals,'omitted_signals':omitted,
            'ambiguous_vocabulary_terms':sorted(k for k,v in counts.items() if len(v-{None})>1),
            'why_ranked':'2 per distinct exact query term;1 per distinct neighbor-only query term. Rank is not confidence or authority.',
            'assessment':core.assessment('ranked_inspection_candidate')})
    hits.sort(key=lambda h:(-h['rank_score'],h['span']['path'],h['span']['char_start'],h['node_id']))
    nodes_by_id={n['id']:n for n in graph['nodes']}
    for hit in hits:hit.update(set_suggestion_class(nodes_by_id[hit['node_id']],query,graph))
    comparison=graph
    if candidate_relater and not graph['comparison_performed']:
        comparison=core.sort_directory(directory,mode='compare',limits=graph['limits'])
        if comparison['nodes']!=graph['nodes']:raise core.SortError('Source nodes changed during relation review')
    links,unresolved,limits=_links(comparison,hits,synonym_ranker) if candidate_relater else ([],[],{'partial':False})
    for link in links:
        link.update(set_suggestion_class(nodes_by_id[link['left']['node_id']],query,graph,kind=link['kind']))
    for item in unresolved:
        item.update(suggestion_class='unresolved_reference_review',automatic_passage_slot=False,
                    automatic_relationship_traversal=False,reader_assigns_passage_slot=True,
                    class_reason='An explicit source reference has no resolved target; retain it for review.')
    result={'schema':VERSION,'label':NOTICE,'sorter_graph':copy.deepcopy(graph),'ranked_hits':hits,
        'candidate_links':links,'unresolved_references':unresolved,'assessment':core.assessment('suggestions_for_review'),
        'configuration':{'query':query,'synonym_ranker':synonym_ranker,'candidate_relater':candidate_relater,
                         'builtin_vocabulary':copy.deepcopy(BUILTIN),'user_glossary':custom,'user_glossary_sha256':core.digest(custom)},
        'limits':limits,'signal_budget_exhausted':signal_partial,'all_matching_statements_retained':True,
        'search_complete':False,'core_extraction_complete':graph['complete'],
        'source_authority_changed':False,'transitive_paths_generated':False,
        'neighbor_overlap_creates_relationship':False,
        'implementation_sha256':core.sha(Path(__file__).read_bytes())}
    result['suggestions_sha256']=core.digest(result)
    if len(json.dumps(result,ensure_ascii=False).encode())>33554432:raise core.SortError('Suggestion output exceeds32MiB; no partial claim is returned')
    return result


def verify_suggestions(result,directory):
    if result.get('schema')!=VERSION:raise core.SortError('Unknown review schema')
    config=result['configuration']
    expected=suggestions(result['sorter_graph'],directory,config['query'],
        synonym_ranker=config['synonym_ranker'],candidate_relater=config['candidate_relater'],user_glossary=config['user_glossary'])
    if expected!=result:raise core.SortError('Review source, vocabulary, scores or links changed')
    return {'status':'replayed_review_suggestions','assessment':core.assessment(),'semantic_truth_verified':False}


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv[:1]==['peruse']:
        p=argparse.ArgumentParser(description=NOTICE);p.add_argument('command');p.add_argument('graph',type=Path)
        p.add_argument('--sources',required=True,type=Path);p.add_argument('--max-items',type=int,default=8);a=p.parse_args(argv)
        try:
            result=core._load(a.graph)
            if result.get('schema')!=VERSION:return core.main(argv)
            if not 1<=a.max_items<=64:raise core.SortError('Perusal bound must be1–64')
            verify_suggestions(result,a.sources)
            print(json.dumps({'label':NOTICE,'ranked_hits':result['ranked_hits'][:a.max_items],
                'candidate_links':result['candidate_links'][:a.max_items],'unresolved_references':result['unresolved_references'][:a.max_items],
                'omitted_hits':max(0,len(result['ranked_hits'])-a.max_items),'omitted_links':max(0,len(result['candidate_links'])-a.max_items),
                'full_results_file':str(a.graph),'assessment':core.assessment()},ensure_ascii=False,indent=2));return 0
        except (ValueError,OSError,KeyError,TypeError,RecursionError) as exc:
            print(json.dumps({'label':NOTICE,'status':'refused','error':str(exc),'assessment':core.assessment()}),file=sys.stderr);return 2
    # No new option means exact delegation, including old hashes and defaults.
    if not any(x in argv for x in ['--synonym-ranker','--candidate-relater']):return core.main(argv)
    p=argparse.ArgumentParser(description=NOTICE);p.add_argument('command',choices=['sort']);p.add_argument('directory',type=Path)
    p.add_argument('--mode',choices=['not-compared','not compared','compare'],default='not-compared');p.add_argument('--query',default='')
    p.add_argument('--synonym-ranker',action='store_true');p.add_argument('--candidate-relater',action='store_true')
    p.add_argument('--glossary',type=Path);p.add_argument('--limits',type=Path);p.add_argument('--prior',type=Path)
    p.add_argument('--output',required=True,type=Path);a=p.parse_args(argv)
    try:
        custom=None
        if a.glossary:
            raw=a.glossary.read_bytes()
            if len(raw)>65536:raise core.SortError('Glossary exceeds64KiB')
            custom=json.loads(raw.decode('utf-8'))
        limits=core._load(a.limits,65536) if a.limits else None
        prior=a.prior.read_bytes().decode('utf-8') if a.prior else None
        graph=core.sort_directory(a.directory,mode=a.mode,limits=limits,prior_text=prior)
        result=suggestions(graph,a.directory,a.query,synonym_ranker=a.synonym_ranker,candidate_relater=a.candidate_relater,user_glossary=custom)
        core._save(a.output,result,a.directory)
        print(json.dumps({'label':NOTICE,'output':str(a.output),'hits':len(result['ranked_hits']),
                          'candidate_links':len(result['candidate_links']),'assessment':core.assessment()},ensure_ascii=False));return 0
    except (ValueError,OSError,KeyError,TypeError,RecursionError) as exc:
        print(json.dumps({'label':NOTICE,'status':'refused','error':str(exc),'assessment':core.assessment()}),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
