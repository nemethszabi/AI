---
name: sa:help
description: Static reference for the sa: command namespace. No live analysis, no project context read.
allowed-tools: []
---

> Version: 2.3.0 — minor: `/sa:screen` (the bid/no-bid pass) documented, the advisory non-artifact pair
> and the screening-band-is-not-an-estimate boundary added to Shared conventions. 2.2.0 — `/sa:brief`'s
> `<slug-or-path>` pre-triage form documented (it was listed
> `<slug>`-only, hiding the form it was built for), and the read-before-you-classify habit added to
> Shared conventions. 2.1.0 — `/sa:brief` documented, and the `doc-briefer` exception to the `req-`
> prefix convention recorded so it isn't "corrected" later.

<reference>
# `sa:` commands — lane-driven Solution-Architect / presales pipeline

Global and generic — works in any project, or standalone with no project at all. Each engagement lives in
its own `ai/sa/<slug>/` folder, so many bids and change requests coexist side by side. Every artifact is
written twice: a `.json` (source of truth) and a rendered `.md` (what humans read).
`sa-framework/ARTIFACT-SCHEMAS.md` is the binding contract for both; `sa-framework/ESTIMATION-METHOD.md`
governs how numbers are derived and what they may be used for.

**v1 is human-driven.** One command per step, with human review in between, and none of them commit. The
single exception is **`/sa:screen`**, which chains the shallow front half (scaffold → ingest → clarify →
screen) because it terminates in an internal bid/no-bid decision rather than in anything a client receives —
it stops dead at the screen and never touches `/sa:design` onward. If you remember one thing from this page:
**`/sa:status <slug>` tells you the single next command** at any point in an engagement.

## Which lane do I need?

`/sa:triage` picks the lane and writes it into `engagement.json`; every command and agent downstream reads
it. The lane decides how much rigor you do and what the client ends up holding.

| If the ask is… | Lane | Pipeline | Deliverables |
|---|---|---|---|
| A ballpark for a call or an email, sub-day turnaround | `rom` | ingest → clarify → estimate → offer | a light offer, effort range only |
| A written priced offer, multi-day turnaround, standard rigor | `offer-sow` | ingest → clarify → design → risk → estimate → estimate-review → offer → audit → package | offer DOCX + estimation XLSX |
| A full design package, multi-week, high commercial weight | `full-design` | everything in `offer-sow`, plus review → design-detail → diagrams | the above plus HLD, LLD, pitch deck |

Genuinely ambiguous? `/sa:triage` classifies **up one tier** and states why — over-delivering on rigor is
recoverable, discovering mid-bid that the ask needed a design package is not. The lane is reversible:
re-run `/sa:triage` to change it, and it never re-scaffolds over existing artifacts.

## Commands

### Setup and navigation — every lane

| Command | What it produces | Dispatches to |
|---|---|---|
| `/sa:triage [path-or-description]` | `engagement.json` + `ENGAGEMENT.md` + `STATE.md`, and the `ai/sa/<slug>/` scaffold. Picks the lane. Always the first command. | none (direct) |
| `/sa:brief <slug-or-path>` | `brief.md` — a comprehension read of the inbound documents: section map, key facts, integration surface, conspicuous gaps, where to read closely. Advisory; touches no pipeline artifact or state. **Takes a bare file/folder path too, with no engagement yet** — that's the pre-triage form, and the one worth reaching for, because the lane call is what needs the read. Follow-ups go to the same agent via `SendMessage`. (`/doc-brief <path>` is the same agent for documents unrelated to any bid.) | `doc-briefer` |
| `/sa:screen <path-or-slug>` | **The bid/no-bid pass — "can we do this, and roughly what would it cost?"** Runs scaffold → ingest → clarify → screen in one command, producing a real `requirements.json` plus an advisory `screen.md`: feasibility verdict (`can-do` / `can-do-if` / `probably-not` / `cannot-assess`), named blockers, and an order-of-magnitude effort band that is **never quotable**. Writes no `estimation.json` and no `offer.json`. Runs on any lane — depth of pass and lane are independent axes. | `req-ingestor` → `req-analyst` → `req-screener` |
| `/sa:status [slug]` | Nothing written — a read-only report of lane, phase, artifacts present vs. the lane's expected set, gate freshness, open `to_clarify` counts, ending in exactly one recommended next command. | none (direct) |
| `/sa:help` | This reference. | none (direct) |

### The `rom` spine — run on every lane

| Command | What it produces | Dispatches to |
|---|---|---|
| `/sa:ingest <slug> <path...> [--recursive]` | `inputs/*.extracted.md` — inbound Excel/Word/PDF/text turned into citable Markdown. `inputs/` is immutable afterwards. Folder scans are one level deep unless `--recursive`. | `req-ingestor` |
| `/sa:clarify <slug-or-description>` | `requirements.json` + `requirements.md` — `REQ-NNN` items with priority, status, source, and the open questions blocking them. | `req-analyst` |
| `/sa:estimate <slug>` | `estimation.json` + `estimation.md` — three-point best/likely/worst per line with computed PERT, K-category compression, contingency rollup, coverage against `must` requirements. | `req-estimator` |
| `/sa:offer <slug>` | `offer.json` + `offer.md` — the client-facing offer's **content**: scope in/out, delivery plan, commercial basis, assumptions, exclusions, client dependencies. Every scope line traces to another artifact. | `req-offer` |

### Added by `offer-sow`

| Command | What it produces | Dispatches to |
|---|---|---|
| `/sa:design <slug>` | `architecture.json` + `architecture.md` — the HLD: approach with weighed alternatives, components, quality attributes, integrations, phasing, full traceability matrix. | `req-architect` |
| `/sa:risk <slug>` | `risk-register.json` + `risk-register.md` — probability × impact scored risks, compliance obligations, and the `contingency_recommendation` that `/sa:estimate` consumes. Run it **before** estimating. | `req-risk-officer` |
| `/sa:estimate-review <slug>` | `estimate-review.json` + `estimate-review.md` — an independent critique of the estimate against `ESTIMATION-METHOD.md`. Advisory; blocks nothing. | `req-estimate-critic` |
| `/sa:audit <slug>` | `audit/audit-<ts>.md` ending in a fenced `sa-verdict` block with a content-based `inputs_hash`. The only gate in the namespace. | `req-auditor` |
| `/sa:package <slug> [type] [--mode=]` | `deliverables/*.docx`, `*.xlsx`, `*.pptx` — the actual files a client receives. Refuses to build without a `PASS`/`PASS-WITH-WAIVERS` from `/sa:audit` on a **matching** hash. | none (direct, via `office-doc-builder`) |

### Added by `full-design`

| Command | What it produces | Dispatches to |
|---|---|---|
| `/sa:review <slug>` | `review.json` + `review.md` — narrative findings against the requirements, with coverage counts. Severity-ranked, **no** PASS/FAIL verdict. | `req-reviewer` |
| `/sa:design-detail <slug>` | `detailed-design.json` + `detailed-design.md` — the LLD: per-component interfaces, data model, key flows, deployment detail. | `req-detailer` |

Diagrams have no `/sa:` command of their own — use `/diagram` (the `mermaid-diagram-maker` agent) and write
into `ai/sa/<slug>/diagrams/`. `/sa:package` renders any `.mmd` there to `.png` before building.

### Internal, any lane

| Command | What it produces | Dispatches to |
|---|---|---|
| `/sa:doc <slug>` | `package.md` — one consolidated **internal** read of the engagement for your own team. Not a client deliverable. | none (direct) |

## Internal vs. client-facing — do not confuse these

Two different documents, two different audiences:

- **Internal**: `/sa:doc` → `ai/sa/<slug>/package.md`. For your team, your manager, your handover. It may
  carry raw effort, coverage gaps and open questions.
- **Client-facing**: `/sa:offer` → `/sa:audit` → `/sa:package` → `ai/sa/<slug>/deliverables/`. Reviewed,
  gated, versioned, and what the client actually receives.

Never send `package.md` to a client, and never treat `/sa:doc` as a substitute for the gated path.

## Shared conventions

- **JSON is the truth, Markdown is generated.** The `.md` is rendered from the `.json` in the same agent
  run. Never hand-edit a rendered `.md` — the next run overwrites it.
- **`inputs/` is immutable.** Once `/sa:ingest` has written there, nothing edits those files.
- **IDs are stable.** `REQ-`, `C-`, `QA-`, `INT-`, `R-`, `CMP-`, `L-`, `PH-`, `F-`, `A-`, `X-`, `D-` are
  never renumbered or reused; a dropped item becomes `withdrawn`, because downstream artifacts cite it.
- **Read before you classify.** `/sa:triage` commits you to a lane but is forbidden from interpreting the
  document, and `/sa:ingest` is extraction-only — so the pipeline's first interpreted output is
  `/sa:clarify`, two steps *after* the lane was chosen. Either triage blind or run `/sa:brief <path>`
  first. It is advisory, so it never appears in any `STATE.md` `Next`: triage and ingest offer it, and
  choosing it is always yours.
- **Two advisory non-artifacts, both optional, both before the binding work.** `brief.md` (`/sa:brief`)
  answers *what does this document say*; `screen.md` (`/sa:screen`) answers *can we do it and roughly what
  would it cost*. Neither has a JSON source of truth, neither defines an ID, nothing cites either, both are
  excluded from `inputs_hash`, and neither is a phase — see `ARTIFACT-SCHEMAS.md` §6.
- **A screening band is not an estimate and is never quotable.** `ESTIMATION-METHOD.md` §8: no PERT, no
  contingency, no compression, no calibration — by specification, not by shortfall. `/sa:estimate` is the
  only path to a number anyone may put in front of a client, and it never reads the band.
- **`STATE.md` is the shared state file.** Every command updates it — lane, phase, last command, and a
  `Next` naming exactly one command. Phase history is appended to, never rewritten.
- **One gate, at the end.** `/sa:review` and `/sa:estimate-review` produce findings, not verdicts. Refusal
  lives in `/sa:package`, and the remedy is always to re-run `/sa:audit`, never to weaken the check.
- **Freshness is content-based**, never mtime — change an artifact and the gate goes stale until re-audited.
- **Effort is not price.** No rate card found means effort-only output, stated plainly; a rate card never
  appears in a client-facing file, only the arithmetic someone chose to show.
- **Nothing here commits.** Writing artifacts is the pipeline's job; `git add`/`git commit` is yours.
- **Agents are `req-`-prefixed** (`req-analyst`, `req-architect`, `req-detailer`, `req-reviewer`,
  `req-risk-officer`, `req-estimator`, `req-estimate-critic`, `req-offer`, `req-auditor`, `req-ingestor`)
  specifically to avoid colliding with same-named agents from other installed frameworks. **`doc-briefer`
  is a deliberate exception, not a naming slip** — it is reusable outside this pipeline entirely (that's
  what `/doc-brief` exists for), so prefixing it `req-` would misdescribe it. Don't "fix" it.
- All agents read the target project's `CLAUDE.md` / `ai/context/*.md` when run inside one, and proceed
  standalone (saying so) when not — this pipeline works before a project exists.
- `.xlsx`/`.xls`/`.docx` extraction uses the `office-doc-reader` skill; `.pdf` uses the built-in `Read`
  tool. Deliverable generation uses `office-doc-builder`, escalating to the `document-skills` plugin when
  a document must be patched in place rather than regenerated.

This command performs no live analysis — it only prints the reference above. For where a specific
engagement actually stands, run `/sa:status <slug>`.
</reference>
