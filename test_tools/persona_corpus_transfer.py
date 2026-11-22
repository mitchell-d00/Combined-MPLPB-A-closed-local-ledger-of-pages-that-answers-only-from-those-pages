"""Replay authored persona questions against isolated synthetic source collections."""
import argparse
from collections import Counter
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from mplpb_answers.body_text import body_text
from mplpb_answers.evidence_contract import pin
from mplpb_answers.pipeline import answer_query
from mplpb_combined.ledger import Ledger, write

FIXTURES = Path(__file__).resolve().parents[1] / 'evaluation/persona-corpus-transfer/panel.json'


def classify(case, answer, sources):
    if case['expected'] == 'withhold':
        if answer['answer_supported']:
            return 'unexpected_support'
        if answer['kind'] == 'partial_answer':
            return 'review_partial'
        return 'withheld'
    if not answer['answer_supported']:
        return 'review_partial' if answer['kind'] == 'partial_answer' else 'missed'
    citations = [cite for claim in answer['claims'] for cite in claim['citations']]
    for cite in citations:
        source = sources.get(cite['source_id'])
        if source is None or source.hash_actual != cite['hash']:
            return 'invalid_citation'
        body = body_text(source.body_html)
        if body[cite['body_start']:cite['body_end']] != cite['quote']:
            return 'invalid_citation'
    matched = any(cite['source_id'] == case['source'] and case['quote'] in cite['quote']
                  for cite in citations)
    if matched and answer['text'] == case['quote']:
        return 'exact_supported'
    return 'review_supported'


def run(path=FIXTURES):
    raw = Path(path).read_bytes()
    fixture = json.loads(raw)
    if fixture.get('schema') != 'mplpb-persona-transfer-v1' or fixture.get('kind') != 'synthetic_fixture':
        raise ValueError('Expected a synthetic persona transfer panel')
    results = []
    for collection in fixture['collections']:
        with TemporaryDirectory(prefix='mplpb-persona-transfer-') as ledger:
            for doc in collection['documents']:
                write(ledger, doc_id=doc['id'], title=doc['title'], scope=collection['domain'],
                      body_html='<pre>' + escape(doc['text']) + '</pre>', origin='machine',
                      source_authorship='declared-machine', when='2026-11-22T00:00:00Z')
            sources = {page.id: page for page in Ledger(ledger).servable()}
            cases = []
            for case in collection['cases']:
                answer = answer_query(ledger, case['question'], mode='strict', as_of='2026-11-22').contract
                outcome = classify(case, answer, sources)
                cases.append({'id': case['id'], 'family': case['family'], 'expected': case['expected'],
                              'outcome': outcome, 'answer': answer})
            results.append({'id': collection['id'], 'domain': collection['domain'],
                            'persona': collection['persona'], 'cases': cases})
    by_family = {}
    for collection in results:
        for case in collection['cases']:
            by_family.setdefault(case['family'], Counter())[case['outcome']] += 1
    report = {'schema': 'mplpb-persona-transfer-run-v1', 'fixture_sha256': sha256(raw).hexdigest(),
              'by_family': by_family, 'collections': results}
    report['run_sha256'] = pin(report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', type=Path, default=FIXTURES)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = run(args.fixtures)
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(report, output, indent=2, sort_keys=True, ensure_ascii=False)
        output.write('\n')
    print(json.dumps(report['by_family'], indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
