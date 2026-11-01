# Frozen probe corrections

## PRE-RELEASE-001 · 2026-11-01

The initial 93-question freeze preceded the finite-grammar preadmission scan. Nine language definitions included an unlicensed `or` disjunction and would have been guaranteed false refusals. Rather than quietly changing the gold, the original complete `probes.v1.pre-amendment.json` is retained. The **questions, ID order, expected source page IDs, and first-release labels remain unchanged**. These nine expected quotation strings were rewritten *before* any evaluation was accepted as a release score.

| Probe | Previous expected quotation | Amended expected quotation |
|---|---|---|
| GKH-0001 | The noun is a word naming a person, place, thing, or idea. | The noun is a word class naming people, places, things, and ideas. |
| GKH-0002 | The verb is a word expressing an action or state of being. | The verb is a word class expressing actions and states of being. |
| GKH-0004 | The adjective is a word modifying a noun or pronoun. | The adjective is a word class modifying nouns and pronouns. |
| GKH-0005 | The adverb is a word modifying a verb, adjective, or another adverb. | The adverb is a word class modifying verbs, adjectives, and other adverbs. |
| GKH-0006 | The conjunction is a word used to join words or clauses. | The conjunction is a word joining words and clauses. |
| GKH-0007 | The preposition is a word used with a noun phrase to express a relation such as place or time. | The preposition is a word expressing relationships of place, time, and direction through noun phrases. |
| GKH-0008 | The article is a word such as a, an, or the used before a noun phrase. | The article is a determiner used before a noun phrase, including a, an, and the. |
| GKH-0009 | The abstract noun is a noun naming an idea or quality. | The abstract noun is a noun naming ideas and qualities. |
| GKH-0010 | The proper noun is a name of a particular person or place. | The proper noun is a name identifying a particular entity. |

This is a developer-authored and revised evaluation, **not an independently blind holdout**. Future results must pin the amended probe bytes and disclose any further corrections rather than mutating a released manifest.

## PRE-RELEASE-002 · 2026-11-01

CI's exact finite-grammar admission validator rejected the original climate averaging interval description because it included a disjunction `or`. The content was narrowed from “The climate averaging interval is a period usually lasting thirty years or more.” to “The climate averaging interval is a standard thirty-year period.”, and its expected quotation was updated before any reference release metrics were accepted. Original gold remains in `probes.v1.pre-amendment.json`; this developer-authored probe remains non-independent. The question, ID, answerable flag and stage remain unchanged.
