# Twelve-person first-use pilot materials

Last reviewed: 2026-11-25.

**Prepared, human execution NOT_RUN.** Mitchell will recruit twelve first-time
users and return actual uncoached observations. There are no participant results.
[Null results](results.json), [frozen materials](freeze.json), [protocol](PROTOCOL.md).

Give each anonymous participant the package assigned by the administrator:
[existing documentation](packages/onboard-existing.zip) or
[compact path](packages/onboard-new_path.zip). Both include the same400KBwheel,
helper, five tasks and fixed synthetic collection. Only ENTRY.md and ENTRY.html
differ. [Package checksums and parity](packages/packages.json). The helper refuses
a changed engine or collection. Each bundle was extracted and run against the
installed wheel with isolated Python; all five native contracts match exactly
and citation opening passes. [Software checks](software-checks/bundle-parity.json).
Those executions are software checks, not simulated human observations.

The engine is fixed at7f6641d, wheel SHA-256
70db08aec72861cc17fea8bc08b7eb6bc7986764e4adf47d0e04ead496253303.
The retained existing entry is byte-exact from2ab4b01 before navigation edits.
The compact path is an unvalidated pilot intervention. Both documentation
versions, collection, tasks, rubric and packages are frozen before human work.
Markdown3.8.2 renders the supplied HTML, with relative repository links pinned
to the control revision. Public outbound content is outside the scored task;
use only the provided local engine.

[Assignment](administrator-assignment.json) and [rubric](administrator-key.json)
are administrator materials, not included in participant bundles. Give six
participants each version. Start ten minutes after identical setup assistance;
then no coaching. Preserve command failures, incomplete tasks and protocol
deviations. Return anonymous forms and actual logs; do not replace missing
participants or fill absent scores. Correct classification needs an explanation
of the source distinction, not just one of the five labels.

Predeclared acceptance: new-path answer-and-citation success at least5/6, at
least two more successes than existing documentation, and at least5/6 correctly
classifying four of five outcomes. These are small-pilot thresholds, not a
population estimate. tools/score_onboarding_pilot.py summarizes actual returned
judgments and checks the frozen assignment and wheel; its arithmetic unit
controls are synthetic and never enter the human results.

Independent historical accuracy, semantic adjudication and native OOCC remain
NOT_RUN; onboarding measures a different question.

The supplied pilot measures this fixed native task path; it does not measure
full browser onboarding or broad research ability. Use a fresh Python environment
for identical setup before timing. Record setup failures separately. Administrator
judgments feed the scoring tool only after actual forms/logs are returned.
