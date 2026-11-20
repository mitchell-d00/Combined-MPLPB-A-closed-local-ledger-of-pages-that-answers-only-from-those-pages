"""Explicit source-bound relation crawling through the existing work coordinator.

The experts are versioned local software roles, not human historians or provider
calls. Their report is documentary evidence for inspection, never a supported
world answer, a grant, or a current operational instruction.
"""
import copy
import json
import os
from pathlib import Path
import tempfile

from mplpb_answers.body_text import body_text
from mplpb_combined import provenance_gate as G
from mplpb_combined.ledger import Ledger
from mplpb_combined.reader import PROFILES, DEFAULT_PROFILE, terms
from . import historical_evidence as documentary
from .historical_verifier import verification_snapshot, verify_observations
from .event_candidates import inspect_events
from .store import WorkStore, digest

VERSION = 'bounded-relation-investigation-v1'
ROLES = ('documentary', 'chronology', 'verification')
OPERATIONS = {role: 'history.'+role+'.v1' for role in ROLES}


def _eligible(root,question,profile):
    gate=G.gather(root,question,profile)
    ledger=Ledger(root)
    if any(r.kind=='pointer' for r in ledger.servable()):
        raise ValueError('Choose a directly selected corpus; expert crawling never follows corpus pointers')
    excluded={s['path'] for s in gate.excluded}
    lexical={s['path'] for s in gate.sources}
    return {r.id:r for r in ledger.servable() if r.kind not in {'pointer','index'}
            and r.path not in excluded and (profile.prose or r.path in lexical)}


def _chronology(observations):
    """Keep precision/basis explicit; dates are declarations, not publication."""
    dates = []
    for observation in observations:
        if observation['kind'] != 'declared_date':
            continue
        value = observation['value']
        dates.append({'source_id': observation['source_id'], 'value': value,
                      'precision': 'timestamp' if 'T' in value else 'day',
                      'basis': 'author_declared_document_date',
                      'citation': copy.deepcopy(observation)})
    # Sorting is a display order only. Mixed precision/time zones never establish
    # invention, causal order, first appearance or publication precedence.
    dates.sort(key=lambda item: (item['value'][:10], item['source_id'], item['value']))
    return {'dates': dates, 'historical_event_order_verified': False,
            'publication_priority_verified': False,
            'notice': 'Declared document dates only. Git timestamps, observation time and event time are separate evidence bases.'}


def _crawl(root, question, profile, start_source_ids, max_hops, max_sources, max_chars,
           *, adaptive_search=False):
    state = verification_snapshot(root, question, profile)
    eligible=_eligible(root,question,profile)
    available={identifier:{'id':identifier,'path':r.path,'hash':r.hash_actual}
               for identifier,r in eligible.items()}
    if start_source_ids:
        if len(set(start_source_ids)) != len(start_source_ids) or any(i not in available for i in start_source_ids):
            raise ValueError('Choose unique, currently eligible source identifiers')
        seeds = list(start_source_ids)
    else:
        seeds = []

    # Header indexing is discovery, never answer evidence. Only visited sources
    # enter the report, and every typed finding goes through the verifier below.
    headers, identities, ranked = {}, {}, []
    discovery_complete = len(eligible) <= 256
    discovery_chars=0
    query_terms=terms(question)
    uncovered_terms=query_terms.copy()
    body_hits={}
    for identifier,record in list(eligible.items())[:256]:
        prefix=record.body_html[:50000]
        if discovery_chars+len(prefix)>1000000:
            discovery_complete=False
            break
        discovery_chars+=len(prefix)
        header=body_text(prefix)[:20000]
        headers[identifier]=documentary.extract(header)
        header_terms=terms(header)
        if adaptive_search:
            body_hits[identifier]=query_terms & header_terms
        score=len(query_terms & (header_terms | terms(record.scope+' '+record.title)))
        if score:ranked.append((-score,identifier))
        for item in headers[identifier]:
            if item['kind'] == 'document_identity':
                identities.setdefault(item['target_id'], []).append((identifier, item['target_version']))
    if not start_source_ids:
        seeds=[identifier for _,identifier in sorted(ranked)[:min(max_sources,12)]]
    queue = [(identifier, 0) for identifier in seeds]
    visited, observations, edges, stops = [], [], [], []
    queued = dict.fromkeys(seeds, 0)
    supersession_targets=set()
    truncated_hops=[]
    used = 0
    observation_budget_reached=False
    while queue:
        next_index = 0
        if adaptive_search and queue[0][1] > 0:
            # Stay in the shallowest layer. Re-rank its frontier as earlier
            # sources cover terms. These hints only schedule source inspection.
            def priority(index):
                target, hop = queue[index]
                return (hop, target not in supersession_targets,
                        -len(body_hits[target] & uncovered_terms), index)
            next_index = min(range(len(queue)), key=priority)
        identifier, depth = queue.pop(next_index)
        if identifier not in headers:
            stops.append({'source_id':identifier,'reason':'discovery_budget'})
            continue
        record=eligible[identifier]
        if len(record.body_html)>max_chars*8+10000:
            stops.append({'source_id':identifier,'reason':'source_projection_budget'})
            continue
        body = body_text(record.body_html)
        if len(visited) >= max_sources or used+len(body) > max_chars:
            stops.append({'source_id':identifier,'reason':'source_or_character_budget'})
            continue
        source = available[identifier]
        extracted=documentary.extract(body)
        if len(observations)+len(extracted)>256:
            observation_budget_reached=True
            stops.append({'source_id':identifier,'reason':'observation_budget'})
            continue
        observation_budget_reached=observation_budget_reached or len(extracted)>=64
        if adaptive_search:
            if uncovered_terms:
                uncovered_terms.difference_update(terms(body))
            if len(extracted)>=64:
                truncated_hops.append(depth)
        used += len(body)
        visited.append({'id':identifier,'path':source['path'],'hash':source['hash'],'depth':depth})
        source_observations = []
        for item in extracted:
            observation = dict(item, source_id=identifier, path=source['path'], hash=source['hash'])
            observations.append(observation)
            source_observations.append(observation)
        for observation in source_observations:
            if observation['kind'] not in {'related', 'supersedes'}:
                continue
            target = observation['target_id']
            edge = {'source_id':identifier, 'relation':'source_declared_'+observation['kind'],
                    'target_document_id':target, 'target_version':observation['target_version'],
                    'citation':copy.deepcopy(observation), 'target_source_id':'', 'status':'unresolved'}
            matches = identities.get(target, []) if target else []
            version = observation['target_version']
            matches = list(dict.fromkeys(s for s,v in matches if not version or v == version))
            if not target:
                edge['status'] = 'unresolved_target_identifier'
            elif not discovery_complete:
                edge['status'] = 'discovery_incomplete'
            elif not matches:
                # Do not reveal whether an excluded/private target exists.
                edge['status'] = 'target_unavailable'
            elif len(matches) != 1:
                edge['status'] = 'ambiguous_target'
            else:
                edge['target_source_id'] = matches[0]
                if adaptive_search and depth < max_hops and observation['kind']=='supersedes':
                    supersession_targets.add(matches[0])
                if matches[0] in queued:
                    edge['status'] = 'already_discovered'
                elif depth >= max_hops:
                    edge['status'] = 'hop_limit'
                else:
                    edge['status'] = 'queued'
                    queue.append((matches[0], depth+1))
                    queued[matches[0]] = depth+1
            edges.append(edge)
    # All endpoints are independently verified too; a header-index guess cannot
    # become a valid relationship target simply because the crawler selected it.
    verification = verify_observations(root, question, profile, observations, state)
    valid = verification.get('verified', [])
    valid_keys = {digest(o) for o in valid}
    identities_valid = {(o['source_id'],o['target_id'],o['target_version'])
                        for o in valid if o['kind']=='document_identity'}
    verified_edges = []
    visited_ids = {s['id'] for s in visited}
    for edge in edges:
        if digest(edge['citation']) not in valid_keys:
            continue
        if edge['target_source_id']:
            binding = (edge['target_source_id'],edge['target_document_id'],edge['target_version'])
            matches = [x for x in identities_valid if x[0]==binding[0] and x[1]==binding[1]
                       and (not binding[2] or x[2]==binding[2])]
            if edge['target_source_id'] not in visited_ids:
                edge['status'] = 'hop_limit' if edge['status']=='hop_limit' else 'source_or_character_budget'
                edge['target_source_id'] = ''
            elif not matches:
                edge['status'], edge['target_source_id'] = 'unverified_target_identity', ''
            elif edge['status'] in {'queued','already_discovered'}:
                edge['status'] = 'traversed'
        verified_edges.append(edge)
    report = {'sources':visited,'observations':valid,'relations':verified_edges,
            'verification':verification,'snapshot':state,'seeds':seeds,
            'stops':stops,'discovery_complete':discovery_complete,
            'discovery_characters_examined':discovery_chars,
            'discovery_limits':{'sources':256,'source_html_prefix':50000,'total_html_characters':1000000},
            'source_characters_examined':used,
            'observation_budget_reached':observation_budget_reached}
    if adaptive_search:
        deepest = max((source['depth'] for source in visited), default=-1)
        incomplete_hops = truncated_hops + [queued[stop['source_id']] for stop in stops]
        completed = min([deepest + 1] + incomplete_hops)-1
        report['adaptive_search'] = {
            'deepest_visited_hop': deepest if deepest >= 0 else None,
            'completed_hop': completed if discovery_complete and completed >= 0 else None,
        }
    return report


def investigate(root, question, *, profile=None, start_source_ids=None, max_hops=2,
                max_sources=12, max_chars=200000, work_directory=None, prose_candidates=False,
                adaptive_search=False):
    """Run a bounded documentary investigation with three capability-gated seats.

    Omit work_directory for ephemeral work; an explicit new directory retains the
    private work ledger and a host credential file for later native recovery.
    No source pages are written, no provider is invoked, and no corpus boundary
    is crossed. A different question's exclusions are never substituted.
    """
    if not isinstance(question,str) or not question.strip() or len(question)>4000:
        raise ValueError('Question must contain 1–4000 characters')
    if type(max_hops) is not int or not 0<=max_hops<=5:
        raise ValueError('Hop budget must be 0–5')
    if type(max_sources) is not int or not 1<=max_sources<=32:
        raise ValueError('Source budget must be 1–32')
    if type(max_chars) is not int or not 1000<=max_chars<=1000000:
        raise ValueError('Character budget must be 1000–1000000')
    if type(prose_candidates) is not bool:raise ValueError('prose_candidates must be a boolean')
    if type(adaptive_search) is not bool:raise ValueError('adaptive_search must be a boolean')
    profile = profile or PROFILES[DEFAULT_PROFILE]
    if profile.name not in PROFILES or profile != PROFILES[profile.name]:
        raise ValueError('Choose a known delivery profile')
    if start_source_ids is not None and (not isinstance(start_source_ids,list)
            or len(start_source_ids)>max_sources or any(not isinstance(i,str) for i in start_source_ids)):
        raise ValueError('Invalid starting source identifiers')
    if start_source_ids:
        eligible=set(_eligible(root,question,profile))
        if len(set(start_source_ids))!=len(start_source_ids) or not set(start_source_ids)<=eligible:
            raise ValueError('Choose unique, currently eligible source identifiers')
    if work_directory is None:
        with tempfile.TemporaryDirectory(prefix='mplpb-history-') as directory:
            return _run(root,question,profile,start_source_ids,max_hops,max_sources,max_chars,
                        directory,False,prose_candidates,adaptive_search=adaptive_search)
    return _run(root,question,profile,start_source_ids,max_hops,max_sources,max_chars,
                work_directory,True,prose_candidates,adaptive_search=adaptive_search)


def _run(root, question, profile, seeds, hops, count, chars, directory, persistent,
         prose_candidates=False, *, adaptive_search=False):
    initial = verification_snapshot(root,question,profile)
    store, authority = WorkStore.create(directory, {'investigation':Path(root).resolve()})
    if persistent:
        credential_path=Path(directory)/'host-credential.json'
        fd=os.open(str(credential_path),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(fd,'w') as stream:
            json.dump({'authority_credential':authority},stream)
    tokens={}
    for role in ROLES:
        grant=store.assign(authority,seat=role,instance=role+'-1',
            model={'name':'deterministic-local-expert','provider':'local-software','version':VERSION,
                   'context_policy_hash':digest({'role':role,'profile':profile.name})},
            contract={'operations':['create:task','revise:task','create:evidence','create:action','execute'],
                      'tools':[OPERATIONS[role]],'scopes':['investigation'],
                      'share_with':list(ROLES),'profile':profile.name,'expires_at':store.clock()+3600},
            expected_head=store.head(authority)['hash'])
        tokens[role]=grant['credential']
    def put(role,identifier,kind,payload,dependencies=None,revision=0):
        return store.put(tokens[role],id=identifier,kind=kind,payload=payload,
            dependencies=dependencies or {},visibility=list(ROLES),expected_revision=revision,
            expected_head=store.snapshot(tokens[role])['head'])
    criteria={role:role+' expert source checks pass' for role in ROLES}
    task={'goal':question,'criteria':list(criteria.values()),'review_budget':3,'state':'open','acceptance':{}}
    put('documentary','investigation','task',task)
    report={}
    arguments={'question':question,'profile':profile.name}
    if adaptive_search:
        arguments['adaptive_search']=True
    def adapter(role):
        def run(request):
            if request['action']['payload']['arguments'] != arguments:
                raise ValueError('Expert arguments changed')
            if role=='documentary':
                report.update(_crawl(root,question,profile,seeds,hops,count,chars,
                                     adaptive_search=adaptive_search))
                report['event_candidates']=inspect_events(root,question,profile,
                    [s['id'] for s in report.get('sources',[])],initial)
            elif role=='chronology':
                report['chronology']=_chronology(report.get('observations',[]))
            else:
                report['verification']=verify_observations(root,question,profile,report.get('observations',[]),initial)
                report['observations']=report['verification'].get('verified',[])
                report['event_candidates']=inspect_events(root,question,profile,
                    [s['id'] for s in report.get('sources',[])],initial)
            current=verification_snapshot(root,question,profile)==initial
            verified=report.get('verification',{})
            passed=(current and verified.get('source_state_current',False) and not verified.get('rejected')
                    and report.get('event_candidates',{}).get('source_state_current',False))
            artifact={'role':role,'report_sha256':digest(report),'source_state_current':current}
            return {'result':'passed' if passed else 'failed','validation':{criteria[role]:passed},
                    'artifact':json.dumps(artifact,sort_keys=True)}
        return run
    receipts=[]
    dependencies={}
    for role in ROLES:
        store.executors[OPERATIONS[role]]=adapter(role)
        action={'task':'investigation','task_revision':1,'operation':OPERATIONS[role],
                'arguments':arguments,'side_effect':'local',
                'executor_seat':role,'state':'proposed','retry_of':{},'retry_reason':''}
        identifier='inspect-'+role
        put(role,identifier,'action',action,dependencies)
        result=store.execute(tokens[role],id=identifier,expected_revision=1,
                             expected_head=store.snapshot(tokens[role])['head'])
        receipts.append({'role':role,'receipt':result['receipt']['id'],'status':result['receipt']['status']})
        if result['receipt']['status']!='passed':
            break
        dependencies[result['attempt']]=1
        task['acceptance'][result['attempt']]=1
        if role=='documentary':
            # Downstream expert actions and completion retain actual source
            # dependencies, not merely the first expert's success label.
            records={r.path:r for r in Ledger(root).servable()}
            for number,source in enumerate(report.get('sources',[]),1):
                record=records[source['path']]
                quote=body_text(record.body_html).splitlines()[0][:1000]
                evidence_id='source-'+str(number)
                put(role,evidence_id,'evidence',{'task':'investigation','corpus':'investigation',
                    'source_id':source['id'],'source_hash':source['hash'],
                    'quote':quote,'query':question})
                dependencies[evidence_id]=1
    unchanged=verification_snapshot(root,question,profile)==initial
    verified=report.get('verification',{})
    passed=len(receipts)==3 and all(r['status']=='passed' for r in receipts) and unchanged
    if passed:
        task['state']='done'
        put('verification','investigation','task',task,revision=1)
    if prose_candidates and passed:
        from .prose_evidence import discover
        report['prose_candidates']=discover(root,question,profile,max_passages=12,max_chars=min(chars,12000))
    # Completion itself performs fresh dependency reads. Recheck the entire
    # serving state afterwards too, before exposing any old source quotation.
    unchanged=verification_snapshot(root,question,profile)==initial
    passed=passed and unchanged
    if not unchanged or not verified.get('source_state_current',False):
        report={'sources':[],'observations':[],'relations':[],
                'verification':{'source_state_current':False,'verified':[],'rejected':[]},
                'notice':'Source eligibility or policy changed; old findings were discarded.'}
    elif not passed:
        report={'sources':[],'observations':[],'relations':[],
                'verification':{'source_state_current':True,'verified':[],'rejected':[]},
                'notice':'An expert stage failed validation; no findings were accepted.'}
    operator_view=store.handoff(tokens['verification'])
    report.update(operator_seconds=operator_view['operator_seconds'],operator_events=operator_view['operator_events'],
                  schema=VERSION,question=question,profile=profile.name,
                  authority='verified_documentary_observations' if passed else 'unverified_investigation',
                  status='evidence_report' if passed else 'needs_recheck',answer_supported=False,
                  truth_verified=False,independence_verified=False,
                  experts=[{'role':r,'operation':OPERATIONS[r],'implementation':'deterministic local software'} for r in ROLES],
                  receipts=receipts,work_retained=persistent,
                  boundaries={'max_hops':hops,'max_sources':count,'max_source_characters':chars,
                              'corpus_escape_allowed':False,'title_guessing_allowed':False,
                              'causal_inference_allowed':False,'source_pages_written':False},
                  unresolved=['Interpretation of the original question beyond the declared fields remains unproved.',
                              'Related and supersedes declarations do not prove causation, endorsement or historical priority.',
                              'Missing, excluded, retired, ambiguous or over-budget targets were not traversed.'])
    report.pop('snapshot',None)
    return report
