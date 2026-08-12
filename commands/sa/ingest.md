---
name: sa:ingest
description: Extract inbound Excel/Word/PDF/text files into readable Markdown for an engagement, via req-ingestor — the on-ramp before /sa:clarify when you're starting from existing documents rather than a free-form description.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
argument-hint: "<slug> <file-or-folder-path...> [--recursive]"
---

> Version: 1.2.0

<objective>
`/sa:ingest <slug> <path...> [--recursive]` extracts one or more Excel/Word/PDF/text files into
`ai/sa/<slug>/inputs/*.extracted.md` via `req-ingestor`, so `/sa:clarify` has readable source material to
cite instead of requiring a free-form text description. Use it when the starting point is real files (an
RFP, a TSD, an existing estimate spreadsheet, a design doc) rather than a paragraph of prose.
</objective>

<process>
<step name="resolve-input">
Parse `$ARGUMENTS` as `<slug> <path...> [--recursive]`. The slug is a kebab-case topic name — normally the
one `/sa:triage` created, but it doesn't have to exist yet. If `$ARGUMENTS` is empty or no slug is given,
ask the user directly for a slug and the file(s)/folder to ingest. If only a slug is given with no path,
default to `ai/sa/<slug>/inbound/` and tell the user to drop files there if it's empty.

`--recursive` is opt-in only — without it, any folder path is scanned one level deep, subfolders listed but
not entered (see `req-ingestor`'s own rules for why: a subfolder can hold an unrelated prior analysis, and
silently pulling it in has caused real confusion before). Pass `--recursive` when you genuinely want every
file under a folder tree treated as source material, no exceptions.
</step>

<step name="read-lane">
Read `lane` from `ai/sa/<slug>/engagement.json` and pass it to the agent.

If `engagement.json` does not exist, say so and recommend `/sa:triage` first — it creates the slug, the
lane and the `ai/sa/<slug>/` scaffold including `inputs/`. Then proceed anyway if the user wants to extract
now; `/sa:triage` can be run afterwards and will not disturb what was ingested. Never infer a lane.
</step>

<step name="dispatch">
Dispatch to `req-ingestor` via `Agent`. Give it the slug, the lane if one was read, the resolved
file/folder path(s), and whether `--recursive` was set.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md` in the canonical shape defined in `sa-framework/ARTIFACT-SCHEMAS.md §6`:
phase `ingest`, last command `/sa:ingest`, next `/sa:clarify`. Append to phase history; never rewrite prior
lines. Record the extracted paths in `engagement.json`'s `inbound_sources` if that file exists, relative to
`ai/sa/<slug>/`.

If no `STATE.md` exists because `/sa:triage` was skipped, do not fabricate one — say that state tracking
starts at `/sa:triage`.
</step>

<step name="relay">
Return the agent's summary (files extracted, files skipped and why, warnings) and the index file path.
Remind the user that `/sa:clarify <slug>` is next — it picks up everything under `ai/sa/<slug>/inputs/`
automatically. If `req-ingestor` flagged a file it couldn't handle (scanned PDF, legacy `.doc`), mention
that the `document-skills` plugin (`anthropic-agent-skills` marketplace — `docx`/`xlsx`/`pptx`/`pdf`
skills, installed at user scope) is available in this session for that specific file via the `Skill` tool
— `req-ingestor` itself never reaches for it, this command surfaces it as an option for you to invoke.
</step>
</process>

<rules>
- **Thin dispatcher only.** All extraction happens inside `req-ingestor`.
- **`inputs/` is immutable.** Once a file is extracted there it is never edited, reformatted, corrected or
  re-summarized — not by this command, not by any later one, not by a human tidying it up. Downstream
  artifacts cite `inputs/<file>.extracted.md:<line>` as evidence, and that citation is worthless if the
  file can move under it. A bad extraction is re-run to a new file, never patched in place.
- **Extraction is not analysis.** This command and its agent never write a requirement, a component or an
  estimate line — that's `/sa:clarify`'s job on the next pass.
- **Never commit.** Writing artifacts is this pipeline's job; committing them is the human's.
</rules>
