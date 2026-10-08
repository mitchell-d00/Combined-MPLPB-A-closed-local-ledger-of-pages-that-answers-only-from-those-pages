# Provenance gate: separate local source bundles

Added 2026-10-08. The original `ask` command still applies the single-owner refusal rule. The new `gate` command implements a different, explicit contract: return all eligible lexical matches as separate source records, retaining their provenance. It does not turn multiple pages into one answer.

## Run

From the repository root, using Python 3 and the standard library:

```bash
python3 -m mplpb_combined gate examples/provenance-gate/separate "1974 dungeons and dragons budget" --json
python3 tools/provenance_bench.py --serve
python3 tools/provenance_bench.py --serve --root /absolute/path/to/your/corpus
```

Open `http://127.0.0.1:8765` for live queries. Open `examples/provenance-gate/index.html` directly for five recorded scenarios and three profiles. Offline snapshots do not accept arbitrary questions; live queries reread the corpus. The server binds to loopback and rejects unexpected hosts, cross-origin submissions, non-JSON requests, and paths outside the selected roots. It never writes to a user-selected corpus.

## The requested example

| Scenario | Result |
|---|---|
| Separate pages | Game history from the game page; general budgeting from the budget page, each with its own origin and citation |
| Budget on both | Both pages remain visible; neither wins or suppresses the other |
| Missing budget | Game context remains visible; the budget term is explicitly uncovered |
| Altered budget page | Failed hash validation excludes the page and its words |
| Supplied cost paper | Full supplied text and its derived budget excerpt are separate records, with a shared-ancestor warning |

The fixture game page mentions Dungeons & Dragons and 1974. General budget material is not evidence of the budget of that game in that year. The scenario with budget on the game page is explicitly fictional test material and contains no invented historical monetary amount. The supplied cost paper concerns MPLPB costs. Its excerpt remains about those costs.

## Selection and provenance

Tokenization, stopwords, and stemming come from the existing lexical reader. A page qualifies when at least one content term occurs in its declared scope, title, or eligible prose. Scope and prose are considered together. All qualifying pages remain; there is no majority-owner decision, semantic paraphrase retrieval, ranking, or specificity pruning. `--no-prose`, `--ignore-not-for`, and existing serving profiles make policy choices explicit.

Before delivery, the gate requires a unique page id, intact sealed hash, explicit valid origin and depth, valid hash-pinned ancestry, acceptable effective status and serving depth, and no applicable `not-for` exclusion. It rejects out-of-root HTML symlinks, indexes, pointers, retired records, invalid ancestors, cycles, missing pins, and malformed lineage. A derivative of a retired or superseded basis is withheld pending rechecking. Following a valid supersession chain is distinct from deriving from a stale basis.

Every record retains full verbatim page text, page id and relative path, title, scope, exclusions, owner declaration, timestamps, declared/effective status, hash, explicit origin and depth, pinned lineage, matching terms, and local location. The result includes excluded records with reasons, uncovered terms, a serving-policy hash, and a corpus snapshot hash. Pages sharing an ancestor are marked as dependent rather than independent corroboration.

`source_bundle` means eligible sources were found. `not_in_corpus` means none were found. CLI exit codes are 0 and 3. `lexical_coverage` reports content-word coverage only, even if all words appear on one page. It does not establish that the request was answered or that a relation among those words exists.

## Limits and falsifiers

Hashes check consistency against the recorded seals; someone able to change a page and reseal it can change those seals. Hashes and declared owners do not authenticate authorship. This gate does not verify signatures, provenance attestations, historical truth, or ratification authority. Original claim basis is not encoded by the legacy page format and is labeled accordingly. A declared human origin for an uploaded author paper remains a declaration.

Policy and corpus fingerprints expose changes; they are not signed identities or authorization controls. Delivery policy does not make private data safe to publish. There is no federation, model synthesis, image generation, or image evidence classification in this text gate. Synonyms, negation, dates, and relationships are not semantically resolved. Broad shared words can retrieve irrelevant pages; their separate delivery prevents fusion but does not fix lexical relevance.

The implementation fails its contract if an altered source passes, a provenance field is silently omitted, a matching eligible budget source disappears because another page owns the query, a stale derived basis passes without recheck, or a shared ancestor is represented as independent corroboration. Twenty-nine regression tests cover these and other gate behaviors. They are controlled fixtures, not independent validation on a new author corpus. The 122 existing tests also pass, for 151 total. Original topic probes and their failures remain archived.

See [UPLOAD_REVIEW.md](UPLOAD_REVIEW.md), [past documentation](past-documentation/README.md), and [papers](../papers/README.md).
