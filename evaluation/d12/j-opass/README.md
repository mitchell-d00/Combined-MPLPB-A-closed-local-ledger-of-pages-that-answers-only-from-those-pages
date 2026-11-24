# J/Opass

Last reviewed: 2026-11-24.

J/Opass tests the handoff from strict proof to user-facing warnings. The
Observer records the documentary plan, native question parts where present,
matched spans under the measured search budgets, the strict outcome, checked
claims, and unresolved parts. The Judge uses deterministic rules to choose
which warnings to show and keeps the proof decision from Strict Ask.
[4score20 source trace](../4score20/README.md)

| Case | Presentation decision |
|---|---|
| Lodge’s duration | Report the missing proof rule. The narrow search already found the evidence. |
| May telegrams | Report both the missing proof rule and the spans missed at the narrow search budget. Flag the quote that crossed a statement boundary. Wider search found all four reference spans. |
| Final communiqué | Withhold the final wording. No draft comparison appears as the answer. |
| Matched docket and dates | Present the checked relationship, citations, and its source scope. |
| Token custody with missing returner | Present the checked holder and explicitly mark the returner unresolved. The signature supplies no returner claim. |
| Conflicting log times | Present both cited times and keep the single answer unresolved. |

The three historical rows reuse frozen D12 inputs. The other three are
authored controls run through the native engine. Search coverage on the
historical rows is measured against the retained reference key. That
measurement is available in this diagnostic and gives no proof authority to
a candidate. [Observer, Judge, and deterministic display records](native.json)

## Live model check

J/Opass gives the model two layout IDs. MPLPB constructs both layouts from
the same deterministic decision. It accepts only an allowed ID or a JSON
object containing exactly that ID, depending on the arm. A rejected reply
falls back to the compact layout. The answer contract and gate are rechecked
after each call. Model text goes into the evaluation log for inspection.

| Local inference arm | Calls | Valid layout choices | Changes to claims, citations, warnings, or proof |
|---|---:|---:|---:|
| Free text | 8 | 0 | 0 |
| JSON enum | 8 | 8 | 0 |

Both arms received six ordinary requests and two requests to overstate an
unresolved claim. The JSON arm always selected compact, including on the two
pressure cases. The free-text arm returned three completed replies with
invalid choices. Five ended at the adapter's invalid-output boundary.
The deterministic stacked layout is exercised separately by the regression
tests. These results measure a layout-selection gate on one small model.
The fixture exercises no model factual reasoning and makes no general model
reliability claim. [Prompts, replies, and resulting display](live-model.json)

## Reproduce

The evaluation uses the answer engine present at `c8762c3`. A local
deterministic replay produces byte-identical output.

```sh
out=$(mktemp -d)
python -m test_tools.j_opass --output "$out/native.json"
cmp "$out/native.json" evaluation/d12/j-opass/native.json
python -m unittest tests.test_j_opass -v
```

The live arm ran on CPU using the following pinned artifacts:

- llama.cpp `b6700` Ubuntu x64 ZIP, SHA-256
  `a6327798efc93e5b6ba377b866fcc9fbab5eaed12002b31b2b19d780b748db1f`.
  [Runtime release](https://github.com/ggml-org/llama.cpp/releases/tag/b6700)
- SmolLM2-135M-Instruct Q4_K_M GGUF at repository revision
  `09816acd5d99df7be770d85ea30822623dab342c`, SHA-256
  `2e8040ceae7815abe0dcb3540b9995eaa1fa0d2ca9e797d0a635ae4433c68c2d`.
  [Model weights](https://huggingface.co/bartowski/SmolLM2-135M-Instruct-GGUF/tree/09816acd5d99df7be770d85ea30822623dab342c)

Start the verified runtime on loopback with the downloaded model and run the
probe with an unused output path.

```sh
llama-server --model /path/to/model.gguf --alias smollm2-jopass \
  --host 127.0.0.1 --port 18089 --ctx-size 2048 --threads 2 --parallel 1
```

```sh
python -m test_tools.j_opass --model smollm2-jopass \
  --base-url http://127.0.0.1:18089/v1 --output /tmp/j-opass-live.json
```

This is an evaluation harness. The existing reader, narrator and application
entry points retain their normal behavior.
