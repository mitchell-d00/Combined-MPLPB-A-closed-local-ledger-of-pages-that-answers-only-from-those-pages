# Apollo-01 receipt provenance through the local bridge

Last reviewed: 2026-11-28.

The released Heka bridge has no producer signature input. That capability
starts as unimplemented. The lab adapter uses Node's standard Ed25519 API
and the unchanged Hermes lab seam. Keep the Heka comparison, reader,
controller, and reservation code intact. The preserved networked component
attests served pages with RFC 8032 Ed25519. Its pure Python implementation
is explicitly unaudited and not constant-time. Apollo uses the standard
runtime verifier for its distinct receipt scope.

Freeze exact input and key digests, the trust table, baseline and scorer before
execution or implementation. Packet generation is deterministic. Lab keypairs
are independently random Ed25519 fixtures. The public keys and fingerprints
are frozen. Only the active producer at the frozen trust snapshot may pass.
A retired key remains verifiable and its receipts are ineligible under that
snapshot. A known fixture outside the accepted roots remains ineligible.
There is no protocol for accepting a supplied key from receipt input.

Sign the UTF-8 JSON serialization of a fixed ordered object containing schema,
producer fingerprint and the exact Heka binding. The binding includes reader,
question, obligation, proof and source snapshot digests, action, ref, expected
and intended Git object IDs, and reservation namespace. The adapter verifies
those exact bytes against lab configuration, checks producer status, and
passes the signed binding to the unchanged comparison at the declared seam.
The host independently provides current source eligibility and authority.
Record signature validity, trust, binding check, native proof, initial and
final admission, attempts, actual Git ref/marker, and durable reservation.

Each draw has seven independent disposable repositories. A correctly signed
active-producer receipt with complete proof and a host grant must perform one
intended Git CAS and record durable completion. A changed payload breaks the
signature. Valid signatures by retired or unaccepted producers cannot proceed.
An authentic wrong-namespace or wrong-target binding fails the unchanged
comparison. A trusted producer signature over an unsupported report and a
complete signed proof without a grant each make zero attempts. A synthetic
producer must never turn an unsupported proof into a supported answer.
All withholds preserve the initial ref, marker and unused reservation.

Signatures demonstrate possession of configured fixture keys. They do not
establish truth, human identity, production authorization, a universal rotation
protocol, or cross-resource atomicity. Both draws share one operator. Fresh
changes the question layout, entities, order, and wrong-scope field while
retaining the same causal structures. Pin the lab candidate before opening
fresh, then retain each first result. Private keys stay outside Git and are
only available to the test producer. No production ingestion or dispatch.
