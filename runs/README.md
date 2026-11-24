# Offline test run evidence

The patched packages contain Combined MPLPB at 046bfaed7bf43917b0b8c2d5608d59538cf5e1fe
and B-Tests at 7c34a664033a330d69839d7422852f741d2d673c. We unpacked and tested
the published ZIPs using Python 3.13.5 with ResourceWarning enabled.

- [MPLPB native](replay/mplpb-native.log) passed 72 tests under a 60-second deadline.
- [B-Tests full](replay/b-tests-full.log) passed 148 tests under a 45-second deadline.
- [Historical and Scout](replay/historical-scout.json) matched all 22 historical
  Strict decisions and 48 Scout graph passes. The replay had a 180-second deadline.
- [B-Tests cutoff retest](replay/b-tests-cutoff-repeats.json) passed 20/20 in
  0.609–0.732 seconds under a 10-second per-run deadline.
- [B-Tests before the fix](replay/b-tests-before-fix.log) retains the allocation
  traceback that led to the cleanup.

The patched runs emitted zero unclosed-database warnings. The fixes affect test fixtures.

The [earlier external reports](reported-external/) retain the native warnings,
the incomplete B-Tests transcript and the structured benchmark JSON. The
earlier external B-Tests transcript ends mid-test and has no exit status.
Its cause remains unresolved. The benchmark JSON records support decisions
on structured record questions.
