# Executable Gates and Human-Maintained Indexing: paper and probes

- `Executable_Gates_and_Human-Maintained_Indexing.md` / `.pdf`: the paper.
- `probes/run_probes.py`: seven paired work-boundary probes against `mplpb_work` (Table 1).
- `probes/results.json`: the raw output of those probes.
- `probes/git_probe.sh`: a test of the same rule kept as a README note and as a pre-receive hook (Table 2).

To reproduce:

```sh
git clone https://github.com/mitchell-d00/Combined-MPLPB-A-closed-local-ledger-of-pages-that-answers-only-from-those-pages mplpb
git -C mplpb checkout 6ba371ca07dd9269f28af762ed1971ad484fb6b5
python3 -I probes/run_probes.py mplpb results.json
sh probes/git_probe.sh
```

Tested with Python 3.13.18 and Git 2.43.0 on 21 November 2026.
