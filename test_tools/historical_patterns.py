"""Measure matched follow-up questions on the frozen historical-22 originals."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from mplpb_answers.body_text import body_text
from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import Ledger
from mplpb_combined.reader import PROFILES
from tools.article_study import file_pins
from tools.sorter_first_study import FAMILIES, ROOT
from tools.unprepared_challenge import code_pins, frozen, read, save, sha
from tools.unprepared_sources import import_corpus

PANEL = ROOT / 'evaluation/historical-patterns/questions.json'
ARMS = ('quote', 'direct', 'paraphrase', 'boundary')


def quote_text(text):
    return ' '.join(text.split()).casefold()


def anchor_matches(anchor, source_id, text):
    return source_id == anchor['source_id'] and quote_text(anchor['quote']) in quote_text(text)


def measured(group, arm, answer, probe):
    anchors = group['anchors'][:1] if arm == 'quote' else group['anchors']
    passages = probe['passages']
    citations = [c for claim in answer['claims'] for c in claim['citations']]
    cited = sum(any(anchor_matches(a, c.get('source_id'), c.get('quote', '')) for c in citations)
                for a in anchors)
    visible = sum(any(anchor_matches(a, p.get('source_id'), p.get('text', '')) for p in passages)
                  for a in anchors)
    if not answer['answer_supported']:
        observed = 'withheld_full_support'
    elif arm == 'boundary':
        observed = 'support_flag_review_required'
    elif cited == len(anchors):
        observed = 'supported_with_all_anchors'
    else:
        observed = 'supported_with_missing_anchors'
    return {'kind': answer['kind'], 'diagnostic': answer['diagnostic']['code'],
            'observation': observed, 'probe_anchors_visible': visible,
            'citation_anchors_visible': cited, 'anchors': len(anchors)}


def compare(rows):
    by_arm = {arm: dict(Counter(r['observation'] for r in rows if r['arm'] == arm))
              for arm in ARMS}
    by_group = {}
    for row in rows:
        by_group.setdefault(row['group'], {})[row['arm']] = row
    pairs = Counter()
    for group in by_group.values():
        direct = group['direct']['observation'] == 'supported_with_all_anchors'
        paraphrase = group['paraphrase']['observation'] == 'supported_with_all_anchors'
        pairs[(('direct' if direct else 'no_direct') + '_' +
               ('paraphrase' if paraphrase else 'no_paraphrase'))] += 1
    return by_arm, dict(pairs)


def run(output):
    panel_raw = PANEL.read_bytes()
    expected = PANEL.with_suffix('.sha256').read_text().split()[0]
    if sha(panel_raw) != expected:
        raise ValueError('Historical pattern panel changed after freeze')
    panel = read(PANEL)
    if panel.get('schema') != 'mplpb-historical-patterns-v1':
        raise ValueError('Unknown pattern panel schema')
    groups = panel['groups']
    if len({group['id'] for group in groups}) != len(groups):
        raise ValueError('Duplicate question group')
    output.mkdir(parents=True, exist_ok=False)
    rows, packets, seals = [], [], {}
    for family, (path, seal_name) in FAMILIES.items():
        corpus = ROOT / path
        seal = frozen(corpus, seal_name)
        parents = {row['id'] for row in read(corpus / 'questions.json')['cases']}
        seals[family] = {'seal_sha256': sha((corpus / seal_name).read_bytes()), 'files': seal['files']}
        with TemporaryDirectory(prefix='mplpb-historical-patterns-') as temporary:
            ledger = Path(temporary) / 'ledger'
            save(output / (family + '-import-receipt.json'), import_corpus(corpus, ledger))
            start = file_pins(ledger)
            bodies = {record.id: body_text(record.body_html) for record in Ledger(ledger).servable()}
            for group in groups:
                if group['corpus'] != family:
                    continue
                if group['parent'] not in parents or not all(
                    anchor_matches(a, a['source_id'], bodies[a['source_id']]) for a in group['anchors']
                ):
                    raise ValueError('Question group lost its source-bound reference: ' + group['id'])
                quote = group['anchors'][0]['quote']
                questions = {'quote': f'Which source contains the exact words "{quote}"?', **group['questions']}
                for arm in ARMS:
                    question = questions[arm]
                    answer = answer_query(ledger, question, PROFILES['internal'], mode='strict',
                                          max_passages=12, max_chars=8000).contract
                    probe = (PassageIndex(ledger, question, PROFILES['internal']).retrieve(
                        [question], max_passages=12, max_chars=8000)
                        if arm in ('direct', 'paraphrase') else {'passages': []})
                    row = {'id': group['id'] + '-' + arm, 'group': group['id'],
                           'pattern': group['pattern'], 'parent_case': group['parent'],
                           'arm': arm, 'question': question, **measured(group, arm, answer, probe)}
                    rows.append(row)
                    packets.append({'id': row['id'], 'answer': answer, 'passage_probe': probe})
            if start != file_pins(ledger):
                raise ValueError('Native queries changed the imported ledger')
        frozen(corpus, seal_name)
    if len(rows) != len(groups) * len(ARMS):
        raise ValueError('One or more groups used an unknown corpus')
    by_arm, pairs = compare(rows)
    report = {'schema': 'mplpb-historical-pattern-report-v1', 'groups': len(groups),
              'questions': len(rows), 'panel_sha256': expected, 'original_seals': seals,
              'revision': (subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
                           if (ROOT / '.git').is_dir() else None),
              'native_sha256': code_pins(ROOT), 'by_arm': by_arm, 'paired_support': pairs,
              'independent_semantic_review': 'NOT RUN', 'cases': rows}
    save(output / 'report.json', report)
    compressed = gzip.compress(json.dumps(packets, ensure_ascii=False, sort_keys=True).encode(), mtime=0)
    (output / 'native.json.gz').write_bytes(compressed)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    report = run(parser.parse_args().output)
    print(json.dumps({name: report[name] for name in ('groups', 'questions', 'by_arm', 'paired_support')},
                     indent=2))


if __name__ == '__main__':
    main()
