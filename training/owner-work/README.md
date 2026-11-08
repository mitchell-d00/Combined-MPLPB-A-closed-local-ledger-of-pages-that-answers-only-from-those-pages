# Owner-authorized candidate material

Last reviewed: 2026-11-08.

`inventory.json` records the supplied source indexes, declared owner permission,
observed repository licenses, source URLs/hashes and actual preparation counts.
The source text/candidate passages are in a separate reviewable archive, not in
this app's runtime or default ledger. Forty-six public root READMEs were captured;
two were unavailable in the supported formats. Full PhilPeople/Academia/Medium
publications have not been ingested. No source fact or authorship was authenticated
by owning the repository or observing a license label.

Reproduce into a **new** directory:

```sh
python tools/prepare_owner_corpus.py --owner YOUR_LOGIN --permission 'Your explicit first-party authorization and scope' --output NEW_DIRECTORY
```

The manual `Prepare owner corpus` Actions workflow performs the same preparation
on a standard public-repository runner and retains an artifact. It does not train
or download model weights, use a GPU, run forever, or configure a paid API.

The result is candidate prose, not reviewed dialogue or a trained checkpoint.
Create and review conversational examples before any supervised fine-tuning;
keep validation/holdout material separate. Exact normalized stored evaluation
questions are screened out of candidate passages; paraphrase contamination and
mixed third-party rights still require review. Private app conversations are not
included. `public-dataset-candidate.json` identifies a possible separately licensed
public conversation source; it has not been downloaded or used for training.
