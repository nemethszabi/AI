---
name: doc-brief
description: Read a document you're about to start work on and get a structured comprehension brief — what it is, its section map, the business problem, key facts and constraints, conspicuous gaps, and where to read closely — then ask follow-up questions answered from the source with citations. Use when someone needs to understand an inbound document before acting on it, or says they want to read/understand/get up to speed on a spec, RFP, TSD, standard, contract, or vendor document. Triggers on "summarize this document", "help me understand this doc", "what's in this TSD/RFP/spec", "brief me on this file", "read this before I start". Not for turning a document into requirements — that's /sa:clarify.
---

> Version: 1.0.0

# Doc Brief

Dispatches the `doc-briefer` agent to read one or more documents in its own context window and return a
structured comprehension brief. The agent reads the full document so the calling conversation doesn't have
to — a 50-page TSD costs tens of thousands of tokens to read inline, and that's context the human needs for
the actual work.

For an SA engagement with a slug, use `/sa:brief` instead — it resolves the engagement's already-extracted
inputs and writes the brief into the engagement folder. This skill is the general-purpose form: any
document, any folder, no pipeline involved.

## Usage

```
/doc-brief <path> [more paths...] [--out PATH] [--recursive]
```

- One or more file paths, or a folder. Folders are scanned one level deep unless `--recursive` is given.
- `--out` sets the brief's destination. Default is a `-brief.md` file beside the first source document.
- Supported directly: `.docx`, `.xlsx`, `.xls`, `.pdf`, `.csv`, `.md`, `.txt`.

## How to run it

1. Resolve the paths the user gave. If none were given, ask for one — don't guess at a document from the
   working directory's contents.
2. Dispatch the `doc-briefer` agent with the resolved paths, the output path, and whether recursion was
   requested. Run it in the background unless the user is waiting on the brief before doing anything else.
3. Relay the agent's summary and the brief's path. The agent's full report isn't shown to the user, so
   surface the counts that matter: the requirement/background/boilerplate split, how many named integrations
   are actually specified, how many gaps were found, and any extraction warnings.
4. Tell the user they can ask follow-up questions against the same agent while it still holds the document.

## Follow-up questions

The Q&A half is the point, not an extra. Once `doc-briefer` has read the document, send further questions to
that same agent with `SendMessage` — it still has the full text in context and answers with section
citations. A new dispatch would re-read and re-extract everything for nothing.

If the agent's session is gone, the fallback is the brief itself plus targeted `Grep` into the extracted
Markdown, whose path the agent reported.

## What this is not

`doc-briefer` produces comprehension, never requirements. It writes no REQ-IDs, no priorities, no design, no
estimate, no risk scores. If the user wants those, route them:

| They want | Command |
|---|---|
| Numbered, traceable requirements from the document | `/sa:clarify` |
| A lane decision and an engagement folder | `/sa:triage` |
| Durable, provenance-headed extraction into an engagement | `/sa:ingest` |
| Mechanical Excel or Word extraction with no interpretation at all | `office-doc-reader` |

A brief is a good input to `/sa:triage` — the lane call needs someone to have read the document, and
`/sa:triage` deliberately doesn't. Feed the brief to the human, not into the pipeline: nothing downstream
cites `brief.md`, and it is excluded from `/sa:package`'s freshness hash on purpose.

## Limits

Scanned or image-only PDFs, legacy `.doc` binaries, and content that lives inside embedded images are beyond
the zero-dependency extractors this skill relies on. The agent reports these plainly rather than guessing at
the content. The `document-skills` plugin (`docx`, `xlsx`, `pptx`, `pdf`) is the documented escalation —
invoke it deliberately, as a second pass, once the agent has named the limitation.
