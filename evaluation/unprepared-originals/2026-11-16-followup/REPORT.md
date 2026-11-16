# Reducing false relationships while retaining useful ones — 2026-11-16

The engineering priority is fewer false relationships without discarding useful correct ones. This iteration improves that tradeoff in source-linked developer assessment. It does **not** establish reliable general historical reconstruction. Independent human review remains **NOT RUN**.

## What changed and why

Starting code: `ee9975a9c6d3a6413a9295763e7cbea068195f17`. The [13-span diagnosis](missing-13-diagnosis.json) found ranking/navigation/context-budget failures, not lost imports. Several relevant passages ranked 18–63; others were outside the first 64. Generic context expansion consumed almost all 12,000 characters before reaching them. Query-facet retrieval now separates document discovery from the requested subject, uses source headings only for discovery, retains declared transcript appearances and reduces navigation dominance. Eligibility, exact-field unranked routing, restrictions, hashes, origin/depth and supersession remain governing.

The first source-proposition prototype (`6499338f00377181a8ffc169b9977d4be31841e1`) exposed genuine interpretation errors even though software regressions passed: Order/title nouns became actions; Union cause and well-received were misread; jurisdictional nouns became actors; shared website templates became proposed historical connections. All failures are retained. [The launch metadata correction](execution-metadata-correction.json) documents a mistyped descriptive commit label, `8ae`; actual executed native hashes bind those unchanged outputs to the stated intermediate commit.

The final native revision is `01f128bc6022ff64c2edf5c363f05f173ac95972`. It rejects common nominal/adjectival matches, respects source HTML paragraphs/site chrome, distinguishes reporting speech from instructions, leaves uncertain/passive roles unresolved and proposes bounded actor-continuity and decision-to-planned-action links. Full source quotations and qualification language stay attached. Every connection remains `answer_supported=false` and `content_truth_verified=false`. No inferred event identity, causality, correction or receipt becomes source authority.

## Actual semantic assessment

All proposed actor/action/modality associations and typed textual connections from the unfamiliar sets were inspected against their original source-linked quotes by Codex, the developer. These are **developer/AI judgments**, not independent human review or authenticated historical truth. Every label, rationale, mistake and unresolved case is public. Correct means a source-consistent candidate association within this finite scope.

| Evaluated code/set | Correct | Incorrect | Unresolved | Irrelevant | Distinct proposals |
|---|---:|---:|---:|---:|---:|
| First prototype, reused unfamiliar records | 15 | 38 | 17 | 8 | 78 |
| Corrected code, same records | 18 | 1 | 37 | 0 | 56 |
| First prototype, cold transfer | 3 | 14 | 1 | 0 | 18 |
| Corrected code, cold transfer | 3 | 0 | 6 | 0 | 9 |

Useful correct proposals rise from **15 to 18**, while incorrect proposals fall from **38 to 1** in the reused unfamiliar-source set. Unresolved proposals increase from **17 to 37**. This is an explicit coverage/uncertainty tradeoff, not unconditional success. The final code retains a known error: United States is assigned an appointing action whose subject is the District. [Final assessment](final-developer-assessment-v2.json) retains that wrong proposal and its evidence.

Examples of useful candidate reconstruction: Roosevelt appoints Eisenhower; Eisenhower decides to proceed without proving a completed operation; he scribbled is tentatively connected to Eisenhower in the same paragraph; Hayden is tentatively connected to writing, supplying photographs and lobbying; the Secretary’s discretionary permission remains distinct from completed leases. These are interpretable, source-linked propositions and connections, not just passage matches. Their semantic status stays unverified.

The original [80-proposal review](intermediate-developer-assessment.json) remains unchanged. Version 2 analysis applies semantic-unit deduplication to both implementations: question-scoped proposition IDs no longer multiply one connection, and reversed directionless pairs collapse. The same correctness judgments are retained. This post-run analytical refinement is disclosed rather than presented as a preregistered independent metric. [Comparable intermediate score](intermediate-semantic-score-v2.json), [final score](final-semantic-score-v2.json).

## Unfamiliar originals and cold transfer

Three separately frozen NARA records cover the Order of the Day, Yellowstone legislation and the Emancipation Proclamation, followed by a separate constitutional repeal/scope record. Their ordinary prose was not rewritten into Event-ID/Related/Corrects fields. Exact original bytes, rights notice, hashes, generic import wrappers, frozen questions/rules and prior outputs are in [unfamiliar](unfamiliar/) and [legal-transfer](legal-transfer/). Published transcriptions and modern archival framing are retained together and distinguished where possible; no autograph authentication is claimed.

A further [Executive Order 8802 record](cold-transfer/) was acquired **after the final native code was committed**. Prior/final executions used the same frozen record, questions, budget and evaluator, with no parser changes after seeing its output. This is a cold transfer check for the code changes, not independent human blinding: Codex read the source and authored the questions. Both versions retain 3 source-consistent proposals; incorrect proposals fall from 14 to 0. Six final proposals remain unresolved. The final parser still misses Randolph’s called off the march response and fails to connect the complex June 25 issuance clause fully to Roosevelt. No zero-error generalization claim follows.

[Finite reference-facet assessment](reference-facet-assessment.json): **23 matched, 13 partial, 2 missing**, across 38 post-run developer-atomized facets from the unchanged pre-run expectations. Partial is not success. Missing examples include the Order of the Day’s distribution relationship and Randolph’s response. This is not complete historical recall or independent gold accuracy.

All fourteen unfamiliar/transfer questions still receive native strict refusals. Developer review finds refusal justified for the three prespecified causal/individual-finding negatives (U08, L03, T03); this is **3/3 scoped negative controls**, not overall answer accuracy. The remaining eleven refusals include answerable source facets and incomplete reconstruction. Receiving a complaint never proves its truth; normative committee duties do not prove completed enforcement.

## Frozen original historical questions

All 14 final questions completed within the unchanged 180-second budget. Draft-reference coverage improves from **10/23 to 18/23**. Eight of the original thirteen missing spans are recovered; [five remain](remaining-missed-draft-spans.json). The original questions, references, source corpus and scoring rules are unchanged. Native supported answers remain **0/14**. Coverage is against incomplete developer references, not historical relationship accuracy.

Remaining misses occur in H06, H10, H11, H12 and H14. In particular, an opening paragraph of the final Declaration cannot establish whole-document absence, and background excerpts do not themselves prove a requested causal link or personal authorization. Those limitations do not excuse the retrieval misses; the frozen score still counts them. The larger original 14-question proposal set has mechanical evidence auditing but no exhaustive semantic review; its overall relationship error rate remains unknown.

## Processing costs and authority regressions

| Execution | Cases completed | CPU s | Worker wall s | Peak RSS MiB | Logical native HTML read GB |
|---|---:|---:|---:|---:|---:|
| historical_prior | 14/14 | 869.15 | 870.11 | 40.60 | 9.413 |
| historical_intermediate | 14/14 | 932.49 | 933.49 | 47.16 | 9.453 |
| historical_final | 14/14 | 970.04 | 971.42 | 48.04 | 9.453 |
| unfamiliar_prior | 8/8 | 50.23 | 50.34 | 19.63 | 0.187 |
| unfamiliar_final | 8/8 | 63.96 | 64.16 | 20.26 | 0.188 |
| legal-transfer_prior | 3/3 | 7.40 | 7.41 | 19.51 | 0.019 |
| legal-transfer_final | 3/3 | 8.23 | 8.24 | 20.13 | 0.019 |
| cold-transfer_prior | 3/3 | 5.08 | 5.08 | 19.75 | 0.011 |
| cold-transfer_final | 3/3 | 5.11 | 5.11 | 19.76 | 0.011 |

CPU/wall/RSS and repeated logical reads are actual measurements. Logical reads are not physical disk I/O. Source import and parent-launch costs are in receipts; concurrent testing can affect wall times. Compute price, human labeling/correction/review/adjudication time and engineering model costs are unknown. Runtime model/API calls are absent; zero API charges are not zero computation. No efficiency improvement is claimed.

The final full regression suite passed **1003 tests**; [receipt/log](final-full-regression.json). The intermediate suite passed 1000 despite its semantic failures, demonstrating that test counts are not reconstruction evidence. Existing tests are unchanged. New controls cover actual correspondence requests, passive legal scope, nominal/adjectival errors, candidate antecedents, corrupted/stale evidence and permission boundaries. The public prepared suite passed **52/52** and the separate published synthetic controls passed **24/24**; neither is independent historical validation.

Every proposed proposition/connection/scope object was checked for current source/policy state, native pins, exact canonical quote coordinates, digest and non-authoritative flags. See each study’s final-evidence-audit.json and [the historical audit](historical-final-evidence-audit.json). Mechanical fidelity is separate from semantic correctness. Final native code passed the archive-first, regression/browser, isolation, infrastructure and handoff CI checks on commit 01f128b; subsequent evidence-only publication commits have their own CI status. No deployment is claimed.

## Reproduce and review

See [the operational guide](../../../docs/PROSE_RECONSTRUCTION_FOLLOWUP.md) for frozen run commands. Existing results refuse overwrite. Use exact implementation commits and the same frozen evaluator/importer and 180-second question budget. `tools/prose_quality_study.py inventory --version 2` generates comparable proposal units; `score` binds all developer judgments to the exact inventory/evidence. `tools/audit_prose_study.py` checks every rich mapping’s mechanical evidence. Independent-review packets contain complete outputs, source projections and blank submissions in each study directory. They remain **NOT RUN**; no reviewer identities, signatures or durations are invented.

The next research question is whether correct useful associations survive broader independent source/question selection while unresolved and false proposals remain manageable. Current evidence supports bounded assistance with source reconstruction, not autonomous historical understanding.
