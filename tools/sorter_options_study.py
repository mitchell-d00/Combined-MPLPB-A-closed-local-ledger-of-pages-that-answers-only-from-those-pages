"""Frozen three-arm review-option study; strict reader files remain unchanged."""
import argparse
from bisect import bisect_left, bisect_right
from contextlib import contextmanager
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from unittest.mock import patch

from tools.sorter_first_study import ROOT, FAMILIES, prepare as base_prepare, locate
from tools.unprepared_challenge import read, save, sha, code_pins, frozen

ARMS = ['sorter-alone', 'synonyms', 'synonyms-relater']


class Locator:
    def __init__(self, bindings, texts):
        self.bindings=bindings;self.texts=texts;self.cache={}

    def span(self,index,span):
        from tools.source_roundtrip import projection_offsets
        from mplpb_answers.body_text import body_text
        from mplpb_work.sorter import _byte_offsets
        binding=self.bindings.get(span['path'])
        if not binding:return None
        record=next((r for r in index.records if r.id==binding['id'] and r.hash_actual==binding['hash']),None)
        if record is None:return None
        key=(span['path'],record.hash_actual)
        if key not in self.cache:
            text=self.texts[span['path']];body=body_text(record.body_html)
            canonical,starts,ends=projection_offsets(text,False)
            if canonical!=body or sha(body.encode())!=binding['projection_sha256']:return None
            valid=[(s,e,i) for i,(s,e) in enumerate(zip(starts,ends)) if s>=0]
            self.cache[key]=(body,[x[0] for x in valid],[x[1] for x in valid],[x[2] for x in valid],_byte_offsets(text),sha(text.encode()))
        body,starts,ends,indices,bytes_at,text_hash=self.cache[key];text=self.texts[span['path']]
        a,b=span['char_start'],span['char_end']
        if (type(a) is not int or type(b) is not int or not 0<=a<b<=len(text)
            or span['source_sha256']!='sha256:'+text_hash or text[a:b]!=span.get('text')
            or bytes_at[a]!=span['byte_start'] or bytes_at[b]!=span['byte_end']):return None
        lo,hi=bisect_right(ends,a),bisect_left(starts,b)
        if lo>=hi:return None
        a,b=indices[lo],indices[hi-1]+1
        import html
        if body[a:b]!=body_text('<pre>'+html.escape(span['text'])+'</pre>'):return None
        return record.id,a,b


def merge(index,base,hints,max_passages,max_chars):
    """Common guard: retain native source-discovery anchors before review hints."""
    if index.exact_status:return base
    selected=[];seen=set();used=0
    def add(p):
        nonlocal used
        key=(p['path'],p['body_start'],p['text'])
        if key in seen or len(selected)>=max_passages or used+len(p['text'])>max_chars:return
        selected.append(p);seen.add(key);used+=len(p['text'])
    for p in base['passages']:
        if p.get('retrieval_reason') in {'source-facet','declared-transcript-section-discovery-only'}:add(p)
    for i in range(max(len(hints),len(base['passages']))):
        for items in [hints,base['passages']]:
            if i<len(items):add(items[i])
    if not index.unchanged():
        from mplpb_answers.evidence_contract import ReaderError
        raise ReaderError('source_changed','Original changed while locating review hints')
    paths={p['path'] for p in selected}
    return dict(base,passages=selected,sources=[s for s in index.sources if s['path'] in paths],
                ranking='experimental-sorter-options-preserved-source-facets-v1',search_complete=False)


@contextmanager
def adapter(graph,bindings,texts,bundle,arm,traces):
    import mplpb_answers.prose_retrieval as retrieval
    original=retrieval.retrieve;locator=Locator(bindings,texts)
    by_node={n['id']:n for n in graph['nodes']}
    def wrapped(index,max_passages=12,max_chars=12000,seed=None):
        base=original(index,max_passages,max_chars,seed=seed)
        if index.exact_status:
            traces.append({'exact_route_preserved':True,'selected_hints':[]});return base
        hints=[];invalid=[]
        if arm=='sorter-alone':
            enriched={k:dict(v,sorter_text=texts[k]) for k,v in bindings.items()}
            pack,_=locate(index,graph,enriched,base,max_passages,max_chars)
            hints=[p for p in pack['passages'] if 'sorter_node_id' in p]
        else:
            ranked=[]
            def propose(node_id,span,score,basis):
                mapped=locator.span(index,span)
                if mapped is None:invalid.append(node_id);return
                source_id,a,b=mapped
                for p in index.passages:
                    if p['source_id']==source_id and p['body_start']<b and p['body_start']+len(p['text'])>a:
                        ranked.append(dict(p,retrieval_score=score,sorter_node_id=node_id,sorter_basis=basis))
            for hit in bundle['ranked_hits']:propose(hit['node_id'],hit['span'],hit['rank_score'],'lexical_ranker_original_location')
            if arm=='synonyms-relater':
                scores={h['occurrence_id']:h['rank_score'] for h in reversed(bundle['ranked_hits'])}
                # Only one hop from an existing query hit; no transitive traversal.
                for link in bundle['candidate_links']:
                    for left,right in [('left','right'),('right','left')]:
                        a,b=link[left],link[right]
                        if a['occurrence_id'] in scores:
                            propose(b['node_id'],b['context_span'] or b['span'],scores[a['occurrence_id']]*0.75,
                                    'candidate_link_one_hop:'+link['id'])
            ranked.sort(key=lambda p:(-p['retrieval_score'],p['path'],p['body_start']))
            seen=set()
            for p in ranked:
                key=(p['path'],p['body_start'])
                if key not in seen:hints.append(p);seen.add(key)
        pack=merge(index,base,hints,max_passages,max_chars)
        traces.append({'selected_hints':[p for p in pack['passages'] if 'sorter_node_id' in p],
            'invalid_hint_nodes':invalid,'passage_count':len(pack['passages']),
            'characters':sum(len(p['text']) for p in pack['passages']),
            'max_passages':max_passages,'max_characters':max_chars,
            'native_source_facets_preserved_first':True,'answer_supported':False})
        return pack
    with patch.object(retrieval,'retrieve',wrapped):yield


def prepare(output):
    output=Path(output);base_prepare(output)
    save(output/'options-protocol.json',{'schema':'sorter-options-study-v1','arms':ARMS,
        'strict_reader_revision':'6350988a2f64d8e5fa53bd187d368f4397bf4f4c',
        'strict_reader_files_sha256':{k:v for k,v in code_pins(ROOT).items() if k.startswith(('mplpb_answers/','mplpb_combined/'))},
        'runtime_sha256':code_pins(ROOT),'adapter_sha256':sha(Path(__file__).read_bytes()),
        'base_adapter_sha256':sha((ROOT/'tools/sorter_first_study.py').read_bytes()),
        'base_freeze_sha256':sha((output/'freeze.json').read_bytes()),
        'common_guard':'Reserve existing source-facet/transcript discovery passages, then interleave optional hints and native ranking. Exact routes unchanged.',
        'options':'Default inspectable vocabulary; no custom glossary or new answer keys. Ranker uses exact and neighbor signals. Relater adds at most one source-anchored candidate hop.',
        'comparison':'All22 original questions/originals and reader/worker/display budgets unchanged. Configured earlier unreserved retest remains separately frozen.',
        'independent_evaluation':'NOT RUN;22 questions are development only; unseen originals reserved.'})


def worker(arm):
    from tools.unprepared_challenge import worker as native_worker
    from mplpb_work.sorter_suggestions import suggestions
    graph=read('/study/compare.json');bindings=read('/study/bindings.json')
    texts={name:(Path('/study/sorter-inputs')/name).read_bytes().decode('utf-8') for name in bindings}
    case=read('/study/question.json');traces=[]
    bundle=None
    if arm!='sorter-alone':
        started=time.perf_counter();cpu=time.process_time()
        bundle=suggestions(graph,'/study/sorter-inputs',case['question'],synonym_ranker=True,candidate_relater=arm=='synonyms-relater')
        stored={k:v for k,v in bundle.items() if k!='sorter_graph'}
        stored.update(base_graph_sha256=graph['graph_sha256'],preprocessing_wall_seconds=time.perf_counter()-started,
                      preprocessing_cpu_seconds=time.process_time()-cpu)
        save('/output/review.json',stored)
    with adapter(graph,bindings,texts,bundle,arm,traces):
        native_worker('/app','/study/ledger','/study/question.json','/output/result.json','updated')
    save('/output/trace.json',{'arm':arm,'calls':traces,'source_authority_changed':False})


def run(output,arm):
    from tools.sorter_first_study import validate
    from tools.unprepared_sources import import_corpus
    from tools.study_sandbox import command,_limits
    output=Path(output).resolve();validate(output);protocol=read(output/'options-protocol.json')
    if protocol['runtime_sha256']!=code_pins(ROOT) or protocol['adapter_sha256']!=sha(Path(__file__).read_bytes()):raise ValueError('Frozen runtime changed')
    rows=[]
    with tempfile.TemporaryDirectory(prefix='mplpb-options-study-') as temp:
        temp=Path(temp);code=temp/'code';code.mkdir();(code/'tools').mkdir()
        for package in ['mplpb_answers','mplpb_combined','mplpb_work']:
            shutil.copytree(ROOT/package,code/package,ignore=shutil.ignore_patterns('__pycache__'))
        for filename in ['sorter_options_study.py','sorter_first_study.py','unprepared_challenge.py','source_roundtrip.py','unprepared_sources.py']:
            shutil.copyfile(ROOT/'tools'/filename,code/'tools'/filename)
        for family,(path,_) in FAMILIES.items():
            inputs=temp/family;inputs.mkdir();receipt=import_corpus(ROOT/path,inputs/'ledger')
            if receipt!=read(output/family/'import-receipt.json'):raise ValueError('Import changed')
            (inputs/'ledger/import-receipt.json').unlink();shutil.copytree(output/family/'sorter-inputs',inputs/'sorter-inputs')
            for name in ['compare.json','bindings.json']:shutil.copyfile(output/family/name,inputs/name)
            dest=output/family/arm;dest.mkdir(exist_ok=False)
            for case in read(ROOT/path/'questions.json')['cases']:
                (inputs/'question.json').write_text(json.dumps({'id':case['id'],'question':case['question']}))
                out=temp/(family+'-'+case['id']);out.mkdir();started=time.perf_counter();logs=''
                program='from tools.sorter_options_study import worker; worker('+repr(arm)+')'
                try:
                    with tempfile.TemporaryFile() as log:
                        process=subprocess.run(command(shutil.which('bwrap'),code,inputs,out,program),stdin=subprocess.DEVNULL,
                            stdout=log,stderr=log,timeout=180,close_fds=True,preexec_fn=_limits)
                        log.seek(0);logs=log.read(100000).decode(errors='replace')
                    if process.returncode:raise ValueError('Worker exit'+str(process.returncode))
                    row=read(out/'result.json');row['execution_status']='completed'
                    if row['implementation_sha256']!=protocol['runtime_sha256']:raise ValueError('Reader drift')
                except Exception as exc:
                    row=read(out/'checkpoint.json') if (out/'checkpoint.json').exists() else {}
                    row.update(case_id=case['id'],question=case['question'],execution_status='partial' if row else 'failed',error=str(exc))
                row.update(experimental_arm=arm,parent_wall_seconds=time.perf_counter()-started)
                save(dest/(case['id']+'.json'),row);(dest/(case['id']+'.log')).write_text(logs)
                for name in ['trace','review']:
                    if (out/(name+'.json')).exists():shutil.copyfile(out/(name+'.json'),dest/(case['id']+'-'+name+'.json'))
                rows.append({'family':family,'id':case['id'],'status':row['execution_status'],'sha256':sha((dest/(case['id']+'.json')).read_bytes())})
                print(arm,family,case['id'],row['execution_status'],flush=True)
    validate(output)
    save(output/(arm+'-receipt.json'),{'arm':arm,'cases':rows,'runtime_sha256':protocol['runtime_sha256'],
        'protocol_sha256':sha((output/'options-protocol.json').read_bytes()),'network_isolated':True,
        'reference_keys_mounted':False,'worker_wall_seconds':180,'independent_human_evaluation':'NOT RUN'})


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['prepare','run']);p.add_argument('output',type=Path)
    p.add_argument('--arm',choices=ARMS);a=p.parse_args()
    if a.command=='prepare':prepare(a.output)
    elif a.arm:run(a.output,a.arm)
    else:p.error('--arm required')


if __name__=='__main__':main()
