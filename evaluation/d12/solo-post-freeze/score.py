"""Score frozen passage anchors and review the native claims from this pilot."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text):
    return " ".join(text.casefold().split())


def matches(anchor, passages):
    return any(p["source_id"] == anchor["source"] and
               normalize(anchor["quote"]) in normalize(p["text"]) for p in passages)


def score(root, run_path):
    pre_run = {path: checksum for checksum, path in
               (line.split(maxsplit=1) for line in (root / "pre-run.sha256").read_text().splitlines())}
    key_path = root / "custody/key.json"
    if sha(key_path) != pre_run["custody/key.json"]:
        raise ValueError("Answer key differs from the pre-run commitment")
    if sha(root / "inputs.sha256") != pre_run["inputs.sha256"]:
        raise ValueError("Input manifest differs from the pre-run commitment")
    for checksum, path in (line.split(maxsplit=1) for line in (root / "inputs.sha256").read_text().splitlines()):
        if sha(root / path) != checksum:
            raise ValueError(f"Input changed: {path}")
    raw = read(run_path)
    if raw["questions_sha256"] != sha(root / "inputs/questions.json"):
        raise ValueError("Raw output used different questions")
    key = {case["id"]: case for case in read(key_path)}
    if set(key) != {case["id"] for case in raw["cases"]}:
        raise ValueError("Output and answer key cases differ")
    rows = []
    for case in raw["cases"]:
        ident = case["id"]
        goal = key[ident]
        contract = case["strict"]
        if contract["answer_supported"]:
            raise ValueError(f"{ident}: a changed support outcome needs fresh citation review")
        if contract["claims"]:
            claims = contract["claims"]
            if ident != "P02-4" or len(claims) != 1 or not claims[0]["text"].startswith(
                    "Exact comparison of the two cited units.") or contract["kind"] != "partial_answer":
                raise ValueError(f"{ident}: unexpected claim content needs fresh citation review")
            # The alignment concerns draft communications and lacks the final communiqué.
            outcome = "withheld_with_nonresponsive_partial"
        else:
            outcome = "justified_withholding" if goal["family"] == "missing" else "missed_answer"
        rows.append({"id": ident, "family": goal["family"], "strict": outcome,
                     "diagnostic": contract["diagnostic"]["code"],
                     "anchor_count": len(goal["anchors"]),
                     "anchor_matches": {arm: sum(matches(anchor, passages) for anchor in goal["anchors"])
                                        for arm, passages in case["discovery"].items()}})
    answerable = [row for row in rows if row["family"] != "missing"]
    discovery = {arm: {"all_anchor_cases": sum(r["anchor_matches"][arm] == r["anchor_count"] for r in rows),
                      "all_anchor_answerable_cases": sum(r["anchor_matches"][arm] == r["anchor_count"] for r in answerable),
                      "total_anchor_matches": sum(r["anchor_matches"][arm] for r in rows)}
                 for arm in rows[0]["anchor_matches"]}
    return {"engine": raw["engine"], "cases": len(rows), "answerable": len(answerable),
            "expected_withholding": len(rows) - len(answerable),
            "anchors": sum(r["anchor_count"] for r in rows),
            "strict_outcomes": dict(Counter(r["strict"] for r in rows)),
            "diagnostics": dict(Counter(r["diagnostic"] for r in rows)),
            "unsupported_supported_answer_assertions": 0,
            "discovery": discovery, "cases_with_sorter_candidates": sum(bool(r["sorter_source_candidates"]) for r in raw["cases"]),
            "advanced_routes": dict(Counter((r["advanced"]["inspection"] or {}).get("path", "none") for r in raw["cases"])),
            "lookup": dict(Counter(r["lookup"]["kind"] for r in raw["cases"])),
            "investigation_verified_observations": sum(len(r["investigation"]["verification"]["verified"]) for r in raw["cases"]),
            "investigation_traversed_links": sum(link["status"] == "traversed"
                    for r in raw["cases"] for link in r["investigation"]["relations"]),
            "assisted": dict(Counter(r["assisted_unconfigured"]["diagnostic"]["code"] for r in raw["cases"])),
            "operator_interventions_during_run": 0,
            "false_event_merge_rate": None,
            "rows": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--raw", type=Path)
    args = parser.parse_args()
    print(json.dumps(score(args.bundle, args.raw or args.bundle / "raw/run.json"), indent=2))
