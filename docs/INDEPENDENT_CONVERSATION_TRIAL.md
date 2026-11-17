# Independent conversation trial

Last reviewed: 2026-11-17. See [current status and result-to-test index](CURRENT_STATUS.md). Dates and numeric results in historical validation sections retain their original scope; this review is not a rerun or independent certification.

Package role: [how this part fits Combined MPLPB](PACKAGE_GUIDE.md#conversation-and-resources). This guide covers bounded conversation or reference routing; context and source authority remain distinct.

Status: protocol prepared; no independent participants recruited or results collected.
Developer smoke tests are not independent validation.

Freeze the release commit before testing. Recruit 8–12 volunteers who did not
author the rules; include first-time users. Do not give them the regression
prompts or suggested conversation scripts. Have each choose two familiar
subjects and one unfamiliar subject, converse naturally for 10–15 minutes,
and try both chat and serious mode. Give them a small independently selected
source collection with known answerable and unanswerable questions.

Ask participants to include a correction, change subjects, return to a previous
subject, and ask an unanswered question in their own words. Record the version,
mode, source collection, and optional consented transcript. Allow pseudonyms;
do not request private personal details. Offer withdrawal and transcript deletion.

Two reviewers independently label each substantive reply:
- Relevance: 0 unrelated, 1 partial, 2 directly addresses the request.
- Memory: correct, incorrect, ambiguous/appropriately clarified, or not applicable.
- Evidence: supported by cited text, user declaration, research note, unsupported,
  or misclassified. Any unsupported claim tagged as MPLPB evidence is a boundary failure.
- Recovery: whether clarification/correction resolves within two further turns.
- Repetition: two consecutive generic fallback replies count as a repeated fallback.

Publish denominators, disagreements and adjudications, failures and anonymized
examples. Report modes separately; do not count greetings as factual precision.
Predeclare release targets: zero evidence-boundary failures, at least 90% correct
explicit memory recalls, and at least 80% directly relevant substantive replies.
These small-sample targets are development gates, not proof of production safety.
Do not tune against the held-out transcripts before the evaluation is finalized.

> Update 2026-11-16: The [public 52-case evidence suite](PUBLIC_EVIDENCE_TESTS.md) and [bounded expert relation path](HISTORICAL_EXPERT_PATH.md) document the current update. Prior dated measurements and preserved historical sources retain their original scope; this note does not rerun or revise them.
