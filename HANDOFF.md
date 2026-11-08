# Repository handoff

Last reviewed: 2026-11-08.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `94249884391442bc6b05f51f27640249d77d73df` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `b4bf80024b59c1b80fe33ce740d314954814748b1dfdace4d6d044543f086399`.

## Latest user update instructions

Feature completeness for intended scope

Production readiness and Ai as middleman user between mplpb and user I’d like Ai to be able to use it as easy as humans ,

Selected connection: Local MCP connection for AI clients

## Implemented scope

- Add a local MCP stdio interface to the full existing native App: policy/status, collection discovery, paginated source inspection, strict questions, saved conversations and session recovery.
- Keep host-fixed collection/profile scope, original engine evidence and uncertainty, source integrity, ancestry, delivery restrictions and no source-fact writes or network acquisition. Native authorized collections retain capture verification and normal derived-cache rebuilding.
- Add explicit message/source/output/storage budgets, staged chat saves and exclusive conversation-namespace locking; test actual SDK/subprocess integration, source revisions and clarification recovery.
- Publish setup, production-readiness boundaries, machine discovery, test/result coverage and repository-owned handoff instructions. Preserve all original reports, sources, questions and labels.

## Validation recorded

- Inspected baseline main acf7800a5f8320ec29ee957d002eaaba8ed4e816. Before changes, 18 focused agent/procedure/polarity tests and real-engine JavaScript API checks passed. Baseline Pages build/deploy/postdeploy check succeeded in Actions run 41502464401.
- 31 authored MCP tests passed, including actual stdio subprocesses, scoped profile/sessions, source/metadata near misses, positive/negative contradiction, revised/withdrawn/tampered sources, capture integrity, process-lock rejection, bounded failure rollback and procedure corrections after reconnect.
- Official MCP Python SDK 1.26.0 completed 45 protocol/workflow checks, including process restart, exact source hash inspection, qualifying procedure evidence, contradictions, changed values and justified refusal. Reports pin tested adapter/client bytes; no external AI model or independent human validation is claimed.
- Documentation inventory, infrastructure synchronization and handoff checks passed. Compared 1425 protected baseline files against original Git blob contents with no changes, including every preexisting evaluation artifact and answer/conversation module. Extracted candidate and final PR/deployment checks remain separate and are not yet certified by this source record.
- Frozen committed candidate 94249884391442bc6b05f51f27640249d77d73df, ZIP SHA-256 9dde3d5ea06f3e3ef4b461f3ed239a40e2fb3c5d174d3abc85445a98236d6873, passes 46 combined focused tests, 45 official SDK checks, real-engine JavaScript API, documentation, infrastructure and handoff checks from extracted bytes. See evaluation/mcp-agent/extracted-zip.json. The full local suite is running separately; this source record does not assert its result.

## Limitations and blocked checks

- The declared scope is a local trusted operator and capable stdio MCP client. This is not a remotely hosted MCP/HTTP service or an OS sandbox, and it does not authenticate users or isolate shared-service tenants.
- The adapter does not provide source management, acquisition, ratification, arbitrary procedural prose understanding or access to another browser’s IndexedDB. Existing source-language limits remain.
- A third-party AI may still invent text or use unrelated tools; this connection cannot enforce model obedience or certify cloud-provider privacy. No independent human usability or answer-quality result is claimed.
- Linux/Python 3.12 and the official SDK protocol client are tested; individual AI applications, Windows/macOS behavior, hard CPU deadlines and deployment-specific recovery/monitoring remain unverified.

## Next steps

- Read docs/MCP_AGENT.md; configure absolute Python/server/data paths and explicitly authorize source keys or leaf ledgers under the intended host delivery profile.
- Local focused/SDK/static/history/committed-extracted-ZIP checks are complete. Inspect exact-head required PR/archive/browser results before merge, then keep postdeployment verification separate.
- For future changes, replace this update record from the latest instructions, maintain the documentation/result index, stage intended files and regenerate/check the handoff.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
