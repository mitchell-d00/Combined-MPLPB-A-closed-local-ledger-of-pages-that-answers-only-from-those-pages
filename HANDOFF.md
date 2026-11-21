# Repository handoff

Last reviewed: 2026-11-21.

Read AGENTS.md before the next update. This is development coordination, not source-ledger evidence.

Base commit: `6572b39d31649b051202c488776403919813f304` (ancestry, not the final self-containing commit).
Source inventory SHA-256: `3fa85b3d0c19c286d6b7668cdd0d4340a879712c58034659fa4fbb4eecfcbb46`.

## Latest user update instructions

Primary? Like uploaded books? Just find a few open source books online use them

Are that a test too called the primary book test

And generate new ones too I want ai and users to be able to run unique tests eac( time if they want

Ncludechow to build them the online search gather and book sorry I’m on my phone typos

## Implemented scope

- Add the Primary Book Test under test_tools. Draw passages from pinned Standard Ebooks editions of firsthand works by Darwin, Seacole and Washington.
- Support new seeds, repeatable offline batches, automated exact-quote controls, externally authored questions and separate custodian keys.
- Document finding, checking reuse terms, downloading and pinning historical book sources.

## Validation recorded

- Two real-book batches each returned three correct source citations and withheld the three altered-quote controls.
- An offline replay with seed 2a reproduced the same excerpts, questions and key byte-for-byte.
- In a nine-question prose pilot, MPLPB abstained on six answerable questions and three questions with missing evidence.
- Ten focused tests, the documentation audit and the infrastructure check passed.

## Limitations and blocked checks

- The default catalog samples the first two chapters of three books. A fresh seed draws another batch and can repeat a passage.
- The automatic scorer checks exact wording and citations. Prose interpretation requires an independent answer key and reviewer.
- Pilot results describe these excerpts and questions.

## Next steps

- Have a human custodian select a fresh batch and draft source-grounded questions before running MPLPB.

## Use this ZIP in your repository

Extract the full ZIP, including dotfiles, into a clean directory. Review its files and run `python tools/build_handoff.py --check`. Copy the source into your existing checkout while preserving its `.git` directory and personal saves. Review the diff, commit on a branch, and push normally. Do not replace your Git history with a new repository. The included Actions workflows then run their configured checks; a local ZIP is not deployment verification.

For the next change, update `handoff/update.json` from the latest instruction, stage intended files, run `python tools/build_handoff.py`, verify with `--check`, and include the generated handoff in the delivery.
