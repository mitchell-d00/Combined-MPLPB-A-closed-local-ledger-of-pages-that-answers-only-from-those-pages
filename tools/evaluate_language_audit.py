"""Replay frozen synthetic cases; exact quote checks, not independent validation."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from mplpb_combined.ledger import write
from mplpb_answers.support import supported_answer, code_pins


def run():
    path = Path('evaluation/language-audit/fresh-synthetic.json')
    raw = path.read_bytes()
    rows = []
    for case in json.loads(raw)['cases']:
        with tempfile.TemporaryDirectory() as root:
            for i, body in enumerate(case['bodies']):
                write(root, doc_id=f'UNFAMILIAR-{i:03}', title='Local notes', scope='notes', body=body)
            a = supported_answer(root, case['question'])
            passed = a.kind == case['kind'] and (a.kind != 'return' or a.text == case['quote'])
            rows.append(dict(case=case, passed=passed, observed=a.to_dict(), text=a.text))
    return dict(revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                code_sha256=code_pins(), fixture_sha256=hashlib.sha256(raw).hexdigest(),
                role='model-authored frozen synthetic cases; not independent validation',
                passed=sum(r['passed'] for r in rows), total=len(rows), rows=rows)


if __name__ == '__main__':
    report = run()
    Path('evaluation/language-audit/fresh-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['passed'], '/', report['total'])
