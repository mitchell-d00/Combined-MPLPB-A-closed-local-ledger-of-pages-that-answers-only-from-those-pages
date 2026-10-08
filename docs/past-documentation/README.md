# Past documentation

This folder preserves the state before the provenance gate was added on 2026-10-08. It keeps the earlier rule and recorded failures reviewable rather than rewriting them around the new behavior.

The [2026-10-08 archive](2026-10-08-before-provenance-gate/) contains the upstream README, original single-owner reader and CLI, and the preceding topic test kit README, specification, manifest, corpus lock, and results. The complete original topic kit ZIP is retained as `original-topic-test-kit.zip`. Its [manifest](2026-10-08-before-provenance-gate/manifest.json) records byte hashes and the upstream commit.

| Stage | Recorded behavior and evidence |
|---|---|
| Upstream Combined MPLPB | One owner returns; multiple owners refuse; no owner refuses. 122 tests at the recorded commit |
| Six-topic HTML kit | RPG history, fossils, animals, dinosaurs, OpenAI history, computing history. Thirty pages, ninety controlled probes; 72 correct, 12 wrong returns, 6 missed paraphrases. Synthetic, author-written tests |
| Provenance gate addition | Separate lexical source records with provenance; original reader preserved. Twenty-nine added gate tests; total 151. See the current specification rather than attributing these behaviors to older papers |

The supplied earlier code archive reported 106 tests. That is a different version from the 122-test upstream checkout. Supplied papers are preserved separately under [papers](../../papers/README.md); their original version claims have not been updated to describe the gate.
