"""Offline raw-text candidate sorter, rules v2. No source support or historical truth engine.

A separate, versioned engine. ``mplpb_work.sorter`` (v1) is unchanged so every
existing v1 graph, frozen study and implementation pin still replays.

Extraction, provisional assessment and comparison are separate pure stages.
Source text is decoded strictly as UTF-8 without newline/Unicode normalization.

Rule changes from v1 (each covered by tests/test_sorter_v2.py):
  R1  identifiers and reference targets never end in . : / - (sentence punctuation)
  R2  numbered designations ("Letter No. 41") are identifiers; a designation line
      in the leading header block is a primary declaration
  R3  a reference target must be an identifier, numbered designation, <message-id>
      or URL; other words are not invented targets
  R4  passive corrections ("SHIP-7 is superseded by this notice", "hereby
      corrected") are references with an explicit direction
  R5  scope is judged per clause for every feature (local_scope); statement
      scope keeps the v1 value for compatibility
  R6  negation must govern the correction cue; double negation is unresolved
  R7  reported speech ("the porter said ...") is its own qualified scope
  R8  descriptive references ("the earlier note") get review-only candidates
All proposals remain review annotations: answer_supported is always false.
"""
import argparse
from array import array
from bisect import bisect_right
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

VERSION = 'offline-candidate-sorter-v2'
V1_VERSION = 'offline-candidate-sorter-v1'
RULES = ('R1-terminal-punctuation','R2-numbered-designations','R3-recognized-targets','R4-passive-direction',
         'R5-clause-local-scope','R6-governing-negation','R7-reported-speech','R8-descriptive-reference-review')
PHRASE_WITNESSES = 8
EXTENSIONS = {'.txt', '.text', '.md', '.markdown'}
DEFAULT_LIMITS = {'files':64, 'file_bytes':1048576, 'total_bytes':8388608,
                  'tree_entries':4096, 'directory_depth':12, 'nodes':4096,
                  'edges':8192, 'statements':2000, 'statement_chars':8000,
                  'comparisons':20000, 'phrase_keys':4096, 'phrase_groups':32,
                  'prior_bytes':1048576, 'output_bytes':33554432}
HEADER = re.compile(r'^\ufeff?[ \t]*(?:>[ \t]*)*(?:#{1,6}[ \t]+)?(Message-ID|Document-ID|Record-ID|Event-ID|Occurrence-ID|Subject|From|To|Sender|Recipient|Date|Date written|Date sent|Date received|Published|Revised|Status)[ \t]*:[ \t]*(\S[^\r\n]{0,499})(?=\r?$)', re.I|re.M)
# R1: internal . : / - stay legal (1850.7, A:B/C) but never the final character.
ID_BODY = r'[A-Z][A-Z0-9]{1,23}-[A-Za-z0-9](?:[A-Za-z0-9_.:/-]{0,74}[A-Za-z0-9_])?'
IDENTIFIER = re.compile(r'(?<![\w-])'+ID_BODY+r'(?![\w-])')
# R2: a document-type word is required, so "No. 1 priority" is not an identifier.
DOC_TYPES = r'(?:letter|despatch|dispatch|memorandum|memo|report|order|telegram|note|circular|minute|notice|invoice|receipt)'
NUMBERED_BODY = r'(?i:'+DOC_TYPES+r')\s+(?i:no)\.?\s*\d{1,6}[A-Za-z]?\b'
NUMBERED = re.compile(r'\b(?P<type>(?i:'+DOC_TYPES+r'))\s+(?i:no)\.?\s*(?P<number>\d{1,6}[A-Za-z]?)\b')
NUMBERED_HEADER = re.compile(r'^﻿?[ \t]*(?P<type>(?i:'+DOC_TYPES+r'))\s+(?i:no)\.?\s*(?P<number>\d{1,6}[A-Za-z]?)[ \t]*(?=\r?$)', re.M)
MESSAGE_ID = re.compile(r'<[^<>\s]{1,200}>')
ID_ALT = r'(?:(?<![\w-])'+ID_BODY+r'(?![\w-])|\b'+NUMBERED_BODY+r')'
REFERENCE_WORDING = re.compile(r'\b(in reply to|reply to|response to|see|reference|ref\.?|corrects|correction to|amends|retracts|supersedes|revises|cancels|errata for|erratum to)[: \t]+', re.I)
CORRECTION_WORDING = re.compile(r'\b(?:correct(?:s|ed)?|correction|amend(?:s|ed|ment)?|retract(?:s|ed|ion)?|supersed(?:e|es|ed)|revis(?:e|es|ed|ion)|errat(?:um|a))\b', re.I)
# Error cues are correction evidence for descriptive references only (R8).
ERROR_CUE = re.compile(r'\b(?:in error|erroneous(?:ly)?|mistaken(?:ly)?|should (?:have )?read|wrong(?:ly)?)\b', re.I)
CORRECTION = re.compile(r'\b(?:corrects?|correction|amends?|amendment|retracts?|retraction|supersed(?:e|es|ed)|revis(?:e|es|ed|ion)|corrected|amended|retracted|errat(?:um|a))\b', re.I)
PASSIVE = re.compile(r'(?P<target>'+ID_ALT+r')\s+(?:(?i:is|was|are|were|has been|have been|stands|hereby)\s+){1,3}'
                     r'(?P<verb>(?i:corrected|amended|superseded|revised|retracted|cancell?ed|withdrawn))'
                     r'(?:\s+(?i:by)\s+(?P<agent>(?i:this|the present)\s+(?i:notice|letter|note|memo(?:randum)?|message|document|report|order|despatch|dispatch|telegram|circular)|'+ID_ALT+r'))?')
PASSIVE_CORRECTING = {'corrected','amended','superseded','revised','retracted'}
DEICTIC = re.compile(r'\b(?:the|my|our|your|his|her|their)\s+(?:earlier|previous|former|last|preceding|prior|above(?:-mentioned)?)\s+(?:[A-Za-z]+\s+){0,3}?'
                     r'(?:note|letter|message|report|memo(?:randum)?|despatch|dispatch|order|entry|notice|telegram|record|account)\b', re.I)
NEGATOR = re.compile(r"\b(?:not|never|no|nor|neither|cannot|can't|don't|doesn't|didn't|isn't|wasn't|aren't|weren't|no longer)\b", re.I)
NEGATIVE_PREDICATE = re.compile(r"\b(?:untrue|incorrect|inaccurate|invalid|improper|impossible|unfounded|without)\b", re.I)
REPORTED = re.compile(r'\b(?:said|says|stated|states|claimed|claims|told|tells|reportedly|alleged(?:ly)?|according to|rumou?r(?:ed|s)?|heard|supposedly)\b', re.I)
# "may" is lowercase-only so the month "May" is not a modal.
CONDITIONAL = re.compile(r'\b(?:(?i:if|unless|would|might|could|will|shall|hope[sd]?|planned|intended|proposed|draft)|may)\b')
ABBREVIATION = re.compile(r'\b(?:No|Nos|Ref|Mr|Mrs|Ms|Dr|St|Co|Ltd|viz|vol|pp|cf|etc|e\.g|i\.e)\.$', re.I)
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
    for match in re.finditer(r'(?m)^\ufeff?[ \t]*(?:>[ \t]*)*(`{3,}|~{3,})([^\r\n]*)',text):
        marker=match[1]
        if opened is None:opened=(match.start(),marker)
        elif marker[0]==opened[1][0] and len(marker)>=len(opened[1]) and not match[2].strip():
            ranges.append((opened[0],match.end()));opened=None
    if opened:ranges.append((opened[0],len(text)))
    return ranges


def _embedded_ranges(text,fences):
    """Bounded layout cues, not semantic document/event identity resolution.

    Coalesced, nonoverlapping character ranges distinguish embedded appearances
    before headers can partition occurrences. Unclosed frames remain uncertain.
    """
    ranges=[];fence_index=0;frame=None;forward_depth=0;example_heading=None;quotation=None
    for line in re.finditer(r'[^\n]*(?:\n|$)',text):
        if line.start()==line.end():continue
        layout=line[0].lstrip('\ufeff') if line.start()==0 else line[0]
        value=layout.strip();context=None
        while fence_index<len(fences) and fences[fence_index][1]<=line.start():fence_index+=1
        fenced=fence_index<len(fences) and fences[fence_index][0]<line.end() and fences[fence_index][1]>line.start()
        if fenced:
            context='fenced_block'
            # A following code block supplies an explicit end for an example
            # introduction; a containing example section/forward remains scoped.
            if line.end()>=fences[fence_index][1] and frame=='introduced_embedded_context':frame=None
        elif re.match(r'^\s*>',layout):context='blockquote_context'
        else:
            heading=re.match(r'^(#{1,6})\s+(.+?)\s*#*$',value)
            if heading and not forward_depth and quotation is None:
                level=len(heading[1])
                if example_heading is not None and level<=example_heading:
                    example_heading=None
                    if frame=='introduced_embedded_context':frame=None
                if re.match(r'^(?:(?:documentation|fictional|worked|code|quoted)\s+)?(?:example|sample|template)(?:\b|:)',heading[2],re.I):example_heading=level
            end=re.match(r'^[-= ]*end\s+(?:of\s+)?(forwarded message|original message|quoted message|quotation|quote|example|sample)[-= .:]*$',value,re.I)
            if quotation is not None:
                context='quotation_context'
                if value==quotation:quotation=None
            elif value in {'"','\u201c'} or re.search(r'\b(?:wrote|said)\s*[:,]?\s*["\u201c]$',value,re.I):
                quotation='\u201d' if value.endswith('\u201c') else '"';context='quotation_context'
            elif end:
                if end[1].lower() not in {'example','sample'}:forward_depth=max(0,forward_depth-1)
                frame='forwarded_or_quoted_context' if forward_depth else None
            elif re.match(r'^[-= ]*(?:(?:begin\s+)?forwarded message|original message|quoted message|quotation|quote)\s*[-= :]*$',value,re.I) or re.match(r'^On .{1,200}\bwrote:\s*$',value,re.I):
                forward_depth+=1;frame='forwarded_or_quoted_context'
            elif not forward_depth and (re.match(r'^(?:(?:the\s+)?following|below|here (?:is|are))\b.{0,180}\b(?:example|sample|illustration|quotation|quoted (?:message|text|letter))\b',value,re.I) or re.match(r'^(?:example|sample|illustration)\s*:',value,re.I)):frame='introduced_embedded_context'
            context=context or ('example_section' if example_heading is not None else frame)
        if context:
            if ranges and ranges[-1][1]==line.start() and ranges[-1][2]==context:
                ranges[-1]=(ranges[-1][0],line.end(),context)
            else:ranges.append((line.start(),line.end(),context))
    return ranges


def _header_context(position,ranges,starts):
    index=bisect_right(starts,position)-1
    return ranges[index][2] if index>=0 and position<ranges[index][1] else 'top_level_text'


def _scope(text):
    """Statement scope, byte-for-byte the v1 rule (kept for compatibility)."""
    if re.search(r'(?m)^\s*>|```|~~~|[\u201c\u201d"]',text):return 'quoted_or_format_scope_unresolved'
    if re.search(r'\b(?:if|unless|would|might|could|will|shall|hope|planned|intended)\b',text,re.I):return 'conditional_or_uncertain'
    if re.search(r'\b(?:not|never|no)\b.{0,50}\b(?:correct|correction|amend|supersed|revis|retract)',text,re.I):return 'negated_correction_mention'
    return 'unqualified_text'


class _Header:
    """Uniform view over HEADER matches and numbered designation lines (R2)."""
    __slots__=('name','raw','value','_s','_e','_vs','_ve','numbered')
    def __init__(self,name,raw,value,s,e,vs,ve,numbered=False):
        self.name,self.raw,self.value,self._s,self._e,self._vs,self._ve,self.numbered=name,raw,value,s,e,vs,ve,numbered
    def __getitem__(self,i):return {1:self.name,2:self.raw}[i]
    def start(self,group=0):return self._s if group==0 else self._vs
    def end(self,group=0):return self._e if group==0 else self._ve


def numbered_key(kind,number):
    return kind.upper()+'-NO-'+number.upper()


def _headers(text):
    found=[_Header(m[1],m[2],m[2].rstrip(),m.start(),m.end(),m.start(2),m.end(2)) for m in HEADER.finditer(text)]
    # A designation line counts only inside the file's leading header block.
    block_end=len(text)
    blank=re.search(r'(?:\r?\n)[ \t]*(?:\r?\n)',text)
    if blank:block_end=blank.start()
    for m in NUMBERED_HEADER.finditer(text,0,block_end):
        found.append(_Header('Numbered-Record-ID',m[0].strip(),numbered_key(m['type'],m['number']),
                             m.start(),m.end(),m.start('type'),m.end('number'),True))
    return sorted(found,key=lambda h:h.start())


def _is_header_line(line):
    return bool(HEADER.match(line) or NUMBERED_HEADER.match(line))


def _clause(text,lo,hi):
    """Clause containing [lo,hi): bounded by ; : ! ? newline or a sentence stop.

    A period ends a clause unless it closes a known abbreviation or sits inside
    a token (1850.7). Bounds are character offsets into ``text``.
    """
    def is_stop(i):
        ch=text[i]
        if ch in ';!?\n':return True
        if ch==':':return not (i+1<len(text) and not text[i+1].isspace())
        if ch!='.':return False
        if i+1<len(text) and not text[i+1].isspace():return False
        return not ABBREVIATION.search(text[max(0,i-6):i+1])
    start=lo
    while start>0 and not is_stop(start-1):start-=1
    end=hi
    while end<len(text) and not is_stop(end):end+=1
    return start,end


def _quote_spans(text):
    spans=[]
    for m in re.finditer(r'"[^"\n]{0,2000}"|\u201c[^\u201d]{0,2000}\u201d',text):spans.append((m.start(),m.end()))
    for m in re.finditer(r'(?m)^[ \t]*>.*$',text):spans.append((m.start(),m.end()))
    return spans


def _local_scope(text,lo,hi,negation=False):
    """R5\u2013R7: qualification of one feature, judged within its own clause.

    ``text`` is the statement; ``lo``/``hi`` are feature offsets in it.
    Order is most-restrictive first so a quoted conditional stays quoted.
    """
    if re.search(r'```|~~~',text):return 'quoted_or_format_scope_unresolved'
    if any(a<=lo and hi<=b for a,b in _quote_spans(text)):return 'quoted_or_format_scope_unresolved'
    a,b=_clause(text,lo,hi);clause=text[a:b];before=text[a:lo]
    if REPORTED.search(clause):return 'reported_speech_scope'
    conditional=CONDITIONAL.search(re.sub(r'\bshould (?:have )?read\b','',clause,flags=re.I))
    if conditional:return 'conditional_or_uncertain'
    if negation:
        window=' '.join(re.findall(r"[\w']+",before)[-5:])
        after=' '.join(re.findall(r"[\w']+",text[hi:b])[:2])
        negators=NEGATOR.findall(window)
        if len(negators)>1 or (negators and NEGATIVE_PREDICATE.search(window)):return 'negation_scope_unresolved'
        if negators:return 'negated_correction_mention'
        if re.match(r'(?i)(?:nothing|none|no one)\b',after):return 'negated_correction_mention'
        if NEGATIVE_PREDICATE.search(window) and re.search(r'(?i)\b(?:is|was)\b',window):return 'negation_scope_unresolved'
    return 'unqualified_text'


def _canonical(value):
    m=NUMBERED.fullmatch(value.strip())
    return numbered_key(m['type'],m['number']) if m else value.strip()


def _reference_target(text,pos,limit):
    """R3: only explicit identifier-like targets; never an ordinary word."""
    m=MESSAGE_ID.match(text,pos,limit)
    if m:return m[0],m[0],'message_id'
    m=NUMBERED.match(text,pos,limit)
    if m:return numbered_key(m['type'],m['number']),m[0],'numbered_designation'
    m=IDENTIFIER.match(text,pos,limit)
    if m:return m[0],m[0],'identifier'
    m=URL.match(text,pos,limit)
    if m:return m[0].rstrip('.,;:)'),m[0].rstrip('.,;:)'),'url'
    return None,None,None


def retain_phrase_witness(appearances, witness):
    if len(appearances) < PHRASE_WITNESSES:
        appearances.append(witness)
        return
    occurrence = witness[-1]
    owners = [item[-1] for item in appearances]
    if occurrence in owners:
        return
    # A distinct occurrence can displace only a redundant occurrence.
    # Retain ordering among surviving spans and keep the cap unchanged.
    for index in range(len(owners) - 1, -1, -1):
        if owners.count(owners[index]) > 1:
            del appearances[index]
            appearances.append(witness)
            return


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
        offsets=_byte_offsets(text);headers=_headers(text);fences=_fence_ranges(text)
        embedded=_embedded_ranges(text,fences);embedded_starts=[r[0] for r in embedded];embedded_ends=[r[1] for r in embedded]
        header_contexts={m.start():_header_context(m.start(),embedded,embedded_starts) for m in headers}
        primary_headers=[m for m in headers if header_contexts[m.start()]=='top_level_text']
        # Explicit identifier layout may delimit several occurrences in a file.
        # A header/date/title is never proof of the underlying event identity.
        marker=None
        for name in ('message-id','document-id','record-id','numbered-record-id'):
            matches=[m for m in primary_headers if m[1].lower()==name]
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
            occurrence['identity_role']=('declared_record_candidate' if any(m[1].lower().endswith('-id') and header_contexts[m.start()]=='top_level_text' for m in local_headers) else 'textual_appearance_only')
            body_start=begin
            for line in text[begin:end].splitlines(keepends=True):
                if not line.strip():body_start+=len(line);break
                if _is_header_line(line) and header_contexts.get(body_start)=='top_level_text':body_start+=len(line)
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
                embedded_index=bisect_right(embedded_ends,a)
                embedded_unit=embedded_index<len(embedded) and embedded[embedded_index][0]<b
                unit_scope='quoted_or_format_scope_unresolved' if embedded_unit else _scope(text[a:b])
                statement=add('statement',source,text,offsets,a,b,occurrence=occurrence['id'],scope=unit_scope)
                if not statement:break
                edge(occurrence,statement,'contains_statement',[statement['id']])
                scope=statement['scope'];items=[];unit=text[a:b]
                def feature(kind,lo,hi,negation=False,local=None,**fields):
                    # Forwarded/example frames qualify every feature inside them.
                    if local is None:
                        local=('quoted_or_format_scope_unresolved' if embedded_unit
                               else _local_scope(unit,lo-a,hi-a,negation))
                    item=add(kind,source,text,offsets,lo,hi,statement=statement['id'],occurrence=occurrence['id'],scope=scope,local_scope=local,**fields)
                    if item:
                        items.append(item);edge(statement,item,'contains_extracted_item',[statement['id'],item['id']])
                    return item
                for m in local_headers:
                    if not a<=m.start()<b:continue
                    name=m[1].lower();value=m.value;lo=m.start(2);hi=m.end(2) if m.numbered else lo+len(value)
                    kind='header_identifier' if name.endswith('-id') else 'declared_status' if name=='status' else 'header'
                    context=header_contexts[m.start()];primary=context=='top_level_text'
                    extra={'designation_text':m.raw} if m.numbered else {}
                    item=feature(kind,lo,hi,value=value,header_name=name,header_context=context,
                                 header_role='record_declaration_candidate' if primary else 'embedded_text_observation',
                                 primary_identity_eligible=primary and kind=='header_identifier',
                                 local='unqualified_text' if primary else 'quoted_or_format_scope_unresolved',**extra)
                    if name=='status' and item and primary:
                        occurrence['declared_status_candidates'].append({'value':value,'evidence_node':item['id']})
                for m in IDENTIFIER.finditer(text,a,b):feature('identifier',m.start(),m.end(),value=m[0])
                for m in NUMBERED.finditer(text,a,b):
                    feature('identifier',m.start(),m.end(),value=numbered_key(m['type'],m['number']),
                            designation_text=m[0],identifier_form='numbered_designation')
                for m in URL.finditer(text,a,b):feature('literal_url',m.start(),m.end(),value=m[0],fetched=False)
                for m in date_cues(text[a:b]):
                    lo=a+m.start();hi=a+m.end();role='unresolved'
                    for h in local_headers:
                        if h.start(2)<=lo<hi<=h.end(2) and header_contexts[h.start()]=='top_level_text':role=DATE_ROLES.get(h[1].lower(),'unresolved')
                    feature('date_expression',lo,hi,value=m[0],date_role=role,normalized_event_time=None)
                recognized=False
                for m in REFERENCE_WORDING.finditer(text,a,b):
                    wording=m[1].lower();key,target_text,form=_reference_target(text,m.end(),b)
                    correction=bool(CORRECTION_WORDING.search(wording))
                    # R3: "see you soon" names no target; only a correction cue is kept.
                    if key is None and not correction:continue
                    recognized=recognized or key is not None
                    feature('reference_mention',m.start(),m.end()+len(target_text) if target_text else m.end(1),
                            negation=correction,value=key,reference_wording=wording,target_form=form or 'unrecognized',
                            correction_wording=correction,reference_direction='self_to_target')
                for m in PASSIVE.finditer(text,a,b):  # R4
                    key=_canonical(m['target']);verb=m['verb'].lower();agent=m['agent']
                    if re.search(r'(?i)\bhereby\b',m[0]) or (agent and re.match(r'(?i)this|the present',agent)):
                        direction,agent_key='self_to_target',None
                    elif agent:direction,agent_key='third_party',_canonical(agent)
                    else:direction,agent_key='agent_unstated',None
                    recognized=True
                    feature('reference_mention',m.start(),m.end(),negation=True,value=key,reference_wording='passive:'+verb,
                            target_form='numbered_designation' if NUMBERED.fullmatch(m['target']) else 'identifier',
                            correction_wording=verb in PASSIVE_CORRECTING,reference_direction=direction,agent_key=agent_key)
                for m in CORRECTION.finditer(text,a,b):feature('correction_mention',m.start(),m.end(),negation=True,value=m[0])
                for m in ERROR_CUE.finditer(text,a,b):
                    feature('correction_mention',m.start(),m.end(),negation=True,value=m[0],cue_kind='error_statement')
                if not recognized and (CORRECTION.search(unit) or ERROR_CUE.search(unit)):  # R8
                    for m in DEICTIC.finditer(text,a,b):
                        feature('descriptive_reference',m.start(),m.end(),negation=True,value=m[0],target_established=False)
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
                    retain_phrase_witness(
                        phrases[key], (source,text,offsets,lo,hi,statement['id'],occurrence['id']))
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
    by_id={n['id']:n for n in nodes};identifiers=defaultdict(list);observed_identifiers=defaultdict(list);subjects=defaultdict(list);phrases=defaultdict(list);checks=0
    for node in nodes:
        if node['kind']=='header_identifier':
            observed_identifiers[node['value']].append(node)
            if node.get('primary_identity_eligible') is True:identifiers[node['value']].append(node)
        elif node['kind']=='header' and node['header_name']=='subject':subjects[node['value']].append(node)
        elif node['kind']=='phrase_key':phrases[node['value']].append(node)
    edge_ids={e['id'] for e in edges}
    def charge():
        nonlocal checks
        checks+=1
        if checks>limits['comparisons']:issues.add('comparison_budget');return False
        return True
    def propose(left,right,kind,evidence,note,**extra):
        if not charge():return
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
                    'Shared primary declaration candidates only. Occurrences remain separate; repeated appearances do not establish independent events.',
                    cluster_id='cluster:'+digest([namespace,key,occurrences])[7:],members=occurrences,
                    identity_namespace=namespace,key=key,changed_bodies=len(bodies)>1,
                    historical_identity_established=False)
    for items in observed_identifiers.values():
        for node in items:
            if node.get('primary_identity_eligible') is True:continue
            propose(node['id'],node['occurrence'],'embedded_identifier_review',[node['id'],node['statement']],
                    'Identifier appears in embedded text, not as a primary record declaration. Matches are lexical review notes, not identity links.',
                    header_context=node.get('header_context'),
                    matching_primary_occurrences=sorted({n['occurrence'] for n in identifiers.get(node['value'],[])}),
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
        correction=bool(node.get('correction_wording'))
        local=node.get('local_scope','unqualified_text');direction=node.get('reference_direction','self_to_target')
        statement=by_id[node['statement']];quote=statement['span']['text'];window={}
        if correction:
            for date in nodes:
                if date.get('statement')!=node['statement'] or date['kind']!='date_expression':continue
                start=date['span']['char_start']-statement['span']['char_start'];prefix=quote[max(0,start-35):start]
                if re.search(r'\beffective\s+(?:from\s+)?$',prefix,re.I):window['from_expression']=date['span']['text']
                if re.search(r'\b(?:until|through)\s*$',prefix,re.I):window['until_expression']=date['span']['text']
        proposal={'correction_window':{'expressions':window,'date_role':'proposed_effective_window_only','applied':False} if correction else None,
                  'claim_scope_quote':quote if correction else None}
        targets={x['occurrence'] for x in identifiers.get(node['value'],[])} if node['value'] else set()
        reason=('unrecognized_target_form' if node['value'] is None
                else ('embedded_only_target' if observed_identifiers.get(node['value']) else 'missing_or_outside_budget') if not targets
                else 'ambiguous_identifier' if len(targets)>1
                else 'self_reference_or_local_identifier' if next(iter(targets))==node['occurrence']
                else 'third_party_relation_reported' if direction=='third_party'
                else 'passive_agent_unstated' if direction=='agent_unstated'
                else 'qualified_or_quoted_reference' if local!='unqualified_text' else None)
        if reason:
            propose(node['id'],node['occurrence'],'unresolved_reference_review',[node['id'],statement['id']],
                    'No documentary hop is resolved; missing, ambiguous or qualified evidence stops the relation.',
                    reason=reason,candidate_count=len(targets),target_key=node['value'],local_scope=local,
                    reference_direction=direction,agent_key=node.get('agent_key'),**proposal)
            continue
        target=next(iter(targets));evidence=[node['id']]+[x['id'] for x in identifiers[node['value']] if x['occurrence']==target]
        partial=correction and bool(re.search(r'\b(?:only|unchanged|remains|in part)\b',quote,re.I))
        propose(node['occurrence'],target,'possible_partial_correction' if partial else 'possible_correction' if correction else 'explicit_reference_candidate',
                evidence+[statement['id']], 'Source wording only; no operational supersession, event identity or completed action is established.',
                reference_wording=node['reference_wording'],**proposal)
    _descriptive_reviews(nodes,by_id,propose,charge)
    return extracted


STOPWORDS = frozenset('''that this with from have were been which their there about would should could these those
other into than then them they what when where while also only some such more most very will your ours note letter
message report earlier previous former last preceding prior above mentioned wrong error read count correction'''.split())


def _content_terms(text):
    return {w.casefold() for w in re.findall(r'[^\W\d_]{4,}',text)}-STOPWORDS


def _shingles(text):
    words=[w.casefold() for w in re.findall(r'\b[^\W_]+\b',text)]
    return {' '.join(words[i:i+4]) for i in range(len(words)-3)}


def _descriptive_reviews(nodes,by_id,propose,charge):
    """R8: list possible targets of "the earlier note"; never pick one.

    Loose word overlap produced false links in the PR #52 workspace (v1 used a
    three-word rule). A candidate therefore needs a shared four-word phrase, or
    at least three shared content words of which one is rare (used by at most
    two occurrences). Candidates stay review-only; none is selected.
    """
    descriptive=[n for n in nodes if n['kind']=='descriptive_reference']
    if not descriptive:return
    terms=defaultdict(set);shingles=defaultdict(set)
    for n in nodes:
        if n['kind']=='statement':
            terms[n['occurrence']]|=_content_terms(n['span']['text'])
            shingles[n['occurrence']]|=_shingles(n['span']['text'])
    spread=defaultdict(int)
    for words in terms.values():
        for w in words:spread[w]+=1
    occurrences=[n for n in nodes if n['kind']=='source_occurrence']
    for node in descriptive:
        statement=by_id[node['statement']];wanted=_content_terms(statement['span']['text'])
        phrases=_shingles(statement['span']['text'])
        found=[]
        for occ in occurrences:
            if occ['id']==node['occurrence']:continue
            if not charge():return
            shared=sorted(wanted&terms[occ['id']]);shared_phrases=sorted(phrases&shingles[occ['id']])
            rare=[w for w in shared if spread[w]<=2]
            if shared_phrases or (len(shared)>=3 and rare):
                found.append((-(len(shared)+4*len(shared_phrases)),occ['span']['path'],occ['id'],shared+shared_phrases))
        found.sort()
        local=node.get('local_scope','unqualified_text')
        propose(node['id'],node['occurrence'],'descriptive_reference_review',[node['id'],statement['id']],
                'Descriptive wording names no record. Candidates share content words only; none is selected.',
                reason='descriptive_reference_only' if local=='unqualified_text' else 'qualified_descriptive_reference',
                local_scope=local,phrase=node['value'],target_established=False,
                candidates=[{'occurrence':o,'path':p,'shared_terms':s} for _,p,o,s in found[:5]],
                candidate_count=len(found))


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
        # A v1 graph is accepted as an untrusted historical snapshot for migration.
        if previous.get('schema') not in (VERSION,V1_VERSION) or previous.get('graph_sha256')!=digest({k:v for k,v in previous.items() if k!='graph_sha256'}):
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
    graph={'schema':VERSION,'rules':list(RULES),'implementation_sha256':sha(Path(__file__).read_bytes()),'mode':mode,'comparison_performed':mode=='compare',
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
