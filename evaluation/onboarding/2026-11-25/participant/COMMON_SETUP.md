# Common setup and task sheet

Both groups receive this same sheet and the same installed software and sources.
The administrator may help install Python and the supplied wheel before timing.
Use the enclosed, checksum-pinned wheel rather than upgrading from the network.

```sh
python -m pip install --no-index --no-deps combined_mplpb-2.1.0rc1-py3-none-any.whl
python pilot.py prepare
python pilot.py tasks
```

Open the supplied ENTRY.html or ENTRY.md as your assigned entry document. Use only the provided local engine for scored tasks; public documentation links may be read, but the live browser app is not the frozen pilot engine. The helper checks exact engine and collection bytes.

The administrator then supplies your assigned entry document and starts the
ten-minute timer. Work alone without coaching. The common interface supports
`python pilot.py ask N` and `python pilot.py passage N`, with optional `--claim`
and `--citation` indices starting at zero. Use task numbers1 through5.

For each task, record the answer you obtained, the passage you opened if any,
and what the available evidence establishes. Classify these five tasks in your
own words: source-supported answer, missing evidence, conflict, source-attributed
instruction, or unproved completion. Each task has a single frozen question.

Record failed commands, installation failures, missing output and tasks left
unfinished. Do not change the source collection or engine. Do not enter personal
or sensitive information. Return the anonymous response form and generated
participant-actions.jsonl to Mitchell. These are actual user observations;
software test runs are reported separately.
