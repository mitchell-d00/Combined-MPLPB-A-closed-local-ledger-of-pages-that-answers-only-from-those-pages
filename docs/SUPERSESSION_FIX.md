# Supersession fix

Applies the rule in SUPERSESSION_POLICY.md on top of 478a86b.

- A replacement retires its predecessor only when identity, hash, pins, origin, and depth are valid.
- An invalid replacement is not served, so it cannot block the predecessor.
- Withdrawing the replacement does not restore the predecessor.
- Restoring the old body is an explicit new page that pins the withdrawn head. revise() on the retired predecessor still fails.
- A derivative of a retired basis is withheld until a new revision pins a current basis.

Published kill-test probes were not modified.

## Review fixes

- A new page cannot supersede an older predecessor while a replacement of that page is still current. Restore pins the withdrawn head, not the page behind a live successor.
- A derivative whose basis pin is missing or does not match the basis hash is not served. Validation still reports C6 or C7.
- The probe-preservation test asserts the frozen SHA-256 values, not merely that the files exist.

## Terminal head

Restoration must pin the terminal authoritative page of the supersession chain.

- In B → R → N, a new page cannot supersede B. N stays the only served page.
- After R is withdrawn, a new page cannot pin B. It must pin R.

## Publication verification

The reviewed third ZIP contributes the ledger implementation, 14 policy tests, and two policy documents. The complete package passes 165 tests. Additional checks reject restoration behind both live and withdrawn terminal heads and accept a new restoration that pins the terminal head. All published files under `killtest/` and `evaluation/` are byte-for-byte unchanged. README and rollback notes describe the new behavior separately from the earlier reader and historical results. These checks establish regression agreement with the policy examples, not independent validation.
