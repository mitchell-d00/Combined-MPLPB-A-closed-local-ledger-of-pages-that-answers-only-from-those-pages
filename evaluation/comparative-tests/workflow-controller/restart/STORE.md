# Frozen lab reservation policy v1

Last reviewed: 2026-11-27.

The restart baseline showed two unretained duplicates reached Git. Its
host-retained-key control blocked before the writer. This separate candidate
wraps the unchanged controller with a reservation directory for one disposable
repository namespace. Only the trusted host chooses the directory, action,
Git ref and payload. Authentication and evidence provenance stay simulated.

A non-existing reservation is available. An atomic exclusive directory create
claims the action/revision before Git dispatch. Sync the store directory
before allowing the writer. The key is SHA-256 over the controller's exact
action/revision string. Use one store shared by both processes for that
repository. The directory itself is the consumed marker. A marker without a
valid synced outcome is indeterminate. Never delete it, recycle it, or retry
automatically. Retain known outcomes as a separate receipt after Git returns
and the host reobserves the exact ref and marker. Sync the receipt and its
containing directory. A completed receipt requires successful Git and exact
intended readback. A known CAS failure requires a Git failure and competing
commit readback. Other uncertain states retain the consumed marker and withhold.

| Boundary | Decision and execution |
|---|---|
| Known consumed key on restart | Withhold duplicate_request, not_run |
| Pending or unreadable outcome on an existing key | Missing reservation_indeterminate, not_run |
| Unavailable store before reservation | Missing reservation_unavailable, not_run |
| Another process claims key after final controller admission | Withhold reservation_conflict, not_run, no Git dispatch |
| Winner | Keep native admission and separate effect outcome |
| Abrupt exit after synced claim or after Git before outcome | No completed worker receipt, indeterminate on restart |

Freeze all cases in candidate.json. Every normal worker receipt is scored for
admission, code, execution, Git writer attempts, writes, competing writes and
store state. Drive two independent processes to a bounded barrier at the start
of the write callback, after inner controller admission and before exclusive
creation. Require one winner and one collision in either process order. Each
driver observes exact ref OID and marker independently at interleaving
boundaries. Abrupt exit codes and absent worker output are scored separately
from normal receipts. The post-Git interruption may already have had an
effect. Its readback never authorizes inferred completion of the request.

Assumptions: one trusted local filesystem and host, atomic mkdir, supported
directory sync, fresh exclusive evidence logs, no external edits to the store,
and a stable repository namespace. This is process-restart protection and
one bounded contention test. Power loss, distributed filesystems, corruption,
manual reconciliation, revocation synchronized across processes and all
production authority remain outside the tested scope.
