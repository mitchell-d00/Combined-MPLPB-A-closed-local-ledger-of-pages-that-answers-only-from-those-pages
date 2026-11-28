# Ares-01 authority revocation across processes

Last reviewed: 2026-11-28.

Use Apollo's merge `e2a4d77ff09150639cde1bcea2fe2bcb245ac963` as the baseline.
Its bridge, controller, reader and reservation store are unchanged. The existing
controller rereads host state, while the old fixture supplied in-process state.
The cross-process authority source and barriers start unimplemented. Apollo and
earlier runs remain consumed preservation.

The lab host owns a local file containing the grant status and epoch. One separate
revoker process changes epoch 1 active to epoch 2 revoked by atomic replacement.
It logs the commit and acknowledges the barrier after replacement. An executor
reads that file synchronously. A bounded file handshake controls exactly where a
revocation occurs. A lab module hook adds the host read and barrier observations
to the hash-pinned Heka worker. The reader, controller and Git writer remain real.
Each case has a separate disposable repository and reservation store.

The last shared read in the existing controller's final authority evaluation is
the linearization point. Freeze this rule for all cases. Epoch 2 observed there
blocks dispatch. In the post-check contrast the write callback has already been
authorized on epoch 1. It pauses before Git dispatch, observes the revoker's
acknowledgement and proceeds under that admission. A later revocation does not
undo that admission under the frozen rule. This does not make authority state
and Git ref changes atomic.

The five ordered contrasts use complete real reader proof and score actual
initial and final controller decisions separately from effects.

- Active permit reads shared epoch 1 and produces one intended write and
  one durable completion.
- Pre-check revocation occurs after the preliminary reads and before the final
  authority read. It produces no writer attempt.
- The stale-cache contrast captures epoch 1 before a separate process revokes.
  Two preliminary reads deliberately use the cached grant. The final read checks
  epoch 2 in the shared file and prevents dispatch.
- A priming worker reads epoch 1 and exits. Revocation follows its exit at a
  driver barrier. A different executor process reads shared epoch 2 initially
  and withholds. No cached grant crosses the restart.
- The post-check handshake starts inside the authorized write callback. A
  separately observed revocation precedes the actual writer attempt. The
  already-admitted write completes and is graded as an observed effect.

Bind event role and PID and retain a single append-ordered trace. Wall-clock
timestamps are not used to establish ordering. Independently inspect the actual
Git ref, marker, reservation and final authority file. Count initial admission,
final admission, writer attempts, effects and durable completion separately.
A blocked request must leave the ref, marker and unused reservation unchanged.

Freeze generator, packets, expectation-key digests and scorer before execution
or implementation. One operator authored and scored the deterministic draws.
Fresh changes question layout, actors and order, and repeats the causal
structures. Keep the private grading keys outside workers and Git. Pin the
candidate before opening fresh. The lab trusts its local host, filesystem and
barrier processes. It does not establish distributed revocation, production
identity, compromised-host resistance or authority/Git atomicity.
