# MPLPB dispatch enforcement controls

## Claim and trust boundary

The study checks the native work coordinator at commit `6ba371ca07dd9269f28af762ed1971ad484fb6b5`. It asks whether a local fixture effect is gated across the supported Python entry point, in-process seat RPC, and the dedicated authenticated loopback HTTP route. Each case uses a fresh SQLite store, one sealed source, a host-registered fixture adapter, and a disposable file for the effect. There are no outside targets or remote effects.

The trusted host owns the adapter, database, corpus files and grant issuance. The seat is modeled as a caller of the supported interface with its own capability or without a capability. Host Python access, unrestricted filesystem access, other seats’ secrets, and direct access to a downstream service fall outside the tested boundary. The Python control calls a trusted embedding interface and exercises its seat checks. It does not establish isolation of Python callers.

## Entry-point inventory

| Surface | Route to the effect | Evidence |
| --- | --- | --- |
| Python | Calls `WorkStore.execute` directly | Nine dynamic controls |
| Seat RPC | Allowlisted `execute` delegates to `WorkStore.execute` | Nine dynamic controls |
| Dedicated loopback HTTP | `POST /api/work` passes a bearer capability to seat RPC | Nine dynamic controls |
| Stock native CLI | Requests pass through the same dispatcher, with no registered adapter in the default process | One dynamic control with a live capability |
| Host-managed investigation | Its internal fixture adapter is invoked through `WorkStore.execute` | Source trace |
| Browser and local MCP | The inspected interfaces expose reading and conversation surfaces. Dedicated work execution is a separate native service. | Source trace |

[Work API and trust model](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/6ba371ca07dd9269f28af762ed1971ad484fb6b5/docs/SPECIALIST_CONTINUITY_API.md) · [Coordinator](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/6ba371ca07dd9269f28af762ed1971ad484fb6b5/mplpb_work/store.py) · [Seat RPC](https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/6ba371ca07dd9269f28af762ed1971ad484fb6b5/mplpb_work/api.py)

## Results

**28/28 controls passed** on Linux with Python 3.12.14. The existing specialist-continuity suite also passed **48/48**.

| Scenario | Observed across the three execution surfaces |
| --- | --- |
| Authorized | One adapter call and marker line. An SQLite `start` and `finish` were appended with a passing receipt. |
| Six denial controls per surface | Changed source, revoked capability, missing tool grant, missing operation grant, stale revision, and missing capability each produced zero calls, marker lines, or new events. |
| Two concurrent identical submissions | Exactly one call, one marker line and one `start`/`finish` pair. One of the two requests was rejected. |
| Source changed after durable reservation | A test hook changes the disposable source immediately after commit of the reservation and before revalidation. The adapter was called zero times and wrote no marker. The ledger retained `start` and `finish`, with an `indeterminate` receipt. |
| Stock native CLI | The one CLI-only control obtained a current view, saw `blocked`, and returned exit 2 with no additional events. |

SQLite event types are read directly and compared before and after each execution. The fixture adapter is counted separately and writes a marker line per invocation. Results record only decision labels, receipts, event types and effect counts.

The first draft of the harness reported 24/25. Its CLI test used a view from the separately configured Python store, whose in-memory adapter changed the view relative to the default CLI process. The final test obtains the CLI’s own view before execution. The preliminary results are retained. No MPLPB runtime code changed during the study.

## Interpretation

The study demonstrates enforcement for the checked routes, conditions and local effects. The zero-event result applies to refusals before reservation. The late-source test demonstrates a different outcome in which the protected effect is withheld and the reservation remains visible in history.

**Complete mediation under adversarial conditions remains unestablished.** The study covers a bounded set of interfaces and one cooperative fixture adapter. Its concurrent control covers a single interleaving class. The source code rechecks evidence before dispatch and then hands off to the adapter, and the documented architecture gives no atomic guarantee across source files, SQLite and external effects. There is no independent assessment of all effect-producing paths or validation of operating-system isolation. A stronger claim needs a defined threat model and complete path inventory, enforced host isolation and independent effect readbacks under those assumptions.

## Reproduce

Use a clean checkout of the exact pin and a new results path. The loopback control requires permission to create a local port. It uses the host operating system’s Python and standard library.

```sh
sha256sum -c SHA256SUMS
git clone https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages mplpb
git -C mplpb switch --detach 6ba371ca07dd9269f28af762ed1971ad484fb6b5
python3 -I -B run_controls.py mplpb replay.json
(cd mplpb && python3 -m unittest tests.test_specialist_continuity -q)
```

Compare cases by boundary and scenario. The response order of concurrent calls can vary. [Final observations](results.json) · [Preliminary observations](preliminary-results.json) · [Existing regression run](existing-defensive-tests.log)
