"""Paired sorter-first retrieval experiment over frozen original-record questions.

The experimental adapter changes passage ranking only. Native reader, grammar,
eligibility and proof kernels are unchanged. No answer key enters the worker.
"""
import argparse
from collections import Counter
from bisect import bisect_left, bisect_right
from contextlib import contextmanager
import hashlib
import json
import math
import html
from html.parser import HTMLParser
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

from tools.unprepared_challenge import read, save, sha, code_pins, frozen

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {
    'original': ('evaluation/unprepared-originals/2026-11-16', 'freeze-v2.json'),
    'government': ('evaluation/unprepared-originals/2026-11-16-followup/unfamiliar', 'freeze.json'),
}


def layout_text(source, raw):
    """Preserve physical text layout; HTML block boundaries add blank lines only."""
    text = raw.decode(source['encoding'])
    if source['media_type'] != 'text/html': return text
    import re
    fragment = re.search(r'<body\b[^>]*>([\s\S]*)</body\s*>', text, re.I)[1]
    class Layout(HTMLParser):
        SKIP = {'h1','h2','h3','h4','h5','h6','script','style','head','title','noscript'}
        BLOCK = {'p','div','li','tr','br','pre','section','ul','ol','table'}
        def __init__(self): super().__init__(); self.parts=[]; self.blocked=[]
        def handle_starttag(self, tag, attrs):
            if tag in self.SKIP: self.blocked.append(tag)
            elif not self.blocked and tag in self.BLOCK: self.parts.append('\n\n')
        def handle_endtag(self, tag):
            if tag in self.blocked:
                i=len(self.blocked)-1-self.blocked[::-1].index(tag); del self.blocked[i:]
                if not self.blocked: self.parts.append('\n\n')
            elif not self.blocked and tag in self.BLOCK: self.parts.append('\n\n')
        def handle_data(self, value):
            if not self.blocked: self.parts.append(value)
    parser=Layout(); parser.feed(fragment); parser.close(); return ''.join(parser.parts)


def locate(index, graph, bindings, base, max_passages, max_chars):
    """Return only existing eligible original passages; hints never become proof."""
    if index.exact_status:
        return base, {'status': 'exact_route_preserved', 'selected_hints': []}
    from mplpb_answers.body_text import body_text
    from mplpb_answers.evidence_contract import ReaderError
    from mplpb_combined.reader import terms
    records = {r.id: r for r in index.records}
    query = terms(index.question)
    statements = [n for n in graph['nodes'] if n['kind'] == 'statement']
    words = [terms(n['span'].get('text', '')) for n in statements]
    df = Counter(w for row in words for w in row)
    bodies = {}; ranked = []; invalid = []; matched = []; maps = {}
    for node, row in zip(statements, words):
        span = node['span']; binding = bindings.get(span['path'])
        if not binding:
            invalid.append({'node_id': node['id'], 'reason': 'unmapped_source'}); continue
        r = records.get(binding['id'])
        if not r:
            continue  # Ineligible originals are never restored by a candidate.
        if r.hash_actual != binding['hash']:
            invalid.append({'node_id': node['id'], 'reason': 'source_pin_changed'}); continue
        if r.id not in bodies:
            bodies[r.id] = body_text(r.body_html)
        body = bodies[r.id]; a = span['char_start']; b = span['char_end']
        layout = binding.get('sorter_text', body)
        if span['path'] not in maps:
            from tools.source_roundtrip import projection_offsets
            from mplpb_work.sorter import _byte_offsets
            canonical, starts, ends = projection_offsets(layout, False)
            positions = [(start, end, i) for i,(start,end) in enumerate(zip(starts,ends)) if start >= 0]
            maps[span['path']] = (canonical == body and sha(body.encode()) == binding['projection_sha256'],
                sha(layout.encode()), [p[0] for p in positions], [p[1] for p in positions], [p[2] for p in positions], _byte_offsets(layout))
        mapping_valid, layout_hash, starts, ends, indices, byte_offsets = maps[span['path']]
        if (type(a) is not int or type(b) is not int or not 0 <= a < b <= len(layout)
                or not mapping_valid
                or span['source_sha256'] != 'sha256:' + layout_hash
                or layout[a:b] != span.get('text')
                or byte_offsets[a] != span['byte_start']
                or byte_offsets[b] != span['byte_end']):
            invalid.append({'node_id': node['id'], 'reason': 'source_span_changed'}); continue
        lo = bisect_right(ends,a); hi = bisect_left(starts,b)
        if lo >= hi: continue
        a, b = indices[lo], indices[hi-1]+1
        quote = body_text('<pre>'+html.escape(span['text'])+'</pre>')
        if (body[a:b] != quote
                or body[a:b] != span.get('text')
                    and 'sorter_text' not in binding):
            invalid.append({'node_id': node['id'], 'reason': 'canonical_roundtrip_failed'}); continue
        shared = query & row
        if not shared:
            continue
        score = sum(math.log(1 + len(statements) / df[t]) for t in shared) / math.sqrt(max(1, len(row)))
        matched.append({'node_id': node['id'], 'source_id': r.id, 'path': r.path,
                        'hash': r.hash_actual, 'body_start': a, 'body_end': b,
                        'quote': body[a:b], 'score': score, 'answer_supported': False})
        for p in index.passages:
            if p['source_id'] == r.id and p['body_start'] < b and p['body_start'] + len(p['text']) > a:
                ranked.append((score, node['id'], p))
    ranked.sort(key=lambda v: (-v[0], v[2]['path'], v[2]['body_start'], v[1]))
    hints = []; seen = set()
    for score, node_id, p in ranked:
        key = (p['path'], p['body_start'], p['text'])
        if key not in seen:
            hints.append(dict(p, retrieval_score=score, sorter_node_id=node_id,
                              retrieval_reason='sorter_statement_location_only')); seen.add(key)
    # Alternate hints and ordinary source discovery under exactly the same cap.
    # The full eligible index and verifier's independent conflict scan remain intact.
    selected = []; seen = set(); used = 0
    for i in range(max(len(hints), len(base['passages']))):
        for items in (hints, base['passages']):
            if i >= len(items): continue
            p = items[i]; key = (p['path'], p['body_start'], p['text'])
            if key in seen or len(selected) >= max_passages or used + len(p['text']) > max_chars: continue
            selected.append(p); seen.add(key); used += len(p['text'])
    if not index.unchanged():
        raise ReaderError('source_changed', 'Original changed during sorter location checks')
    paths = {p['path'] for p in selected}
    pack = dict(base, passages=selected, sources=[s for s in index.sources if s['path'] in paths],
                search_complete=False, ranking='experimental-sorter-original-location-interleave-v1')
    trace = {'status': 'candidate_locations_only', 'selected_hints': [p for p in selected if 'sorter_node_id' in p],
             'matched_statements': matched[:64], 'matched_statement_count': len(matched),
             'invalid_hints': invalid, 'passage_count': len(selected), 'characters': used,
             'max_passages': max_passages, 'max_characters': max_chars,
             'graph_complete': graph['complete'], 'graph_limits': graph['limits_or_exclusions'],
             'comparison_edges_used_as_semantic_proof': False, 'answer_supported': False}
    return pack, trace


@contextmanager
def adapter(graph, bindings, traces):
    """Explicit experiment hook; never modify native source or verifier code."""
    import mplpb_answers.prose_retrieval as retrieval
    original = retrieval.retrieve
    def wrapped(index, max_passages=12, max_chars=12000, seed=None):
        base = original(index, max_passages, max_chars, seed=seed)
        pack, trace = locate(index, graph, bindings, base, max_passages, max_chars)
        traces.append(trace)
        return pack
    with patch.object(retrieval, 'retrieve', wrapped):
        yield


def prepare(output):
    from tools.unprepared_sources import import_corpus, verify, projected, inside
    from tools.unprepared_challenge import projections
    from tools.source_roundtrip import projection_offsets
    from mplpb_work.sorter import sort_directory, verify_graph
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    runtime = code_pins(ROOT)
    protocol = {'schema': 'sorter-first-paired-protocol-v1',
        'baseline_complete_source_supported_answers': 2, 'baseline_total': 22,
        'baseline_successes': ['H02', 'H05'], 'cases': 'all 22 unchanged questions',
        'reader_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'reader_sha256': runtime, 'adapter_sha256': sha(Path(__file__).read_bytes()),
        'worker_harness_sha256': sha((ROOT/'tools/unprepared_challenge.py').read_bytes()),
        'intervention': 'Same native reader; experiment-only retrieval hook interleaves sorter-located eligible original passages with ordinary retrieval. No grammar, kernel or eligibility patch.',
        'budgets': {'worker_wall_seconds': 180, 'worker_cpu_seconds': 300, 'address_space_bytes': 2*1024**3,
                    'answer_passages': 12, 'answer_characters': 8000, 'candidate_passages': 12,
                    'candidate_characters': 12000, 'investigation_characters': 200000},
        'sorting': 'Default bounds; original physical text layout or HTML text with block separators. Checked canonical roundtrip and fixed pre-existing native import cuts. Both modes identical nodes; edges are not semantic proofs.',
        'metrics': ['native complete answers', 'native partial answers', 'outcome changes with exact original citations',
                    'draft span discovery separate from answers', 'old success regressions', 'timeouts and costs'],
        'independent_human_evaluation': 'NOT RUN', 'model_calls': 0,
        'reference_notice': 'Existing incomplete developer references; no complete historical accuracy or recall claim.'}
    save(output/'protocol.json', protocol)
    for name, (path, seal_name) in FAMILIES.items():
        corpus = ROOT/path; frozen(corpus, seal_name)
        family = output/name; family.mkdir(); raw = family/'sorter-inputs'; raw.mkdir()
        with tempfile.TemporaryDirectory() as tmp:
            receipt = import_corpus(corpus, Path(tmp)/'ledger')
            texts = projections(corpus, receipt)
        layouts = {}
        for source in verify(corpus)['sources']:
            raw_source = inside(corpus,source['path']).read_bytes(); layout = layout_text(source,raw_source)
            canonical, starts, ends = projection_offsets(layout,False)
            if canonical != projected(source,raw_source)[0]: raise ValueError('Layout changed canonical source text')
            layouts[source['id']] = (layout,starts,ends)
        bindings = {}
        for ident, (record, body) in texts.items():
            layout, starts, ends = layouts[record['original_id']]
            a,b=record['projection_character_start'],record['projection_character_end']
            positions=[i for i in range(a,b) if starts[i]>=0]
            text=layout[starts[positions[0]]:ends[positions[-1]]]
            from mplpb_answers.body_text import body_text
            if body_text('<pre>'+html.escape(text)+'</pre>') != body: raise ValueError('Import chunk layout roundtrip failed')
            filename = ident+'.txt'; (raw/filename).write_bytes(text.encode('utf-8')); bindings[filename] = record
        save(family/'bindings.json', bindings); save(family/'import-receipt.json', receipt)
        started = time.perf_counter(); cpu = time.process_time()
        plain = sort_directory(raw, mode='not-compared'); compared = sort_directory(raw, mode='compare')
        assert plain['nodes'] == compared['nodes'] and plain['sources'] == compared['sources']
        save(family/'not-compared.json', plain); save(family/'compare.json', compared)
        replay = verify_graph(compared, raw)
        save(family/'sort-receipt.json', {'wall_seconds': time.perf_counter()-started,
             'cpu_seconds': time.process_time()-cpu, 'peak_process_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
             'scope': 'Both sort modes and fresh graph replay, once per corpus; not charged to each question.',
             'graph_replay': replay, 'nodes_identical_between_modes': True,
             'complete': compared['complete'], 'limits': compared['limits_or_exclusions'],
             'nodes': len(compared['nodes']), 'edges': len(compared['edges']), 'source_bytes_read': plain['source_bytes_read']+compared['source_bytes_read']})
        save(family/'frozen-inputs.json', {'source_corpus': path, 'seal_file': seal_name,
             'seal_sha256': sha((corpus/seal_name).read_bytes()), 'questions_sha256': sha((corpus/'questions.json').read_bytes()),
             'graph_sha256': sha((family/'compare.json').read_bytes()), 'bindings_sha256': sha((family/'bindings.json').read_bytes()),
             'source_projections': {p.name: sha(p.read_bytes()) for p in sorted(raw.iterdir())},
             'added_answer_fields': False, 'canonical_projection_only': True})
    save(output/'freeze.json', {'protocol_sha256': sha((output/'protocol.json').read_bytes()),
         'family_freeze_sha256': {name: sha((output/name/'frozen-inputs.json').read_bytes()) for name in FAMILIES}})


def validate(output):
    output = Path(output); seal = read(output/'freeze.json'); protocol = read(output/'protocol.json')
    if seal['protocol_sha256'] != sha((output/'protocol.json').read_bytes()): raise ValueError('Protocol changed')
    if protocol['reader_sha256'] != code_pins(ROOT): raise ValueError('Reader changed after freeze')
    if protocol['adapter_sha256'] != sha(Path(__file__).read_bytes()): raise ValueError('Adapter changed after freeze')
    for name, (path, seal_name) in FAMILIES.items():
        frozen(ROOT/path, seal_name); family = output/name; pins = read(family/'frozen-inputs.json')
        if sha((family/'frozen-inputs.json').read_bytes()) != seal['family_freeze_sha256'][name]: raise ValueError('Input pins changed')
        for filename, key in [('compare.json', 'graph_sha256'), ('bindings.json', 'bindings_sha256')]:
            if sha((family/filename).read_bytes()) != pins[key]: raise ValueError('Sorter input changed')
        for filename, pin in pins['source_projections'].items():
            if sha((family/'sorter-inputs'/filename).read_bytes()) != pin: raise ValueError('Original projection changed')
    return protocol


def worker(case, output, treatment):
    from tools.unprepared_challenge import worker as native_worker
    traces = []
    if treatment:
        graph = read('/study/compare.json'); bindings = read('/study/bindings.json')
        for filename,binding in bindings.items():
            binding['sorter_text']=(Path('/study/sorter-inputs')/filename).read_bytes().decode('utf-8')
        with adapter(graph, bindings, traces):
            native_worker('/app', '/study/ledger', case, output, 'updated')
    else:
        native_worker('/app', '/study/ledger', case, output, 'updated')
    save(Path(output).parent/'sorter-trace.json', {'enabled': treatment, 'calls': traces,
         'native_files_changed': False, 'authority': 'passage location only'})


def run(output, arm):
    from tools.unprepared_sources import import_corpus
    from tools.study_sandbox import command, _limits
    output = Path(output).resolve(); protocol = validate(output)
    if arm == 'sorter-first' and not (output/'direct-receipt.json').exists():
        raise ValueError('Finish unchanged direct arm first')
    rows = []
    with tempfile.TemporaryDirectory(prefix='mplpb-sorter-first-') as tmp:
        tmp = Path(tmp); code = tmp/'code'; code.mkdir()
        for package in ('mplpb_answers', 'mplpb_combined', 'mplpb_work'):
            shutil.copytree(ROOT/package, code/package, ignore=shutil.ignore_patterns('__pycache__'))
        (code/'tools').mkdir()
        for filename in ['sorter_first_study.py', 'unprepared_challenge.py', 'source_roundtrip.py', 'unprepared_sources.py']:
            shutil.copyfile(ROOT/'tools'/filename, code/'tools'/filename)
        for name, (path, _) in FAMILIES.items():
            inputs = tmp/name; inputs.mkdir(); receipt = import_corpus(ROOT/path, inputs/'ledger')
            if receipt != read(output/name/'import-receipt.json'): raise ValueError('Import changed')
            (inputs/'ledger/import-receipt.json').unlink()
            if arm == 'sorter-first':
                shutil.copytree(output/name/'sorter-inputs', inputs/'sorter-inputs')
                for filename in ['compare.json', 'bindings.json']:
                    shutil.copyfile(output/name/filename, inputs/filename)
            dest = output/name/arm; dest.mkdir(exist_ok=False)
            for case in read(ROOT/path/'questions.json')['cases']:
                (inputs/'question.json').write_text(json.dumps({'id': case['id'], 'question': case['question']}))
                out = tmp/('out-'+arm+'-'+case['id']); out.mkdir()
                program = 'from tools.sorter_first_study import worker; worker("/study/question.json", "/output/result.json", '+repr(arm == 'sorter-first')+')'
                started = time.perf_counter()
                try:
                    with tempfile.TemporaryFile() as log:
                        process = subprocess.run(command(shutil.which('bwrap'), code, inputs, out, program),
                            stdout=log, stderr=log, stdin=subprocess.DEVNULL, close_fds=True, timeout=180, preexec_fn=_limits)
                        log.seek(0); logs = log.read(100000).decode(errors='replace')
                    if process.returncode: raise ValueError('Worker exit '+str(process.returncode))
                    row = read(out/'result.json'); row['execution_status'] = 'completed'
                    if row['implementation_sha256'] != protocol['reader_sha256']: raise ValueError('Worker pin mismatch')
                except Exception as exc:
                    logs = 'Execution failed: '+str(exc)
                    row = read(out/'checkpoint.json') if (out/'checkpoint.json').exists() else {}
                    row.update(case_id=case['id'], question=case['question'], execution_status='partial' if row else 'failed', error=str(exc))
                row.update(parent_wall_seconds=time.perf_counter()-started, experimental_arm=arm)
                save(dest/(case['id']+'.json'), row); (dest/(case['id']+'.log')).write_text(logs)
                if (out/'sorter-trace.json').exists(): shutil.copyfile(out/'sorter-trace.json', dest/(case['id']+'-sorter-trace.json'))
                rows.append({'family': name, 'case_id': case['id'], 'status': row['execution_status'],
                             'sha256': sha((dest/(case['id']+'.json')).read_bytes())})
                print(arm, name, case['id'], row['execution_status'], flush=True)
    validate(output)
    save(output/(arm+'-receipt.json'), {'arm': arm, 'reader_revision': protocol['reader_revision'],
         'reader_sha256': protocol['reader_sha256'], 'freeze_sha256': sha((output/'freeze.json').read_bytes()),
         'cases': rows, 'worker_wall_timeout_seconds': 180, 'network_isolated': True,
         'reference_keys_mounted': False, 'independent_human_evaluation': 'NOT RUN'})


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('command', choices=['prepare', 'run'])
    p.add_argument('output', type=Path); p.add_argument('--arm', choices=['direct', 'sorter-first']); args = p.parse_args()
    if args.command == 'prepare': prepare(args.output)
    elif not args.arm: p.error('--arm required')
    else: run(args.output, args.arm)


if __name__ == '__main__': main()
