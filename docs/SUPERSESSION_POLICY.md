# Supersession policy examples

Desired rule, written before reading what `478a86b` does on these cases.
The published kill-test probes are not part of this file and are not inputs.

A replacement retires its predecessor only when its identity, hash, pinned
references, origin, and depth are valid. Withdrawing that replacement does
not restore the predecessor. Restoring old content requires an explicit new
revision. Derivatives of a retired basis are withheld until rechecked.

Each example names the pages, the mutation, and the only acceptable read.
"Served" means the reader may return that page. A withheld page stays in
the folder.

## P1. Valid replacement retires its predecessor

- B current, intact, unique id, origin human, depth 0.
- R new id, intact hash, `supersedes` pin equals B's hash, origin human, depth 0.
- Read: B retired. R served. A question B owned is answered by R.

## P2. Damaged replacement does not retire

- Same as P1, then R's body is changed and the hash is left as it was.
- Read: R has no authority. B stays current and is served. R is not served.

## P3. Duplicate id does not retire

- Same as P1, then a second file carries R's id.
- Read: neither copy of R has authority. B stays current and is served.

## P4. Missing pin does not retire

- R names B in `supersedes` with no hash pin.
- Read: B stays current and is served. R is not a successor.

## P5. Wrong pin does not retire

- R's `supersedes` pin is a hash that is not B's hash.
- Read: B stays current and is served.

## P6. Invalid origin or depth does not retire

- R is otherwise a valid successor, but origin is not human or machine, or
  declared depth does not match the lineage.
- Read: B stays current and is served.

## P7. Withdrawing the replacement does not restore the predecessor

- P1, then R is withdrawn. No other write.
- Read: B stays retired. R stays retired. The question is not in the corpus.
  Nothing flips B back to current.

## P8. Restoring old content is a new revision

- After P7, the old body comes back only as a new page N.
- N has a new id, an intact hash, and a `supersedes` pin to the withdrawn
  replacement R (the head that was current).
- Read: N served. B and R stay retired. Editing B's status line back to
  current is not a restore.

## P9. Stale derivative is withheld until rechecked

- B current. D derived from B, depth 1, its own hash intact.
- B is then validly replaced by R, or withdrawn.
- Read: D stays in the folder and is not served. A question only D owned is
  not in the corpus. D is served again only after an explicit recheck: a new
  revision of D whose `derived-from` pin names a current basis.

## What these examples are not

They are not the pottery probes in `killtest/`. Those files stay frozen.
A green run of those probes does not decide P7, P8, or P9.
