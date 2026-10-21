# Deterministic generation within MPLPB boundaries

## Explicit goal

Increase expressive complexity through repeatable construction from small,
auditable rules and explicit inputs. Generative does not have to mean
nondeterministic: the goal is new combinations, not only retrieval of fixed
answers, without introducing a language model or weakening MPLPB authority.

For a fixed grammar version, exact subject and turn, the idea constructor returns
identical text and trace. End-to-end chat additionally depends on the same session,
mode, loaded corpus bytes and configured resources. Live acquisition can change
those inputs; this is not a promise that arbitrary online sessions are identical.

## Implemented increment

`tools/procedural_generation.py` composes an operation, a user topic, a lens and
an exploratory output form. Six operations × four lenses × four forms yield 96
slot combinations per topic. Three distinct operations are offered per turn;
all 96 combinations occur over 32 turns before the sequence repeats. This is a
finite variation count, not a measure of semantic creativity or usefulness.

The subject and grammar digest determine a stable SHA-256 starting offset.
Mixed-radix enumeration covers the complete product without random sampling,
clock dependence, Python hash randomization or hidden global state. Subject text
is substituted literally; it cannot add grammar rules. A different subject may
share an offset, but retains its own literal text and input digest.

Try `brainstorm lantern gardens`, then `brainstorm`. Numbered selection and
existing follow-up rules still work. Changing the topic starts its sequence at
turn one. Saved sessions retain the turn across reload; free chat remains
unsaved. Listening preference still suppresses the closing question.

Each reply carries `response_structure.construction`: grammar version and digest,
input digest, exact subject, turn, chosen slot IDs and indices, finite space size
and cycle. Replaying `construct(trace['subject'], trace['turn'])` under matching
grammar bytes reconstructs the proposals. The trace identifies construction; it
is neither a source citation nor a cryptographic proof of factual correctness.
Grammar changes require a version change; old bytes are required for old replay.

## Boundaries retained

- Imagined proposals are labeled conversation, have no evidence sources, and
  retain `factual_claims=False` and `mplpb_supported=False`.
- Generation supplies no facts, citations, page ownership or proof of completed
  procedural steps. User text and assistant output do not become ledger evidence.
- Requests still pass the existing router, language planner and final validator.
  Brainstorming does not authorize automatic source acquisition.
- The reader, source-support gate, scope isolation, ambiguous/missing-source
  outcomes, provenance pins, lineage, retirement and derivation rules are unchanged.
- Source-backed answers retain their original evidence and checks. This grammar
  operates only on explicitly exploratory brainstorming requests.

## Verification and limits

`python -m unittest tests.test_procedural_generation -q` checks the full cycle,
process-independent replay, literal slot binding, state reload and application
boundary behavior. `tools/check_browser_wasm.mjs` exercises the built standalone
bundle in Chat, Serious and free chat, including the shared validator and lack of
source/network authority. Existing evidence and conversation regressions remain
release gates.

These are developer-authored regression checks. They do not establish fluent,
unrestricted reasoning, independent factual accuracy, or that every combination
is useful. Authored constraints and richer typed compositions are future work;
adding variation must never substitute for evidence authorization.

### Release checks for this increment

The standalone HTML was rebuilt using the pinned Pyodide 314.0.7 archive and
passed the real WebAssembly harness, including generation in all three modes.
UI script, browser transport and crawler fixture checks passed. The fixed
conversation run passed 78/78 turns, and the context matrix passed 360/360 checks.
The existing hosted page was also exercised in a browser for chat and reload
persistence before updating main. These checks are bounded development evidence,
not an independent assessment of generated ideas.

## Replay scope verified 2026-10-21

The audit repeats construction across process hash seeds and serialized state.
Two separate fresh sessions given the same brainstorming request produced equal
response payloads, but different session IDs and transcript hashes. Repeatable
construction is not byte-identical observation metadata across fresh sessions;
live acquisitions also depend on retained source revisions. See
[SYSTEM_AUDIT_2026-10-21.md](SYSTEM_AUDIT_2026-10-21.md).
