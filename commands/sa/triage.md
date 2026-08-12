---
name: sa:triage
description: Classify an inbound SA ask into the rom / offer-sow / full-design lane and scaffold ai/sa/<slug>/ with engagement.json, ENGAGEMENT.md and STATE.md.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
argument-hint: "[path-or-description]"
---

> Version: 1.1.0 — minor: offers `/sa:brief` in the confirm step when inbound documents were classified
> unread, without making it a `Next` (the advisory carve-out, `ARTIFACT-SCHEMAS.md` §6).

<objective>
`/sa:triage [path-or-description]` classifies an inbound solution-architect ask into exactly one lane —
`rom`, `offer-sow`, or `full-design` — and scaffolds `ai/sa/<slug>/` per `sa-framework/ARTIFACT-SCHEMAS.md`
§6. It writes three files: `engagement.json` (the exact §4.1 schema, source of truth), `ENGAGEMENT.md`
(rendered from that JSON, what humans read), and `STATE.md` (phase / last command / next / phase history).
No agent dispatch and no deep analysis — the lane is the only judgment made here; requirements work
belongs to `/sa:clarify`. This is the first command of the pipeline, and the only one that writes
`engagement.json`; every downstream `/sa:*` command and `req-*` agent reads its `lane`.
</objective>

<process>
<step name="resolve-input">
Read `sa-framework/ARTIFACT-SCHEMAS.md` §2, §4.1 and §6 before writing anything — that file is the binding
contract for the JSON you are about to produce.

Then resolve `$ARGUMENTS`:
- A path to an existing file or folder → the inbound material. Do not copy, summarize or rewrite it; record
  its path. Extraction is `/sa:ingest`'s job.
- Free-form prose → the ask itself.
- Empty → check for an existing `ai/sa/*/engagement.json`. Exactly one → treat this as a re-triage of that
  slug (see `re-triage` below). Otherwise ask the user for a one-line description of the ask or a path.

Derive the slug as kebab-case `<client>-<project>` (e.g. `ams-osiguranje-client-portal`). If the client
isn't known yet, slug from the project alone. Confirm the derived slug with the user before creating
directories — the slug is the folder name and every downstream command's handle on this engagement.
</step>

<step name="re-triage">
If `ai/sa/<slug>/engagement.json` already exists, this is an update, not a new engagement. Read it first.
Skip the scaffold step entirely for directories that already exist, keep every value the human has since
edited unless the intake answers explicitly contradict it, increment `meta.revision`, and set
`meta.supersedes` to the previous revision number. Never delete or overwrite any other artifact in the
folder — a lane change rewrites `engagement.json`, `ENGAGEMENT.md` and `STATE.md` only.
</step>

<step name="intake-questions">
Use `AskUserQuestion` for **3-5** lane-classifying questions. Choose the most informative ones given what
`$ARGUMENTS` and any inbound material already answer — never ask all of them, and never ask something the
material already states. Candidates:

- Client and industry.
- Expected turnaround (today / this week / multi-week — or a hard date).
- Deliverable shape (verbal or email estimate / written priced offer / full design package).
- Rough commercial size (band, not a figure).
- Compliance flags at intake (GDPR / PCI / HIPAA / AI Act / national or sector-specific).
- Locale and deliverable language (these can differ — e.g. `sr-RS` locale, English document).
- Existing template or brand file to follow, and the client's mandated file-naming convention if any.
- New prospect or existing client; incumbent platform or greenfield.

Anything left unanswered is `to_clarify` in the JSON. Never fill a gap with a plausible-sounding guess.
</step>

<step name="classify">
Pick exactly one lane from `ARTIFACT-SCHEMAS.md` §4.1:

- `rom` — verbal/email ROM; sub-day turnaround; no formal client document; wide uncertainty acceptable.
  Pipeline: ingest → clarify → estimate → offer. Deliverable: a light offer.
- `offer-sow` — a written priced offer; multi-day turnaround; standard rigor. Pipeline: ingest → clarify →
  design → risk → estimate → estimate-review → offer → package. Deliverables: offer DOCX + estimation XLSX.
- `full-design` — multi-week; client-graded rigor; high commercial weight. Pipeline: everything in
  `offer-sow` plus review → design-detail → diagrams → package. Deliverables: the above plus HLD, LLD, and
  a pitch deck.

When genuinely ambiguous, classify **up one tier** and state why in `lane_rationale`. Over-delivering on
rigor is recoverable; discovering mid-bid that the ask needed a design package is not.
</step>

<step name="scaffold">
Create the §6 layout with **separate `mkdir -p` calls** — no brace expansion, which fails on non-bash
shells. The primary shell here is PowerShell on Windows; run these through the `Bash` tool (Git Bash), or
use `New-Item -ItemType Directory -Force <path>` per line if running them in PowerShell instead.

```bash
mkdir -p ai/sa/<slug>
mkdir -p ai/sa/<slug>/inputs
mkdir -p ai/sa/<slug>/audit
mkdir -p ai/sa/<slug>/diagrams
mkdir -p ai/sa/<slug>/deliverables
mkdir -p ai/sa/<slug>/deliverables/.snapshots
```

Skip any directory that already exists. Never touch `inputs/` beyond creating it — it is immutable once
`/sa:ingest` has written there.
</step>

<step name="write-engagement-json">
Write `ai/sa/<slug>/engagement.json` in exactly this shape (`ARTIFACT-SCHEMAS.md` §2 `meta` + §4.1 payload).
Use `to_clarify` as the value for any unknown string field, `[]` for an unknown list, `null` only where the
schema's own example shows `null`:

```json
{
  "meta": {
    "schema_version": "1.0",
    "artifact": "engagement",
    "slug": "<slug>",
    "lane": "<rom | offer-sow | full-design>",
    "generated_by": "sa:triage",
    "generated_at": "<ISO 8601 UTC>",
    "revision": 1,
    "supersedes": null
  },
  "client": "<name or to_clarify>",
  "project": "<name or to_clarify>",
  "lane": "<rom | offer-sow | full-design>",
  "lane_rationale": "<one or two sentences — why this lane, and why up-tiered if it was>",
  "industry": "<or to_clarify>",
  "counterparty_role": "<prospect | client | partner | internal | to_clarify>",
  "locale": "<e.g. sr-RS, hu-HU, en-US, or to_clarify>",
  "deliverable_language": "<e.g. English, or to_clarify>",
  "currency": "<e.g. EUR, or to_clarify>",
  "template_path": null,
  "file_naming": "<ORG>-<YYYY>-<CLIENT>-<NNN>-<artifact>-v<NN>.<ext>",
  "commercial_size": "<band or to_clarify>",
  "turnaround": "<date or relative, or to_clarify>",
  "incumbent_platform": "<or to_clarify>",
  "compliance_flags": [],
  "inbound_sources": [],
  "open_questions": []
}
```

`meta.lane` and the top-level `lane` are both present and must always agree. `inbound_sources` holds paths
relative to `ai/sa/<slug>/` (e.g. `inputs/RFP.docx.extracted.md`) — leave it `[]` until `/sa:ingest` runs.
`open_questions` holds every question the intake left unresolved, phrased as a question.
</step>

<step name="write-engagement-md">
Render `ai/sa/<slug>/ENGAGEMENT.md` **from the JSON you just wrote**, in the same run — never from memory
of what you intended to write (`ARTIFACT-SCHEMAS.md` §1):

```markdown
# Engagement — <client> — <project>

> Rendered from `engagement.json` rev <n>. Do not hand-edit — `/sa:triage` overwrites this file.

| Field | Value |
|---|---|
| Lane | `<lane>` |
| Lane rationale | <lane_rationale> |
| Client | <client> |
| Project | <project> |
| Industry | <industry> |
| Counterparty role | <counterparty_role> |
| Locale | <locale> |
| Deliverable language | <deliverable_language> |
| Currency | <currency> |
| Template | <template_path or "none"> |
| File naming | `<file_naming>` |
| Commercial size | <commercial_size> |
| Turnaround | <turnaround> |
| Incumbent platform | <incumbent_platform> |
| Compliance flags | <comma-joined, or "none raised at intake"> |

## Lane pipeline
<the §4.1 pipeline row for this lane, as a single arrow chain, plus its deliverables line>

## Inbound sources
- <path or "none yet — run /sa:ingest">

## Open questions at triage
- <question, or "none">
```
</step>

<step name="write-state-md">
Write `ai/sa/<slug>/STATE.md`. On a re-triage, **append** to the phase history — never rewrite or drop
prior lines:

```markdown
# State — <slug>

- **Lane**: `<lane>`
- **Phase**: triage
- **Last command**: `/sa:triage`
- **Last update**: <ISO 8601 UTC>
- **Next**: <the single recommended next command>

## Phase history
- <YYYY-MM-DD HH:MM UTC> — triage — initialized as `<lane>`
```

`Next` is `/sa:ingest <slug> <path>` when inbound files exist and haven't been extracted yet, otherwise
`/sa:clarify <slug>`.
</step>

<step name="confirm">
Print, and nothing more:

```
Triaged <slug> as <lane> (rev <n>).
<n> open questions · <n> fields marked to_clarify.
Scaffolded: ai/sa/<slug>/

Next: <the same command written into STATE.md's Next>
```

On a re-triage where the lane changed, add one line naming the old and new lane and which artifacts the
new lane additionally expects.

**When inbound documents exist and you asked the lane question without having read them**, add one further
line offering `/sa:brief <slug>` — a comprehension read (section map, key facts, integration surface,
conspicuous gaps) that this command is forbidden to produce itself. Offer it; never run it, and never write
it into `Next`. `/sa:brief` is an advisory non-artifact (`ARTIFACT-SCHEMAS.md` §6) and `brief` is not a
value in the phase enum, so it cannot be a `Next` without making `/sa:status` report a phase the lane model
doesn't contain. Skip the line entirely when `brief.md` already exists or the triage input was a free-form
description rather than a document — the lane is reversible, so a brief that changes the picture is
answered by re-running `/sa:triage`, not by having blocked on it here.
</step>
</process>

<rules>
- **Never invent client details.** Anything the user or the inbound material hasn't stated is
  `to_clarify` — not a plausible default, not an inference from the industry.
- **Never commit.** No `git add`, no `git commit`, no `git push` — staging and committing are the human's
  call under `CONSTITUTION.md` Articles II and VII. This is a deliberate divergence from the reference
  framework's version of this command, which auto-committed at the end.
- **Artifacts live under `ai/sa/<slug>/`, never `.sa/` at repo root.** This pipeline is multi-topic: a
  project accumulates many engagements side by side, and a single root-level folder would collide. Also a
  deliberate divergence from the reference framework's single-engagement layout.
- **Re-running is non-destructive.** Update `engagement.json` in place, bump `revision`, and leave every
  other artifact — including anything under `inputs/`, `audit/`, `diagrams/`, `deliverables/` — untouched.
- **The Markdown is generated, the JSON is the truth.** If they ever disagree, re-render `ENGAGEMENT.md`
  from `engagement.json`; never patch the Markdown to match.
- **No analysis here.** No requirements, no components, no estimate lines, no risks — this command decides
  a lane and writes state.
</rules>
