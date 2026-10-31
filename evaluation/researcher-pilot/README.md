# Synthetic researcher pilot

Six fictional independent researchers execute complete native application journeys
across history, archives, software, library policy, community policy and collections.
The personas are scripts, not AI agents or recruited humans. The application,
loopback HTTP requests, CLI subprocesses, source inspection, SQLite work records,
disk saves, fresh interpreter recovery and deliberate fault checks are real.

Run from the source checkout:

```sh
python -m tools.evaluate_researcher_pilot --output /tmp/new-researcher-pilot.json
python -m unittest tests.test_researcher_pilot -v
```

Use a writable directory on your system. Existing reports are never overwritten.
`journeys.json.sha256` freezes all persona/source/question/expectation bytes.
Only source text and questions reach the application. Gold quotations and expected
outcomes are used solely by the outer scorer. These are developer-inspected
development controls, deliberately including easy finite-grammar questions and
known limitations. Do not interpret their scores as representative research accuracy.

## Complete native journeys

Each researcher:

1. Creates a collection and imports two inline documents through real HTTP routes.
   Pasted text retains unknown authorship and is never described as a download.
2. Asks four frozen questions: definition, year, source-authored conditions, and an
   absent founder. Independently measures passage retrieval and answer construction.
3. Opens each answer's source through the native inspection service; verifies
   source ID/hash and exact canonical body offsets. Compares the strict CLI payload
   with the application payload in a separate subprocess.
4. Imports a conflicting bulletin and confirms no single year is returned.
5. Saves a multi-sentence note containing the unresolved issue and failed route.
6. Records pinned findings, an actual unsuccessful single-year determination,
   challenge, decision and action proposals in the native specialist store. Ends
   the first instance and grants a distinct successor; the old capability fails.
7. Reopens the saved investigation in a fresh interpreter. Verifies exact transcript
   continuity, notes, contested claim, failed attempt, and current permission to
   inspect sources while the dependent publication proposal remains blocked.
8. Restores a quiescent copy of application files in a second location and fresh
   interpreter. This is **test infrastructure**, not a new backup product feature;
   it does not establish portable specialist-store relocation.
9. Damages the saved session and a captured source in turn. Confirms explicit
   rejection, preserves damaged session bytes, then restores original fixture bytes.

“Tomorrow” means process interruption/replacement. No calendar-day soak, power-loss,
OS sandbox, provider autonomy, or long-duration storage behavior is inferred.
The fresh process uses the same code version: this is not a schema upgrade test.

## Browser journey

`tools/browser_researcher_pilot.py` is called by the existing candidate and
postdeployment Chromium smoke. One persona creates a collection and pastes text
through visible controls, asks, clicks the cited source, encounters a reader
limitation and conflicting bulletin, saves a multi-sentence note, reloads the real
engine from IndexedDB, and rechecks the disagreement. This is one actual browser
script, not six browser participants or a synthetic DOM test.

The normal browser smoke accepts `--npc-report NEW.json`. A report is written only
after the smoke completes; failed CI logs/artifacts remain investigation evidence.
All browser state is in disposable contexts. No real user's collections are touched.

## Observed baseline and repair

The initial six full runs found a real product defect: `remember` followed by
multiple sentences was split into independent clauses, then clarified rather than
saved. All six note-recovery checks failed. The baseline summary preserves those
failures and the original full-run digest in `strict-baseline.json`.

The repair routes an explicit `remember ` command as a single literal, bounded
working-note payload. Embedded commands, punctuation and negation are stored as
data. The note receives user-declaration authority, never source authority, and
requires no source read. Existing length limits and atomic session-save behavior
remain in force. Regression tests cover embedded search/forget/load commands,
literal echo, restart, overlength rejection and unchanged history after failure.

After repair the six native workflows pass their 108 checks. Across the 24 scored
questions, the strict reader returns 12 exact-gold answers from 18 answerable
questions (66.7% coverage), with six unnecessary refusals and no wrong returns
under this narrow literal oracle. All 18 gold passages are retrieved, exposing an
interpretation gap rather than hiding it as retrieval failure. Six additional
conflict queries are recorded as journey events and checked separately; they are
not part of the 24-question denominator. The original pottery scores are unchanged.

The final full native run is retained in `strict-after.json`; each event, response,
citation check, retrieval result and workflow check is inspectable. Reports include
suite/code pins, a run digest and measured native query/recovery timings. Timing
does not measure human effort. Failed journeys remain in the answerable denominator
and receive no success credit; the remaining personas continue and the CLI exits 1.

## Optional live reader

```sh
python -m tools.evaluate_researcher_pilot --reader-model YOUR_INSTALLED_MODEL --output /tmp/new-assisted-pilot.json
```

The native host must already have a trusted local inference service and installed
model. No weights are downloaded. Assisted output is always ungraded for semantic
correctness by this harness, even when it quotes a gold passage. It contributes
neither a correct-answer claim nor a wrong-answer claim until human review. Use
the separate packaged general-answer evaluator for pinned human grading and
release-risk thresholds. This pilot does not turn its observed strict 66.7% into
an assisted-reader performance claim. No live model was available for the retained
strict reports.

## Seven product goals: what these runs establish

| Goal | Exercised now | Still needed |
| --- | --- | --- |
| One researcher and job | Six fictional personas follow a frozen research workflow | Real audience selection and user interviews |
| Easy import, answer, inspect, resume | Native HTTP/CLI runs; actual candidate Chromium script | Human task-completion time and onboarding observation; broader file formats |
| Useful uncertainty | Refusal diagnostics, source conflicts, failure retention | Reliable missing-evidence versus reader-limit distinction and actionable product controls |
| Better language coverage | Retrieval and answering scored separately; known misses retained | Live-model runs, independent questions and human semantic grading |
| Visible continuity | Real structured work handoff and permission checks | Dedicated investigation overview UI; browser specialist-work support |
| Everyday reliability | Reload, fresh process, fixture copy recovery, corrupted saves/source rejection | User-facing portable backup/restore, installation usability, schema upgrade and long-term retention tests |
| Private pilot | Scripted native/browser journeys and reproducible logs | Actual consenting participants; synthetic personas do not measure satisfaction or replace people |

Both PR and extracted-ZIP workflows run the native pilot and retain reports.
The candidate Chromium gate includes the visible-control journey. Pages builds
retain a native pilot report with installation artifacts; the existing postdeploy
Chromium smoke runs the browser journey against the updated public site.

Synthetic checks can establish repeatable behaviors and reveal defects. They
cannot certify product readiness, independent accuracy, or that people find an
interface effortless. Those remain explicit gaps, not simulated successes.
