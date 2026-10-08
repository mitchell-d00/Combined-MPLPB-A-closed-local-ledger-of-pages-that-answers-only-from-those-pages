# Patch canned and local UI

Based on published main `b3de809de3c2b86168e99d090753c39bd86e71e3`.
This delivery adds a local UI and corrects the uneven-name reader failure.
It does not publish to main.

The subsequent game-style front end and its launchers are described in
[the browser UI notes](../BROWSER_UI.md). Current package total: 236 passing tests.
The verification counts below describe the first UI delivery.

## Launch

From the extracted repository folder:

```sh
python3 tools/ledger_ui.py
```

Open http://127.0.0.1:8766. No packages or account are required. Choose a corpus,
ask a question, and inspect the reader decision, separate source cards and sealed
metadata. Revision history displays the retained wiki captures, their timestamps,
source revision pins, parent links and active local head. The UI makes no live
wiki requests and does not import, edit or promote captures.

For your own local corpus:

```sh
python3 tools/ledger_ui.py --root /path/to/corpus
```

Select “Your local corpus”. The server binds only to loopback. Source bodies are
shown as text, not executed HTML. External profile restrictions apply to queries
and full-page reads. This is a local inspection interface, not a hosted service.

## Corrected rule

At the declared-scope step, find nonempty declarations whose complete term sets
are present in the question. Drop strict subsets of another fully named
declaration. If two or more remain, return ambiguity before majority ownership.
Otherwise run the existing majority, specificity and prose rules.

This reproduces the supplied uneven-title failure without live Wikipedia:

- `Phrynomedusa vanzolinii Hyundai Engineering and Construction`: ambiguous.
- Either complete title alone: its own page.
- `kiln firing` with scopes `kiln` and `kiln firing`: the specific scope leads.

The two pages in `examples/patch-canned` are sealed synthetic fixtures. Their
bodies explicitly say they are not downloaded wiki articles or verified claims.
This remains lexical retrieval. Expanding wiki metadata, paraphrase retrieval and
semantic topic detection are separate work and are not implemented here.

## Supplied files and applicable patch

`supplied/` preserves every uploaded file byte-for-byte, including the experiment
note and its reported results. Those live observations were not independently
rerun. The uploaded patch has malformed hunk counts. Applying its intended logic
also breaks the established subset-specificity test.

`reader-corrected.patch` contains the corrected reader change and six regression
tests. It applies to the base commit above. The full repository ZIP already has
it applied; do not apply it again. The patch does not include the UI.

## Verification and limits

- 234 package tests passed, including six guard tests and eight HTTP UI tests.
- JavaScript syntax checked with Node.
- All four executable legacy parts passed their tests (351 total); local-mirror
  validation and all adoption checks passed.
- Frozen studio probe files and stored results were not rewritten. All three
  probe sets were rerun; observations are in `validation/`.

| Probe set | Scoped correct | Wrong returns | Wrong refusals |
| --- | ---: | ---: | ---: |
| First, 56 probes | 50 | 0 | 6 |
| Held-out, 30 probes | 22 | 1 | 7 |
| Adjacent, 20 probes | 15 | 3 | 2 |

The guard corrects the demonstrated uneven-name case. Other lexical failures
remain; these results do not establish general wiki accuracy.

- A first full-suite run hit an example-rebuild file collision in the synced
  workspace. Generated files were restored; the complete rerun passed.
- Cloud browser preview was blocked by automatic approval review. Visual layout
  and browser interactions have not been verified in a browser. HTTP tests cover
  the real endpoints, outcomes, withholding, input rejection and source access.
- Changing the reader invalidates the engine pins of earlier wiki captures.
  Historical reports remain intact. Create a new capture using
  `python3 tools/wiki_live_eval.py run` before scoring this engine; no new live
  wiki score is claimed in this delivery.

## Walk back

For a full rollback, return to base commit `b3de809`. For the reader alone,
reverse `reader-corrected.patch`; the two-name guard and its six tests are removed.
Retained source captures and frozen probes are not changed by this delivery.
