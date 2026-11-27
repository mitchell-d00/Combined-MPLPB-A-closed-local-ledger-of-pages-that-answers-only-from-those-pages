# PR #110 diagnostic compatibility proposal v1

Last reviewed: 2026-11-27.

**Proposed and inactive.** [Versioned exception manifest](diagnostic-compatibility-proposal-v1.json)
SHA-256 `22868e9f9604a4c3fee87226eecc7ef2aa5d5bdb1982eaa3c47e176b5d7ae97a`.
The [original exact run](retained-exact-96.json) remains failed at 87/96.
The candidate and raw artifacts retain their original bytes. The
[verification receipt](diagnostic-compatibility-verification-v1.json)
rechecked all 96 retained before and after pairs, both reader runtime ZIPs,
runtime files, case registries and raw result hashes. This is a retrospective
readback. The prospective acceptance result is NOT_RUN.

| Required move from `interpretation_unsupported` | Exact IDs |
|---|---|
| `reported_object_unresolved` | C3-REPL-P02-A, P02-B, X01-A, X01-B, X03-A, X03-B |
| `requested_source_condition_unresolved` | C3-REPL-P03-A, X04-A, X05-A |

All nine are abstentions with zero claims and false answer support in both
arms. Only the top-level `diagnostic` object changes after the existing
recursive code-fingerprint normalization. All other fields are identical.
The manifest binds the exact complete diagnostic objects as well as the
remaining-field fingerprints. The roster hash covers all 96 case and arm
memberships. Unlisted cases require complete normalized equality. Missing,
duplicate, unrecognized and failed executions reject. Seventy-two readback
probes on copies rejected extra cases, changed codes or diagnostic details,
changed verdicts, added claims and changes outside the diagnostic.

The new interpretation reaches an object or condition proof check, which
withholds without an eligible proof. Earlier cases with a positive expectation
remain misses. These transitions recover zero answers.

## Repository consumer impact

- **Strict Ask and APIs.** The refusal kind, support flag, claims, exact
  source and retrieval fields remain identical. The diagnostic code, category,
  stage, message and suggestions are externally observable. The category
  moves from `unsupported_question_grammar` to `insufficient_evidence`.
  Integrations that filter exactly by the old code or category would see
  different refusal telemetry. External clients were not exercised.
- **Browser and native presentation.** Browser copy omits the unsupported
  grammar hint and renders the evidence diagnostic. The presentation judge
  omits its `proof_rule_missing` warning, records `bounded_records` as the
  stopping stage and suggests inspecting evidence. Work-router explanations
  shift to insufficient evidence and omit grammar-specific classing help.
  Direct helper probes on all nine retained pairs verified the display stays
  a refusal with zero claims. The JavaScript probe exercised the renderer's
  code path without launching a browser.
- **Existing tools and fixtures.** `current_failure_inventory.py` and
  `evaluate_user_collections.py` can classify the same refusal under proof
  or unresolved evidence when their own discovery and expectation checks
  permit. `analyze_failure_inventory.py` asserts the old exact code in
  another pinned report cohort. Some Python tests explicitly require that
  code on their own fixtures. These historical assertions and tool behavior
  remain in place. Exact comparison or external code-based telemetry can
  detect the change.

## Activation and acceptance

Mitchell must explicitly approve v1 **at the manifest SHA-256 above** for
these 96 retained case-and-arm memberships on the exact reader pair. Freeze
the approval and policy first. The separate prospective result must reject
anything beyond the nine pinned transitions. Recheck applicable release
requirements on the exact candidate before deciding on merge and deployment.
Preserve the original strict failure alongside any later result. The current
release gate and workflow are unchanged.

The prior PR head's documentation failures identified two unclassified
existing freeze metadata files, `candidate-pin.txt` and `phase.txt`. This
proposal registers them by their original SHA-256 without editing them.
