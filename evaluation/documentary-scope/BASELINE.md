# Baseline inspection

Last reviewed: 2026-11-16.

Initial checkout: 38e273855e577cff038f704c63fe09b22ac6889a, clean working tree. No original files changed. Baseline archive: /tmp/mplpb-baseline. Full unittest and public-evidence commands launched before implementation changes; terminal receipts are recorded in RESULTS.md.

Architecture inspected: pipeline.answer_query delegates strict source support to the existing finite grammars, checks eligibility through provenance_gate, and rechecks source state before returning. PassageIndex reuses that gate. Documentary investigation follows explicit declared IDs through bounded specialist actions; event_candidates groups explicit identifiers only. Scoped ledger corrections remain explicit write operations. prose_evidence discovers gated contexts, prose_relations proposes fallible interpretations, and source_mapping reconstruct reloads pins/offsets/policy. Original-byte mapping lives in tools/source_roundtrip.py and the import receipt. These layers do not establish historical truth.

Frozen historical-experts records measure explicit documentary interfaces (52 public controls), not ordinary-history semantic accuracy. Existing unprepared-originals records retain 18/23 incomplete draft-span coverage and 0/14 native support. Missing causality, global priority, event identity and absent intermediates require refusal. Useful discovered passages alone cannot satisfy the strict grammar. Some fixable interpretation failures remain in candidate reports.

Direct baseline probes expose three concrete limitations: `Ruth reported that Mira sent the archive report` loses reported scope; `Mira did not write and send the archive report` marks send as source_reports_action; `If Mira wrote and sent ...` loses the condition at and. `The archive report was sent by Mira to Ruth` leaves the explicit passive agent unrepresented. These are interpretation errors even though support remains false. Tests and unchanged-original replays will measure the repair without adding answer support.

Initial frozen replays failed at bubblewrap network namespace setup (`Failed to create NETLINK_ROUTE socket: Operation not permitted`); all failed cases retained. A retry outside the outer sandbox uses the unchanged sandbox runner, rather than bypassing its isolation. Independent semantic metrics and human time remain unknown until genuine review.
