---
name: sa:doc
description: Consolidate an engagement's JSON artifacts into one internal, team-readable package document. Not a client deliverable — that path is /sa:offer → /sa:audit → /sa:package.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
argument-hint: "<slug from /sa:triage>"
---

> Version: 2.1.0

<objective>
`/sa:doc <slug>` consolidates whichever of `ai/sa/<slug>/`'s artifacts exist into one clean document at
`ai/sa/<slug>/package.md`, for **internal** use — your own team, a colleague picking the engagement up, a
manager who wants the whole picture in one file. No agent dispatch: consolidating already-written artifacts
is squarely a command's own job.

This is **not** the client-facing path. That is `/sa:offer` (content) → `/sa:audit` (gate) →
`/sa:package` (the actual DOCX/XLSX/PPTX under `deliverables/`). Different document, different audience,
different rigor — see the rules below.
</objective>

<process>
<step name="resolve-slug">
Same resolution as `/sa:design`: explicit argument if it names an existing `ai/sa/<slug>/`, else glob
`ai/sa/*/requirements.json` (exactly one → use it; multiple → ask which engagement; none → tell the user to
run `/sa:triage` and `/sa:clarify` first).
</step>

<step name="read-inputs">
Read `engagement.json` for lane, client, project, currency and deliverable language. Then read whichever of
these exist under `ai/sa/<slug>/`:

| Artifact | Source of truth | Section it feeds |
|---|---|---|
| `requirements.json` | `req-analyst` | Requirements |
| `architecture.json` | `req-architect` | Design (High-Level) |
| `review.json` | `req-reviewer` | Design Review |
| `detailed-design.json` | `req-detailer` | Detailed Design |
| `risk-register.json` | `req-risk-officer` | Risks & Compliance |
| `estimation.json` | `req-estimator` | Effort |
| `estimate-review.json` | `req-estimate-critic` | Estimate Critique |
| `offer.json` | `req-offer` | Offer Position |

**Read the `.json`, not the rendered `.md`** — the JSON is the source of truth
(`sa-framework/ARTIFACT-SCHEMAS.md §1`) and carries IDs, statuses and computed figures the narrative
rounds off. Fall back to the paired `.md` **only** where no `.json` exists at all, and when you do, mark
that section `(pre-schema — read from <name>.md)` so nobody mistakes a legacy narrative for a validated
artifact.

Note which of the lane's expected artifacts are missing (`ARTIFACT-SCHEMAS.md §4.1`): `rom` expects
requirements, estimation, offer; `offer-sow` adds architecture, risk-register, estimate-review;
`full-design` adds review and detailed-design. The document is still produced from what's available —
clearly marked partial.
</step>

<step name="check-commercial-basis">
Read `estimation.json.basis.rate_card`. If it is `null` (or the card exists with all rates at `0`),
**state effort only** — no price, no cost, no derived total, not even an illustrative one. Say plainly:
"Effort only — no rate card configured; pricing is a management decision
(`ESTIMATION-METHOD.md §5`)."

If a rate card **was** used, present cost as the arithmetic consequence of effort × rate, labelled as an
input to a pricing decision rather than as the price — and never reproduce the rate card itself.

Lead with the **baseline** (must-have) figure — `estimation.json.rollup.baseline`, AI-assisted, per
`ESTIMATION-METHOD.md §9.1`. Show `rollup.optional`'s total separately, clearly marked as priced but not
included. If `basis.model` is `traditional`/`both` (opt-in only, per §2), show the `traditional` figure
alongside `ai_assisted` labelled as a comparison, never merged into one figure. If `basis.commitment_gate`
is set, carry it verbatim next to the baseline AI-assisted number.
</step>

<step name="write-package">
Write `ai/sa/<slug>/package.md`. Omit any section whose artifact doesn't exist — never emit an empty
heading:

```markdown
# <Client> — <Project> — Internal Package
<date> · Lane: `<lane>` · Status: <"Complete for lane" | "Partial — missing: <list>">

> **Internal document.** Consolidated from the JSON artifacts in `ai/sa/<slug>/` for the delivery team.
> Not for the client — the client-facing path is `/sa:offer` → `/sa:audit` → `/sa:package`, and its output
> lives in `deliverables/`.

## Executive Summary
<3-5 sentences: what's being asked for, the recommended approach, headline effort (and the one thing most
likely to change it) — written for someone who won't read past this section>

## Requirements
<table of REQ-NNN · priority · status · one-line description, from requirements.json; then a line naming
every still-open `to_clarify` item and every open question with its D-NNN id>

## Design (High-Level)
<chosen approach and why, the alternatives rejected and their reasons, one line per C-NNN component, the
QA-NNN targets, and every INT-NNN integration with its confidence — `assumed`/`unknown` integrations
called out explicitly>

## Design Review — Key Findings
<summary plus every high- and medium-severity F-NNN finding from review.json, with its coverage numbers
(requirements traced vs. total, and any untraced `must`)>

## Detailed Design (Low-Level)
<one line per component from detailed-design.json — name and purpose only; link to detailed-design.md
rather than reproducing interface sketches>

## Risks & Compliance
<the top-watchlist risks with derived severity, treatment and residual; the recommended contingency % and
its rationale; every risk with `priced_in: false`; every compliance obligation with `blocking_deliverable:
true`>

## Effort
<baseline (must-have) rollup best/likely/worst, AI-assisted, contingency and buffer shown as separate
figures with their own rationales; the optional (should/could) total shown separately and marked "not
included above"; `must` coverage; everything in `not_estimated` with its reason; a `traditional`
comparison figure only if one was explicitly produced — per the commercial basis resolved above>

## Estimate Critique
<finding count by severity, the recommended adjustments not yet applied, and any lifecycle gaps from
estimate-review.json — clearly marked advisory>

## Offer Position
<commercial basis, delivery phases, and the scope in/out counts from offer.json, plus a pointer to the
built deliverable under `deliverables/` if one exists — a summary of what was offered, not a second offer>

## Open Items
<one consolidated list of every open question, assumption, `to_clarify` and client dependency across all
artifacts, each with its own id and the artifact it came from, so nothing unresolved hides in a subsection>
```
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md` in the canonical shape defined in `sa-framework/ARTIFACT-SCHEMAS.md §6`:
set last command `/sa:doc` and the current timestamp, and append one phase-history line. **Leave `Phase`
and `Next` as they were** — `doc` is not a phase in §6's enum and this command advances nothing; an
internal consolidation must not make the pipeline look further along than it is. If `Next` is empty or
names `/sa:doc` itself, set it to `/sa:status <slug>`.
</step>

<step name="offer-formats">
If a document-generation skill is available in this session, mention that a formatted internal version can
be produced on request — don't generate one unprompted. Do **not** route this through `/sa:package`, which
exists only for gated client deliverables.
</step>

<step name="relay">
Return the Executive Summary, the file path written, the artifacts that fed it, and any that were missing
or read from a legacy `.md`.
</step>
</process>

<rules>
- **Internal and client-facing are different documents.** `package.md` is for the team;
  `deliverables/` is for the client, and only `/sa:offer` → `/sa:audit` → `/sa:package` produces it. Never
  describe this file as an offer, never suggest sending it to a client, and never let it stand in for the
  gated path because the artifacts "look finished".
- **Never state a price when `estimation.json.basis.rate_card` is `null`.** Effort only, and say why —
  inventing or illustrating a rate to make a document look complete is the exact failure
  `ESTIMATION-METHOD.md §5` exists to prevent. A rate card, if one was used, never appears here either.
- **JSON is the source of truth.** Read `.md` only where no `.json` exists, and label that section as such.
- **Never claim completeness the inputs don't support.** A partial package says so in its own Status line,
  not just in this command's chat output.
- **No new analysis.** This command consolidates what the `req-*` agents produced — it never re-derives a
  figure, re-scores a risk, softens a finding, or resolves an open question on their behalf.
- **Never commit.** Writing artifacts is this pipeline's job; committing them is the human's.
</rules>
