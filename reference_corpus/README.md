# MPLPB Reference Corpus — machine-derived research preview

**Status:** versioned, offline-generatable release candidate. **Not human-ratified, not certified authoritative, and not available to the default `internal` or `external` delivery profiles.** Its existing `lab` profile (maximum origin depth 2) is required. Original machine-origin source citation records have depth 1, and derived fact records have depth 2. The existing engine, finite grammar, and profiles remain unchanged.

## Contents, frozen questions, and staged growth

The [catalog](catalog.v1.json) contains **73 narrowly scoped source-derived descriptions** across basic English grammar/WordNet-style lexical structure, NIST SI quantities, NOAA/USGS Earth systems, NASA solar-system structure, and National Archives civic history. Each fact has its own exact `scope`, precise `when-to-use`, stable ID and single body statement `The SUBJECT is VALUE.`. Neither page title nor scope is answer evidence.

The [93-question fixture](probes.v1.json) has 73 declared positives and 20 missing-information controls. These probes were authored by the developer, **not independent human participants or a blind holdout**. The nine pre-release gold-quotation corrections are fully traceable: [original snapshot](probes.v1.pre-amendment.json) and [amendment log](PROBE_AMENDMENTS.md). After admission, no release artifact is silently overwritten.

| Release | Added facts | Total fact pages | Focus | Acceptance target (not independently verified) |
|---|---:|---:|---|---:|
| v0.0.0 | 0 | 0 | empty baseline | 0/73 |
| v0.1.0 | 23 | 23 | grammar and lexical categories | 23/73 |
| v0.2.0 | 25 | 48 | SI, weather and water-cycle concepts | 48/73 |
| v0.3.0 | 25 | 73 | planets and founding documents | 73/73 |

Each version is built as an **independent, never-overwritten sealed ledger snapshot**. The audit records per-question response, exact supporting record ID/hash, pinned lineage, negative refusals, wrong returns, new ambiguities and specific refusal→supported transitions. This progression is the acceptance target; CI must establish the actual figures. No metric is inferred from raw page count.

## Attribution versus fact certification

Primary references include [Purdue OWL](https://owl.purdue.edu/owl/general_writing/mechanics/parts_of_speech_overview.html), [Open English WordNet](https://en-word.net/), [NIST SI Units](https://www.nist.gov/pml/owm/metric-si/si-units), [USGS Water Cycle](https://www.usgs.gov/special-topics/water-science-school/water-cycle), [NOAA weather/climate](https://www.noaa.gov/explainers/what-s-difference-between-climate-and-weather), [NASA planets](https://science.nasa.gov/solar-system/planets/), and the [National Archives Bill of Rights](https://www.archives.gov/founding-docs/bill-of-rights/what-does-it-say) and [Declaration](https://www.archives.gov/milestone-documents/declaration-of-independence). The [catalog](catalog.v1.json) supplies per-claim publisher, URL, topic anchor and domain.

Each `SRC-XXXX` **machine-origin source citation record** is a sealed local attribution, **not** an authenticated publisher-owned source snapshot. Each `REF-XXXX` fact is a separate sealed, machine-derived record with `derived-from` pinning the actual local source-record hash. Source bytes are **not** pinned or independently authenticated; neither the hash nor the trusted website name establishes the correctness of an authored paraphrase. Facts have no human ratification or external-serving rights. The `SRC` records are non-answer provenance infrastructure and are not counted as knowledge fact pages.

A human claiming authority must deliberately review the original external citation, the paraphrase, scope and qualifiers and then issue a named ratification under the existing ledger ratify/revise contract. A machine never labels itself ratified; an unreviewed collection is available only for research and testing in `lab`. Do not silently promote the proposed corpus to default search, ship it as a publisher-signed dataset, or equate developer-scored synthetic tests with independent answer quality.

## Admission and invariants

`python -m tools.build_reference_corpus --output NEW_EMPTY_DIRECTORY` uses the original `mplpb_combined.ledger.write` and `mplpb_answers.support.supported_answer` unchanged; it introduces **no new runtime dependency**. It validates:
- Allowed HTTPS source hosts, complete publisher/anchor citations, unique source IDs and presence of a local citation record
- Page IDs, exact non-overlapping scopes, unique declared question forms, grammar-eligible body assertions and rejection of speculative/conditional values
- Intact SHA-256 seals, valid `derived-from` hashes, machine origin and depth 2, proper current status and external exclusion
- Positive, negative, ambiguity and wrong-return outcomes at each release stage, with per-case source IDs and hash pins
- Pre-release gold amendments against immutable original fixture and explicit hashes for every release run
- Failed or repeat builds do not rewrite existing files

The deliberately **synthetic** competing-owner test is run in a separate temporary copy, producing ambiguity without adding contradiction to the released scope-unique corpus. Mutation and revision tests verify that damaged source content is withheld and a valid replacement creates a new ID, pins the predecessor and preserves retired history. The original `6/59` pottery result and later `12/59` graph development result remain unaffected.

## Reproduce locally, use via existing API

```sh
python -m unittest tests.test_reference_corpus -v
python -m tools.build_reference_corpus --output /tmp/mplpb-reference-release-new
# Use an EMPTY path each time; do not overwrite snapshots.
python -m mplpb_answers ask /tmp/mplpb-reference-release-new/v0.3.0/ledger "What is noun?" --profile lab
```

The generated `release-audit.json` and version-specific `audit.json` are exact-case artifacts; CI retains them with each proposed revision. The generated corpus is **not automatically loaded** into a visitor's browser or into shipped default collections. A developer may explicitly copy/import a tested ledger and query it through the existing `window.MPLPB.query(question, {corpus, profile:'lab'})` or local CLI. `ok:true` means the API request completed, **not** that support is verified; inspect `reader.kind`, `reader.answer_support`, record ID, hash and `derived_from`.

Repository infrastructure—including root `index.html`, standalone HTML builder, JavaScript API contract, docs, archive-first workflow and reference-corpus audit—must pass the [automated infrastructure synchronization gate](../docs/REPOSITORY_INFRASTRUCTURE.md) on each PR, main-branch change and scheduled weekly check.

## Limitations and next increments

This is **73 bounded, machine-derived claims**, not a comprehensive reference encyclopedia. Narrow scopes are deliberately disjoint; an intentionally contested question belongs in a separate ambiguity test with two eligible owners, not a merged page. Follow-on content can draw from the already pinned Open English WordNet JSON and carefully reviewed public-domain or licensed facts, but those data need their own byte-level source provenance, attribution, license review, lexical-sense disambiguation and dedicated held-out evaluation. The corpus itself does not expand the reader grammar or automatically discover correct facts.