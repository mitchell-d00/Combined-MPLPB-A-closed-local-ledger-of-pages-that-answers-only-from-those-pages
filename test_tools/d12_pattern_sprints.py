"""Replay the original nine coordinator questions with their exact excerpts."""
import argparse
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from mplpb_answers.body_text import body_text
from mplpb_answers.passages import PassageIndex
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import write
from mplpb_combined.reader import PROFILES


def run(inputs):
    profile = PROFILES['internal']
    results = []
    for case in json.loads(inputs):
        with TemporaryDirectory(prefix='mplpb-d12-packet-') as ledger:
            sources = {}
            for number, (locator, excerpt) in enumerate(case['pages'], 1):
                record = write(ledger, doc_id=f'{case["id"]}-EXCERPT-{number}', title=locator,
                               scope='Supplied documentary excerpt', body_html='<pre>' + escape(excerpt) + '</pre>',
                               when='2026-11-23')
                if body_text(record.body_html) != excerpt.replace('\n\n', '\n'):
                    raise ValueError(f'Excerpt projection changed for {record.id}')
                sources[record.id] = locator

            question = case['question']
            native = answer_query(ledger, question, profile, mode='strict').contract
            probe = PassageIndex(ledger, question, profile).retrieve([question], max_passages=12, max_chars=8000)
            results.append({'id': case['id'], 'sources': sources, 'native': native, 'separate_passage_probe': probe})

    return {
        'input_sha256': sha256(inputs).hexdigest(),
        'rows': [{
            'id': row['id'], 'kind': row['native']['kind'], 'diagnostic': row['native']['diagnostic'],
            'text': row['native']['text'], 'claims': row['native']['claims'], 'missing': row['native']['missing'],
            'source_locators': row['sources'],
            'probe_quotes': [p['text'] for p in row['separate_passage_probe']['passages']],
        } for row in results],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    fixture = Path(__file__).resolve().parents[1] / 'evaluation/d12/pattern-sprints/original-questions.json'
    parser.add_argument('--input', type=Path, default=fixture)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    report = run(args.input.read_bytes())
    with args.output.open('x') as output:
        json.dump(report, output, ensure_ascii=False, indent=2)
        output.write('\n')
    for row in report['rows']:
        print(row['id'], row['kind'], row['diagnostic']['code'])


if __name__ == '__main__':
    main()
