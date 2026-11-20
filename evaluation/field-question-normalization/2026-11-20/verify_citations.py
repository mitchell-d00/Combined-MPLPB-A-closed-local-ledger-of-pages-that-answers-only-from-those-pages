"""Read back accepted public-fixture citations; no semantic or truth adjudication."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from mplpb_combined.ledger import Ledger
from mplpb_combined.provenance_gate import gather
from mplpb_combined.reader import PROFILES, DEFAULT_PROFILE
from mplpb_answers.body_text import body_text


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases', type=Path, required=True)
    p.add_argument('--fixtures', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    checked = 0
    questions = 0
    for line in args.cases.open():
        row = json.loads(line)
        result = row['result']
        if not result['answer_supported']:
            continue
        root = args.fixtures/row['question']['record_id']
        eligible = {(s['id'], s['hash']) for s in gather(root, result['question'], PROFILES[DEFAULT_PROFILE]).sources}
        records = Ledger(root).records
        assert result['claims'], 'Accepted answer has no claims'
        for claim in result['claims']:
            assert claim['citations'], 'Accepted claim has no citations'
            for cite in claim['citations']:
                assert (cite['source_id'], cite['hash']) in eligible
                matches = [r for r in records if r.id == cite['source_id'] and r.hash_actual == cite['hash'] and r.path == cite['path']]
                assert len(matches) == 1
                text = body_text(matches[0].body_html)
                a, b = cite['body_start'], cite['body_end']
                assert type(a) is int and type(b) is int and 0 <= a < b <= len(text)
                assert text[a:b] == cite['quote'] == claim['text']
                checked += 1
        questions += 1
    report = {'accepted_questions_checked': questions, 'exact_eligible_citations_checked': checked,
              'observed_at': datetime.now(timezone.utc).isoformat(),
              'profile': DEFAULT_PROFILE, 'historical_truth_verified': False,
              'scope': 'Exact canonical quotation and fresh native eligibility at check time; not independent semantic judgment.'}
    with args.output.open('x') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
