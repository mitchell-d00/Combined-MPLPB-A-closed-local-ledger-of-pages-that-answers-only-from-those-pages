# Frozen restart baseline v1

Last reviewed: 2026-11-27.

Pin the current controller at released main
`a01369392071bd6781be379a4b580d9a9d0bc460`. The checksum inventory binds
the unchanged controller, canary template, B-Tests pin and original case
inventories. Run each scenario in a fresh disposable local repository.
Use two fresh Node processes per scenario, with the identical action and
original target revision. HEAD remains fixed. The separately observed
`refs/heads/canary` is never reset between the two requests.

1. Start with the template's current host authority. The first request
   attempts a fixed Git compare-and-swap from the initial commit to
   the intended commit. In the contrast a separate Git process writes
   the competing commit in the existing `beforeWrite` hook.
2. Read the exact ref and marker before and after each process from the
   driver. Record PID per invocation, exact expected Git old value, verdict,
   execution, Git writer attempts, successful writes, and host reservation
   input. An additional same-process evaluation reads back consumption of
   the volatile reservation through `duplicate_request` without writing.
3. Run the identical request in a new process. For the host-retained control
   only, pass the consumed key in the trusted host's `used` array. Leave the
   ref where the first process left it.

Score each phase's admission, execution, writer attempts, intended writes,
competitor writes and final ref plus marker against the frozen packet.
The expected pairs are exactly in `baseline.json`. The baseline has no
durable store. A later rejection from Git counts as an attempted write,
with `execution: failed`, including if the intended ref is already present.
A no-write duplicate must produce a withheld admission and zero writer
attempts. Process startup or missing output is an execution problem, not
a policy match. Preserve the first receipts and diagnostic logs.
