# FRUS-Proposition

Last reviewed: 2026-11-24.

This replay pins `623f3c4abb38499020df193b037d303d3a329a7f` and the
same eight ordered cases from FRUS-Boundary. The [freeze receipt](freeze.json)
binds the original packet seal, evaluator key digest, previous evaluation
and [candidate rule](candidate-rule.md). The operator used the original
rendered FRUS documents, questions, source order, internal profile and
budgets. The verifier ran separately after the Strict Ask worker. The
assessor used only exact source locations for kernel proposals and kept
expected outcomes and the key in evaluator custody. The worker reported
`os_isolated: false`.

| Case | Discovery before → after | Strict Ask before → after | Proposition admission result |
|---|---|---|---|
| PE-01 | 2/2 → 2/2 | Abstain → abstain, answerable miss | The bounded assertion forms admit neither the address’s evaluative assessment nor the article’s forecast with its author and prospective scope. |
| PE-02 | 2/2 → 2/2 | Abstain → abstain, answerable miss | The intent and task clauses fit neither assertion form. Existing extraction emits no letter-instruction proposal to bind the two letter roles. |
| PE-03 | 2/2 → 2/2 | Abstain → abstain, answerable miss | The sentence stating a need lacks an in-unit named speaker. The required reporter-to-speaker attachment and the separate conditional address recommendation produce no certificate. |
| PE-04 | 2/2 → 2/2 | Abstain → abstain, answerable miss | Named advice and the reported first-person presentation fit neither native assertion form. The verifier produces no certificate preserving their distinct roles. |
| PE-01 control | — | Correct withhold → correct withhold | No witness establishes abolition or links an abolition to the address. |
| PE-02 control | — | Correct withhold → correct withhold | No witness establishes a concluded agreement or its proposed cause. |
| PE-03 control | — | Correct withhold → correct withhold | No witness establishes creation of a consultation body or its proposed cause. |
| PE-04 control | — | Correct withhold → correct withhold | No witness establishes removal of trade barriers or its proposed link. |

Discovery found both anchors in **4/4 → 4/4**. Strict Ask completed
**0/4 → 0/4** and returned **0 → 0** partials. All four controls correctly
withheld in both runs. No false-supported bridge occurred.

Each anchor belonged to one complete native source unit. For every pair
the evaluator proposed the two known native assertion kinds on the two
exact units. All **16** proposals returned
`assertion_grammar_or_context_unresolved`. Those source units also returned
no candidate relation from the action or relationship syntax checks.
No letter-instruction proposal covered either letter in PE-02. The
kernel independently reopened current eligible sources, completed all
four rereads and hit no scan limit. The largest reread used **50,502
characters and 359 units**, under the existing **200,000-character and
1,000-unit** limits. Every reread sent four proposals under the existing
12-proposal cap. Discovery results and kernel diagnostics are separate
measurements. [Proposition readback](proposition.json)

Withhold if the exact witness cannot produce a native certificate for
the requested relation with its speaker, reporting layers and modality.
Keep one certified proposition as a checked partial when available.
Complete a comparison only with both certificates and separate evidence
for any additionally claimed chronology or cause. The four positives
still lack both certificates and retain their answerable labels. This
cycle applies that boundary to the existing verifier.

## Replay

Extract [the same operator packet](operator-packet.tar.gz) and use the
previously pinned local captures or [restore instructions](../focus-extend/README.md#replay)
for the two permission-reprinted pages. The [public raw receipt](native-readbacks.tar.gz)
preserves the complete receipt checksum and summarizes those two sources
without their full projections and retrieval excerpts.

```sh
EVIDENCE=evaluation/pole/open-items/frus-proposition
sha256sum -c "$EVIDENCE/evidence.sha256"
python -m tools.pole_focus_extend run-prose --packet PACKETS/prose --implementation CHECKOUT --output native.json
python -m tools.pole_frus_proposition --packet PACKETS/prose --custody PROSE_CUSTODY --rule "$EVIDENCE/candidate-rule.md" --freeze "$EVIDENCE/freeze.json" --previous evaluation/pole/open-items/frus-boundary/boundary.json --receipt native.json --output proposition.json
```

The prior artifacts and runtime modules remain byte-identical. Focus-12
and the existing scan and phrase limits remain open under their previous
accounting. Outside scoring, independent historical accuracy, independent
semantic adjudication and native OOCC remain **NOT_RUN**.

[Exact source archive validation](validation.json)
