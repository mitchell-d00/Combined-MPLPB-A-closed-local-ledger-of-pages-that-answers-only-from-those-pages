# Dual-mode sorter technical paper

Last reviewed: 2026-11-17.

Package role: [how this part fits Combined MPLPB](../../PACKAGE_GUIDE.md#documentary-research). The sorter paper is a dated technical report; current package usage and authority boundaries are documented separately.

**Mitchell D. McPhetridge** — *A Dual-Mode Sorter for MPLPB: Turning Unformatted
Material into Inspectable Candidates*, with subtitle *Source-Anchored Candidate
Extraction for Closed Local Ledgers*. Version1.1, 17 November2026.

Download/read the same report in [Markdown](dual-mode-sorter.md),
[plain text](dual-mode-sorter.txt), or [PDF](dual-mode-sorter.pdf).
The PDF has nine pages. Markdown is the source of record; text and PDF are generated.
[manifest.json](manifest.json) pins each format, the renderer and its version.

The report describes the implemented offline sorter, identical nodes across its
modes, non-authoritative review edges, exact source anchoring and native retired
snapshot acceptance/withholding. Its source/measurement references are frozen
engineering commits and dated developer-authored controls, not new independent
historical accuracy results. Original papers,
corpora, questions and prior reports remain unchanged.

Use the [operational guide](../../PREPROCESSING_SORTER.md) for current commands.
See the [initial contract evidence](../../../evaluation/preprocessing-sorter/2026-11-17/RESULTS.md)
and [native export refinement](../../../evaluation/preprocessing-sorter/2026-11-17-native-export/RESULTS.md)
for retained source hashes, failed attempts, software checks and limitations.
Publication workflows validate their exact submitted head separately; neither
this paper nor old green checks certify another commit or historical truth.

## Rebuild

The sorter itself has no ReportLab dependency. Only rebuilding the PDF requires
ReportLab (the retained build uses4.4.9). Text-only rendering uses the standard
library. Do not regenerate protected historical original papers.

```bash
python tools/make_paper.py \
  --source docs/research/dual-mode-sorter/dual-mode-sorter.md \
  --title 'A Dual-Mode Sorter for MPLPB: Turning Unformatted Material into Inspectable Candidates' \
  --author 'Mitchell D. McPhetridge' \
  --subject 'Source-Anchored Candidate Extraction for Closed Local Ledgers; technical report v1.1' \
  --footer 'A Dual-Mode Sorter for MPLPB | v1.1 | 2026-11-17' \
  --invariant
```

For text only, use the same `--source` and add `--txt`. The invariant PDF option
fixes the PDF producer timestamp to its reproducibility epoch (2000-01-01); the
report date is printed in its content and is not that metadata epoch. Repeat builds
were byte-identical under the recorded renderer version. PDF metadata carries the
requested title and author. Text extraction and rendered-page inspection checked
content and layout; those checks do not validate the report's historical semantics.
