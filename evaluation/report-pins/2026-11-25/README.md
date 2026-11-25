# Report-pin selection: frozen Markdown fence replay

Last reviewed: 2026-11-25.

This synthetic coordination test starts at PR #100 head
`a26ec527e2e3a5bab7883e7892aa00c348ea65dc`. It does not evaluate source support
or historical semantics. H is forty `a` characters; S is forty `b` characters.
The mocked GitHub response always has actual `head.sha = H`.

## Frozen inputs and baseline

`fixtures.json` freezes six bodies and expected report pins, match decisions,
and match/stale/missing classifications. `fixtures.sha256` seals the input
bytes before the parser change. Each fixture runs through `--al` and `--betty`:
twelve fresh processes per revision, with a thirty-second timeout per process.
The preloader replaces `fetch` entirely and asserts every request against
three exact mock endpoints; no live HTTP is used by this replay.

The baseline bridge blob is `b97f45de84f9b3b6cc4e794224473dfcec28c304`.
`baseline.json` retains complete stdout, stderr, exit codes, expected and actual
decisions. It passed 8/12, failed 4/12, and produced four false-current matches.
Both roles incorrectly accepted the example-only H and the fenced H preceding
a real stale S. The other eight decisions passed. These failures remain intact.

The initial connector capture had one added terminal newline. Its separate
`capture-attempt.json` and receipt are preserved for transparency. The baseline
above was rerun with bytes verified against the original Git blob, before
changing the parser; its decisions were identical.

| Body | Baseline (both roles) | Repaired (both roles) |
|---|---|---|
| Current H | match | match |
| Historical H | match | match |
| Stale S | stale | stale |
| No pin | missing | missing |
| Fenced H only | false current | missing |
| Fenced H before real S | false current | stale |

## General failure mechanism and repair

The old multiline regex searched all Markdown lines, allowing a code example to
become the live report pin. The repair scans lines outside fenced code blocks.
It tracks backtick or tilde delimiters and their opening lengths; a closing
delimiter must use the same character, be at least as long, and have only
trailing whitespace. Up to three leading spaces and CRLF are supported. An
unclosed fence withholds its remainder. Backtick fence info cannot contain
backticks. The first exact live `Current PR head` or legacy `Public evidence pin`
label still supplies the pin. This is a bounded metadata parser, not semantic
authentication of the report or a complete Markdown renderer.

The same sealed twelve executions pass after the repair: 12/12 expected
decisions, zero failures and zero false-current matches. The only changed
decisions are the four baseline failures. Additional JavaScript regression
controls cover tilde fences, longer delimiters, misleading shorter/different
closers, unclosed blocks and CRLF. Existing newest-PR discovery, explicit
historical override, fork handoff links and empty listing controls remain.

## Reproduce

Run from an extracted source checkout:

```sh
(cd evaluation/report-pins/2026-11-25 && sha256sum -c fixtures.sha256)
python tools/replay_report_pins.py --runtime . --fixtures evaluation/report-pins/2026-11-25/fixtures.json --output /tmp/report-pin-replay.json
node tests/javascript-api.cjs
python -m unittest tests.test_ledger_ui -q
```

The checksum file is relative to its evidence directory. To reproduce the
baseline, run the same retained replay tool against a clean checkout of the
baseline commit; the tool deliberately exits nonzero for its retained failures.
`archive-validation.json` records the exact tested candidate commit, tree,
ZIP SHA-256 and actual extracted-source check results. Subsequent evidence-only
commits do not retroactively certify another ZIP or deployed site.

The first HTTP run in a filtered checkout ran 13 tests with two failures: omitted
experiment assets and history metadata were unavailable. Its complete log is
`filtered-checkout-http.log`; no runtime change was made to hide those failures.
Restoring those tracked assets made all thirteen HTTP tests pass;
`checkout-http.log` retains that run. The full extracted-source rerun is recorded
separately in the archive receipt.

## Remaining scope and next proposal

Independent historical accuracy, independent semantic adjudication and native
OOCC remain `NOT_RUN`. This repair establishes only the synthetic metadata
decisions and the separately recorded software checks.

Mitchell relayed Al's review of PR #97 at
`7618be370c334b082cb91c50eaf665f979ce5c1e` and initially chose **Retain as the next proposal**. The latest direction
authorizes that test after this repair, with both cycles in PR #101.
The proposed next test targets only the Smith-letter PE-02 obligation, with full
canonical-body addressee, signature and instruction witnesses. The Laird `RN`
attribution stays unresolved; the target is a supported partial, not completion
or execution. Keep FRUS-D10/FRUS-D16, all eleven prior cases, six signed-instruction
controls, separately held scoring, and the unchanged 8-record/200,000-character/
1,000-unit/12-passage/8,000-output-character and phrase limits. PE-02 tests and reader changes belong to the subsequent, separately frozen
cycle. Al's reported
8/11 reproduction is relayed advice, not a new result measured by Betty.

The extracted pin archive passed 1,723 Python tests (two skipped), all 52 public
controls, the pinned WebAssembly check and the real Chromium candidate preview.
The first browser orchestration used an unsupported flag; its corrected live
run failed `ERR_CERT_AUTHORITY_INVALID` before loading the published app. Both
attempts are retained. No live-baseline or postdeployment pass is inferred.
