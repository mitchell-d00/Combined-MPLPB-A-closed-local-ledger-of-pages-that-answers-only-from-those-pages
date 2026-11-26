# Newcomer navigation: software verification

Last reviewed: 2026-11-26.

The root README is below the **180-line limit**. It leads to three entry areas:
[MPLPB](../../docs/MPLPB.md), [Experimental Lab](../../docs/EXPERIMENTAL_LAB.md),
and [Testing and Training Apparatus](../../docs/TESTING_APPARATUS.md).
The [component map](../../docs/COMPONENT_MAP.md) maps all seven existing departments;
the [Test Index](../../docs/TEST_INDEX.md) remains the authoritative test inventory.
No implementation files, imports, commands or frozen evidence were moved.

## Exact released quick start

The README command block was extracted verbatim, then executed in a new empty
directory with a newly created virtual environment. Its only download was the
public small native ZIP; pip installed its wheel with `--no-index`.
The [receipt](released-verification/verification.json) records Python, README,
script, ZIP and wheel hashes. [Source fingerprints](released-source-fingerprints.json)
compare the wheel's native Python files against released main `c01021c`.

- [Exact commands](released-verification/commands.sh)
- [Complete standard output](released-verification/stdout.txt)
- [Shell trace and standard error](released-verification/stderr.txt)
- [Citation, partial, ownership and competing-owner commands](released-verification/additional-commands.json)

Expected first answer lines are:

```text
SUPPORTED ANSWER
Opening time: 09:00.
```

The missing-field command begins `NO SUPPORTED ANSWER` / `Not in the corpus.`
and exits 3. A supported answer exits 0. The write reports a new DOC-0001 and
its content hash; hashes and installation progress need not be copied by users.
The exact citation lives at `answer_contract.claims[].citations[]` in CLI JSON.
Its quote is `Opening time: 09:00.`. The partial preserves opening time and marks
closing time unresolved. Competing owners display `AMBIGUOUS`, exit 2, and retain
both exact owner statements. None of these invented examples establishes a real
museum's hours or a real studio's ownership.

Reproduce from a checkout (use fresh paths):

```sh
python tools/verify_readme_quickstart.py --work /tmp/mplpb-new-user --output /tmp/mplpb-new-user-check
```

## Retained verification failures

[Attempt 1](attempt-1/failure.json) executed the quick start but the host checker
looked for claims at the JSON root. [Attempt 2](attempt-2/failure.json) passed the
quick start and citation check but assumed the wrong competing-owner display and
exit code. Original checker sources, transcripts and failed classifications are
retained. The reader was not changed to satisfy either assumption. The third
clean run passed every check with the corrected documented CLI contract.

## Human usability and custody

This is same-operator software verification, not a newcomer experiment or an
independent semantic assessment. The [twelve-person trial](../onboarding/2026-11-25/README.md)
and its frozen documentation arms remain unchanged. Mitchell will supply actual
participant observations. Human execution, independent historical/semantic
adjudication, independent preparation/blinding and outside-custodian scoring
remain **NOT_RUN**.
