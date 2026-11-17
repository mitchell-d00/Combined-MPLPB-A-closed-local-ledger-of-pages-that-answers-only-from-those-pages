"""Offline raw-text candidate sorter. No source support or historical truth engine.

Extraction, provisional assessment and comparison are separate pure stages.
Source text is decoded strictly as UTF-8 without newline/Unicode normalization.
"""
import argparse
from array import array
from collections import defaultdict
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tempfile
import sys
import time

from .prose_relations import date_cues

VERSION = 'offline-candidate-sorter-v1'
EXTENSIONS = {'.txt', '.text', '.md', '.markdown'}
DEFAULT_LIMITS = {'files':64, 'file_bytes':1048576, 'total_bytes':8388608,
                  'tree_entries':4096, 'directory_depth':12, 'nodes':4096,
                  'edges':8192, 'statements':2000, 'statement_chars':8000,
                  'comparisons':20000, 'phrase_keys':4096, 'phrase_groups':32,
                  'prior_bytes':1048576, 'output_bytes':33554432}
HEADER = re.compile(r'^\ufeff?[ \t]*(?:#{1,6}[ \t]+)?(Message-ID|Document-ID|Record-ID|Event-ID|Occurrence-ID|Subject|From|To|Sender|Recipient|Date|Date written|Date sent|Date received|Published|Revised|Status)[ \t]*:[ \t]*(\S[^\r\n]{0,499})(?=\r?$)', re.I|re.M)
IDENTIFIER = re.compile(r'(?<![\w-])[A-Z][A-Z0-9]{1,23}-[A-Za-z0-9][A-Za-z0-9_.:/-]{0,75}(?![\w-])')
TOKEN = r'<?[A-Za-z0-9][A-Za-z0-9_.:@/+\-]{1,98}>?'
REFERENCE = re.compile(r'\b(in reply to|reply to|response to|see|reference|ref\.?|corrects|correction to|amends|retracts|supersedes|revises|cancels)[: \t]+('+TOKEN+r')', re.I)
CORRECTION = re.compile(r'\b(?:corrects?|correction|amends?|amendment|retracts?|retraction|supersedes?|revises?|revision)\b', re.I)
ACTION = re.compile(r'\b(?:sent|received|wrote|published|arrived|ordered|requested|planned|reported|canceled|cancelled|aborted|surrendered|evacuated)\b', re.I)
URL = re.compile(r'https?://[^\s<>"\u201c\u201d]{1,1000}')
WORD = re.compile(r'\b[^\W_]+\b', re.UNICODE)
DATE_ROLES = {'date written':'document_written','date sent':'document_sent',
              'date received':'document_received','published':'publication',
              'revised':'revision','date':'document_stated_role_unresolved'}


class SortError(ValueError):
    pass


def sha(raw):
    return 'sha256:'+hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8'))


def assessment(status='unassessed_candidate'):
    return {'status':status, 'answer_supported':False, 'source_support_established':False,
            'historical_truth_independently_verified':False, 'serving_eligibility':'not_evaluated'}


def limits_for(overrides=None):
    result=dict(DEFAULT_LIMITS)
    if overrides:
        if set(overrides)-set(result):raise SortError('Unknown resource limit')
        for key,value in overrides.items():
            if type(value) is not int or not 1<=value<=DEFAULT_LIMITS[key]:
                raise SortError('Limits may only lower the published positive integer bounds')
            result[key]=value
    return result


def _paths(root,limits,issues):
    """Bound traversal before sorting; no link following or hidden directories."""
    pending=[(root,0)];files=[];examined=0
    while pending:
        directory,depth=pending.pop()
        try:
            with os.scandir(directory) as iterator:
                entries=[]
                for entry in iterator:
                    examined+=1
                    if examined>limits['tree_entries']:
                        issues.add('tree_entry_budget');break
                    entries.append(entry)
        except OSError as exc:raise SortError('Cannot inspect source directory') from exc
        for entry in sorted(entries,key=lambda e:e.name):
            if entry.name.startswith('.'):continue
            path=Path(entry.path)
            if entry.is_symlink():issues.add('symlink_excluded');continue
            if entry.is_dir(follow_symlinks=False):
                if depth>=limits['directory_depth']:issues.add('directory_depth_budget')
                else:pending.append((path,depth+1))
            elif path.suffix.lower() in EXTENSIONS:
                if not entry.is_file(follow_symlinks=False):issues.add('non_regular_file_excluded')
                else:files.append(path.relative_to(root).as_posix())
        if examined>limits['tree_entries']:break
    files.sort()
    if len(files)>limits['files']:issues.add('file_count_budget')
    return files[:limits['files']]


def _read(root,relative,limit):
    """Safe relative regular-file access with no-follow components on POSIX.

    On platforms without dir_fd/no-follow support, reject links and require a
    trusted local filesystem. No claimed protection from a hostile OS/host.
    """
    parts=PurePosixPath(relative).parts
    if (not relative or '\\' in relative or PurePosixPath(relative).is_absolute()
            or any(p in {'','.', '..'} for p in relative.split('/'))):raise SortError('Unsafe source path')
    fd=None
    try:
        if hasattr(os,'O_NOFOLLOW') and os.open in os.supports_dir_fd:
            fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            for part in parts[:-1]:
                child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
                os.close(fd);fd=child
            child=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
            os.close(fd);fd=child
        else:
            current=root
            for part in parts:
                current=current/part
                if current.is_symlink():raise SortError('Source link is not permitted')
            current.resolve().relative_to(root)
            if not current.is_file():raise SortError('Source is not a regular file')
            fd=os.open(current,os.O_RDONLY)
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):raise SortError('Source is not a regular file')
        if before.st_size>limit:return None
        chunks=[];size=0
        while True:
            chunk=os.read(fd,min(65536,limit+1-size))
            if not chunk:break
            size+=len(chunk)
            if size>limit:return None
            chunks.append(chunk)
        after=os.fstat(fd)
        identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        if identity(before)!=identity(after) or size!=after.st_size:raise SortError('Source changed during reading')
        return b''.join(chunks)
    except OSError as exc:raise SortError('Source is unavailable or unsafe: '+relative) from exc
    finally:
        if fd is not None:os.close(fd)


def _byte_offsets(text):
    values=array('I',[0]);offset=0
    for char in text:
        offset+=len(char.encode('utf-8'));values.append(offset)
    return values


def _span(source,text,offsets,start,end,quote=True):
    result={'source_id':source['id'],'source_sha256':source['raw_sha256'],
            'path':source['path'],'char_start':start,'char_end':end,
            'byte_start':offsets[start],'byte_end':offsets[end]}
    if quote:result['text']=text[start:end]
    return result


def assign_status(kind,value=None,scope=None):
    """Provisional labels only. Never change ledger or preceding claim state."""
    status='unassessed_candidate'
    if kind=='source_occurrence':status='source_occurrence_candidate'
    if kind=='event_candidate':status='possible_event_candidate'
    if kind=='correction_mention':status='possible_correction'
    if kind=='declared_status' and isinstance(value,str) and value.lower() in {'current','retired'}:status=value.lower()+'_candidate'
    if scope and scope!='unqualified_text':status+=';scope_review_required'
    return assessment(status)


def _fence_ranges(text):
    ranges=[];opened=None
    for match in re.finditer(r'(?m)^[ \t]*(`{3,}|~{3,})[^\r\n]*',text):
        marker=match[1]
        if opened is None:opened=(match.start(),marker)
        elif marker[0]==opened[1][0] and len(marker)>=len(opened[1]):
            ranges.append((opened[0],match.end()));opened=None
    if opened:ranges.append((opened[0],len(text)))
    return ranges


def _scope(text):
    if re.search(r'(?m)^\s*>|```|~~~|[\u201c\u201d"]',text):return 'quoted_or_format_scope_unresolved'
    if re.search(r'\b(?:if|unless|would|might|could|will|shall|hope|planned|intended)\b',text,re.I):return 'conditional_or_uncertain'
    if re.search(r'\b(?:not|never|no)\b.{0,50}\b(?:correct|correction|amend|supersed|revis|retract)',text,re.I):return 'negated_correction_mention'
    return 'unqualified_text'


def extract(root,limits):
    """Raw extraction does not resolve references, identity, or chronology."""
    issues=set();sources=[];nodes=[];edges=[];phrases=defaultdict(list);statements=0;bytes_read=0
    def add(kind,source,text,offsets,a,b,**fields):
        if len(nodes)>=limits['nodes']:issues.add('node_budget');return None
        evidence=_span(source,text,offsets,a,b)
        node={'id':'node:'+digest([kind,source['id'],a,b])[7:], 'kind':kind,
              'span':evidence,'assessment':assessment(),
              **fields}
        nodes.append(node);return node
    def edge(left,right,kind,evidence,**extra):
        if not left or not right:return
        if len(edges)>=limits['edges']:issues.add('edge_budget');return
        edges.append({'id':'edge:'+digest([left['id'],right['id'],kind])[7:],
                      'from':left['id'],'to':right['id'],'kind':kind,'evidence_nodes':evidence,
                      'confidence':None,'evidence_note':'Literal source-text observation; no historical relationship established.',
                      'assessment':assessment(),**extra})
    paths=_paths(root,limits,issues);scan_issues=set(issues)
    for relative in paths:
        remaining=limits['total_bytes']-bytes_read
        if remaining<=0:issues.add('total_byte_budget');break
        raw=_read(root,relative,min(limits['file_bytes'],remaining))
        if raw is None:issues.add('file_or_total_byte_budget');continue
        bytes_read+=len(raw)
        source={'id':'source:'+digest([relative,sha(raw)])[7:], 'path':relative,
                'raw_sha256':sha(raw),'bytes':len(raw),'encoding':'utf-8',
                'policy_status':'not_evaluated','assessment':assessment()}
        sources.append(source)
        try:text=raw.decode('utf-8')
        except UnicodeDecodeError:
            source['decoding']='rejected_invalid_utf8';issues.add('invalid_utf8');continue
        offsets=_byte_offsets(text);headers=list(HEADER.finditer(text));fences=_fence_ranges(text)
        # Explicit identifier layout may delimit several occurrences in a file.
        # A header/date/title is never proof of the underlying event identity.
        marker=None
        for name in ('message-id','document-id','record-id'):
            matches=[m for m in headers if m[1].lower()==name]
            if matches:marker=matches;break
        starts=[0]+([m.start() for m in marker[1:]] if marker else [])
        for begin,end in zip(starts,starts[1:]+[len(text)]):
            if begin==end:continue
            occurrence=add('source_occurrence',source,text,offsets,begin,end,
                           boundary_basis='identifier_header_layout_candidate' if len(starts)>1 else 'whole_file_appearance',
                           event_identity=None,independent_event_established=False)
            if not occurrence:break
            # Do not duplicate a large whole source as quoted node text.
            occurrence['span'].pop('text')
            local_headers=[m for m in headers if begin<=m.start()<end]
            body_start=begin
            for line in text[begin:end].splitlines(keepends=True):
                if not line.strip():body_start+=len(line);break
                if HEADER.match(line):body_start+=len(line)
                else:break
            occurrence['body_span']=_span(source,text,offsets,body_start,end,False)
            occurrence['body_sha256']=sha(text[body_start:end].encode('utf-8'))
            occurrence['declared_status_candidates']=[]
            cursor=begin
            # Complete physical paragraphs, including wrapped lines. Oversized
            # units are not silently chopped into purported complete statements.
            boundaries=[(m.start(),m.end()) for m in re.finditer(r'(?:\r?\n)[ \t]*(?:\r?\n)',text[begin:end])]
            ends=[begin+a for a,b in boundaries]+[end]
            nexts=[begin+b for a,b in boundaries]+[end]
            for stop,nxt in zip(ends,nexts):
                a=cursor;b=stop;cursor=nxt
                if not text[a:b].strip():continue
                statements+=1
                if statements>limits['statements']:issues.add('statement_budget');break
                if b-a>limits['statement_chars']:issues.add('statement_character_budget');continue
                unit_scope='quoted_or_format_scope_unresolved' if any(lo<b and hi>a for lo,hi in fences) else _scope(text[a:b])
                statement=add('statement',source,text,offsets,a,b,occurrence=occurrence['id'],scope=unit_scope)
                if not statement:break
                edge(occurrence,statement,'contains_statement',[statement['id']])
                scope=statement['scope'];items=[]
                def feature(kind,lo,hi,**fields):
                    item=add(kind,source,text,offsets,lo,hi,statement=statement['id'],occurrence=occurrence['id'],scope=scope,**fields)
                    if item:
                        items.append(item);edge(statement,item,'contains_extracted_item',[statement['id'],item['id']])
                    return item
                for m in local_headers:
                    if not a<=m.start()<b:continue
                    name=m[1].lower();value=m[2].rstrip();lo=m.start(2);hi=lo+len(value)
                    kind='header_identifier' if name.endswith('-id') else 'declared_status' if name=='status' else 'header'
                    item=feature(kind,lo,hi,value=value,header_name=name)
                    if name=='status' and item:
                        occurrence['declared_status_candidates'].append({'value':value,'evidence_node':item['id']})
                for m in IDENTIFIER.finditer(text,a,b):feature('identifier',m.start(),m.end(),value=m[0])
                for m in URL.finditer(text,a,b):feature('literal_url',m.start(),m.end(),value=m[0],fetched=False)
                for m in date_cues(text[a:b]):
                    lo=a+m.start();hi=a+m.end();role='unresolved'
                    for h in local_headers:
                        if h.start(2)<=lo<hi<=h.end(2):role=DATE_ROLES.get(h[1].lower(),'unresolved')
                    feature('date_expression',lo,hi,value=m[0],date_role=role,normalized_event_time=None)
                for m in REFERENCE.finditer(text,a,b):
                    feature('reference_mention',m.start(),m.end(),value=m[2],reference_wording=m[1].lower())
                for m in CORRECTION.finditer(text,a,b):feature('correction_mention',m.start(),m.end(),value=m[0])
                for m in list(ACTION.finditer(text,a,b))[:8]:feature('event_candidate',m.start(),m.end(),value=m[0],event_occurrence_established=False)
                # Bounded four-word shingles are lexical keys, not event keys.
                words=list(WORD.finditer(text,a,b))
                if len(words)>256:issues.add('phrase_token_budget')
                for j in range(min(len(words)-3,253)):
                    lo,hi=words[j].start(),words[j+3].end()
                    if hi-lo>160 or hi-lo<16:continue
                    key=' '.join(w[0].casefold() for w in words[j:j+4])
                    if key not in phrases and len(phrases)>=limits['phrase_keys']:
                        issues.add('phrase_key_budget');break
                    if len(phrases[key])<8:
                        phrases[key].append((source,text,offsets,lo,hi,statement['id'],occurrence['id']))
                for i,left in enumerate(items[:6]):
                    for right in items[i+1:6]:edge(left,right,'textual_cooccurrence',[statement['id'],left['id'],right['id']])
            if statements>limits['statements']:break
    groups=0
    for key,appearances in sorted(phrases.items()):
        if len(appearances)<2:continue
        if groups>=limits['phrase_groups']:issues.add('repeated_phrase_group_budget');break
        groups+=1
        for source,text,offsets,a,b,stmt,occ in appearances:
            item=add('phrase_key',source,text,offsets,a,b,value=key,statement=stmt,occurrence=occ,
                     normalization='four consecutive lexical word tokens; casefold and punctuation/whitespace ignored',scope='lexical_key_only')
            if item:edge({'id':stmt},item,'contains_extracted_item',[stmt,item['id']])
    return {'sources':sources,'nodes':nodes,'edges':edges,'issues':issues,'bytes_read':bytes_read,'paths':paths,'scan_issues':scan_issues}


def assign_statuses(extracted):
    """Label an extracted graph without changing any source or old assessment."""
    for node in extracted['nodes']:
        node['assessment']=assign_status(node['kind'],node.get('value'),node.get('scope'))
        if node['kind']=='source_occurrence':
            values={d['value'].casefold() for d in node['declared_status_candidates']}
            node['provisional_ledger_status']=(next(iter(values))+'_candidate' if len(values)==1
                and values<={'current','retired'} else 'ambiguous_candidate' if len(values)>1 else 'undetermined_candidate')
    return extracted


def compare(extracted,limits):
    """Append review edges only; never alter raw nodes, statuses or sources.

    Candidate clusters are hyperedge annotations (members), not merged or new
    nodes. Missing/ambiguous links become review annotations, not guessed hops.
    """
    nodes=extracted['nodes'];edges=extracted['edges'];issues=extracted['issues']
    by_id={n['id']:n for n in nodes};identifiers=defaultdict(list);subjects=defaultdict(list);phrases=defaultdict(list);checks=0
    for node in nodes:
        if node['kind']=='header_identifier':identifiers[node['value']].append(node)
        elif node['kind']=='header' and node['header_name']=='subject':subjects[node['value']].append(node)
        elif node['kind']=='phrase_key':phrases[node['value']].append(node)
    edge_ids={e['id'] for e in edges}
    def propose(left,right,kind,evidence,note,**extra):
        nonlocal checks
        checks+=1
        if checks>limits['comparisons']:issues.add('comparison_budget');return
        if len(edges)>=limits['edges']:issues.add('edge_budget');return
        edge={'id':'edge:'+digest([left,right,kind,evidence])[7:],'from':left,'to':right,
              'kind':kind,'evidence_nodes':evidence,'confidence':None,'evidence_note':note,
              'assessment':assessment('needs_review'),'comparison_only':True,**extra}
        if edge['id'] not in edge_ids:edges.append(edge);edge_ids.add(edge['id'])
    for key,items in sorted(identifiers.items()):
        namespaces=defaultdict(list)
        for item in items:namespaces[item['header_name']].append(item)
        for namespace,members in namespaces.items():
            occurrences=sorted({m['occurrence'] for m in members})
            if len(occurrences)<2:continue
            bodies={by_id[o]['body_sha256'] for o in occurrences}
            propose(occurrences[0],occurrences[1],'candidate_identity_cluster',[m['id'] for m in members],
                    'Shared declared identifier only. Occurrences remain separate; repeated appearances do not establish independent events.',
                    cluster_id='cluster:'+digest([namespace,key,occurrences])[7:],members=occurrences,
                    identity_namespace=namespace,key=key,changed_bodies=len(bodies)>1,
                    historical_identity_established=False)
    for key,members in sorted(subjects.items()):
        values=list({m['occurrence']:m for m in members}.values())[:16]
        for i,left in enumerate(values):
            for right in values[i+1:]:
                changed=by_id[left['occurrence']]['body_sha256']!=by_id[right['occurrence']]['body_sha256']
                propose(left['occurrence'],right['occurrence'],'shared_header_review',[left['id'],right['id']],
                        'Equal subject wording is not identity; '+('bodies differ.' if changed else 'body bytes repeat.'),changed_bodies=changed)
    for key,members in sorted(phrases.items()):
        values=list({m['occurrence']:m for m in members}.values())
        for left,right in zip(values,values[1:]):
            propose(left['occurrence'],right['occurrence'],'repeated_phrase_review',[left['id'],right['id']],
                    'Lexical overlap only. No identity, chronology, causality or corroboration is established.')
    for node in nodes:
        if node['kind']!='reference_mention':continue
        correction=bool(CORRECTION.search(node['reference_wording']))
        statement=by_id[node['statement']];quote=statement['span']['text'];window={}
        if correction:
            for date in nodes:
                if date.get('statement')!=node['statement'] or date['kind']!='date_expression':continue
                start=date['span']['char_start']-statement['span']['char_start'];prefix=quote[max(0,start-35):start]
                if re.search(r'\beffective\s+(?:from\s+)?$',prefix,re.I):window['from_expression']=date['span']['text']
                if re.search(r'\b(?:until|through)\s*$',prefix,re.I):window['until_expression']=date['span']['text']
        proposal={'correction_window':{'expressions':window,'date_role':'proposed_effective_window_only','applied':False} if correction else None,
                  'claim_scope_quote':quote if correction else None}
        targets={x['occurrence'] for x in identifiers.get(node['value'],[])}
        reason=('missing_or_outside_budget' if not targets else 'ambiguous_identifier' if len(targets)>1
                else 'self_reference_or_local_identifier' if next(iter(targets))==node['occurrence']
                else 'qualified_or_quoted_reference' if node['scope']!='unqualified_text' else None)
        if reason:
            propose(node['id'],node['occurrence'],'unresolved_reference_review',[node['id'],statement['id']],
                    'No documentary hop is resolved; missing, ambiguous or qualified evidence stops the relation.',
                    reason=reason,candidate_count=len(targets),target_key=node['value'],**proposal)
            continue
        target=next(iter(targets));evidence=[node['id']]+[x['id'] for x in identifiers[node['value']] if x['occurrence']==target]
        partial=correction and bool(re.search(r'\b(?:only|unchanged|remains|in part)\b',quote,re.I))
        propose(node['occurrence'],target,'possible_partial_correction' if partial else 'possible_correction' if correction else 'explicit_reference_candidate',
                evidence+[statement['id']], 'Source wording only; no operational supersession, event identity or completed action is established.',**proposal)
    return extracted


def sort_directory(directory,mode='not-compared',limits=None,prior_text=None):
    if mode=='not compared':mode='not-compared'
    if mode not in {'compare','not-compared'}:raise SortError('Mode must be compare or not-compared')
    root=Path(directory).resolve()
    if not root.is_dir():raise SortError('Source directory does not exist')
    limits=limits_for(limits)
    prior=None
    if prior_text is not None:
        if len(prior_text.encode('utf-8'))>limits['prior_bytes']:raise SortError('Prior graph exceeds history budget')
        previous=json.loads(prior_text)
        if previous.get('schema')!=VERSION or previous.get('graph_sha256')!=digest({k:v for k,v in previous.items() if k!='graph_sha256'}):
            raise SortError('Prior graph integrity/schema mismatch')
        prior={'raw_sha256':sha(prior_text.encode('utf-8')),'snapshot_json':prior_text,
               'authority':'Untrusted historical assessment snapshot; never active source or support.'}
    data=assign_statuses(extract(root,limits))
    if mode=='compare':compare(data,limits)
    # Re-read every included source before returning. Policy is deliberately not
    # inferred: raw files have no established ledger serving authorization.
    rescanned_issues=set()
    if _paths(root,limits,rescanned_issues)!=data['paths'] or rescanned_issues!=data['scan_issues']:
        raise SortError('Source inventory changed during sorting')
    for source in data['sources']:
        current=_read(root,source['path'],limits['file_bytes'])
        if current is None or sha(current)!=source['raw_sha256']:raise SortError('Source changed during sorting')
    return emit_graph(data,mode,limits,prior)


def emit_graph(data,mode,limits,prior=None):
    """Build an inspectable candidate envelope; never an answer contract."""
    if mode not in {'compare','not-compared'}:raise SortError('Unknown emission mode')
    for item in data['sources']+data['nodes']+data['edges']:
        state=item.get('assessment',{})
        if any(state.get(k) is not False for k in ('answer_supported','source_support_established','historical_truth_independently_verified')):
            raise SortError('Candidate emission cannot promote an assessment to source authority')
    graph={'schema':VERSION,'implementation_sha256':sha(Path(__file__).read_bytes()),'mode':mode,'comparison_performed':mode=='compare',
           'sources':data['sources'],'nodes':data['nodes'],'edges':data['edges'],
           'assessment':assessment(),'limits':limits,'complete':not data['issues'],
           'limits_or_exclusions':sorted(data['issues']),'source_bytes_read':2*data['bytes_read'],
           'prior_assessment':prior,'transitive_paths_generated':False,
           'notice':'Derived candidate graph only. Source fidelity, source support and historical truth are separate. No ledger state was changed.'}
    graph['graph_sha256']=digest(graph)
    if len((json.dumps(graph,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))>limits['output_bytes']:raise SortError('Graph exceeds output budget; lower extraction limits')
    return graph


def verify_graph(graph,directory):
    """Independent source reload and deterministic replay, not semantic proof."""
    if graph.get('schema')!=VERSION or graph.get('graph_sha256')!=digest({k:v for k,v in graph.items() if k!='graph_sha256'}):
        raise SortError('Graph integrity/schema mismatch')
    prior=graph.get('prior_assessment')
    rebuilt=sort_directory(directory,graph['mode'],graph['limits'],prior['snapshot_json'] if prior else None)
    if rebuilt!=graph:raise SortError('Source state, graph proposals or implementation changed; no old evidence accepted')
    return {'status':'source_fidelity_replayed','graph_sha256':graph['graph_sha256'],
            'assessment':assessment(),'complete':graph['complete'],
            'notice':'Exact extraction replay only; serving policy, semantic correctness and historical truth are not verified.'}


def export_retired(graph,directory,ledger):
    """Explicit new-ledger snapshot; existing retirement gate withholds it."""
    verify_graph(graph,directory)
    root=Path(directory).resolve();destination=Path(ledger).resolve()
    if destination==root or root in destination.parents:raise SortError('Ledger output must be outside the source tree')
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():raise SortError('Ledger destination must be new')
    from mplpb_combined.ledger import write,withdraw,Ledger
    # Retire in a private staging directory before publishing any page into the
    # requested collection. An interrupted write cannot publish a current page.
    with tempfile.TemporaryDirectory(dir=destination.parent,prefix='.mplpb-sorter-') as tmp:
        stage=Path(tmp)
        title='Unverified sorter candidate snapshot'
        page=write(stage,doc_id='SORTER-CANDIDATES',title=title,
                   scope='sorter candidate inspection',origin='machine',external='no',source_authorship='declared-machine',
                   body_html='<pre>'+html.escape(json.dumps(graph,ensure_ascii=False,indent=2))+'</pre>')
        withdraw(stage,page.id,note='Candidate graph snapshot only; never serving evidence')
        native=Ledger(stage,serving=False)
        # A sealed page is a storage format, not a supported proposition. Use the
        # existing native validator and re-read the actual serialized artifact.
        if native.findings():raise SortError('Native snapshot validation failed; destination not published')
        records=[r for r in native.records if r.kind!='index']
        if len(records)!=1 or not records[0].intact or records[0].status!='retired':
            raise SortError('Candidate snapshot failed integrity/retirement check')
        snapshot=records[0]
        prefix='<h1>'+html.escape(title,quote=False)+'</h1>\n<pre>'
        if snapshot.body_html!=prefix+html.escape(json.dumps(graph,ensure_ascii=False,indent=2))+'</pre>':
            raise SortError('Native snapshot body differs from the candidate graph')
        recovered=json.loads(html.unescape(snapshot.body_html[len(prefix):-6]))
        if recovered!=graph:raise SortError('Native snapshot graph round trip failed')
        if any(r.kind!='index' for r in native.servable()):raise SortError('Candidate snapshot failed retirement gate')
        destination.mkdir(mode=0o700,exist_ok=False)
        os.replace(stage,destination)
    return {'status':'retired_candidate_snapshot','record_id':page.id,'ledger_page_hash':page.hash_actual,
            'graph_sha256':graph['graph_sha256'],'assessment':assessment(),
            'native_validation':{'errors':0,'warnings':0,'graph_roundtrip_verified':True},
            'notice':'Retired sealed snapshot, withheld by existing serving gates. Import originals through normal source workflows; never reactivate graph proposals as facts.'}


def _load(path,limit=33554432):
    with Path(path).open('rb') as f:raw=f.read(limit+1)
    if len(raw)>limit:raise SortError('Input graph exceeds byte budget')
    return json.loads(raw.decode('utf-8'))


def _save(path,value,source_directory=None):
    target=Path(path).resolve()
    if source_directory is not None:
        source=Path(source_directory).resolve()
        if target==source or source in target.parents:raise SortError('Output must be outside the unchanged source tree')
    encoded=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if len(encoded)>DEFAULT_LIMITS['output_bytes']:raise SortError('Serialized output exceeds byte budget')
    target.parent.mkdir(parents=True,exist_ok=True)
    fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sort=sub.add_parser('sort');sort.add_argument('sources');sort.add_argument('--mode',choices=('compare','not-compared','not compared'),default='not-compared')
    sort.add_argument('--output',required=True);sort.add_argument('--prior');sort.add_argument('--limits',help='JSON file of lowered resource bounds')
    for name in ('verify','peruse','export-retired'):
        p=sub.add_parser(name);p.add_argument('graph');p.add_argument('--sources',required=True)
        if name=='export-retired':p.add_argument('--ledger',required=True)
        if name=='peruse':p.add_argument('--max-items',type=int,default=12)
    start=time.perf_counter();cpu=time.process_time()
    args=parser.parse_args(argv)
    try:
        if args.command=='sort':
            prior=None
            if args.prior:
                with Path(args.prior).open('rb') as f:raw=f.read(DEFAULT_LIMITS['prior_bytes']+1)
                if len(raw)>DEFAULT_LIMITS['prior_bytes']:raise SortError('Prior graph exceeds history budget')
                prior=raw.decode('utf-8')
            result=sort_directory(args.sources,args.mode,_load(args.limits) if args.limits else None,prior)
            _save(args.output,result,args.sources)
            result={'status':'candidate_graph_written','graph_sha256':result['graph_sha256'],'nodes':len(result['nodes']),
                    'edges':len(result['edges']),'complete':result['complete'],'limits_or_exclusions':result['limits_or_exclusions'],
                    'assessment':assessment(),'source_bytes_read':result['source_bytes_read']}
        else:
            graph=_load(args.graph)
            result=export_retired(graph,args.sources,args.ledger) if args.command=='export-retired' else verify_graph(graph,args.sources)
            if args.command=='peruse':
                if not 1<=args.max_items<=64:raise SortError('Perusal limit must be1–64')
                result.update(mode=graph['mode'],items=graph['nodes'][:args.max_items],
                              displayed=len(graph['nodes'][:args.max_items]),omitted=len(graph['nodes'][args.max_items:]))
        result['wall_seconds']=time.perf_counter()-start;result['cpu_seconds']=time.process_time()-cpu
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (ValueError,OSError,KeyError,TypeError,RecursionError) as exc:
        print(json.dumps({'status':'refused','error':str(exc),'assessment':assessment()}),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
