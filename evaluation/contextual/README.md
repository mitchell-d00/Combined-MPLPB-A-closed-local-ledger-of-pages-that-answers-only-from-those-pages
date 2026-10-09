# Contextual chat experiments

This directory contains **synthetic developer tests, not independent human validation**.
The independent protocol is in [PROTOCOL.md](PROTOCOL.md); recruitment and blinded
human judgments remain pending. Existing 36-question evaluations are unchanged.

Run from the repository root:

```sh
python tools/evaluate_grounded_chat.py evaluation/contextual/developer-cases.json \
  --sha256 "$(cat evaluation/contextual/developer-cases.sha256)" \
  --out evaluation/contextual/developer-results.json
python tools/benchmark_grounded_chat.py --sizes 10 50 100 --repeats 5 \
  --out evaluation/contextual/scale-results.json
python tools/prepare_chat_review.py evaluation/contextual/developer-cases.json \
  --sha256 "$(cat evaluation/contextual/developer-cases.sha256)" \
  --out evaluation/contextual/blind-review-practice.json
```

The JSON records all 54 questions, outcomes, gold evidence, response traces, code
hashes and limitations. Six domains include permission/procedure traps, missing
attributes, conditions, topic drift and working-note distractions. Six answerable
paraphrases outside the recognizer deliberately expose its limited coverage.

| Development result | Contextual chat | Lexical page-return baseline |
| --- | ---: | ---: |
| Unsupported questions answered | 0 / 36 | 1 / 36 |
| Supported answers with gold evidence | 12 / 18 | 10 / 18 |
| Answer precision | 12 / 12 | 10 / 11 |
| Unnecessary refusals | 6 / 18 | 8 / 18 |

The six chat misses are all recorded as failures of coverage. These templated probes
were authored alongside the implementation; they are not an unseen holdout.
The 95% Wilson upper bound for 0/36 is about 9.6%, even before accounting for template
correlation. The results do not establish a low real-world error rate. Gold quotations
are a mechanical scoring aid; independent reviewers must judge semantic sufficiency.

Scale results contain raw timings and environment details for 10, 50 and 100 short
synthetic pages, five sequential questions each. Do not extrapolate these to production
traffic. Source building time is not a measurement of human authoring effort.

The practice review packet removes labels, scopes, exclusions and system outputs.
For real evaluation use independent question authors and two blinded reviewers, not
a relabeling of these public development cases. Copy the manifest structure, replace
inline pages with an explicitly pinned corpus root if needed, and retain reviewer
and adjudication records separately. Never put confidential corpora in this public
repository just to run the experiment.
