---
name: sa:doc
description: Consolidate requirements + design + estimate (whichever exist) into one stakeholder-readable package document.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
argument-hint: "<slug from /sa:clarify>"
---

> Version: 1.0.0

<objective>
`/sa:doc <slug>` consolidates `ai/sa/<slug>/requirements.md`, `architecture.md`, and `estimation.md` —
whichever exist — into one clean, stakeholder-readable document at `ai/sa/<slug>/package.md`. No agent
dispatch — this command reads and writes directly, since consolidating already-written documents is
squarely within a command's own job, not a role needing a dedicated agent.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:design`/`/sa:estimate`: explicit argument if it names an existing `ai/sa/<slug>/`,
else glob `ai/sa/*/requirements.md` (exactly one → use it; multiple → ask which topic; none → tell the user
to run `/sa:clarify` first).
</step>

<step name="read-inputs">
Read whichever of `requirements.md`, `architecture.md`, `estimation.md` exist under `ai/sa/<slug>/`. Note
which are missing — the package still gets produced with what's available, clearly marked as partial.
</step>

<step name="write-package">
Write `ai/sa/<slug>/package.md`:
```markdown
# <Topic> — Requirements & Design Package
<date> · Status: <"Complete" if all three inputs exist, otherwise "Partial — missing: <list>">

## Executive Summary
<3-5 sentences: what's being asked for, the recommended approach, and the headline estimate (Likely
effort/cost) if available — written for someone who won't read past this section>

## Requirements
<the Requirements table from requirements.md, plus a one-line note on any still-open `to_clarify` items>

## Design
<the Approach + Components summary from architecture.md, if available — omit this section header
entirely if architecture.md doesn't exist yet, don't show an empty section>

## Estimate
<the Totals table from estimation.md, if available — same omission rule>

## Open Items
<consolidated list of every open question / assumption / to_clarify item across all three inputs, so a
stakeholder sees everything unresolved in one place>
```
</step>

<step name="offer-formats">
If a document-generation skill (e.g. a `docx`/`pptx` skill) is available in this session, mention that a
formatted version can be produced on request — don't generate one unprompted, markdown is the default
deliverable.
</step>

<step name="relay">
Return the package's Executive Summary and the file path written.
</step>
</process>

<rules>
- **Never claim completeness the inputs don't support.** A package built from partial inputs says so in
  its own Status line, not just in this command's chat output.
- **No new analysis.** This command only consolidates what `req-analyst`/`req-architect`/`req-estimator`
  already produced — it doesn't re-derive or second-guess their content.
</rules>
