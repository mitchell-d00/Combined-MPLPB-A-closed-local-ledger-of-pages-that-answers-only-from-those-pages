# Documentary article assembly: development record

Last reviewed: 2026-11-19.

This study adds a bounded research dossier over the existing checker. It does
not add a historical proof rule, choose between competing accounts, merge
events, infer missing links or count independent witnesses. Source authority
and article assembly remain separate. See [usage and contracts](../../../docs/DOCUMENTARY_ARTICLES.md).

Baseline source: `c10a81bcc519a0208ddcc5762edda8e79ea6f9b8`, the source tree
merged in PR #54 (`3a79603e1865f1ef0a1cd1dc72bb656ba5542d8c`).
The 52 focused reconstruction/assertion baseline tests passed. The new article
test module initially failed to import because the capability did not exist;
this is a missing-feature control, not evidence of an old authority defect.

Fifteen new development controls passed in the working tree: separate checked
sections; explicit conflicting positive/negative accounts; three appearances
sharing one declared root; absent ancestry; shared roots across questions;
unchanged native qualifiers/dates; all delivery profiles; question restrictions;
missing causal bridges and actors; source changes between sections; source
corruption; admission budgets; strict plan shape; deterministic replay; and CLI.
These are fictional author-written controls, not independent historical scoring.

The full suite, public-evidence controls and unchanged-original study are in
progress at this candidate freeze. Final receipts and exact commands will be
retained here after execution. No pending test is claimed as passed.

The original-record study groups the 22 unchanged questions in source order into
plans of at most eight sections, using the same 12-passage/8,000-character native
budget. It compares entire native contracts against standalone calls, keeps
source import receipts and candidate graphs, rechecks seals, and checks ledger
immutability. It never loads expected-answer files. This is a preservation
experiment, not a key-isolated or independently judged accuracy benchmark.

The prior historical result of 2 complete answers out of 22 is not a claim of
improvement from this work. Prior D% results are unchanged retained evidence;
this addition does not rerun or supersede that benchmark.

Independent semantic review: **NOT RUN**. Hidden historical dependencies,
undocumented copying, source authenticity and general event reconstruction
remain unmeasured. Article-level support and historical truth remain false.

Reproduction:

```sh
python -m unittest tests.test_documentary_article -q
python -m unittest discover -s tests -q
python -m tools.evaluate_public_evidence --require-capabilities --output /tmp/article-public.json
python -m tools.article_study --output /tmp/new-original-article-study
```

Run against the recorded source revision in a fresh extracted archive. New study
output directories are required so prior runs cannot be overwritten. Costs
measure the entire preservation study, including standalone comparisons and
imports; they are not isolated per-query latency or an efficiency improvement.
