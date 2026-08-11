---
name: sa:ingest
description: Extract inbound Excel/Word/PDF/text files into readable Markdown for a topic, via req-ingestor — the on-ramp before /sa:clarify when you're starting from existing documents rather than a free-form description.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
argument-hint: "<slug> <file-or-folder-path...>"
---

> Version: 1.0.0

<objective>
`/sa:ingest <slug> <path...>` extracts one or more Excel/Word/PDF/text files into
`ai/sa/<slug>/inputs/*.extracted.md` via `req-ingestor`, so `/sa:clarify` has readable source material to
cite instead of requiring a free-form text description. Use this when the starting point is real files
(an RFP, an existing estimate spreadsheet, a design doc) rather than a paragraph of prose.
</objective>

<process>
<step name="resolve-input">
Parse `$ARGUMENTS` as `<slug> <path...>`. The slug is a kebab-case topic name — it doesn't need to exist
yet (this is often the *first* command run for a new topic). If `$ARGUMENTS` is empty or no slug is given,
ask the user directly for a topic slug and the file(s)/folder to ingest. If only a slug is given with no
path, default to `ai/sa/<slug>/inbound/` and tell the user to drop files there if it's empty.
</step>

<step name="dispatch">
Dispatch to `req-ingestor` via `Agent`. Give it the slug and the resolved file/folder path(s).
</step>

<step name="relay">
Return the agent's summary (files extracted, files skipped and why, warnings) and the index file path.
Remind the user that `/sa:clarify <slug>` is the next step — it will pick up everything under
`ai/sa/<slug>/inputs/` automatically. If `req-ingestor` flagged a file it couldn't handle (scanned PDF,
legacy `.doc`), mention that the `document-skills` plugin (`anthropic-agent-skills` marketplace —
`docx`/`xlsx`/`pptx`/`pdf` skills, installed at user scope) is available in this session for that specific
file via the `Skill` tool — `req-ingestor` itself never reaches for it, this command surfaces it as an
option for you to invoke.
</step>
</process>

<rules>
- **Thin dispatcher only.** All extraction happens inside `req-ingestor`.
- **Extraction is not analysis.** This command (and the agent it dispatches to) never writes a
  requirement, a component, or an estimate line — that's `/sa:clarify`'s job on the next pass.
</rules>
</output>
