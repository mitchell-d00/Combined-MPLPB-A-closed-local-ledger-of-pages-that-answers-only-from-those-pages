"""Trace corpus-scoped planning, graph discovery, admission, and cited output."""
import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from mplpb_answers.documentary import plan
from mplpb_answers.passages import PassageIndex
from mplpb_answers.report_sections import locate, request
from mplpb_answers.synonym_graph import build, open_index
from mplpb_combined.reader import PROFILES
from test_tools.historical_graph_study import DATA, discovery, visible
from tools.sorter_first_study import FAMILIES, ROOT
from tools.unprepared_challenge import code_pins, frozen, read, sha
from tools.unprepared_sources import import_corpus


def _coverage(anchors, spans):
    """Count covered draft-anchor characters once, even for overlapping spans."""
    results = []
    for anchor in anchors:
        intervals = sorted((max(anchor['start'], span['body_start']),
                            min(anchor['end'], span['body_end']))
                           for span in spans if span['source_id'] == anchor['source_id'])
        covered = 0
        previous = anchor['start']
        for start, end in intervals:
            if end > max(start, previous):
                covered += end - max(start, previous)
                previous = end
        results.append({'source_id': anchor['source_id'], 'covered_characters': covered,
                        'anchor_characters': anchor['end'] - anchor['start']})
    return results


def run(replay):
    report = read(replay / 'report.json')
    if report['cases'] != 22 or report['runtime_sha256'] != code_pins(ROOT):
        raise ValueError('Replay the original 22 on this exact runtime first')
    archive = (replay / 'packets.json.gz').read_bytes()
    answers = {ident: answer for packet in json.loads(gzip.decompress(archive))
               for ident, answer in zip(packet['ids'], packet['standalone'], strict=True)}
    catalog = DATA / 'catalog.json'
    results = []
    with TemporaryDirectory(prefix='mplpb-historical-seams-') as scratch:
        root = Path(scratch)
        graph_path = root / 'catalog.sqlite'
        build(graph_path, read(catalog))
        with open_index(graph_path) as graph:
            for collection, (directory, seal) in FAMILIES.items():
                corpus = ROOT / directory
                frozen(corpus, seal)
                pins = report['originals'][collection]
                if pins['seal_sha256'] != sha((corpus / seal).read_bytes()):
                    raise ValueError('Historical source seal changed')
                ledger = root / collection
                import_corpus(corpus, ledger)
                references = {case['id']: case['citations'] for case in read(corpus / 'reference-draft.json')['cases']}
                for case in read(corpus / 'questions.json')['cases']:
                    ident, question = case['id'], case['question']
                    answer, anchors = answers[ident], references[ident]
                    if answer['question'] != question:
                        raise ValueError('Historical question changed: ' + ident)
                    graph_records = graph.lookup(collection, question)['records']
                    plain, guided, eligible, _ = discovery(ledger, question, graph_records)
                    summary = request(question)
                    section = None
                    if summary:
                        index = PassageIndex(ledger, question, PROFILES['internal'])
                        if found := locate(index, summary['report']):
                            record, body, (begin, end) = found
                            section = {'source_id': record.id, 'hash': record.hash_actual,
                                       'retained_by_graph': set(eligible) == {record.id},
                                       'body_start': begin, 'body_end': end,
                                       'anchor_visibility': visible(anchors, {'passages': [
                                           {'source_id': record.id, 'text': body[begin:end]}]}),
                                       'source_support_established': False}
                    support = answer.get('documentary_support') or {}
                    admission = support.get('admission', {})
                    cites = [c for claim in answer['claims'] for c in claim['citations']]
                    results.append({
                        'case_id': ident, 'question': question, 'draft_anchors': len(anchors),
                        'native_question_plan': plan(question), 'summary_request': summary,
                        'eligible_graph_records': sorted(eligible),
                        'ordinary_probe_anchors': visible(anchors, plain),
                        'record_graph_probe_anchors': visible(anchors, guided), 'section_edge': section,
                        'native_admitted_witnesses': admission.get('passages_admitted'),
                        'native_blocked_witnesses': admission.get('blocked', []),
                        'native_review_only_hints': admission.get('review_only_hint_count'),
                        'native_obligations': support.get('obligations'),
                        'native_output_budget': answer.get('passage_budget'),
                        'native_kind': answer['kind'], 'native_diagnostic': answer['diagnostic']['code'],
                        'native_text': answer['text'], 'native_citations': cites,
                        'native_citation_coverage': _coverage(anchors, cites),
                    })
    return {'schema': 'mplpb-historical-seams-v1', 'n': len(results),
            'native_replay_sha256': sha256(archive).hexdigest(),
            'catalog_sha256': sha(catalog.read_bytes()),
            'native_outcomes': dict(Counter(row['native_kind'] for row in results)), 'cases': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-replay', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.original_replay)
    with args.output.open('x') as out:
        json.dump(result, out, ensure_ascii=False, indent=2)
        out.write('\n')
    print(result['native_outcomes'])


if __name__ == '__main__':
    main()
