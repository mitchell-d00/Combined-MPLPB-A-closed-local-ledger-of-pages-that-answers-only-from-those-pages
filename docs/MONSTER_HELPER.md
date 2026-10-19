# Monster helper and Reason Mode

Monster is the optional, renameable **presentation helper** inside the existing
MPLPB Chat screen. It does not run a model, create its own evidence, change
source ownership, relax refusals, or publish local browser data.

## Use the controls

1. Open **Chat** and expand **Monster helper settings**.
2. Rename Monster if desired (up to 32 characters). Names are display text,
   escaped by the UI and stored only in browser UI preferences.
3. Uncheck **Show helper identity** to show ordinary MPLPB chat labels instead.
4. Toggle **Reason Mode**. When on, the interface expands *Evidence and decision
   rules* below chat messages and *Reader decision trace* in the Ask screen. When
   off, those details are still available but collapsed.

These settings never alter query payloads or the behavior of the reader,
supported-answer path, chat authorities, source profiles or network permissions.
"Reason Mode" means **showing the engine's inspectable decision trace**; it does
not claim unrestricted AI reasoning or expose hidden model reasoning.

Monster's existing Chat interface can be used to ask questions, clarify topics,
inspect sources, navigate collections, or request help. Factual replies still
come from MPLPB's eligible local pages and deterministic rules.

## External AI clients

A browser-capable AI may open the hosted site and use window.MPLPB.relay() or
window.MPLPB.query() inside the loaded page, following
[JAVASCRIPT-API.md](../JAVASCRIPT-API.md). Monster is a local UI helper, not a
remote API server or a service credential. The API remains the authoritative
route: preserve kind, answer_support, citations, provenance, and refusal
outcomes. A website URL alone does not expose another user's browser saves.

## Coverage extension

The bounded literal grammar in mplpb_answers/literal_evidence.py adds support
for explicit forms of seven request types, including abbreviation, location,
atomic number, event start, economy classification, merger, and a specified-list
complement. It is called through the same provenance gate, checks eligible page
bodies rather than scope/title strings, detects conflicting positive values,
and returns unchanged evidence sentences.

It is **not** a general semantic reasoner. Negated/hypothetical questions and
unsupported relations still abstain; hashes still check bytes, not truth.

The previously inspected 20-item SQuAD excerpt is **development material after
these changes**. Improvements measured on it must not be presented as untouched
external validation. Keep evaluation/reliability/squad-sample.json and archived
after.json intact; record new extension results separately. Evaluate against
fresh independently authored corpora and questions before production claims.

## Release safety

- Merge by reviewed pull request, not direct modification of main.
- Run the existing full Python, JavaScript API, browser transport and actual
  WebAssembly workflows.
- Compare older saved transcripts, provenance pins and browser storage behavior.
- Rebuild the standalone bundle; code hashes naturally change in new answers.
  Do **not** rewrite archived manifests to make them appear newly verified.
- Verify the new reason setting is purely visual and cannot turn candidate-only,
  ambiguous or not-in-corpus decisions into supported returns.
