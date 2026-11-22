"""Test an explicitly named summary section as a separate discovery hint."""
import argparse
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory

from mplpb_answers.body_text import body_text
from mplpb_answers.passages import PassageIndex
from mplpb_answers.synonym_graph import build, open_index
from mplpb_combined.reader import PROFILES
from tools.sorter_first_study import FAMILIES, ROOT
from tools.unprepared_challenge import frozen, read, save, sha
from tools.unprepared_sources import import_corpus
from test_tools.historical_patterns import PANEL, anchor_matches

CATALOG = ROOT / 'evaluation/historical-synonym-graph/catalog.json'
NUMBERED_SECTION = r'[ \t]*(?:[1-9][0-9]?|I)\.[ \t]*0[ \t]*'
HEADING = re.compile(r'^' + NUMBERED_SECTION + r'\n(?:[ \t]*\n)*[ \t]*SUMMARY[ \t]*\n'
                     r'(?:[ \t]*\n)*(?P<first>[^\n]+)', re.M | re.I)
NEXT_SECTION = re.compile(r'^' + NUMBERED_SECTION + r'\n(?:[ \t]*\n)*[ \t]*[A-Z][A-Z \t]+$', re.M)
SUMMARY_LIMIT = 2400


def summary_span(body):
    """Require a unique numbered heading followed by a substantive prose line."""
    heads = [match for match in HEADING.finditer(body)
             if len(re.findall(r'\b[a-z]{2,}\b', match['first'])) >= 6]
    if len(heads) != 1:
        return None
    start = heads[0].start('first')
    following = NEXT_SECTION.search(body, heads[0].end())
    end = min(len(body), start + SUMMARY_LIMIT, following.start() if following else len(body))
    return start, end


def named_summary(ledger, question, graph):
    index = PassageIndex(ledger, question, PROFILES['internal'])
    ordinary = index.retrieve([question], max_passages=12, max_chars=8000)
    if not re.match(r'According to (?:the )?[^,?!;]{1,180}\bsummary,\s', question, re.I):
        return ordinary, [], 'summary_not_requested'
    hints = graph.lookup('original', question)['records']
    owners = [record for record in index.records if record.id in hints]
    if len(owners) != 1:
        return ordinary, [], 'source_not_unique'
    record = owners[0]
    span = summary_span(body_text(record.body_html))
    if span is None:
        return ordinary, [], 'summary_not_unique'
    start, end = span
    chosen, size = [], 0
    for p in index.passages:
        lo, hi = p['body_start'], p['body_start'] + len(p['text'])
        if (p['source_id'] == record.id and lo < end and hi > start
                and len(chosen) < 12 and size + len(p['text']) <= 8000):
            chosen.append(p)
            size += len(p['text'])
    return ordinary, chosen, 'summary_candidates_only'


def run(output):
    folder, seal = FAMILIES['original']
    corpus = ROOT / folder
    frozen(corpus, seal)
    if sha(PANEL.read_bytes()) != PANEL.with_suffix('.sha256').read_text().split()[0]:
        raise ValueError('Historical question panel changed')
    group = next(row for row in read(PANEL)['groups'] if row['id'] == 'apollo')
    rows = []
    with TemporaryDirectory(prefix='mplpb-section-probe-') as temp:
        root = Path(temp)
        ledger = root / 'ledger'
        import_corpus(corpus, ledger)
        build(root / 'graph.sqlite', read(CATALOG))
        with open_index(root / 'graph.sqlite') as graph:
            for arm in ('direct', 'paraphrase'):
                question = group['questions'][arm]
                ordinary, sections, status = named_summary(ledger, question, graph)
                def matches(passages):
                    return any(anchor_matches(group['anchors'][0], p['source_id'], p['text']) for p in passages)
                rows.append({'arm': arm, 'question': question, 'status': status,
                             'ordinary_anchor_visible': matches(ordinary['passages']),
                             'section_anchor_visible': matches(sections), 'section_candidates': sections})
    save(output, {'questions_sha256': sha(PANEL.read_bytes()), 'catalog_sha256': sha(CATALOG.read_bytes()),
                  'corpus_seal_sha256': sha((corpus / seal).read_bytes()), 'cases': rows})
    print(json.dumps([{k: v for k, v in row.items() if k != 'section_candidates'} for row in rows], indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output)


if __name__ == '__main__':
    main()
