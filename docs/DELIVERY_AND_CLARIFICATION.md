# Sealed delivery and human clarification

The optional `external`, `source-authorship`, and `clarify-options` fields are included in a page's hash when present. Legacy pages without those fields retain their existing seals. Changing or removing an existing field breaks the seal. A deliberately resealed record is a new declaration, not authenticated authority.

Both `ask` and `gate` use the same delivery policy for `external` and customized `external*` profiles. A sealed `external=no` page is withheld; a source explicitly labeled unknown is also withheld externally. Other profile behavior is preserved. Importers write restrictions together with the page and original ledger event rather than editing sealed pages afterward. Revisions preserve them. Old imported files with previously unsealed external fields must be re-ingested or explicitly migrated before they can pass the new seal checks; do not silently reseal them as verified.

Page origin still describes the local record format's human/machine declaration. Source authorship is tracked separately as `unknown`, `declared-human`, or `declared-machine`; none is called verified. Unknown material imported by the formatter receives machine record origin and source authorship unknown. Local results explicitly say: “Who made this source is unknown. A person can supply a source attribution for review.” Providing a declaration does not authenticate identity or automatically authorize external delivery.

Broad `dog` requests offer “dogs in general”, “dog breeds”, and “dogs as companions”. These are fixed example intent choices for a person, not semantic retrieval, evidence, or a promise that a page exists. They do not alter the current return/refusal or synthesize an answer. A more specific request is evaluated normally. Other one-term requests can use author-supplied, sealed `clarify-options` separated by semicolons. The local query bench exposes the choices as buttons; CLI/JSON expose the same prompt.

```bash
python3 -m mplpb_combined ask examples/clarification-dogs "dog"
python3 -m mplpb_combined ask examples/clarification-dogs "dog breeds"
python3 -m mplpb_combined gate examples/clarification-dogs "dog" --profile external --json
python3 tools/provenance_bench.py --serve --root examples/clarification-dogs
```

The three dog pages are synthetic demonstration material with unknown authorship, not independently verified animal advice. Internal reads can expose them with that warning; external delivery withholds them. A human's clarification narrows the subject, not its truth or authorship.

Eleven new regression tests exercise both delivery paths, customized external profiles, flag alteration/removal, unknown authorship, importer log consistency, revision preservation, legacy hashes, and clarification without invented evidence. The full package passes 176 tests. Existing frozen probe/evaluation files remain unchanged. Wiki raw/live mismatch and missing historical API payload pins still prevent scoring the preserved snapshot; neither this fix nor a green unit run establishes independent validation.

The wiki engine/checker hashes are updated for these local bytes. The base commit is recorded separately from a published revision. Historical wiki manifests and uploaded reports retain their historical context. This reviewed fix is prepared for publication to main with its separate byte pins.
