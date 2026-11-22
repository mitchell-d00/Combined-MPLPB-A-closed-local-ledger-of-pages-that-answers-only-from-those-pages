"""Run the historical panels through graph-assisted passage discovery."""
import argparse
from collections import Counter, defaultdict
from contextlib import ExitStack
import gzip
from html import escape
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from mplpb_answers.body_text import body_text
from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query
from mplpb_answers.relation_graph import declared_fields
from mplpb_answers.synonym_graph import build, open_index
from mplpb_combined.reader import PROFILES
from mplpb_combined.ledger import Ledger, write
from tools.article_study import file_pins
from tools.sorter_first_study import FAMILIES, ROOT
from tools.unprepared_challenge import code_pins, frozen, read, save, sha
from tools.unprepared_sources import import_corpus
from test_tools.historical_patterns import ARMS, PANEL, anchor_matches, measured

DATA = ROOT / 'evaluation/historical-synonym-graph'
PROFILE = PROFILES['internal']


def visible(anchors, probe):
    return sum(any(anchor_matches(a, p['source_id'], p['text']) for p in probe['passages'])
               for a in anchors)


def discovery(root, question, records):
    index = PassageIndex(root, question, PROFILE)
    baseline = index.retrieve([question], max_passages=12, max_chars=8000)
    eligible = {record.id for record in index.records}
    selected = set(records) & eligible
    selected_fields = {field['field'] for record in index.records if record.id in selected
                       for field in declared_fields(record)}
    if not selected:
        return baseline, baseline, selected, selected_fields
    # Apply a candidate restriction to a separate retrieval probe. The native
    # answer path never consumes the restricted set, which could hide conflicts.
    index.passages = [p for p in index.passages if p['source_id'] in selected]
    index.sources = [s for s in index.sources if s['id'] in selected]
    guided = index.retrieve([question], max_passages=12, max_chars=8000)
    return baseline, guided, selected, selected_fields


def execute(output):
    topics = read(DATA / 'topics.json')
    inputs = {'catalog': sha((DATA / 'catalog.json').read_bytes()),
              'new_topics': sha((DATA / 'topics.json').read_bytes()),
              'historical_questions': sha(PANEL.read_bytes())}
    if inputs['historical_questions'] != PANEL.with_suffix('.sha256').read_text().split()[0]:
        raise ValueError('Historical questions changed')
    groups = read(PANEL)['groups']
    prior = PANEL.parent / 'native.json.gz'
    runtime = code_pins(ROOT)
    baseline = read(prior.with_name('report.json'))
    if baseline['panel_sha256'] != inputs['historical_questions'] or baseline['native_sha256'] != runtime:
        raise ValueError('Retained strict baseline differs in questions or native code')
    with gzip.open(prior, 'rt', encoding='utf-8') as stream:
        previous = {r['id']: r['answer'] for r in json.load(stream)}
    output.mkdir(parents=True, exist_ok=False)
    rows, packets, field_inventory = [], [], {}
    by_collection = defaultdict(Counter)
    with ExitStack() as stack:
        workspace = Path(stack.enter_context(TemporaryDirectory(prefix='mplpb-historical-graph-')))
        db = workspace / 'graph.sqlite'
        build(db, read(DATA / 'catalog.json'))
        graph = stack.enter_context(open_index(db))
        for collection in (*FAMILIES, 'new'):
            ledger = workspace / collection
            if collection == 'new':
                ledger.mkdir()
                for source in topics['sources']:
                    html = '<p>' + escape(source['text']) + '</p>'
                    write(ledger, doc_id=source['id'], title=source['title'], scope='public history summary',
                          body_html=html, origin='machine', when='2026-11-22')
                relevant = topics['groups']
            else:
                folder, seal = FAMILIES[collection]
                corpus = ROOT / folder
                frozen(corpus, seal)
                import_corpus(corpus, ledger)
                relevant = [group for group in groups if group['corpus'] == collection]
            original = file_pins(ledger)
            eligible = {r.id: r for r in Ledger(ledger).servable()}
            bodies = {ident: body_text(r.body_html) for ident, r in eligible.items()}
            field_inventory[collection] = {ident: sorted({f['field'] for f in declared_fields(r)})
                                           for ident, r in eligible.items()}
            for group in relevant:
                if not all(anchor_matches(a, a['source_id'], bodies.get(a['source_id'], ''))
                           for a in group['anchors']):
                    raise ValueError('Prepared or original anchor differs from source: ' + group['id'])
                phrase = group['anchors'][0]['quote']
                questions = {'quote': f'Which source contains the exact words "{phrase}"?', **group['questions']}
                for arm in ARMS:
                    ident = group['id'] + '-' + arm
                    question = questions[arm]
                    hit = graph.lookup(collection, question)
                    answer = answer_query(ledger, question, PROFILE, mode='strict',
                                          max_passages=12, max_chars=8000).contract if collection == 'new' else previous[ident]
                    if answer['question'] != question:
                        raise ValueError('Existing native output belongs to a different question')
                    anchors = group['anchors'][:1] if arm == 'quote' else group['anchors']
                    base, guided, selected, fields = discovery(ledger, question, hit['records'])
                    before, after = visible(anchors, base), visible(anchors, guided)
                    key = by_collection[collection]
                    key['cases'] += 1
                    key['any_record_hint'] += bool(selected)
                    key['all_reference_records_suggested'] += {a['source_id'] for a in anchors} <= selected
                    key['record_hint_competition'] += len(selected) > 1
                    key['usable_record_field_pair'] += bool(len(selected) == 1 and set(hit['fields']) & fields)
                    key['strict_full_support'] += answer['answer_supported']
                    if arm in ('direct', 'paraphrase'):
                        key['direct_and_paraphrase_cases'] += 1
                        key['all_anchors_baseline'] += before == len(anchors)
                        key['all_anchors_graph_probe'] += after == len(anchors)
                        key['cases_more_anchors'] += after > before
                        key['cases_fewer_anchors'] += before > after
                    row = {'id': ident, 'collection': collection, 'arm': arm, 'question': question,
                           'native': measured(group, arm, answer, base), 'graph': hit,
                           'hinted_eligible_records': sorted(selected), 'declared_fields': sorted(fields),
                           'baseline_anchors': before, 'graph_anchors': after}
                    rows.append(row)
                    if collection == 'new':
                        packets.append({'id': ident, 'answer': answer})
            if original != file_pins(ledger):
                raise ValueError('Replay modified native ledger')
    report = {'inputs_sha256': inputs, 'native_sha256': runtime,
              'retained_baseline_sha256': sha(prior.read_bytes()), 'comparisons': by_collection,
              'declared_fields_in_imports': field_inventory,
              'independent_review': 'NOT RUN', 'cases': rows}
    save(output / 'report.json', report)
    save(output / 'new-topic-native.json', packets)
    print(json.dumps(by_collection, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    execute(parser.parse_args().output)


if __name__ == '__main__':
    main()
