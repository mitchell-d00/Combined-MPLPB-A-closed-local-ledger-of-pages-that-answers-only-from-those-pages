"""Post-run scoring/audit adapter for the frozen known-weakness producer.

No source/expected outcome changes. Reads only after each shard is complete.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
from tools import dpercent as D
from tools import dpercent_expanded as E
from tools import dpercent_weaknesses as W


def audit(packets, custodian, output):
    packets, custodian, output = map(Path, (packets, custodian, output))
    manifest = D.read(packets/'study.json')
    if manifest != D.read(custodian/'study-copy.json'): raise ValueError('Study manifest changed')
    totals = Counter(); costs = Counter(); peak = 0; revisions = set(); runtime_pins = set()
    source_errors = []; graph_failures = []; outcomes = Counter(); positives = negatives = 0
    for shard in manifest['shards']:
        name = shard['name']; dest = output/name
        if not (dest/'run.json').exists(): continue
        if D.sha((packets/name/'seal.json').read_bytes()) != shard['seal_sha256']: raise ValueError('Shard seal changed')
        D.verify(packets/name, custodian/name)
        record = D.read(dest/'run.json'); revisions.add(record['checkout_revision'])
        runtime_pins.add(D.sha(json.dumps(record['runtime_sha256'], sort_keys=True).encode()))
        if record['packet_seal_sha256'] != shard['seal_sha256']: raise ValueError('Run seal differs')
        score_path = output/(name+'-score.json')
        if not score_path.exists(): W.score_shard(packets/name, custodian/name, dest, score_path)
        score = D.read(score_path)
        keys = {k['id']: k for k in D.read(custodian/name/'key.json')['cases']}
        for row in score['cases']:
            outcomes[row['outcome']] += 1
            if row['expected'] == 'answer': positives += 1
            else: negatives += 1
        for entry in record['cases']:
            totals['executed'] += 1
            if entry['execution'] != 'completed': totals['execution_failed'] += 1; continue
            case_id = entry['case_id']; path = dest/case_id/'result.json'
            if D.sha(path.read_bytes()) != entry['sha256']: raise ValueError('Result hash differs')
            data = D.read(path); graph = data['sorter']
            totals['completed'] += 1
            checks = W.graph_checks(graph, keys[case_id]['structural_expectations'])
            if not all(checks.values()): graph_failures.append({'shard': name, 'id': case_id, 'family': keys[case_id]['family'], 'checks': checks, 'limits_or_exclusions': graph['limits_or_exclusions']})
            raw_sources = {s['path']: (packets/name/'packets'/case_id/'sources'/s['path']).read_bytes() for s in graph['sources']}
            if any(s['raw_sha256'] != 'sha256:'+D.sha(raw_sources[s['path']]) for s in graph['sources']):
                source_errors.append({'shard': name, 'id': case_id, 'error': 'source hash mismatch'})
            if any(any(item.get('assessment', {}).get(flag) is not False for flag in
                       ('answer_supported', 'source_support_established', 'historical_truth_independently_verified'))
                   for item in graph['nodes']+graph['edges']):
                source_errors.append({'shard': name, 'id': case_id, 'error': 'candidate authority flag not false'})
            for node in graph['nodes']:
                span = node['span']; raw = raw_sources[span['path']]
                text = raw.decode('utf-8'); a, b = span['char_start'], span['char_end']; ba, bb = span['byte_start'], span['byte_end']
                valid = (type(a) is int and type(b) is int and type(ba) is int and type(bb) is int
                         and 0 <= a < b <= len(text) and 0 <= ba < bb <= len(raw)
                         and span['source_sha256'] == 'sha256:'+D.sha(raw)
                         and len(text[:a].encode()) == ba and len(text[:b].encode()) == bb
                         and raw[ba:bb].decode() == text[a:b]
                         and ('text' not in span or span['text'] == text[a:b]))
                totals['node_spans_checked'] += 1
                if not valid: source_errors.append({'shard': name, 'id': case_id, 'node': node['id']})
            measurements = data['measurements']
            for metric in ('cpu_seconds', 'wall_seconds', 'explicit_original_read_calls', 'explicit_original_bytes_read'):
                costs[metric] += measurements[metric]
            peak = max(peak, measurements['peak_rss_bytes'])
    summary = W.summarize(packets, custodian, output)
    complete = totals['executed'] == manifest['cases'] and not totals['execution_failed']
    result = {'schema': W.VERSION+'-audit', 'generator_sha256': manifest['generator_sha256'],
              'scorer_sha256': D.sha(Path(W.__file__).read_bytes()), 'audit_sha256': D.sha(Path(__file__).read_bytes()),
              'revision_labels': sorted(revisions), 'runtime_pin_digests': sorted(runtime_pins),
              'planned': manifest['cases'], 'counts': dict(totals), 'outcomes': dict(outcomes),
              'answerable_executed': positives, 'unsupported_executed': negatives,
              'E': outcomes['detected_answer']/positives if complete and positives else None,
              'F': outcomes['false_alarm']/negatives if complete and negatives else None,
              'graph_obligation_failures': graph_failures, 'source_span_errors': source_errors,
              'resources': dict(costs, peak_worker_rss_bytes=peak, total_pipeline_source_bytes_read=None,
                                human_review_seconds=None), 'independent_validation': 'NOT RUN',
              'semantic_relationship_precision': None, 'semantic_relationship_recall': None,
              'limits': 'Worker wall is summed across cases, not batch elapsed time; quoted-span fidelity is not semantic truth.'}
    D.save(output/'audit.json', result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('packets', 'custodian', 'output'): p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args(); print(json.dumps(audit(a.packets, a.custodian, a.output), indent=2))


if __name__ == '__main__': main()
