# Production threat model

Status: engineering threat model, not a penetration-test report or certification.
Scope: Python reader and local UI, static WebAssembly site, browser persistence,
and optional separately deployed crawler. The supported deployment assumption is
one trusted operator per local instance/browser profile. Public multi-tenant
service operation is not approved by this document.

## Assets and trust boundaries

Protect source bytes and revision history, collection separation, profile delivery
restrictions, conversation privacy, crawler secrets/quota, and accurate attribution.
Trusted components are the deployed program, operator-approved configuration, and
host/browser security. Source HTML, declarations, questions, user notes, model
outputs, network responses, and imported archives are untrusted data. Source
publishers and users can be mistaken or actively malicious. A compromised build,
operator, browser extension or host is outside the current integrity guarantee.

| Threat / attacker capability | Existing boundary | Residual risk and production requirement |
|---|---|---|
| Publisher stuffs scope with query words or supplies irrelevant prose | Lexical ownership and not-for checks | The UI answer path now adds finite statement support; raw reader/legacy CLI remain candidate retrieval. Unknown grammar abstains, but zero observed false returns does not prove general entailment. Require human review for consequential use. |
| Publisher seals false, outdated or contradictory material | Hash/revision checks and ambiguity handling | Hashes prove matching bytes, not truth, author identity or freshness. Require trusted ingestion, review dates and explicit provenance. |
| User or source embeds instructions to cross collection boundaries | Conversation authority labels; gated reader | Labels are not access control. Regression-test source/user/assistant separation. Do not allow imported instructions to alter executable code or delivery profiles. |
| Malicious HTML/import or persistent chat payload | Existing rendering and capture paths | Require maintained escaping/sanitization and browser CSP review; tests are not a complete XSS audit. Treat origin compromise as loss of all browser data. |
| Network attacker or hostile crawl destination | HTTPS, token, bounded pages/bytes, redirect/IP restrictions documented in crawler | Verify DNS/private-address handling, redirects and egress enforcement in the actual deployment. CORS is not authentication. No claim of complete SSRF prevention. |
| Quota theft or request amplification | Crawler token and bounded traversal | Token holders share quota. Add per-user quotas/rate limits, secret rotation, monitoring and an emergency disable switch before public service. |
| Another user reads session data | Browser profile/local filesystem boundary | No tenant isolation claim. Deploy authentication/authorization and separate stores before shared hosting. Never put secrets in chat or exports. |
| Huge inputs, many captures or exhausted storage | Some bounded parsing/crawling and local persistence | Bound request size, CPU/time, graph/replay growth and total storage at every public entry point; test concurrent load and eviction. |
| Malicious corpus pointer or filesystem path | Reader route limits; UI path tests | Local trusted-corpus assumption is material: review pointer target containment separately before accepting untrusted filesystem corpora. |
| Compromised dependency/build/publisher | Repository and deployment workflow | Pin/review build dependencies, protect main, restrict deployment rights and retain rollback artifacts. A regenerated hash can accompany malicious content. |

## Required release decisions

Local research/demo use can proceed with the limitations above. Internet-facing
shared service use requires an owner to verify authentication, tenant isolation,
resource budgets, egress/SSRF defenses, sanitization/CSP, backup/restore, secret
rotation and incident response. These are deployment gates, not assertions that
all controls already exist. High-stakes automated decisions are outside scope.

On suspected compromise: disable crawling/public writes, revoke crawler tokens,
preserve logs without publishing private transcripts, identify the affected build
and corpus hashes, restore a reviewed release, and notify affected operators.
Do not silently reseal questionable evidence. Retest the original exploit before
re-enabling access. Threat-model changes accompany new execution capabilities,
remote storage, authentication, model integration or autonomous code adaptation.


## Statement-support release boundary

The 600-case development diagnostic records zero wrong returns on the new gated
path and zero false refusals after grammar fixes on the same development set. It is not independent testing. Gate status and exact
supporting spans are returned in `answer_support`; `candidate_only` indicates
inspection, never a supported factual answer. The underlying sealed ledger, pins
and legacy candidate API are unchanged. Deployments must route factual requests
through the gate rather than directly calling the old reader. Other specialized
summary, quote and structured-relation paths retain their own contracts; this
release does not certify every chat utterance or sentence against this suite.
