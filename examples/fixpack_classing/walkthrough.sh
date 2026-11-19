#!/usr/bin/env bash
# Run from the repository root after applying the patches:
#   bash /path/to/mplpb-fixpack/examples/walkthrough.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"
cp -r "$HERE/demo_dump" "$WORK/dump"
echo "== 1. Ask with no ledger yet: unofficial answer + classing help"
python -m mplpb_work.answer_router ask "How many barrels did SHIP-7 carry?" --dump "$WORK/dump" || true
echo; echo "== 2. Propose drafts and decisions"
python -m mplpb_work.classing propose "$WORK/dump" --auto-accept-clean --output "$WORK/review.json"
echo; echo "== 3. A person reviews (scripted stand-in)"
python "$HERE/apply_reviewer_choices.py" "$WORK/review.json" "$WORK/review-reviewed.json"
python -m mplpb_work.classing status "$WORK/review-reviewed.json"
echo; echo "== 4. Build, rehearsed and validated"
python -m mplpb_work.classing build "$WORK/review-reviewed.json" --dump "$WORK/dump" --ledger "$WORK/ledger" \
  --ratify-by "Demo Reviewer" --receipt "$WORK/receipt.json" > /dev/null
python -m mplpb_combined validate "$WORK/ledger"
echo; echo "== 5. Ask again"
for q in "What is the from for record SHIP-7?" "Who sent SHIP-7?" "What is the cargo for record SHIP-7?" \
         "How many bales were shipped in Letter No. 41?" "What are the freight rates for flour?"; do
  echo "----"; python -m mplpb_work.answer_router ask "$q" --ledger "$WORK/ledger" --dump "$WORK/dump" || true
done
echo "----"; python -m mplpb_work.answer_router ask "What is the from for record SHIP-7?" --ledger "$WORK/ledger" --profile external || true
echo; echo "work folder: $WORK"
