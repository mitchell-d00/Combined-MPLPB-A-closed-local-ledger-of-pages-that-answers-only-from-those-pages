# Seshat, Anubis and Horus batch closed at the frozen boundary

Last reviewed: 2026-11-27.

[Scope and predeclared gates](SCOPE.md). Released reader
`a442c8f0c9629b65a3af38ba57319aa9c2af8dbe`. Frozen cumulative reader
`426791113348b259797223316f6ca2d6e6b7ccb8`, scoped runtime ZIP SHA-256
`8c767ab82c2941c8a30d63bb522da87c326e7d44cdb3f513d12aa8e553fa71b2`.
The fresh operator inputs were published at `55fea85035ea1b51cb45b5441b3ecb76568b0adf`
after pinning and hashing the native packages. Keys remain separately held.

| First fresh results | Cases / distinct questions per reader | Released complete | Candidate complete | Useful partials | Expected withholds on both | Unsupported claims | Lost valid answers | Execution failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Seshat | 6 / 4 | 0/3 | 3/3 | 0 | 3/3 | 0 | 0 | 0 |
| Anubis | 6 / 3 | 0/3 | 3/3 | 0 | 3/3 | 0 | 0 | 0 |
| Horus | 6 / 5 | 0/3 | 3/3 | 0 | 3/3 | 0 | 0 | 0 |

Each set had three released target misses and zero candidate misses. Both
readers ran the same three fresh sets once, with no intervening repairs.
All 36 fresh executions completed under the existing isolated runner. All
nine required target witnesses were found by discovery on both readers.
Discovery and Strict Ask were scored separately. Controls include matched
questions intentionally reused with a changed source or eligibility state.

Development ordered Seshat, Anubis, then Horus. The released reader found
all nine target witnesses and completed none of those targets. Seshat
first recovered 3/3, then Anubis recovered 3/3 with Seshat retained.
Horus first recovered 2/3. The permission request with subject before
modal missed in interpretation. The first score is retained. After the
development-only permission repair, each set scored 3/3 supported and
3/3 withheld on the cumulative pin.

| Set | Added rule | Limit retained |
|---|---|---|
| Seshat | An object request naming the reporter and embedded writer reaches the existing verifier. The one eligible exact report supplies the object and any independently printed recorder label remains a separate source role. | Withhold when the role fails, the quote is nested in another context, the source is ineligible or more than one object remains. |
| Anubis | Explicit report questions bind outer and embedded negation independently. The existing witness must match both polarities. | A denial of speaking is not a claim about the embedded action. Withhold on missing or opposite polarity. |
| Horus | An explicit leading or trailing condition is bound separately to a named instruction or intention. A bounded embedded condition-of-permission question reaches the existing policy check. | Keep the exact condition and selected modality. An instruction, intention or permission does not establish action or fulfillment. |

The changes add bounded interpretation. They make no measured consolidation
claim. Other report predicates, indirect attribution, compound requests and
general permission or modality inference remain outside this evaluation.

## Preservation and release

- [Public capability gate](public-capability-gate.json) 52/52, zero false-supported bridges.
- [BB receipt](bb-receipt.json) 900/900 exact positive contracts and eligible citations, 200/200 exact withholds.
- [Public preservation](public-preservation-832.json) 832/832 exact contracts, zero execution failures.
- [Unchanged exact retained replay](retained-exact-96.json) 87/96. All 96 executed. All 46 previously claim-bearing contracts matched. Nine existing abstentions changed only their diagnostic. [Per-case readback](retained-exact-diagnostic-readback.json) preserves the failed exact comparator and each changed code.

**Release held.** The exact retained comparison remains failed. The
protected answer outcomes were preserved, and no prior abstention became
supported. The nine cases previously stopped at interpretation and now
stop in named report or condition proof. Spot checks of P02-A and P03-A
on their original inputs locate whole-body exclusion from the existing
fictional-title context guard. That guard remains in force. Changing
diagnostics is separate from recovering those earlier target cases.
An automatic review rejected a proposed modification to the release
preservation workflow and its acceptance logic. The original check was
then run without modification and remains the release hold. A later
decision on the nine diagnostic differences should freeze a prospective
contract and retain this failed exact check. This batch is closed.
Main and the live deployment remain at the released Thoth pin.

The first GitHub CLI artifact download failed at the signed storage
redirect. The same artifact was recovered through the connector and its
SHA-256 matched. No reader execution was repeated for that transport retry.

Preparation and scoring were same-operator. Worker receives synthetic inputs
and budgets only. Independent preparation/blinding, independent historical
and semantic adjudication, outside scoring, native OOCC and human onboarding
remain NOT_RUN. Original 17 private checks are incomplete, original 100 held
cases stay NOT_RUN, and recovery remains INTERRUPTED / UNRECOVERED.
The pre-existing Git-history publication incident remains separately open.

## Retained artifacts

- [Released development](released-development.zip) and [Seshat stage](seshat-development.zip).
- [Anubis stage](anubis-development.zip) and [first Horus stage](horus-first-development.zip).
- [Final development](cumulative-development.zip) and [first fresh readings](fresh-first.zip).
- [Archive digests](ARCHIVES.sha256). Scores live in the three set directories.
