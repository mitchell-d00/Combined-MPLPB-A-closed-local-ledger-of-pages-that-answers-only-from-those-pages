# Exact-field source cards: retained browser failure and correction

Last reviewed: 2026-11-25.

The first committed tag candidate2af8ba8 passed72development,280preservation,
24once-only transfer decisions and1,834native tests, but failed its candidate
browser journey. [Original browser logs](failed-c4-browser). A verified PRINT202
field answer offered lexical page cards; the first opened PRINT201.

The browser assertion also checked source text before waiting for the newly
opened dialog, so earlier passing journeys could inspect retained closed-dialog
content. Their receipts remain passes under their original observer, with this
newly identified limitation; they are not proof that every second-source click
opened correctly. [Frozen failing controls](frozen-controls.cjs), [baseline](baseline.log),
[freeze](freeze.json).

The general UI correction builds exact-field evidence cards from native citation
ID/path/hash tuples, including a verified owner absent from lexical matches.
Candidate inspection still shows lexical pages. Source-open actions retain the
verified hash. The strengthened browser assertion waits for the actual dialog
to open before checking its owner and text. No fixture identifiers occur in the
implementation. Rendering controls and35browser-bridge/integrity tests pass.

Native packages remain byte-identical to the once-tested transfer engine. The
transfer packet is not rerun or renamed fresh. A new delivery ZIP receives its
own JavaScript/HTTP/browser checks and exact publication-head CI; the first
delivery candidate remains failed for browser acceptance.
