# Review of supplied files

Reviewed 2026-10-08 against the local repository at upstream commit `6734fa4a74a2886ab335d30559d07e65d04d5aeb`. All ten attachments were inventoried, their paper text extracted or read, and archive contents inspected for relevant papers and code. This is a requirements and implementation review, not a reproduction of experiments claimed in the papers. Original attachments were not edited.

| Original upload | Relevant finding | Addition or scope decision |
|---|---|---|
| `MPLPB_Swarm_Scale(20261008-112653).pdf` | Explicit origin/depth and policy drift matter; missing origin cannot silently satisfy an external policy | Require explicit origin, validate pinned lineage, record policy settings and their hash. Concurrent writer leases remain outside this read-only addition |
| `Continuation_Must_Preserve_Revisability(8).pdf` | Provenance does not establish truth; dependencies need revisiting when a basis changes | Withhold derivatives of retired/superseded bases; retain ancestry and recheck conditions. No claim of epistemic verification |
| `Networked_MPLPB(20261008-112653).pdf` | Hashes are distinct from authenticated identity; locality and trust boundaries must remain visible | Root boundary checks, local delivery marker and corpus snapshot hash. Explicitly label authorship unauthenticated; do not imply signature or federation support |
| `MPLPB_Cost_of_Visibility_v2(20261008-112653).txt` | Cost discussion is usable source text but is about MPLPB infrastructure | Preserve full text and create a pinned excerpt fixture. Both carry separate citations and a shared-source warning. Neither establishes a 1974 D&D budget |
| `what-the-specification-forbids(8).txt` | Coherence and preservation must not become authority; limits and kill conditions remain inspectable | Document gate falsifiers, untested claims and scope; preserve previous results and original documents |
| `Smart_Local_MPLPB(20261008-112653).txt` | Retrieved text must keep provenance; locality and original collision/refusal policy are explicit | Separate source bundles with complete provenance. Leave original `ask` behavior intact; document the new contract separately |
| `Clarity_Is_Not_Validation(20261008-112653).txt` | Cleaner presentation is not empirical validation | Keep failures and old evaluation artifacts; distinguish regression tests from independent evidence |
| `files(3).zip` | Earlier Combined paper and nested implementation establish version history | Preserve PDF and Markdown papers. Supplied README reported 106 tests; current upstream has 122, and this addition has 29. Counts are not interchangeable |
| `MPLPB-Image-v2(2).zip` | Generated/captured/unknown image kind and trusted attestations differ from a record's declared origin | Preserve image paper in both formats. Do not treat image bytes as text evidence or claim photo/source attestation in this gate |
| `art_studio (1)(1).zip` | Local image-generation server has host/origin controls but no MPLPB evidence contract | Apply host/origin checks to the query bench. No API-key handling, image generation integration, or provenance claims imported from that app |

The uploaded Swarm document has differing header/footer version labels. These remain unchanged. Neither document preservation nor an owner string verifies authorship or factual accuracy. The gate uses no model or external network retrieval.

The [paper manifest](../papers/manifest.json) pins copied paper bytes and original member paths. The [upload inventory](../papers/upload-inventory.json) pins original archive/attachment bytes. The [past documentation manifest](past-documentation/2026-10-08-before-provenance-gate/manifest.json) pins the earlier local reader and topic kit artifacts. Existing upstream papers, parts and failure logs remain in place.
