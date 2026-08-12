---
name: sa:clarify
description: Clarify an incoming requirement/change request — free-form text or files already ingested via /sa:ingest — into a structured, reviewable requirements list, via req-analyst.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
argument-hint: "<slug, or a requirement/change-request description>"
---

> Version: 1.1.0

<objective>
`/sa:clarify <slug-or-description>` turns ingested source material and/or a free-form requirement or change
request into a structured requirements list via `req-analyst`, written to `ai/sa/<slug>/requirements.json`
(source of truth) and the rendered `ai/sa/<slug>/requirements.md`. It is the step every lane runs, and the
step every later artifact traces back to — a scope commitment with no `REQ-` behind it is the defect this
pipeline exists to prevent.
</objective>

<process>
<step name="resolve-input">
If `$ARGUMENTS` names an existing `ai/sa/<slug>/` (or an `ai/sa/<slug>/inputs/` folder, i.e. `/sa:ingest`
already ran), treat it as that slug — the ingested files are the source material, no free-form description
required, though one may be given alongside as extra verbal context. Otherwise take `$ARGUMENTS` as a
free-form REQ/CR description. If empty and no slug resolves, ask the user to describe it directly, or point
them at `/sa:ingest` if they meant to start from files.
</step>

<step name="read-lane">
Read `lane` from `ai/sa/<slug>/engagement.json` and pass it to the agent — it sets the rigor expected of
everything downstream.

If `engagement.json` does not exist, say so and recommend `/sa:triage` first, since without it there is no
lane, no `STATE.md` and no scaffold. Then proceed anyway if the user wants a standalone requirements pass:
this command works before an engagement is triaged, and `/sa:triage` can be run afterwards without
disturbing what was written here. Never infer a lane from the other artifacts.
</step>

<step name="dispatch">
Dispatch to `req-analyst` via `Agent`. Give it the resolved slug, the description if one was given, the
lane if one was read, and the current working directory as the target project (it detects project context
itself, or proceeds standalone if none exists).
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md` in the canonical shape defined in `sa-framework/ARTIFACT-SCHEMAS.md §6`:
phase `clarify`, last command `/sa:clarify`, and `Next` naming exactly one command — `/sa:estimate` on the
`rom` lane, `/sa:design` on every other lane (and when no lane is known). Append to phase history; never
rewrite prior lines.

If no `STATE.md` exists because `/sa:triage` was skipped, do not fabricate one — say that state tracking
starts at `/sa:triage`.
</step>

<step name="relay">
Return the agent's summary (requirement count, must/should/could split, `to_clarify` count, open questions
raised) and both file paths written, plus the slug it chose — the human needs that slug for every later
command on this topic. Then name the one next command that went into `STATE.md`.
</step>
</process>

<rules>
- **Thin dispatcher only.** All analysis happens inside `req-analyst`.
- **`requirements.json` is the source of truth**; `requirements.md` is rendered from it in the same run and
  is never hand-edited.
- **Never commit.** Writing artifacts is this pipeline's job; committing them is the human's.
</rules>
