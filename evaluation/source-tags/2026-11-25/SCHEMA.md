# Source-linked proposals, version1

Last reviewed: 2026-11-25.

This experimental native inspection API checks report-content proposals that the
ordinary reader already supports. It does not add ordinary-language coverage or
participate in normal answering. Import it explicitly:

```python
from mplpb_answers.source_tags import verify_proposals
result = verify_proposals(collection_root, full_question, packet, profile)
```

The [valid frozen example](development/inputs/ST-D-001/tags.json) contains a
document root, a complete statement and person/object children. Relationships
link those children to the reporter, attributed author and object. Other frozen
examples deliberately contain invalid annotations.

`source` pins the record ID, path, sealed content hash and admitted body-HTML
SHA-256. Each non-root node has canonical `body_start`/`body_end`, exact `quote`,
and `original_start_byte`/`original_end_byte`. The original-byte coordinate space
is **UTF-8 of the admitted record's body_html**, including its generated title;
it is not the full HTML-file byte space or a pre-import document byte space.
Use the existing source-roundtrip receipts when a separate original import must
be resolved. No raw-original alignment is inferred from a tag.

Containment must agree in both canonical and original coordinates; IDs must be
unique and parents acyclic. A governing statement must match the complete native
citation. Person/object links must select the exact literal roles of the native
proposition, preserving reporter, printed writer, embedded actor, negation,
conditions and reporting layer. Full native query verification independently
includes eligible counterevidence and checks final source state. Tags do not
rewrite questions or resolve incomplete obligations.

The API returns an inspection certificate only after a unique complete native
source-scoped answer. It rejects unsupported and partial goals, unavailable or
withdrawn records, stale pins, wrong roles, pruned context, policy fields and
budget excess. Ordinary answers and useful native partials stay unchanged.
`authoritative: false` means the tree does not become a ledger source or host
authorization. Accepted relations repeat checked native propositions/citations;
node classifications and historical truth remain unverified.

Imported private/public labels cannot set permissions. Host profiles and source
eligibility govern access. Famous, date-role and inferred-identity annotations
are outside this first schema; they remain unverified. A reported instruction
does not gain execution evidence through this API.

Native limits remain eight records,200,000 scanned canonical characters,1,000
units,twelve passages,8,000 context/output characters and existing phrase limits.
Additional proposal limits are64KBJSON,64nodes and twelve nonduplicate relations.
The isolated worker also retains30CPU seconds,45wall seconds,2GBaddress space,
8MBfile output and256MBscratch. These metadata limits do not expand native proof.

Same-operator tests are not independent historical or semantic adjudication.
