# Guided conversational interface

On the first visit, the app asks whether the user wants guidance. Yes, guide me
opens a saved four-step tutor in Chat. Declining hides the invitation; Guide me
in the header is always available after startup. The choice is a browser preference,
separate from source captures and chats. Wikipedia is the default topic source.

The tutor introduces MPLPB, offers existing pages or topic exploration, teaches
source questions, then explains saving and clearing. “Next step”, “previous step”
and “stop guide” navigate without deleting data. At the topic step, a short topic
reply such as “dinosaurs” offers explicit search/selection choices. A successful
search build carries guide progress into its new collection without copying old
working notes. Guide state saves with its chat and survives refresh.

Show my MPLPB presents eligible local titles and exact topic choices in chat.
If verification is blocked, it explains that saved files remain and offers help
with a fresh search, explicit reimport or confirmed clearing. It does not unlock
invalid sources. App help also works in Ask without requiring a valid source
corpus. The answer is labelled interface instructions, not a source answer.

Suggested questions fill the composer and require Send. A topic learning request
offers topic/search choices; it never silently fetches. Common source phrases
like “Can you summarize this?” map to existing pinned-source operations and record
the interpreted command in the decision trace. Summaries remain source excerpts.

Help matching recognizes finite aliases and constrained procedural word patterns
about app use. This is not general semantic understanding. Unknown world questions
still use the original lexical reader, ambiguity and refusal rules. Interface
lessons are program-authored instructions, not facts acquired from a corpus.

Walk back: revert tutor, UI and App routing together. Preserve saved chats and
source captures. New guide state is chat memory; removing this feature does not
justify rewriting frozen probes or historical source captures.

# Light topic conversation

Chat supports a finite conversational layer for handling topics. With a page selected, “let’s talk about it”, “I’m confused”, “that’s interesting”, and “what should I ask next” offer an overview, source inspection, or another page. Without a selected page, it asks the user to choose material. Suggestions require Send and do not fetch automatically.

“Keep it short” and “give me more detail” save a conversational style in the current chat. This changes navigation replies, not source quotations. Each reply has a `response_structure` containing its intent, topic, style and next step, with `factual_claims: false`. Its authority is `conversation_structure`, with no source evidence asserted. Topic labels are saved selections, not newly verified source claims. Factual questions still use the existing reader and provenance gate. Opinions are not fabricated. Unrecognized wording is not general semantic understanding.


## Clickable chat links

Every title displayed by a new “show my MPLPB” response is selectable directly in chat. Selecting it sends an exact local topic-selection request through the existing reader, retaining profile and provenance checks. Suggested questions still fill the composer for review before Send. Historical list turns without structured title metadata remain plain text; ask for a fresh list to get selectable titles.

HTTP and HTTPS addresses in chat messages, quoted relation evidence and decision details open in a separate tab. Source text is escaped before rendering. Other schemes and URLs containing embedded credentials remain text. Clicking a web link visits that site; it does not import it or verify it as MPLPB evidence.

Walk back: revert the link renderer and structured topic-list field together; saved chat text and source pins need no rewriting.

## Small talk and optional topic transitions

Greetings, casual day-to-day phrases, purpose questions and a canned joke have finite, deterministic replies. These replies do not claim feelings or personal experiences. Creator questions still read the sealed self-reference. The “Just chat” button fills the composer.

When a recognized casual message contains an exact eligible title from the current collection, the bot offers a source-backed discussion. Title matching is literal, with word boundaries; it is not semantic topic detection. No topic selection or network request happens until acceptance. A single title can be accepted with “yes please”; several titles require choosing one. “Keep chatting” clears the offer. Offers survive reopening the chat, but cannot authorize a selection after a corpus/profile change. Acceptance rechecks source eligibility. Blocked collections can still small-talk but cannot supply topic offers from invalid pages.

Walk back: revert small-talk routing, templates and UI together. Preserve existing saved chats, notes, captures and evaluation probes; obsolete pending offers are inert if the feature is removed.
