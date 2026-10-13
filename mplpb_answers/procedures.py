"""Explicit source-authored procedure constraints; context is a selector, never proof."""
import json
import re
from mplpb_combined.record import text_of
from mplpb_combined.ledger import Ledger
from mplpb_combined.provenance_gate import gather

VERSION = 'procedure-constraints-v1'
MARKER = 'MPLPB-PROCEDURE/1 '


def request(question):
    q = question.strip().rstrip('?.!')
    m = re.fullmatch(r'(?:show )?procedure ([A-Za-z0-9_-]{1,80})', q, re.I)
    if m: return {'procedure': m[1].casefold(), 'step': None}
    m = re.fullmatch(r'(?:show )?step ([1-9][0-9]{0,2}) of procedure ([A-Za-z0-9_-]{1,80})', q, re.I)
    if m: return {'procedure': m[2].casefold(), 'step': int(m[1])}
    return None


def _pairs(items):
    result = {}
    for k, v in items:
        if k in result: raise ValueError('Duplicate field: '+k)
        result[k] = v
    return result


def _text(value):
    return isinstance(value, str) and 0 < len(value) <= 2000 and not any(ord(c)<32 for c in value)


def validate(doc):
    if not isinstance(doc, dict) or set(doc) != {'id', 'steps'}:
        return ['Procedure needs exactly id and steps.']
    if not isinstance(doc['id'], str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', doc['id']):
        return ['Invalid procedure id.']
    steps = doc['steps']
    if not isinstance(steps, list) or not 1 <= len(steps) <= 100:
        return ['Procedure needs 1–100 explicitly ordered steps.']
    for n, step in enumerate(steps, 1):
        if not isinstance(step, dict) or set(step) != {'order','action','prerequisites','conditions','warnings'}:
            return [f'Step {n} needs order, action, prerequisites, conditions and warnings.']
        if type(step['order']) is not int or step['order'] != n:
            return [f'Missing, repeated or out-of-order step {n}.']
        if not _text(step['action']): return [f'Step {n} has no supported action text.']
        p = step['prerequisites']
        if not isinstance(p, list) or any(type(i) is not int or not 1 <= i < n for i in p) or len(set(p)) != len(p):
            return [f'Step {n} has missing, cyclic or invalid prerequisites.']
        # This first schema only licenses a linear sequence. Branches abstain.
        if n > 1 and n-1 not in p:
            return [f'Step {n} must explicitly require preceding step {n-1}.']
        for field in ('conditions','warnings'):
            if not isinstance(step[field], list) or any(not _text(s) for s in step[field]):
                return [f'Step {n} needs an explicit {field} list.']
    return []


def check(root, query, profile=None):
    """Re-read eligible bytes on every call, retaining all matching sources."""
    matches, errors = [], []
    gate = gather(root, 'MPLPB PROCEDURE '+query['procedure'], profile)
    records = {r.path:r for r in Ledger(root).servable()}
    for source in gate.sources:
        rec = records[source['path']]
        body=text_of(rec.body_html)
        blocks=[(line.strip(),'json') for line in body.splitlines() if line.strip().startswith(MARKER)]
        lines=body.splitlines()
        starts=[i for i,line in enumerate(lines) if re.fullmatch(r'Procedure: [A-Za-z0-9_-]{1,80}',line.strip())]
        for position,start in enumerate(starts):
            end=starts[position+1] if position+1<len(starts) else len(lines)
            block='\n'.join(lines[start:end]).strip()
            if lines[start].strip()[11:].casefold()!=query['procedure']: continue
            content='\n'.join(lines[start+1:end])
            recognized=all(not line.strip() or re.fullmatch(r'\s*(?:[1-9][0-9]{0,2}[.)] .+|(?:Prerequisites|Conditions|Warnings): .+)',line) for line in lines[start+1:end])
            draft=automatic_tags(content,{'id':rec.id,'path':rec.path,'hash':rec.hash})
            if not recognized:
                errors.append('Unrecognized procedure construction in '+rec.id); continue
            doc={'id':query['procedure'],'steps':[{k:step[k] for k in ('order','action','prerequisites','conditions','warnings')} for step in draft['steps']]}
            blocks.append((block,doc))
        for raw, format_spec in blocks:
            if len(raw)>256000:
                errors.append('Procedure block exceeds the bounded parser limit in '+rec.id); continue
            try:
                doc = json.loads(raw[len(MARKER):], object_pairs_hook=_pairs) if format_spec=='json' else format_spec
            except (ValueError, TypeError, RecursionError):
                errors.append('Malformed procedure block in '+rec.id); continue
            if not isinstance(doc, dict) or str(doc.get('id','')).casefold() != query['procedure']: continue
            gaps = validate(doc)
            if gaps: errors.extend(rec.id+': '+g for g in gaps); continue
            pin = {'id':rec.id,'path':rec.path,'hash':rec.hash,'quote':raw,
                   'format':'json' if format_spec=='json' else 'explicit-numbered-lines'}
            tags = [dict(s, source=dict(pin, pointer='/steps/'+str(i))) for i,s in enumerate(doc['steps'])]
            matches.append((rec, tags))
    result = {'version':VERSION,'status':'unsupported','procedure':query['procedure'],
              'requested_step':query['step'],'steps':[],'gaps':errors,
              'context_is_evidence':False,'execution_verified':False}
    if len(matches)>1:
        result.update(status='conflict',gaps=['Multiple eligible definitions; no procedure chosen.'])
    elif errors: pass
    elif not matches: result['gaps']=['No eligible source-authored procedure tags for this identifier.']
    else:
        rec, tags = matches[0]
        if query['step'] is not None and query['step'] > len(tags):
            result['gaps']=['Required step '+str(query['step'])+' is missing. No continuation invented.']
        else:
            result.update(status='supported',steps=tags,source={'id':rec.id,'path':rec.path,'hash':rec.hash})
            return result, rec
    return result, None


def render(result):
    if result['status'] != 'supported': return 'No supported procedure. '+ ' '.join(result['gaps'])
    rows = ['Source-declared procedure '+result['procedure']+'. This describes instructions; completion and real-world conditions are not verified.']
    for step in result['steps']:
        if result['requested_step'] is not None and step['order'] != result['requested_step']: continue
        rows += [f"Step {step['order']}: {step['action']}",
                 'Prerequisite steps: '+(', '.join(map(str,step['prerequisites'])) or 'none declared'),
                 'Conditions: '+('; '.join(step['conditions']) or 'none declared'),
                 'Warnings: '+('; '.join(step['warnings']) or 'none declared'),
                 'Source: '+step['source']['id']+' '+step['source']['hash']+' '+step['source']['pointer']]
    return '\n'.join(rows)


def automatic_tags(text, source):
    """Draft tags only: literal numbered lines; unknown constraints stay unknown.

    This does not write a source or mark it supported. Promotion requires review,
    complete explicit fields and a normal sealed ledger revision.
    """
    steps=[]
    for line_number,line in enumerate(text.splitlines(),1):
        m=re.fullmatch(r'\s*([1-9][0-9]{0,2})[.)] (.+)',line)
        if m:
            steps.append({'order':int(m[1]),'action':m[2], 'prerequisites':None,
                          'conditions':None,'warnings':None,
                          'source':dict(source,line=line_number,quote=line),
                          'status':'draft_unvalidated','field_sources':{}})
        elif steps:
            field=re.fullmatch(r'\s*(Prerequisites|Conditions|Warnings): (.+)',line,re.I)
            if field:
                name=field[1].casefold(); value=field[2].strip(); step=steps[-1]
                # Repeated declarations are ambiguous; retain the gap rather than overwrite.
                if name in step['field_sources']:
                    step[name]=None
                    step['field_sources'][name].append(dict(source,line=line_number,quote=line))
                    continue
                step['field_sources'][name]=[dict(source,line=line_number,quote=line)]
                if value.casefold()=='none': step[name]=[]
                elif name=='prerequisites':
                    if re.fullmatch(r'[1-9][0-9]*(?:, *[1-9][0-9]*)*',value):
                        step[name]=[int(x.strip()) for x in value.split(',')]
                else: step[name]=[value]
    gaps=[f"Step {step['order']}: {name} needs explicit, unambiguous source evidence." for step in steps for name in ('prerequisites','conditions','warnings') if step[name] is None]
    if not steps: gaps=['No explicit numbered step lines found.']
    return {'version':VERSION,'status':'draft_unvalidated','steps':steps,
            'gaps':gaps,
            'eligible_for_generation':False,'context_is_evidence':False}
