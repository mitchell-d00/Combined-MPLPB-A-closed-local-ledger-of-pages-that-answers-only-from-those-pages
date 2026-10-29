# Page retrieval and answer authority

[Documentation index](README.md) · [JavaScript API](../JAVASCRIPT-API.md)

The October 27 repair added provenance-gated single-owner page retrieval. It complements supported answers and the earlier separate-source gate; it does not replace their contracts. Lexical ownership can identify a useful page while its body lacks an answer to the question.

## Select the interface

| Interface | Entry point | Success kind | Meaning |
|---|---|---|---|
| Supported answer | `python -m mplpb_answers ask ROOT QUESTION`; installed `mplpb-combined ask`; JS `query` or default `relay` | `return` | Eligible body evidence matches the finite supported grammar. |
| Candidate inspection | `python -m mplpb_answers candidates`; installed `mplpb-combined candidates`; legacy `python -m mplpb_combined ask`; JS query mode `candidates` | CLI lexical `return`; UI/API may label `candidate_only` | Inspect lexical material without asserting answer support. |
| Gated page retrieval | Python `mplpb_combined.retrieval.retrieve`; JS `MPLPB.retrieve`; local transport `/api/retrieve` | `retrieved` | Exactly one selected owner passes provenance checks. Always `answer_supported:false`. |
| Separate source bundles | `python -m mplpb_combined gate`; local provenance bench | `source_bundle` | All eligible lexical matches, separately attributed; no combined answer. |

Ambiguity/refusal remain explicit. `ok:true` is a JavaScript operation envelope, not evidence authority. `/api/retrieve` is a transport operation inside the desktop server/browser bridge, not a remotely hosted HTTP API on GitHub Pages.

## Retrieve a page locally

```python
from mplpb_combined.retrieval import retrieve
from mplpb_combined.reader import PROFILES

result = retrieve(
    'examples/studio',
    'how fast should I heat raw clay on its first firing',
    PROFILES['internal'],
)
print(result['kind'], result['answer_supported'])
if result['kind'] == 'retrieved':
    print(result['reply'])
    print(result['citation'])
```

There is no dedicated `retrieve` CLI subcommand in the current parser. Use the Python function or the page-local JavaScript method:

```js
const result = await window.MPLPB.retrieve(
  'how fast should I heat raw clay on its first firing',
  {corpus: 'studio', profile: 'internal'}
);
if (!result.ok) throw new Error(result.error);
console.log(result.data.kind, result.data.answer_supported);
```

Find keys with `listCorpora()`. `retrieve` accepts `corpus` and optional `profile`; network/mode/session options are rejected. The Python question must be nonempty, at most 4,000 characters, and free of disallowed control characters.

## Selection and checks

The lexical reader retains its majority-scope and every-word prose paths, with additional bounded rules:

- The discourse wrapper “what does it mean if …” can be stripped for page lookup while preserving the complete condition, quantities, and polarity.
- When ordinary scope/prose paths find no owner, a complete multi-term `when-to-use` clause can select its declaring page. Multiple matching owners stay ambiguous; clauses from separate pages are not combined.
- Proposed owners cannot silently omit a requested term explicitly excluded by eligible pages. A legitimate owner of that term is not globally banned.

Retrieval gathers provenance diagnostics and requires the selected owner's ID, path, actual hash, and full text to match one eligible source exactly. It checks seals, explicit origin/depth, pinned current lineage, status, exclusions, delivery profile, and root boundaries. It rejects pointer-based corpus expansion and does not try a replacement owner when the selected one fails the gate.

The response includes `version:'gated-page-retrieval-v1'`, `kind`, `reply`, `decision`, `citation`, `source`, `gate`, `answer_supported:false`, and `authority:'source_page_retrieval'`. On unsuccessful retrieval, `reply` and the selected citation are empty and `source` is null. Gate diagnostics can still contain separately eligible material; they do not override refusal. Statement support is explicitly `not_evaluated`.

## Verification and limits

```sh
python -m unittest tests.test_page_retrieval -v
node tests/javascript-api.cjs
```

The 18 Python tests cover clause/polarity/quantity handling, multiple owners, exclusions, missing body support, duplicate/tampered pages, missing origin, gate rejection without replacement, stale dependencies, external withholding, symlink escape, pointers, argument validation, bridge parity, and frozen-probe score floors. These are development regressions, not new independent evaluation. [Root FIXLOG](../FIXLOG.md) records before/after measurements.

The supported-answer grammar remains separate: retrieving a page does not certify its truth, the requested relationship, permission to act, or an answer to the question. Hashes show consistency with sealed bytes, not authenticated authorship.
