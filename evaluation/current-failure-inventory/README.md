# Current-reader failure inventory and frozen next proposal

Last reviewed: 2026-11-25.

**Read-only inventory; no reader repair implemented.** The attribution trial is
finished, merged in PR #102 and deployed. This report replays old synthetic cases
on merged reader `851de6c093394060ce624eb63ba72400b047a7ce`, then recommends one
next repair. Native module bytes and budgets remain unchanged.

The **605 misses are historical**, measured on reader
`2427d80e777b9cc76e071b2529e91a14b9bdb991` in the
[4,096-case study](../dpercent-known-weaknesses/2026-11-20/REPORT.md).
This inventory replays 22 of those missed positives, not all 605. It does not
extrapolate the two sampled recoveries to the **583 unreplayed historical misses**.
Focus results originally used reader `78f6a464212214a29a84f400a199be46a25db8bf`.

## Measured results

Selection was frozen before replay: the two lowest case IDs in each of 32 Known
families (64 cases), and all 32 Focus cases. Their source/question bytes and
legacy keys are unchanged. All inputs are synthetic; no omitted FRUS originals
were substituted. [Selection and source hashes](selection.json),
[per-case analysis](analysis.json), [receipt audit](audit.json).

| Set | Cases | Old complete → current | Current partial | Positive misses after partials | No-full-support controls retained |
|---|---:|---:|---:|---:|---:|
| Known sample | 64 | 10 → 12 | 2, unchanged | 18 | 32/32 |
| Focus | 32 | 0 → 0 | 2, unchanged | 10 | 20/20 |
| Fresh contrasts and matched controls | 15 | No older run → 1 | 0 | 6 | 8/8 |

Across the **111 completed current-reader executions**: 13 complete answers,
four partials, two conflicts and 92 abstentions. There are 51 positive targets
and 60 no-full-support controls. All 12 Known completions match the unchanged
authored typed/field/quotation keys; the fresh direct-writing completion matches
its authored proposition key. No negative target received a complete answer;
no invalid canonical citations were found. These are software-key checks, not
independent semantic accuracy judgments.

The two recovered completions are **DP00074 and DP00201**, both compound fields.
They were already recoverable on today's reader before this inventory. No
implementation in this branch caused those gains. The ten old valid completions
are preserved: **zero lost valid answers**. Meaning/citation views are identical
for **94/96** old cases; only those two recoveries differ. All 32 Focus discovery
packs and meaningful answer contracts are identical. Its old keyed discovery
coverage therefore remains **8/12**, inferred by comparing the identical packs
with retained original keyed scores, not by a new independent key.

All four partials preserve their actual propositions, qualifications, missing
obligations and citations. They remain incomplete; this replay does not certify
their usefulness independently. Among the 34 selected old positive misses,
today's outcomes are two completions, four partials and 28 abstentions.

## Current failure table

This table covers the old missed-positive families, rather than pooling all
negative controls into an answer score. Full discovery requires all statements
specified by the retained source key. A first stopping point is diagnostic;
it does not prove that every later proof obligation would pass after repair.

| Family / candidate operation | Selected positives | Complete | Partial | Remaining abstentions | Full keyed discovery | Observed boundary |
|---|---:|---:|---:|---:|---:|---|
| Reported statements / source voice | 5 | 0 | 0 | 5 | 5/5 | No admitted documentary goal; interpretation unsupported |
| Negated statements / polarity | 2 | 0 | 0 | 2 | 2/2 | Interpretation unsupported; denial must remain answerable |
| Instruction arrangements / modality | 2 | 0 | 0 | 2 | 2/2 | Unsupported question/arrangement; preserve conditions and execution distinction |
| Date roles / documentary references | 5 | 0 | 0 | 5 | 5/5 | No writing-date goal; distinguish writing/event date |
| Earliest observation / time role | 2 | 0 | 0 | 2 | 2/2 | Relational question/proof remains unsupported |
| Header location / documentary role | 2 | 0 | 0 | 2 | 2/2 | Header-role question/proof remains unsupported |
| Partial correction / comparison | 4 | 0 | 0 | 4 | 0/4 | Required witness discovery incomplete; proof remains unestablished |
| Wording change / multiple obligations | 4 | 0 | 4 | 0 | 4/4 | Changed wording checked; unchanged destination obligation missing |
| Identical wording / comparison | 2 | 0 | 0 | 2 | 0/2 | Required witness discovery incomplete |
| Explicit chain / document links | 4 | 0 | 0 | 4 | 0/4 | Required connecting witnesses not all discovered |
| Compound fields / multiple obligations | 2 | 2 | 0 | 0 | Not scored | Exact field set and citations now match legacy keys |

These are candidate repair families, not a claim that one implementation cause
explains every member. The full per-case record includes admitted goal types,
reference requests, native diagnostic/trace, discovered statement counts and
source-key status. Discovery misses, interpretation stops and unestablished
proof remain distinct.

## Recommended next repair: reported-content attribution

Five unchanged failures reproduce across Known and Focus:
**DP00196, DP00284, POLE-f2d6d27cee88948d-00005, -00007 and -00011**.
All five have full required discovery, empty documentary goal plans and
`interpretation_unsupported`. The instruction-attribution repair does not by
itself cover generic reports of authorship.

Recommend a shared source-scoped report-content goal and native role checker.
It must bind the named reporter, attributed author, action/object and polarity
from eligible canonical bytes. Preserve writer, reporter and quoted actor as
separate roles. A report can establish its attributed content; it cannot by
itself establish independent actual authorship. A reported denial and a denial
that reporting occurred need different polarity scopes.

Fresh contrasts retain six positive misses, including **FRESH-05**, whose broad
summary question failed to isolate this operation. It was not edited or
relabeled. Two later, separately frozen matched controls show that a direct
“Who wrote…?” question succeeds on direct authorship (**FRESH-14**) and withholds
on reported authorship (**FRESH-15**). This supports adding a source-scoped goal;
it does not justify relaxing the direct-fact checker.

The [frozen rule](proposal/rule.md), [20-case development manifest](proposal/development.json),
[additive role obligations](proposal/role-obligations.json),
[preservation suite](proposal/preservation.json), [freeze](proposal/freeze.json)
and [scoring seal](proposal/scoring-seal.json) precede any future implementation.
Ten primary targets are the five old reports and five fresh source-scoped
report/denial cases. The other retained contrasts include the broad interpretation
miss and already-valid direct control. Preserve all 111 decisions/claim views,
all 17 PE-02 contracts, all 96 consumed attribution cases and 56 targeted controls.
No next reader rule has been implemented or claimed accepted here.

**24 future transfer inputs and their key remain unopened and unexecuted**.
The [transfer seal](proposal/transfer-seal.json) binds generator, seed and packet
hashes. New source structures use postposed quoted passive authorship and passive
outer reporting; selected development uses other reporting structures. Keep the
reserved constructions out of supplemental development. The visible same-operator
generator can reproduce them, so this is procedural sealing, not independent
blinding. Open only after a future committed ZIP candidate is frozen, run once,
retain failures, and replace the packet if its failures inform a repair.
Expectations depend on actor, reporting layer and polarity; quotations and denials
are not blanket withholds. The 24 planned decisions include 12 source-scoped
positives and 12 withholds.

## Budget and custody boundaries

There were **zero reported proof-budget stops** and **five partial sorter graphs**.
Partial graphs remain a separate resource/completeness signal. Internal work and
counterevidence completeness were not comprehensively measured. The retained
per-case receipts report CPU/wall time, peak RSS and explicit original-read
calls/bytes. Do not compare speed with the older isolated runs as an engine gain.
No cap was raised: eight records, 200,000 scanned characters, 1,000 units,
12 passages, 8,000 output characters and existing phrase limits remain intact.

The unchanged `tools/pole_worker.py` used the original admission, source-state,
retrieval and native-answer adapter. Current runs used Python `-I -B`, a 30-second
CPU limit and 45-second wall limit. They were **not OS-isolated**; the older D%
driver used bwrap. Its isolation checks were not bypassed or altered. Input bytes,
ledger read-state and native module fingerprints were checked for mutation.

The first launcher attempt used a relative worker path from a temporary cwd:
96 launches failed before any native execution. Its receipt/example log are
retained. The corrected absolute-path run completed all 96. An analysis import
error was also corrected without source/key/native changes. These harness failures
are not counted as answer misses or refusals. See [harness events](harness-events.json).

One operator selected/prepared/saw/scored the public and fresh development
material and authored the future transfer templates. Keys were passed separately
from the replay worker, but this is not independent custody. **Independent
historical accuracy, semantic adjudication, preparation, blinding,
outside-custodian scoring and native OOCC remain `NOT_RUN`.** Synthetic software
progress and the prepared historical independent-review packets remain separate
milestones.

## Reproduction and attribution release receipt

`tools/current_failure_inventory.py` implements `prepare`, `run` and `summarize`.
Prepare/run require an unchanged worktree at the exact baseline commit. Use new
output directories; frozen packets and results are never overwritten. For the
published inputs:

```sh
python tools/current_failure_inventory.py run --packet evaluation/current-failure-inventory --implementation /path/to/851de6c-worktree --output /tmp/new-inventory-run
python tools/analyze_failure_inventory.py
```

The second command audits all 111 frozen input/result hashes, source-key and
preservation comparisons without rerunning native answers or opening transfer.
The per-case summaries and raw `replay/` outputs retain native claims, exact
citations, missing obligations and measurements. Replaying fresh material now is
development/preservation, not a new transfer result. The future transfer generator
is `tools/freeze_reported_content_proposal.py`; do not consume its private packet
before candidate freeze.

PR #102 publication head is `71b27255f6afc69510561f0e0fa3742ccbd8b8cf`.
Its final native source is `7ed65a589d8051ff659495972fab922ff802b20e`; the merged
tree at the inventory baseline is identical to the publication head. Exact-head
CI ZIP SHA-256:
**`54fd1d5455516814908594fe226973481d93140c11a7b3850e7d8ac32047f394`**.
[Archive-first CI](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/45621196004)
passed 1,779 Python tests (two skipped), JavaScript/HTTP/report pins, SDK/install,
WebAssembly, Chromium and helper/persistence checks. All nine publication-head
checks passed.
[Deployment](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/actions/runs/45623603579)
also passed build, deploy and live browser checks. Attribution development passed
48/48; fresh once-only same-operator transfer passed 24/24, with zero final false
support. The first transfer remains retained as consumed development because of
structural overlap with supplemental controls. No historical coverage gain was
claimed.

An extra local deployed-browser attempt timed out on a preferences reload after
the NPC journey. Its [failed log](release-receipts/attribution-postdeployment-attempt1.log)
is retained. A fresh diagnostic retry passed the complete journey and both
preferences reloads, with initial/final module hashes matching the frozen source:
[receipt](release-receipts/attribution-postdeployment-retry.json),
[log](release-receipts/attribution-postdeployment-retry.log),
[observer](release-receipts/verify_attribution_deployed_retry.py).
Receipt SHA-256: `7e79072b2b3422921d1ab2a75aeb284544507b34d52d5c32418f1c5217b951f6`.
TLS hostname/chain and curl public-key pin were verified; Chromium used only that
matching SPKI exception with `ignore_https_errors=False`. This retains the
environment trust-root limitation and does not claim default Chromium TLS trust.

Al's next judgment: does the proposed report-content operation explain the
reproduced failures while preserving independent authorship withholding and
polarity scope? Mitchell selects the next implementation cycle after that review.
