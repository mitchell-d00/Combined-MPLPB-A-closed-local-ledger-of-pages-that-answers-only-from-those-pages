# Parts

The five earlier MPLPB implementations, carried whole. Each still runs on its own from its own
directory, and each keeps its own README, paper and licence. Nothing here is superseded by the
combined package; `docs/Combined_MPLPB.md` section 7 says what each one does that the core
does not.

| Directory | What it is | Upstream |
|---|---|---|
| `local-mirror/` | MPLPB-LOCAL-008 v4: a corpus as a plain HTML site, with crawl, search and validate tools | github.com/mitchell-d00/-The-Local-Mirror-MPLPB-as-a-Self-Contained-Offline-Site |
| `smart-local/` | MPLPB-SMART-011 v1: the retrieval-bounded reader, modes, teaching | github.com/mitchell-d00/SMART-LOCAL-MPLPB-A-Retrieval-Bounded-Front-End-for-a-Local-Web |
| `swarm/` | MPLPB-SWARM-013 v3: leases with fencing, origin depth, registry, profiles, the ablation harness | github.com/mitchell-d00/mplpb-swarm-scale |
| `networked/` | Networked MPLPB: seeds, nodes, hubs, Ed25519 signatures | github.com/mitchell-d00/networked-mplpb |
| `image/` | MPLPB-IMAGE-016 v2: signed image pages with evidence and attestation | the uploaded `MPLPB-Image-v2.zip` |

## As run

From the repository root, `python3 tools/check_parts.py` runs every part's own tests and then
adopts each part's example site into the combined format. On Linux, Python 3.12, 2026-10-07:

```
test suites
  combined (this repo)    106 tests  OK
  smart-local              52 tests  OK
  swarm                   145 tests  OK
  networked                61 tests  OK
  image                    93 tests  OK
  local-mirror           its own validate.py exits 0

adoption: copy each part's example site, seal it, validate it in the combined format
  local-mirror           4 sealed, 3 current, 1 retired, 0 error(s)
  smart-local            5 sealed, 4 current, 1 retired, 0 error(s)
  swarm corpus-a         3 sealed, 2 current, 1 retired, 0 error(s)
  swarm corpus-b         1 sealed, 1 current, 0 retired, 0 error(s)
  networked seed         4 sealed, 4 current, 0 retired, 0 error(s)
```

To run one part by hand:

```
cd parts/smart-local && python3 -m unittest discover -s tests -t .
cd parts/swarm       && python3 -m unittest discover -s tests
cd parts/networked   && python3 -m unittest discover -s Tests -t .
cd parts/image       && python3 -m unittest discover -s tests
cd parts/local-mirror && python3 tools/validate.py site
```

## What was changed in these copies

Three things, and nothing else. No source file was edited.

1. **Directory case, `smart-local/` and `local-mirror/`.** Upstream the directories are `Site`,
   `Tests`, `Tools` and `Docs`. Their READMEs, and Smart Local's test imports, say `site`,
   `tests`, `tools` and `docs`. On a case-sensitive filesystem the upstream Smart Local tests fail
   at import. The directories are lower case here.
2. **`swarm/` comes from the archive, not the tree.** The upstream repository tree is missing
   `ablation/v2/arm-structured/deploy/_index.html` and has a stray `registry` directory inside
   `site/corpus-b`, so 2 tests fail and 1 errors there. The `MPLPB-SWARM-v3.zip` bundled in the
   same repository is complete and passes. This copy is that archive, unpacked. Its paper says
   144 tests; the suite has 145.
3. **Housekeeping.** `.git` directories, `__pycache__`, and the archives nested inside two of
   the repositories were removed.

`networked/` keeps its upper-case `Docs`, `Seed`, `Tests` and `Tools`, because its README uses
those names.
