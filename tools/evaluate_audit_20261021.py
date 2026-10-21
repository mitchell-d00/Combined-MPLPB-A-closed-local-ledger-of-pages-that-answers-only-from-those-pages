"""New audit development probes, separate from historical/held-out fixtures."""
import argparse
import json
import tempfile
from pathlib import Path
from mplpb_combined.ledger import write
from mplpb_answers.support import supported_answer, code_pins

CASES = Path(__file__).resolve().parents[1] / 'evaluation/audit-2026-10-21/cases.json'

def run(cases=CASES):
    rows = []
    for case in json.loads(Path(cases).read_text()):
        with tempfile.TemporaryDirectory() as root:
            for n, body in enumerate(case['bodies']):
                write(root, doc_id=f'AUD-{n+1:04}', title='Audit source',
                      scope=case['question'], body=body, when='2026-10-21T00:00Z')
            result = supported_answer(root, case['question'])
            rows.append(dict(case, actual=result.kind, text=result.text,
                             support=result.support, passed=result.kind == case['expected']))
    return dict(protocol='audit-authored development controls, not held-out validation',
                code_pins=code_pins(), total=len(rows),
                passed=sum(row['passed'] for row in rows), rows=rows)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', type=Path, default=CASES)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = run(args.cases)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f"{report['passed']}/{report['total']} audit controls passed")
    raise SystemExit(0 if report['passed'] == report['total'] else 1)
