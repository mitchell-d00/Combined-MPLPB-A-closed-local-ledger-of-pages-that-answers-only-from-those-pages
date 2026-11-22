"""Compare synonym lookups with strict proof for reviewed persona questions."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from mplpb_answers.pipeline import answer_query
from test_tools.persona_corpus_transfer import FIXTURES, classify, seal_collection
from test_tools.synonym_index import CATALOG, SynonymIndex

PROBES = CATALOG.with_name('synonym-probes.json')
AS_OF = '2026-11-22'


def study():
    inputs = {path.name: path.read_bytes() for path in (FIXTURES, CATALOG, PROBES)}
    catalog = SynonymIndex(json.loads(inputs[CATALOG.name]))
    probes = json.loads(inputs[PROBES.name])
    rows = []
    for collection in json.loads(inputs[FIXTURES.name])['collections']:
        ident = collection['id']
        natural = next(case for case in collection['cases'] if case['id'] == 'natural')
        with TemporaryDirectory(prefix='mplpb-synonym-study-') as ledger:
            sources = seal_collection(ledger, collection)
            for arm, question in [('original', natural['question']), ('alternative', probes[ident])]:
                hits = catalog.lookup(ident, question)
                baseline = answer_query(ledger, question, mode='strict', as_of=AS_OF).contract
                row = {'collection': ident, 'arm': arm, 'question': question,
                       'candidate': hits, 'baseline': classify(natural, baseline, sources),
                       'reviewed_proof': None}
                if hits['status'] == 'candidate':
                    # Only the preselected, authored controls exercise this
                    # handoff. Lookup alone never rewrites a user's question.
                    answer = answer_query(ledger, question, mode='strict', as_of=AS_OF,
                                          record_id=next(iter(hits['records'])),
                                          field=next(iter(hits['fields']))).contract
                    row['reviewed_proof'] = classify(natural, answer, sources)
                    row['native_verified'] = answer
                rows.append(row)
            scoped = natural['question'].rstrip('?') + ' before the earlier documented event?'
            rows.append({'collection': ident, 'arm': 'extra_obligation', 'question': scoped,
                         'candidate': catalog.lookup(ident, scoped), 'reviewed_proof': None})
    totals = {}
    for row in rows:
        tallies = totals.setdefault(row['arm'], Counter())
        tallies['lookup_' + row['candidate']['status']] += 1
        if 'baseline' in row:
            tallies['baseline_' + row['baseline']] += 1
        if row['reviewed_proof']:
            tallies['reviewed_' + row['reviewed_proof']] += 1
        else:
            tallies['proof_not_requested'] += 1
    pins = {name: sha256(raw).hexdigest() for name, raw in inputs.items()}
    return {'input_sha256': pins, 'totals': totals, 'cases': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = study()
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(result, output, ensure_ascii=False, indent=2, sort_keys=True)
        output.write('\n')
    print(json.dumps(result['totals'], indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
