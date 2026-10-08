# Publication and walk back

Published base: b3de809de3c2b86168e99d090753c39bd86e71e3.
The update retains three stages in history:

- Reader/name guard and first UI: 17e04b7cf6b286c01013018cf33e78776228e9a6.
- RPG front end: 3c8ceff2de79e98e75489385d018046a640fa1ab.
- Chat, topic import and system/creator reference: the subsequent commit titled
  “Add pinned topic chat and system creator reference”.

The first two published trees match the original local commits f08a1b5 and e1fb011
exactly. Their published commit IDs differ because publication records new commit
metadata. Retained source captures record the local base actually observed; those
records were not rewritten to invent a publication-time capture.

## Revert the chat layer

Locate the commit with:

```sh
git log --oneline --grep='Add pinned topic chat and system creator reference'
```

Run `git revert` with that commit hash on a new branch, run the tests and publish
the revert. This retains the RPG front end and corrected reader. It preserves
history; do not force-reset shared main.

For the earlier interface alone, revert the RPG front-end commit above after the
chat revert. For a full code rollback to the published base, revert the three new
commits in reverse order. User-imported captures under ignored `local/` are separate
from versioned code; retain or archive them yourself.

The full ZIP has the reader patch already applied. Do not apply it again. The
reader-only corrected patch is included for review and can be reversed separately,
with its six regression tests, if that is the desired scope.

## Evidence and limits

256 Python package tests passed. The front-end element-stub checks passed. A live
Wikipedia search/import and contextual follow-up succeeded for Dinosaur; raw source
pins and a separate offline replay are retained under docs/chat-validation.
This is one workflow exercise, not an evaluation score or general accuracy claim.

Frozen probes, stored evaluations and existing source captures were not rewritten.
The deterministic chat layer adds only the documented structured-fact rules and
explicit context handling. General semantic/AI conversation is not implemented.
Browser visual testing and Windows launcher execution remain unverified.
