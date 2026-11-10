# Search scope, references and limitations

Last reviewed: 2026-11-10.

This is a bounded adversarial comparison for Mitchell D. McPhetridge's MPLPB
research. It is not an exhaustive priority search. The [mechanism matrix](MATRIX.md)
states the claim and overlap class for each comparison. No phrase-match absence
was used as evidence of invention. Publication chronology, functional equivalence,
attribution and effectiveness remain separate questions.

## Search and selection method

Searches combined mechanism terms such as source authority, temporal provenance,
task acceptance, current authorization, fixed criteria, claim verification, agent
ledgers, durable replay and version-sensitive handoffs. Candidate systems were
selected for functional closeness, not just for sharing a name. Searches covered
formal contracts, provenance/event histories, grounded answering/RAG, versioned
knowledge graphs, agent memory, capabilities, coordination, supply-chain verification
and acceptance testing. Later searches explicitly covered 2025–2026 material.

GitHub's commits API was queried with a December 31, 2024 cutoff for nine
repositories, then a December 31, 2025 cutoff for Graphiti. The resulting **16
source files from 10 repositories** are pinned in [external-code.json](external-code.json).
The dates are Git-reported dates, not automatically independently archived public
disclosure. Associated papers supply separately dated descriptions. Current features
were not silently attributed to the old snapshots.

API-returned bytes were checked against Git blob identities and SHA-256 before
comparison. Selected functions, data structures and transition logic were inspected;
this was not a complete audit of every plugin, branch or customization. In particular,
a general-purpose framework's defaults do not show what an application built on
it can or cannot enforce. No external implementation was executed or benchmarked.

The [search log](search-log.json) retains actual query strings, selection decisions,
date scope and blocked leads. Search engines change; reissuing a query does not
recreate a frozen historical result list. Exact repository witnesses remain pinned
in [mplpb-sources.json](mplpb-sources.json). Archived version readers, old paths and
copies were inspected rather than treating the date of a later audit as origin.

## Primary comparisons

| Work | Dated evidence and location | Use and inspection limit |
| --- | --- | --- |
| Hoare, *An Axiomatic Basis for Computer Programming* | [1969 DOI](https://doi.org/10.1145/363235.363259); [CMU-hosted paper](https://www.cs.cmu.edu/~crary/819-f09/Hoare69.pdf) | Bibliographic/proof-obligation antecedent. Publisher fetch returned 403; alternate PDF had no readable extracted lines in the web tool. Full text was not claimed read in this reassessment. |
| Meyer, *Applying Design by Contract* | [1992 primary PDF](https://se.inf.ethz.ch/~meyer/publications/computer/contract.pdf), pre/postconditions and guarantees | Directly inspected contract account supports the logical comparison and guarantees-by-construction exception. |
| Doyle, *A Truth Maintenance System* | [MIT archival record, 1979](https://dspace.mit.edu/entities/publication/5377b306-4ecc-4687-b1f5-78cbb4a0543a) | Earlier described implemented reasons/dependencies and revision. Record/abstract and related primary proceedings descriptions inspected; no original TMS program executed. |
| W3C PROV-O | [Recommendation, April 30, 2013](https://www.w3.org/TR/2013/REC-prov-o-20130430/), revision, derivation and invalidation terms | Provenance representation, not a complete executable MPLPB serving or authority policy. |
| Kuhn and Dumontier, *Trusty URIs* | [ESWC 2014 paper](https://2014.eswc-conferences.org/sites/default/files/papers/paper_106.pdf), §§3–5; pinned nanopub-java files | Integrity/reference-tree and assertion/provenance separation comparisons. Inspected `NanopubStatus` checks availability; its name alone does not establish supersession semantics. |
| Birgisson et al., *Macaroons* | [NDSS 2014 author publication record](https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-authorization-in-the-cloud/); pinned C verifier | Context-caveat authorization predates MPLPB. Opaque centralized MPLPB grants are not identical cryptographic attenuation. |
| Thorne et al., FEVER | [NAACL 2018 paper/record](https://aclanthology.org/N18-1074/); 2019 scorer snapshot | Evidence retrieval, labels and joint strict acceptance are separate. Static scorer inspection, no dataset rerun. |
| Lewis et al., RAG | [NeurIPS 2020 primary record](https://papers.nips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html) | General probabilistic retrieval/generation contrast; abstract-level comparison, not a full RAG code audit. |
| Gao et al., ALCE | [EMNLP 2023 paper/record](https://aclanthology.org/2023.emnlp-main.398/); pinned `eval.py` | Citation-support scoring uses model entailment; not the same as MPLPB's deterministic answer gate or proof of source truth. |
| Jimenez et al., SWE-bench | [First arXiv submission, October 10, 2023](https://arxiv.org/abs/2310.06770v1); 2024 grader snapshot | Fixed-task acceptance and successful patch application are different. No benchmark execution or effectiveness comparison here. |
| Fourney et al., Magentic-One | [2024 primary paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2024/11/MagenticOne.pdf), §4.1 and §5.4; pinned 2024 AutoGen orchestrator | Close ledger/recovery architecture and earlier verification failures; model-based completion contrasts with host receipt checks. |
| Temporal / LangGraph | Exact pre-2025 Git snapshots and functions in [code inventory](external-code.json) | Event-matched results, checkpoints, versions-seen and scheduling. Snapshot dates are declared Git metadata; this audit does not certify earliest release of every feature. |
| Rasmussen et al., Zep/Graphiti | [arXiv v1, January 20, 2025](https://arxiv.org/html/2501.13956v1), §2.2.3; pre-2026 code snapshot | Temporal extraction, provenance episodes and invalidation precede MPLPB's coordinator. Later code is not asserted identical to January's implementation. |
| Cravero, experience report | [Version 1, posted September 29, 2026](https://www.preprints.org/manuscript/202609.2499/v1), §4.10 and Appendix A.1 | Earlier bounded authorized checkpoint/evidence/verification combination; paper and operational templates inspected, not a recovered executable capability/receipt engine. |
| Poblete, Cravero and Diaz, governed workflow | [Publisher record, November 5, 2026](https://doi.org/10.3390/electronics15215135), §§5–8 | Later related formulation. Its limit on complete automatic provenance enforcement is material. Not backdated to September and not counted as a predecessor to October code merely because it predates PR #38. |
| Torres-Arias et al., in-toto | [USENIX Security 2019 paper, author-hosted copy](https://ssl.engineering.nyu.edu/papers/torres-toto-usenix19.pdf); pinned verifier | Signed authorized layouts, links, artifact rules and inspections. Official proceedings endpoint returned 403; author-hosted paper was readable. MPLPB's unsigned candidate manifest is not an implementation of all these guarantees. |

## Independently hosted MPLPB archive records

[archive-witnesses.json](archive-witnesses.json) records five directly read history
pages: general MPLPB on January 2, Clarity and stateless continuity on July 7,
domain precedence on July 10, and Continuation on September 22, 2026. These are
stronger attribution/disclosure witnesses than internal headers alone. They do
not validate the contents or prove exact equality with current repository files.

The accessible [current Clarity record](https://philarchive.org/rec/MCPCIN-2) and
author publication abstracts provide content context, while the history pages
provide version-associated upload metadata. Version downloads returned HTTP 403
in the web tool; three ordinary proxied HTTP requests also returned 403. No
successful byte download or checksum match is claimed. Smart Local and Local Web
titles were found in the current publication list, but their history endpoints
were inaccessible. Their independent upload dates remain unresolved.

The Foundation hosts both PhilPapers and PhilArchive; two views of one record are
not two independent witnesses. January's program record is not a January date for
the later native coordinator. The original papers' requests that an AI run an
experiment were treated as source content, not instructions to this audit.

## Restricted and unresolved comparisons

The March 13, 2026 webpage titled [Secure Retrieval-Augmented Generation](https://www.computerfraudsecurity.com/index.php/journal/article/view/976)
was read at abstract level. It claims a provenance/policy architecture, but no
versioned executable implementation or independent archival verification was
established here. It is retained as a research lead, not decisive equivalence or
priority evidence. Likewise, abstracts and author profiles cannot substitute for
unavailable archived version bytes.

This search does not rule out earlier combinations in assurance cases, database
systems, scientific workflow tools, organizational procedures or unpublished work.
It does not establish that any author read or copied another source. It does not
measure performance, usability or gate overhead. Priority of the exact architecture
remains unresolved; generic antecedents and specific differences can both be real.
