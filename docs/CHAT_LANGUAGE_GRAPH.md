# Base chat language graph

The offline resource `resources/chat_language_graph.json` connects phrase forms to subject aliases, then to intent nodes and existing read-only handlers. `tools/chat_language_graph.py` traverses these relations in the shared continuity pass before answer routing. Both buttons and typed requests use that pass, including a fresh session with zero collections loaded.

The first graph covers collection inspection, topic listing, system identity, search help, memory help and language help. For example, “Can you tell me about loaded MPLPB?” traverses `loaded mplpb -> loaded_collections -> inspect_loaded -> show loaded MPLPB`. Results come from current application state, not a stored list. Matching is bounded to complete supported phrases after polite-prefix normalization. It does not rewrite a literal repetition, negated command, arbitrary topic or partially recognized compound instruction. An existing identity clarification branch retains priority.

This is a foundation, not a general semantic graph or unrestricted conversation engine. It contains authored language relationships, not verified world facts. Adding a subject alias expands supported wording; it does not establish an evidential relationship between the named things. Each matched request records its graph version, resource hash and traversed path in the interpretation record. User memory, research notes and eligible MPLPB evidence retain their existing authority and delivery rules.

The browser composer also preserves a newly typed draft when an earlier answer arrives, and rejects concurrent submissions. It previously cleared the input unconditionally, which could erase the next message during a slow request.

Validation: graph phrase combinations and negative controls, public `App.chat` tests in both modes and on a fresh session, the full regression suite, and real Python/WebAssembly dialogue tests. Live browser testing reproduced the reported collection-routing bug. These tests are developer-authored; they do not establish full language coverage or independent human validation.
