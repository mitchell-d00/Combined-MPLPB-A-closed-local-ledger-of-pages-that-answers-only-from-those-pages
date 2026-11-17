INDEPENDENT MPLPB SORTER PROBE - November 17, 2026

Source: Combined MPLPB sorter, commit ccbb5804eb47f78c2338d57c142ad087b47be710
https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages/blob/ccbb5804eb47f78c2338d57c142ad087b47be710/mplpb_work/sorter.py

This package contains eight fictional source documents, the summary of a local
sorter-core test, and a Python script to rerun the same fixture against the
actual upstream Combined MPLPB checkout.

LOCAL TEST PERFORMED:
- Transcribed the original sorter core (extract, status and compare) from GitHub.
- Replaced only the external prose_relations.date_cues dependency with a small
  regex compatibility stub because the full repository was not downloadable
  from this environment. Date handling, CLI integration, and native export are
  NOT verified by that local core test.
- The original native Python package and official test suite were NOT run.
- Two core modes were run against freshly authored communication records.
- Result JSON is included. This is a developer experiment, NOT a blinded
  historical-accuracy benchmark.

UPSTREAM REPRODUCTION:
1. Check out the exact Combined MPLPB commit above.
2. From that repository's root, execute:
   python /path/to/unpacked_probe/reproduce_upstream.py
3. The script runs sorter sort in both modes and sorter verify on the full
   native program, then checks the output invariants and quoted-header case.
4. It writes its temporary JSON artifacts outside the source tree and removes
   them at the end. Run in a disposable clean checkout with no sensitive data.

Notable question: The quoted example in 07-quoted-header.md has the same
Message-ID as a real source. Does the candidate identity cluster include the
quoted header? In the local reproduced core test it did. That is candidate
noise, not automatic false historical proof, because the output keeps support
and identity confirmation false.

No private legal/OOCC benchmarks are contained in this package.
