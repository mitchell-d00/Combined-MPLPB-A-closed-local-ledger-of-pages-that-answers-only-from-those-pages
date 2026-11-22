# Persona and corpus transfer panel

Last reviewed: 2026-11-22.

Eight scripted personas work with eight separately sealed collections. The
documents are invented fixtures. Care records contain observations and omissions
for the reader to distinguish. Folklore and speculative records retain their
story or fictional setting. Coelacanths are real animals, and the coelacanth
fixture uses a mock specimen catalog.

| Persona | Corpus | Evidence decision |
|---|---|---|
| Inez, shift operator | Municipal sewage treatment | A recorded observation time leaves the cause open |
| Jo, foster volunteer | Cat care | A meal observation leaves veterinary diagnosis open |
| Min, aquarium keeper | Aquarium fish care | A tank observation does not supply a general care recommendation |
| Rafi, greenhouse volunteer | Plant care | One tray's observation cannot explain another tray's outcome |
| Dara, folklore cataloger | Mystical creatures | A story supplies a claim about its own setting |
| Ellis, local archivist | Bigfoot reports | A witness description does not identify the figure |
| Sora, fiction archive editor | Alien and exocreature fiction | An in-world report is limited to the simulation |
| Niko, museum trainee | Coelacanth zoology | A specimen catalog does not give a wild population count |

Each collection has two source documents and four questions. One question
asks for a declared field by record ID. A second asks for the same value
using a natural description. The remaining two ask for an inference or an
absent fact. The runner checks native answer contracts and rereads quoted
spans against eligible records. It credits exact expected answers and flags
other supported or partial responses for semantic review.

## Replay and baseline

```sh
python -m test_tools.persona_corpus_transfer --output /tmp/persona-transfer.json
python -m unittest tests.test_persona_corpus_transfer -q
```

On the D20 repair engine at `d8e5b6d`, the strict reader found **8/8** exact
declared fields, **0/8** natural-description equivalents, and withheld support
on **16/16** negative controls. These are 32 authored questions, with no human
participants. The fixture and scoring expectations are public. The natural
questions change both wording and how the record is identified. The repeated
miss isolates a useful area to investigate, and a later study should vary
wording and identity cues independently before changing the grammar.

For independent real-source evaluation, capture openly licensed originals
and their stable references before writing or scoring questions. Ask what
each source records, who observed it, which restrictions it includes, and
when it leaves a conclusion open. Keep the new questions and answer key
with an outside custodian during development.

[Frozen panel](panel.json) · [Native baseline](native-baseline.json.gz) ·
[Test Index for humans and AI](../../docs/TEST_INDEX.md)

## Experimental synonym index

The prototype looks for reviewed whole phrases inside one collection. It
suggests record IDs and field labels and shows the phrases that matched.
When a phrase maps to competing IDs or field labels, the index reports
ambiguity and retains the alternatives. A lookup returns candidate selectors.
Review the intended record, field, and all conditions in the original question
before using those selectors with the strict reader.

```sh
python -m test_tools.synonym_index --collection coelacanth 'What catalogue number belongs to the coelacanth display specimen?'
python -m test_tools.synonym_index_study --output /tmp/synonym-study.json
python -m unittest tests.test_synonym_index -q
```

The unhinted native reader missed **16/16** authored natural questions.
The index produced one record and field candidate for all 16. After the
preselected study prompts were checked for what they ask, the native reader
returned **16/16** exact answers with verified source citations when supplied
both selectors. The same lookup also found candidate pairs on **8/8**
questions with an added, unresolved time condition. The study did not submit
those pairs for proof. This shows why a unique lexical match alone cannot
authorize a rewrite. A separate regression retains competing record and
field alternatives.

The catalog and questions were authored for this experiment, so the results
demonstrate the lookup-to-verification workflow under known vocabulary.
They do not measure blind language coverage. The default reader uses its
existing verification and grammar. [Synonym catalog](synonyms.json) ·
[Additional wording](synonym-probes.json) · [Native study](synonym-study.json.gz)
