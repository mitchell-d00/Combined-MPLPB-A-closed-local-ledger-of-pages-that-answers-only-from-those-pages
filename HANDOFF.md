# Repository handoff

Last reviewed: 2026-11-08.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `28fccbdc8c928bd87a8e3ab4791337ed9fa847e0` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `0a25b64d8572c3c6d422effcee80442a996be0199904f6c25d7abc5b5123766c`.

## Latest user update instructions

The user supplied mplpb-model-load-report.json after reporting an iPad model download completing and initialization failing. Continue investigating and repairing the actual failure. Report text: “Object has already been disposed”. [The repair objective is inferred from the attached report and ongoing debugging request.]

Persisting user constraint: “this can’t cost me anything, I build very cheap”.

## Implemented scope

- Repair a confirmed mismatch between adapter capacity and actual requested device limits. Request min(1 GiB upstream target, supported capacity) independently for allocation/binding limits, without changing other required GPU features/compute/count limits.
- Pass the same declared model-tensor minimum from loader preflight to an explicit local runtime extension; validate actual device limits before uploading parameters and retain those limits in the bounded report. Revalidate the small config/runtime HTTP resources after deployment without changing weight/cache identity.
- Preserve original vendor parts/licenses and reconstruct a versioned local runtime derivative with exact source-context matching, input/patch/output hashes and byte count. Identify that derivative explicitly in model/runtime metadata and documentation; do not silently call it unmodified upstream.
- Preserve all source-answer authority, integrity, ancestry, collection/delivery rules, frozen questions/labels and historical evaluations. Add no paid provider, training, weight changes or source/cache deletion.

## Validation recorded

- Baseline main 28fccbdc8c928bd87a8e3ab4791337ed9fa847e0 passed 873-test required regressions and public helper deployment checks. The supplied report is actual failure evidence, not independent model-quality validation. Its full private browser metadata/stack report is not published.
- Executed the actual pinned upstream negotiation function with authored adapter values matching the report: 512 MiB adapter becomes 256 MiB allocation / 128 MiB binding requests. Both are below the declared 307298304-byte tensor minimum. This establishes an undersized device configuration; it does not prove every later failure cause or total-RAM exhaustion.
- 12 actual production-function checks pass across 256/128, 384, 512, 768, 1024 and 2048 MiB capacities; they exercise clamping, unchanged other requirements, actual-device/binding near misses, invalid minima and upstream callers without a host minimum. Adapters/devices are authored stubs, not physical GPU tests.
- 13 loader/state/DOM/API cases and 33 native-engine helper checks pass. Ten focused Python asset/data tests pass, including fail-closed modified-patch and stale active-runtime-pin rejection. The actual pinned runtime API is constructed/unloaded without weights; there is no neural inference claim.
- Compared 884 protected baseline files against original Git blobs, unchanged. Focused browser/archive/required-CI/postdeployment results are retained separately and will not be claimed before completion.
- 12 actual Chromium/WebAssembly helper workflows passed for the candidate, including source/citation/conflict checks, recovery after reload, diagnostic display and physical JSON report export. Model availability is simulated as unsupported in that workflow; this is not Phi-4 inference or a physical iPad repair result.

## Limitations and blocked checks

- The patch repairs a confirmed per-buffer negotiation defect. A sufficient 512 MiB single-buffer capacity does not establish enough total device/process memory, successful full Phi-4 initialization or usable generation. Physical iPad retesting remains required.
- The reported disposed-object failure can follow GPU device loss. Its exact causal sequence is not fully captured in the supplied report; do not relabel it as proven RAM exhaustion or an independently reproduced tensor-lifetime bug.
- Tests execute actual production functions and pinned runtime code with authored resource values. They do not substitute for real-device or independent human answer-quality validation. Existing source-language limits remain.
- The static public app uses visitor hardware; no paid AI API, hosted inference/MCP service or mandatory purchase is configured. Hosting/cache/device limits remain, and no fine-tuning occurs.

## Next steps

- Freeze a committed candidate, archive/extract it, complete the required exact-head source/ZIP/SDK/WebAssembly/browser/documentation/handoff gates, then merge and verify the actual public deployment separately.
- After the patched runtime is published, reload and make one explicit model-load attempt on the iPad. The report should identify local patch webgpu-device-limits-v1 and actual negotiated limits. Confirm initialization/generation rather than treating a completed download as success; inspect any new failure evidence.
- For future updates, replace this record from the latest instructions, review affected docs/result links, stage intended files and regenerate/check the repository-owned handoff. Keep private user context out of public sources/training artifacts.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
