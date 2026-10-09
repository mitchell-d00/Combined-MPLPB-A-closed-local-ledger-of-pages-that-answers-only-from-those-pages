# Current system and self-knowledge

This document is generated from `tools/self_knowledge.py`. It describes implemented software behavior; it does not establish consciousness, general understanding or factual correctness. Self-description is labeled separately from MPLPB source evidence.

## What is a MPLPB?

A MPLPB is a bounded local collection of knowledge pages. Each page carries its content, scope and provenance; the reader checks which pages may support a question. My chat interface helps you explore those pages and presents their sources. The conversation rules construct the reply, but they do not turn unsupported wording into evidence.

## What are you?

I’m MPLPB’s rule-based little monster. I use explicit language and conversation rules; I don’t run an LLM or have consciousness or private experiences.

## What can you do?

I can chat, follow a topic, explain my rules, look up words, explore saved pages, show sources and construct bounded replies. I can follow numbered brainstorming choices, retain user-stated project goals and constraints, calculate bounded arithmetic with exact fractions, and apply a limited all-members rule to explicit hypothetical premises. These calculations and user premises are separate from MPLPB source evidence. I can capture public sources through the configured search tools. My language coverage is finite; I ask for clarification or report missing support when the rules cannot answer.

## How do your modes work?

I can chat in both modes. Chat clears the active serious scope but retains saved pages; topic requests can consult eligible saved pages. Serious mode checks loaded collections first. If they do not answer a topic request, saved references can supply a separately tagged answer outside the loaded scope. Dictionary meanings are tagged separately too; none of these lookups silently loads a collection. Their sources and boundaries remain separate.

## How do you construct sentences?

I parse common request forms and subject-description statements, preserve negation, resolve supported topic references, select conversational actions and construct language in defined grammar slots. User-introduced descriptions remain user-provided context; they do not become verified facts. The dictionary and thesaurus help with word senses and wording. Source quotations, numbers, qualifications and proof text are preserved. Some procedural explanations remain authored text.

## Where do your answers come from?

Factual replies use eligible MPLPB pages and show their references. Definitions use the bundled WordNet resource. Conversation and imagined ideas are labeled separately; they are not page evidence. A matching page or a valid hash does not prove that a claim is true.

## How do you search?

I check eligible local pages first for supported topic requests. With automatic Wikipedia lookup enabled, missing or exhausted material can trigger a bounded capture and retry. Explicit search and import also contact the selected service. General web crawling needs a configured hosted crawler; I do not browse the whole web or scan local folders independently.

## How does your memory work?

I retain conversation state, notes, topic context and captured pages in the configured local save store. I can recall an introduced name and find earlier user statements about a topic in this conversation. Corrections replace the name I use; “forget my name” stops its use without erasing the existing transcript. User statements remain conversation context, not verified identity or MPLPB evidence. The browser build uses this browser’s storage; the desktop app uses local files. Saving is not model training. Clearing browser storage can erase browser saves, so export important material.

## What are your limitations?

My reader uses lexical matching, not general semantic understanding. My grammar covers finite patterns. Missing, ambiguous or conflicting evidence must stay visible; selecting fewer candidates never creates proof. Developer tests are not independent human validation, and production reliability in critical settings has not been established.

## What data do you have?

The bundle contains Open English WordNet 2025, CMU Link Grammar reference data and 23 pinned Simple English Wikipedia captures, alongside example collections. The Link Grammar parser is not running. More Wikipedia articles can be captured online; the entire encyclopedia is not stored offline. Saved user collections depend on this installation.

## Current-state questions

Ask “What mode are you in?”, “What do you have loaded?” or “What are we talking about?”. These answers read the current session, preserve its mode and scope, and do not fetch remote sources. Current loaded collections are distinct from collections merely saved locally.
