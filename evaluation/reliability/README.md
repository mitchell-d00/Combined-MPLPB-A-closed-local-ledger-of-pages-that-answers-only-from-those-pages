# Reliability evidence

See [the complete review](../../docs/ANSWER_RELIABILITY.md) for individual frozen
failure diagnoses, exact metrics, compatibility and remaining limitations.

- `before-frozen.json`: legacy and old supported baseline observations.
- `baseline_support.py`: exact `tools/answer_support.py` at `715d1b5`, retained
  for reproduction only, not imported by runtime code.
- `development-cases.json`: 28 developer-authored adversarial cases. Used for fixes.
- `squad-sample.json`: 20 independently authored external questions with original
  contexts and labels. Selection fixed before evaluation; no fixes trained on it.
- `after.json`: old legacy, old supported and new supported outputs and metrics.

SQuAD attribution: Pranav Rajpurkar, Robin Jia, Percy Liang and the Stanford
SQuAD contributors/crowdworkers, SQuAD 2.0. Dataset source:
https://rajpurkar.github.io/SQuAD-explorer/ and
https://github.com/rajpurkar/SQuAD-explorer/blob/master/dataset/dev-v2.0.json .
Distributed under CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/ .
The subset selection/JSON packaging is a modification; original contexts,
questions and answers are preserved. The sample and its reproduced source text
in results remain CC BY-SA 4.0. The full downloaded dataset SHA-256 is recorded
in the sample; no live download is required to run this evaluation.

These data distinguish regression behavior from answer accuracy. No human
independent validation of MPLPB is claimed. Precision is null when no answers
are returned. Ambiguity, false refusals and answerable coverage are separate.

`mode-comparison.json` contains synthetic constrained-versus-free-chat examples; it is not an accuracy benchmark or a saved private conversation. See `docs/PROCEDURAL_CONSTRAINTS.md` for automatic tagging, source constraints and ephemeral-mode limits.
