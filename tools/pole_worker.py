"""Replay one trusted Pole source packet in a fresh, disposable ledger."""
import hashlib
import html
import json
from pathlib import Path
import resource
import sys
import time


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def snapshot(root):
    return {path.relative_to(root): digest(path.read_bytes())
            for path in root.rglob('*') if path.is_file()}


def execute(inputs, ledger, destination):
    from mplpb_answers.body_text import body_text
    from mplpb_answers.passages import PassageIndex
    from mplpb_answers.pipeline import answer_query
    from mplpb_answers.prose_retrieval import retrieve
    from mplpb_combined.ledger import write, withdraw
    from mplpb_combined.reader import PROFILES
    from mplpb_work.sorter_explorer import label_graph
    from mplpb_work.sorter_v2 import sort_directory

    start, cpu = time.perf_counter(), time.process_time()
    raw_snapshot = snapshot(inputs)
    case = json.loads((inputs / 'case.json').read_text())
    receipts = []
    source_bytes = 0
    for number, source in enumerate(case['sources'], 1):
        path = (inputs / source['path']).resolve()
        path.relative_to(inputs / 'sources')
        raw = path.read_bytes()
        source_bytes += len(raw)
        if source['source_class'] != 'original':
            continue
        record = write(ledger, doc_id=f'SOURCE-{number:04d}', title=f'Synthetic source {number}',
                       scope='archival records', body_html='<pre>' + html.escape(raw.decode()) + '</pre>',
                       origin='machine', source_authorship='declared-machine',
                       external=source.get('external', ''), not_for=source.get('not_for', ''),
                       when='2026-11-19T00:00Z')
        receipts.append({'source_id': record.id, 'hash': record.hash_actual,
                         'canonical_body': body_text(record.body_html)})
        if source.get('retired'):
            withdraw(ledger, record.id, note='Synthetic current-policy boundary')
        if source.get('corrupt'):
            page = ledger / record.path
            page.write_text(page.read_text().replace('wrote', 'invented', 1))
    sealed = snapshot(ledger)
    profile = PROFILES[case['profile']]
    question = case['question']
    passages, characters = case['budget']['passages'], case['budget']['characters']
    index = PassageIndex(ledger, question, profile)
    retrieval = {'native_facets': retrieve(index, passages, characters),
                 'simple_bm25': index.retrieve([question], passages, characters)}
    answer = answer_query(ledger, question, profile, max_passages=passages,
                          max_chars=characters).contract
    sources = inputs / 'sources'
    before = sort_directory(sources, 'not-compared')
    after = sort_directory(sources, 'compare')
    labels = [label_graph(graph, sources) for graph in (before, after)]
    if raw_snapshot != snapshot(inputs) or sealed != snapshot(ledger):
        raise ValueError('Reader modified the source or sealed ledger')
    result = {
        'case_id': case['id'], 'answer': answer, 'retrieval': retrieval, 'source_receipts': receipts,
        'sorter': {
            'nodes': after['nodes'], 'edges': after['edges'], 'complete': after['complete'],
            'nodes_identical_between_modes': before['nodes'] == after['nodes'],
            'node_labels_identical_between_modes': labels[0]['node_labels'] == labels[1]['node_labels'],
            'all_labels_non_authoritative': all(
                not label['answer_supported'] and not label['historical_truth_independently_verified']
                for view in labels for label in view['node_labels'] + view['edge_labels']),
        },
        'measurements': {
            'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.perf_counter() - start,
            'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'explicit_original_read_calls': len(case['sources']),
            'explicit_original_bytes_read': source_bytes,
        },
    }
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, allow_nan=False)


if __name__ == '__main__':
    implementation, inputs, ledger, destination = map(Path, sys.argv[1:])
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024**2, 8 * 1024**2))
    sys.path.insert(0, str(implementation))
    execute(inputs, ledger, destination)
