"""Compare graph-guided discovery on the original, unchanged 22 questions."""
import argparse
from collections import Counter
from contextlib import ExitStack
import gzip
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from mplpb_answers.body_text import body_text
from mplpb_answers.synonym_graph import build, open_index
from mplpb_combined.ledger import Ledger
from tools.article_study import file_pins
from tools.sorter_first_study import FAMILIES, ROOT
from tools.unprepared_challenge import code_pins, frozen, read, save, sha
from tools.unprepared_sources import import_corpus
from test_tools.historical_graph_study import DATA, discovery, visible
from test_tools.historical_patterns import anchor_matches


def execute(replay, output):
    baseline = read(replay / 'report.json')
    if baseline['cases'] != 22 or baseline['runtime_sha256'] != code_pins(ROOT):
        raise ValueError('Generate an original article replay for this native revision first')
    with gzip.open(replay / 'packets.json.gz', 'rt', encoding='utf-8') as stream:
        previous = {ident: answer for block in json.load(stream)
                    for ident, answer in zip(block['ids'], block['standalone'])}
    rows, counts, kinds = [], Counter(), Counter()
    with ExitStack() as stack:
        scratch = Path(stack.enter_context(TemporaryDirectory(prefix='mplpb-original-22-graph-')))
        db = scratch / 'graph.sqlite'
        build(db, read(DATA / 'catalog.json'))
        graph = stack.enter_context(open_index(db))
        for collection, (folder, seal) in FAMILIES.items():
            corpus = ROOT / folder
            frozen(corpus, seal)
            pins = baseline['originals'][collection]
            if (pins['seal_sha256'] != sha((corpus / seal).read_bytes()) or
                    pins['questions_sha256'] != sha((corpus / 'questions.json').read_bytes())):
                raise ValueError('Historical replay input pins differ from frozen originals')
            questions = read(corpus / 'questions.json')['cases']
            references = {row['id']: row['citations'] for row in read(corpus / 'reference-draft.json')['cases']}
            ledger = scratch / collection
            import_corpus(corpus, ledger)
            original = file_pins(ledger)
            bodies = {record.id: body_text(record.body_html) for record in Ledger(ledger).servable()}
            for case in questions:
                ident, question = case['id'], case['question']
                answer = previous[ident]
                anchors = references[ident]
                if answer['question'] != question or not all(
                        anchor_matches(a, a['source_id'], bodies.get(a['source_id'], '')) for a in anchors):
                    raise ValueError('Question or reference anchor changed: ' + ident)
                hit = graph.lookup(collection, question)
                base, guided, selected, fields = discovery(ledger, question, hit['records'])
                before, after = visible(anchors, base), visible(anchors, guided)
                counts['cases'] += 1
                counts['with_reference_anchors'] += bool(anchors)
                counts['with_graph_record_hint'] += bool(selected)
                counts['cases_with_competing_record_hints'] += len(selected) > 1
                counts['usable_record_field_pairs'] += bool(len(selected) == 1 and set(hit['fields']) & fields)
                counts['all_reference_records_suggested'] += bool(anchors) and {a['source_id'] for a in anchors} <= selected
                counts['all_anchors_baseline'] += bool(anchors) and before == len(anchors)
                counts['all_anchors_graph_probe'] += bool(anchors) and after == len(anchors)
                counts['more_anchors'] += after > before
                counts['fewer_anchors'] += after < before
                kinds[answer['kind']] += 1
                rows.append({'id': ident, 'question': question, 'native_kind': answer['kind'],
                             'native_diagnostic': answer['diagnostic']['code'], 'anchors': len(anchors),
                             'graph': hit, 'baseline_anchors': before, 'graph_anchors': after})
            if original != file_pins(ledger):
                raise ValueError('Replay changed the imported ledger')
    if len(rows) != len(previous) or len(rows) != 22:
        raise ValueError('Original 22 case coverage differs')
    save(output, {'revision': baseline['revision'], 'originals': baseline['originals'],
                  'native_replay_sha256': sha((replay / 'packets.json.gz').read_bytes()),
                  'catalog_sha256': sha((DATA / 'catalog.json').read_bytes()),
                  'native_outcomes': kinds, 'counts': counts, 'cases': rows})
    print(json.dumps({'native_outcomes': kinds, 'counts': counts}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-replay', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    execute(args.original_replay, args.output)


if __name__ == '__main__':
    main()
