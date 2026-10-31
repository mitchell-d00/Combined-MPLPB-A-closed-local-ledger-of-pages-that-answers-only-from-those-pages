# Specialist work API and operation

The native `mplpb_work` coordinator preserves task relationships, evolving claims,
failed routes, specialist identities and permission history. It is part of the
Combined MPLPB distribution and uses the Python standard library, including SQLite.
The strict answer engine continues to answer only from eligible source pages.
Work records never become supported answers merely because they survived a handoff.

## Try the complete example

```sh
python -m tools.demo_specialist_continuity
python -m unittest tests.test_specialist_continuity -q
```

The demonstration creates an isolated temporary project and four seat contracts.
Instances A, B and C contribute evidence, a challenge and a failed implementation,
then end. A new process reads the successor D's filtered handoff. Reviewer E
revises the inherited premise using the original source and resolves the challenge.
D runs a changed fixture; completion needs its passing execution receipt. Five
instance identities use the same declared model name. There are no provider calls.
The report contains neither capabilities nor a saved private database.

## Bootstrap and credentials

A trusted host initializes the store and registers exact local corpus roots:

```sh
mkdir -p local
umask 077
python -m mplpb_work init local/research-work --corpus studio=examples/studio > local/research-host.json
```

`mplpb-work` is the installed equivalent. `mplpb-combined work ...` also forwards
to this CLI. Initialization returns a host authority credential once. Preserve it
outside model context. Store creation refuses to overwrite an existing database.
The database is created with mode 0600 and a new containing directory with mode
0700 where supported; SQLite journal files follow database permissions.

Submit JSON requests through stdin or an explicit file. Credentials are read from
an explicit JSON credential file or `MPLPB_WORK_TOKEN`, never a command argument:

```sh
python -m mplpb_work request local/research-work --credential-file local/research-host.json --input head-request.json
```

For that request, `head-request.json` contains `{"op":"head"}`. Host credential files
use the `authority_credential` field returned by initialization. A seat assignment
returns a `credential` field, which can be saved in a separate private file and
passed through the same option. The CLI accepts host administration operations;
the HTTP seat API does not.

## Issue a seat from host code

```python
import time
from mplpb_work import WorkStore
from mplpb_work.store import digest

store, authority = WorkStore.create("local/project-work", {"studio": "examples/studio"})
policy = {"projection": "record-visibility-v1", "task_scope": "T1"}
grant = store.assign(
    authority,
    seat="researcher",
    instance="researcher-runtime-1",
    model={"name": "declared-model", "provider": "declared-provider",
           "version": "declared-version", "context_policy_hash": digest(policy)},
    contract={
        "operations": ["create:task", "create:evidence", "create:claim"],
        "tools": [], "scopes": ["T1"], "share_with": [],
        "profile": "internal", "expires_at": time.time() + 3600,
    },
    expected_head=store.head(authority)["hash"],
)
credential = grant["credential"]  # host delivers only this seat's capability
view = store.snapshot(credential)
view = store.put(
    credential, id="T1", kind="task", expected_revision=0,
    payload={"goal": "Investigate a question", "criteria": ["fixture passes"],
             "review_budget": 3, "state": "open", "acceptance": {}},
    dependencies={}, visibility=["researcher"], expected_head=view["head"],
)
```

Each actual assignment uses a fresh instance ID. Reassigning a seat increments its
fencing generation and invalidates the former capability. `continues_work_of`
records a predecessor instance without claiming that the model or runtime is the
same object. Ending or revoking an instance preserves its contributions. Model
metadata and context-policy hashes are declarations; use explicit `unknown` when
a policy hash is unavailable. This is not provider attestation.

Host contracts declare exact operations, versioned tool names, task scopes,
permitted sharing recipients, a serving profile and an expiry. Examples of
operations are `create:claim`, `revise:claim`, `execute`, `transfer` and
`resolve_review`. There is no model-accessible grant operation or wildcard right.
A scope of `*` can be issued deliberately by the host; narrow task scopes are also
supported. Reads still require explicit record visibility.

## Record contracts

Every `put` supplies an ID, kind, complete payload, `dependencies` mapping IDs to
positive integer revisions, explicit `visibility` seats, `expected_revision`, and
the caller's current view `expected_head`. Creation expects revision 0. Updates
append a new revision and preserve all prior versions, authors and timestamps.
Kind/task changes are rejected. Evidence and attempts are immutable; new work gets
a new ID. The `attempt:` namespace is reserved for host execution receipts.

| Kind | Payload and behavior |
| --- | --- |
| Task | `goal`, distinct `criteria`, `review_budget` (1–100), `state` (`open`, `done`, `cancelled`), `acceptance` mapping passing attempt IDs to revisions. Task dependencies form a prerequisite graph. |
| Evidence | `task`, registered `corpus`, `source_id`, `source_hash`, exact body `quote`, retrieval `query`. The existing MPLPB gate checks hashes, lineage, status, profile, depth, delivery restrictions and not-for exclusions. Headings and metadata cannot supply the span. |
| Claim | `task`, `proposition`, `basis` (`observation` or `inference`), `assessment`, `assumptions`, `alternatives`, `revisit_when`. Working support needs pinned evidence/claim dependencies; it does not certify entailment or truth. |
| Attempt | `task`, `method`, `result` (`failed` or `inconclusive` for specialist submissions), `failure`, `retry_when`, `artifact`. Passing attempts are created only by host dispatch/reconciliation, linked to a receipt and exact inputs. |
| Decision | `task`, `choice`, `alternatives`, `reason`, `assessment` (`proposed`, `accepted`, `withdrawn`), `recheck_when`, `failed_attempts` mapping historical unsuccessful attempts to revisions. Failure is contextual evidence, not a successful prerequisite. |
| Action | `task`, `task_revision`, versioned `operation`, JSON `arguments`, `side_effect` (`local`, `external`), `executor_seat`, `state` (`proposed`, `cancelled`), `retry_of` mapping at most one unsuccessful attempt to its revision, `retry_reason`. Inputs go in `dependencies`. |
| Review | `task`, a single pinned claim `target`, declared `target_variable`, `regime`, `finding`, `outcome` (`challenge`, `support`, `inconclusive`, `resolved`), `resolution`. Observations go in `dependencies`. |

A claim's working assessment can be `proposed`, `supported_under_scope`,
`contested`, `withdrawn` or `needs_recheck`. There is no terminal `true` state.
The store computes an **effective status** separately from the specialist's
assessment. Challenges remain live across claim revisions until an authorized
reviewer resolves them with current source evidence. A stale resolution reopens
the problem. A claim owner cannot erase or redirect another review.

All source/prerequisite revisions are checked. Changes propagate through the graph
as `needs_recheck`, including receipt-backed task completion. A changed task
revision prevents an old action or old passing receipt from satisfying the new
contract. The original quote and old claim remain recoverable for authorized
readers even if their current source is stale.

Review creations and substantive revisions consume the task's declared budget.
Resolving a live challenge does not spend another review round. Shared provenance
roots and exact source-span fingerprints are recorded separately: a different span
from one source can be new information without being an independent source. Copies
do not acquire independent corroboration. `discrimination` remains `unmeasured`;
no mutual-information stopping theorem or general review effectiveness is claimed.

## Views, transfer and handoff

`snapshot(credential)` and `handoff(credential)` rebuild the current permitted view.
Both return working records, authorized histories, the current instance/contract,
computed statuses, a seat-specific head, and `next_actions`. Private content,
identifiers, event counts, credentials, hidden history versions and redaction
markers are absent. Reference visibility is checked recursively so public wrappers
cannot expose an otherwise withheld dependency. Serving-profile restrictions also
apply to historical evidence and derivative records.

A store-wide host head protects administrative operations. A seat head covers its
visible work and contract, so an unrelated private note does not reveal a changed
global sequence or spuriously conflict with that seat's next write. Eligibility
and blocked-action status can change when relevant conditions change; this is not
a claim of eliminating every timing or availability side channel.

`transfer` requires the `transfer` right, an allowed `share_with` recipient, the
current head/revision and `include_history=True`. It explicitly discloses the entire
record history. Dependencies must be transferred first. A new record cannot widen
its source visibility or share outside its author's host-granted recipients.
Dispatched actions cannot be rewritten or transferred. Transfer changes a revision,
so dependents conservatively require rechecking.

## Host adapters and action execution

Host code registers an operation; a specialist cannot register arbitrary Python,
shell commands, network clients or an execution adapter through the API:

```python
def run_fixture(request):
    # Use this key for any downstream service that supports idempotent requests.
    key = request["idempotency_key"]
    arguments = request["action"]["payload"]["arguments"]
    # Validate arguments against this adapter's own fixed contract.
    return {"result": "passed", "validation": {"fixture passes": True},
            "artifact": "fixed fixture completed"}

store.executors["fixture.run.v1"] = {"run": run_fixture, "side_effect": "local"}
```

A bare callable is a local-effect adapter. External-effect adapters must declare
`side_effect="external"`; an action cannot downgrade that declaration. Hosts must
bind versioned operation names to reviewed implementations and preserve their
configuration. This coordinator does not automatically verify a tool's code or
make its result true.

`execute` takes the seat credential, action ID, revision and current view head. It
checks the active instance/fence, expiry, scope, tool right, task revision,
prerequisites, challenges, source eligibility and available adapter. It reserves a
durable execution receipt, then rechecks immediately at the dispatch boundary.
The adapter receives a copy of the permitted context, the exact action and an
idempotency key. Its result records a passing, failing or inconclusive attempt,
validation results and an artifact digest. Only passing host validations covering
every criterion can complete a task.

A crash or uncertain exception leaves an `indeterminate` outcome; it is never
silently retried or reported as successful. Another action cannot bypass an
unresolved run of the same task/operation. A failed route needs an explicit
`retry_of`, a reason, and changed arguments, input pins or task constraints.
The latest unsuccessful attempt is linked; unchanged historical failed routes
remain blocked. A host operator can `reconcile` an uncertain receipt after checking
external state, recording the reason and validation. Earlier uncertainty remains
in history. The operator must not reconcile a still-running external operation as
if its outcome were known.

SQLite cannot make a remote side effect atomic. A trusted external adapter must
honor idempotency where available and handle its own external conditions. A source
file may also change immediately after a byte check; the receipt preserves the
checked pins, and later reads re-evaluate freshness. No filesystem-wide lock or
remote exactly-once execution guarantee is claimed.

## Dedicated local HTTP seat API

```sh
python tools/ledger_ui.py --work-store local/research-work --port 8767
```

This opt-in mode serves **only** `POST /api/work`. Normal UI, query, page, state and
history routes are unavailable there, so source inspection cannot bypass the work
projection. The ordinary UI runs separately without `--work-store`. Work mode keeps
existing loopback Host/origin and JSON request-size checks. It creates no store
implicitly and requires `Authorization: Bearer <seat capability>` on every request.
For example, the JSON body `{"op":"handoff"}` returns the caller's current view.

HTTP supports `snapshot`, `handoff`, `put`, `transfer`, `end` and `execute` only.
Issuing/revoking grants, audit/checkpoint access and reconciliation remain host
operations. The command above has no registered execution adapters; its actions
remain blocked until a host application mounts a `WorkStore` with reviewed adapters
through `App(work_store=store)` and `handler(app)`. The CLI does not import arbitrary
adapter symbols from untrusted requests.

## Trust and storage boundaries

Permissions are enforced at this trusted coordinator's API boundary. Restricted
specialists must receive only their capability and projected work, with no direct
access to the database, authority credential, unrestricted corpus readers, another
seat's token, or host Python/OS execution. A process with unrestricted filesystem
access can bypass an API; this package is not an operating-system sandbox or an
AI-provider isolation service. Model memory, shared provider buffers and deliberate
semantic disclosure beyond this API are outside its enforcement boundary.

Store directories contain a private SQLite database and transaction journals. Back
up a coherent store using SQLite's backup facilities. Keep a host `audit` checkpoint
(`seq`, `hash`) independently if rollback detection matters. Every API operation
checks the chain against the local head; `audit(authority, checkpoint)` also checks
an independently retained historical head. Rewriting both the database and every
trusted checkpoint defeats a local hash chain. Hashes do not authenticate source
truth or authorship.

This release supplies a native coordinator, CLI and dedicated local API. There is
no hosted-browser work-store UI, hosted specialist service or AI-provider scheduler.
The five-instance demonstration validates deterministic work recovery and guards;
[the research model](SPECIALIST_CONTINUITY.md) retains the separate experiments
needed to assess real specialist usefulness.
