# Atomic publication of staged ledger generations

Last reviewed: 2026-11-18.

The optional `mplpb_work.ledger_generations` publisher keeps complete ledger generations under `STORE/generations/ID/ledger` and publishes one POSIX `STORE/current` symlink. Use `STORE/current` as the publication endpoint. For a multi-read investigation concurrent with publication, resolve that symlink once and pass the resulting generation path for the entire operation; repeatedly reopening the mutable pointer is not a read transaction. The reader's grammar, ownership, revision/hash checks and delivery profiles are unchanged. Source support remains distinct from historical truth.

```bash
python -m mplpb_work.ledger_generations init EXISTING_LEDGER --store NEW_STORE
python -m mplpb_work.ledger_generations build review.json --dump DUMP --store STORE --reviewed-by 'Your name'
python -m mplpb_answers ask STORE/current 'What is owner for record RECORD-1?'
python -m mplpb_work.ledger_generations inspect --store STORE
# Explicit recovery selection, never automatic newest/similar selection:
python -m mplpb_work.ledger_generations recover --store STORE --select GENERATION_ID
```

A new store can also be created by `build` without `init`. The store parent must exist. Source/store/dump locations must be disjoint. The native classing writer operates only on a private staged copy; accepted choices, literalness, machine origin, named review and opt-in ratification still apply. The generation's native validation and complete file hashes are checked before publication. Unknown authorship can still withhold a depth0 ratified page from external delivery.

Publication checkpoints are: staged native validation; fsync staged files/directories; install the complete content-addressed generation and fsync its parent; prepare a relative temporary pointer; atomically replace `current`; fsync the store. A POSIX advisory writer lock is released by the OS on process death. Existing complete generations remain untouched by this API and hash checked.

`tests/test_ledger_generations.py` terminates a subprocess at all six checkpoints. Normal reads see the complete old generation before pointer replacement or the complete new generation afterward. Orphaned complete generations and staging files are not promoted. Corruption and pointer escapes refuse. Recovery selection is explicit and validates bytes first. A failed/terminated call after pointer replacement may already have committed: inspect before retrying.

Limits: single-host local POSIX filesystem with symlink/rename/directory-fsync support, at most4096 ledger files/64MiB per staged snapshot,2MiB manifests and at most32 generations per default inspection (truncation is reported). This is process-interruption testing, not physical power-loss certification, network-filesystem support or protection from a hostile filesystem owner. Immutability is an API rule plus hash verification; a trusted operator can still alter files manually.

Old generation directories are historical snapshots; `STORE/current` is the serving endpoint. As with other copied local ledgers, the plain reader has no global revocation registry across arbitrary roots. Do not present a direct query of an old snapshot as the current published generation.
