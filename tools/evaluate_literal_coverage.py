"""Re-score the already inspected external excerpt as DEVELOPMENT material.

Do not overwrite historical SQuAD labels or the archived before/after report.
External authors wrote the questions, but this subset has been inspected to
develop the literal extension. New independent validation remains necessary.
"""
import argparse
import json
import tempfile
from pathlib import Path

from mplpb_answers.support import supported_answer
from mplpb_combined.ledger import write

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "evaluation/reliability/squad-sample.json"


def run():
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    rows = []
    for case in sample["cases"]:
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, doc_id="EXT-0001", title=case["title"],
                  scope=case["title"], body=case["context"],
                  when="2026-01-01T00:00Z")
            result = supported_answer(tmp, case["question"])
            answers = {item["text"].casefold() for item in case["answers"]}
            correct_return = (not case["unanswerable"] and result.kind == "return"
                              and any(value in result.text.casefold()
                                      for value in answers))
            rows.append({
                "id": case["id"], "question": case["question"],
                "expected": "not_in_corpus" if case["unanswerable"] else "return",
                "kind": result.kind, "return_correct": correct_return,
                "evidence_spans": result.support.get("spans", []),
                "source_id": result.record.id if result.record else None,
                "candidate_count": len(result.candidates),
            })
    true_answerable = sum(row["expected"] == "return" for row in rows)
    true_negative = sum(row["expected"] == "not_in_corpus" for row in rows)
    right_answer = sum(row["return_correct"] for row in rows)
    false_positive = sum(row["kind"] == "return" and not row["return_correct"] for row in rows)
    correctly_refused = sum(row["expected"] == "not_in_corpus"
                            and row["kind"] != "return" for row in rows)
    return {
        "protocol": "inspected-squad-excerpt-development-only",
        "claim": "Neither independent nor held-out system validation",
        "sample_size": len(rows), "answerable": true_answerable,
        "answered_correctly": right_answer,
        "answerable_coverage": right_answer / true_answerable if true_answerable else None,
        "unanswerable": true_negative, "correctly_non_returned": correctly_refused,
        "wrong_returns": false_positive, "rows": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="Optional output path; does not modify frozen archives.")
    args = parser.parse_args()
    report = run()
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: val for key, val in report.items() if key != "rows"}, indent=2))
