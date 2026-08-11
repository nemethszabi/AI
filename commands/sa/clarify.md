---
name: sa:clarify
description: Clarify an incoming requirement/change request — free-form text or files already ingested via /sa:ingest — into a structured, reviewable requirements list, via req-analyst.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
argument-hint: "<requirement or change-request description>"
---

> Version: 1.0.0

<objective>
`/sa:clarify <description>` turns a free-form requirement or change request into a structured requirements
list via `req-analyst`, written to `ai/sa/<slug>/requirements.md` in the current project (or the current
directory if run standalone, outside any project). This is normally the first step of the lightweight
clarify → design → estimate → doc pipeline.
</objective>

<process>
<step name="resolve-input">
If `$ARGUMENTS` names an existing `ai/sa/<slug>/inputs/` folder (i.e. `/sa:ingest` already ran for this
slug), treat it as that slug — the ingested files are the source material, no free-form description
required (though one may still be given alongside, e.g. extra verbal context on top of the ingested
files). Otherwise take `$ARGUMENTS` as a free-form REQ/CR description. If empty and no ingested slug is
found, ask the user to describe it directly, or point them at `/sa:ingest` if they meant to start from
files.
</step>

<step name="dispatch">
Dispatch to `req-analyst` via `Agent`. Give it the description and/or the resolved slug, and the current
working directory as the target project (it detects project context itself, or proceeds standalone if
none exists).
</step>

<step name="relay">
Return the agent's summary (requirement count, must/should/could split, `to_clarify` count) and the file
path written, plus the slug it chose — the human needs this slug for `/sa:design`, `/sa:estimate`, and
`/sa:doc` on this same topic.
</step>
</process>

<rules>
- **Thin dispatcher only.** All analysis happens inside `req-analyst`.
</rules>
