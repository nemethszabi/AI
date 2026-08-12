# The `/sa:*` Workflow — Requirement to Offer

How to take an inbound client requirement — a TSD, an RFP, a change request, or a paragraph in an email —
and turn it into a reviewed solution, a defensible estimate, and a client-facing offer.

This is the **presales / bid** pipeline. It is not the same job as designing something you've already been
contracted to build; see [Two different jobs](#two-different-jobs) below for why that distinction drives
the whole design.

- **Doctrine**: `sa-framework\ARTIFACT-SCHEMAS.md` (what artifacts look like) ·
  `sa-framework\ESTIMATION-METHOD.md` (how numbers are derived)
- **Quick reference**: `/sa:help`
- **Where am I?**: `/sa:status`

---

## Two different jobs

The `sa:` namespace covers two workflows that look similar and fail differently.

| | **Internal solution design** | **Presales / bid response** |
|---|---|---|
| Trigger | We're going to build this | A client hands us a TSD or RFP |
| Audience | Our own dev team | The client, contractually |
| Ends in | HLD/LLD → handoff to `dev:` | Offer + estimate → signature |
| Failure mode | Technical — the wrong design | **Commercial** — under-priced, unbounded scope, risk silently absorbed |

Before v1 of this workflow the pipeline only served the left column: it terminated in `package.md`, an
internal consolidation. Nothing produced a client-facing priced document, and the estimation method that
had been developed on real bids lived in a single spreadsheet in one project folder rather than in the
framework.

v1 adds the right column. The **lane** you pick at triage is what selects between them.

---

## The three lanes

Pick once, at `/sa:triage`. It's reversible — re-running triage updates the engagement in place.

### `rom` — rough order of magnitude
Hours. A number for a conversation, not a document to sign.

```
/sa:ingest → /sa:clarify → /sa:estimate → /sa:offer
```

### `offer-sow` — written priced offer
Days. **The default for an inbound TSD or RFP.**

```
/sa:ingest → /sa:clarify → /sa:design → /sa:risk → /sa:estimate
           → /sa:estimate-review → /sa:offer → /sa:audit → /sa:package
```

### `full-design` — full design package
Weeks. Client-graded rigor, high commercial weight.

```
…everything above, plus /sa:review, /sa:design-detail, /diagram,
and a richer package set (HLD, LLD, pitch deck)
```

When a case is genuinely ambiguous, triage classifies **up** one tier and says why. Over-delivering on a
small bid costs a few hours; under-delivering on a large one costs the bid.

---

## The commands

| Command | Produces | Agent |
|---|---|---|
| `/sa:triage` | `engagement.json` + `ENGAGEMENT.md` + `STATE.md`, and the lane | — |
| `/sa:brief` | `brief.md` — a comprehension read of the inbound documents *(advisory)* | `doc-briefer` |
| `/sa:ingest` | `inputs/*.extracted.md` from Excel/Word/PDF | `req-ingestor` |
| `/sa:clarify` | `requirements.json` — REQ-IDs, priority, status, source | `req-analyst` |
| `/sa:design` | `architecture.json` — HLD, components, NFRs, integrations, phasing | `req-architect` |
| `/sa:review` | `review.json` — narrative critique of the design | `req-reviewer` |
| `/sa:design-detail` | `detailed-design.json` — LLD *(full-design lane only)* | `req-detailer` |
| `/sa:risk` | `risk-register.json` — scored risks + compliance register | `req-risk-officer` |
| `/sa:estimate` | `estimation.json` — three-point effort, one or two delivery models | `req-estimator` |
| `/sa:estimate-review` | `estimate-review.json` — optimism bias, coverage, lifecycle gaps | `req-estimate-critic` |
| `/sa:offer` | `offer.json` — the client-facing content | `req-offer` |
| `/sa:audit` | `audit/audit-<ts>.md` — **the gate** | `req-auditor` |
| `/sa:package` | `deliverables/*.docx`, `*.xlsx`, `*.pptx` | — |
| `/sa:status` | Where you are and the single next command | — |
| `/sa:doc` | `package.md` — **internal** consolidation | — |
| `/sa:help` | Static reference | — |

**`/sa:doc` and `/sa:offer` are not the same thing.** `/sa:doc` is an internal consolidation for your own
team. `/sa:offer` → `/sa:audit` → `/sa:package` is the client-facing path. Confusing them is how internal
risk language reaches a client.

**`/sa:brief` is deliberately absent from all three lane sequences.** It is an *advisory non-artifact*
(`ARTIFACT-SCHEMAS.md` §6): it writes no JSON, defines no IDs, updates no `STATE.md`, and is excluded from
`/sa:package`'s `inputs_hash`, so it can never stale a gate. Run it, or don't — the pipeline behaves
identically either way. Don't add it to a lane chain.

Its reason to exist is a gap in the ordering above: `/sa:triage` makes you commit to a lane, which
determines everything downstream, but triage is forbidden from *interpreting* the inbound material ("No
analysis here"), and `/sa:ingest` is likewise extraction-only. The first interpreted output is
`/sa:clarify` — two steps after the lane was chosen. `/sa:brief` closes that without weakening either
rule. `/doc-brief <path>` is the same thing outside an engagement.

---

## Five design decisions worth understanding

### 1. Every artifact is written twice

Each step writes `<artifact>.json` (source of truth) **and** renders `<artifact>.md` from it in the same
run. The Markdown is what you read; the JSON is what the pipeline reads.

This buys four things: content-hash gating, real XLSX generation with live cells, cross-artifact
validation as set operations over IDs, and patch-mode document editing. The cost is honest — two
representations that can drift — which is why the render always comes *from* the JSON just written, never
from the agent's memory of what it meant to write.

**Never hand-edit a rendered `.md`.** The next run overwrites it. Change the source and re-run.

### 2. Risk feeds contingency; contingency is never a default

`req-risk-officer` scores each risk by probability × impact, **derives** severity from a fixed matrix, and
recommends a contingency band from the register's composition. `req-estimator` *consumes* that
recommendation — it doesn't invent a percentage.

Two rules keep this honest:
- Every integration marked `assumed` or `unknown` **must** produce a risk. Unspecified interfaces are the
  most reliable cause of estimate failure.
- Every risk marked `priced_in: false` **must** appear as an exclusion in the offer. An unpriced,
  undisclosed risk is the exact failure this pipeline exists to prevent.

### 3. Effort is not price

`req-estimator` produces effort. It never produces price. With no rate card it says so plainly rather than
inventing a number; with one, cost is presented as arithmetic offered *into* a pricing decision, not as
the decision.

This matters most under an AI-assisted model, where pricing man-days against a compressed base can quietly
destroy revenue on work whose value to the client hasn't changed. The pipeline flags that; it doesn't
resolve it.

### 4. Compression is differentiated, never uniform

Where an AI-assisted estimate is produced, each line is compressed by its **own** work-type factor
(`ESTIMATION-METHOD.md §2`): UI and CRUD compress hard, external integration barely, UAT and coordination
almost not at all.

The most expensive misreading of a compressed estimate is generalising one headline factor to everything.
Calendar time, client decisions, third-party roadmaps and UAT windows **do not compress**. Every
AI-assisted estimate says this out loud, and the offer repeats it.

An AI-assisted figure also stays **uncommitted** until a short calibration sprint measures real velocity on
real items from *this* engagement. Until then it's quoted as a range with the gate named. Present that as
a strength — it converts an unbounded estimation risk into a bounded, client-visible checkpoint.

### 5. One hard gate, in one place

`/sa:package` refuses to build a client deliverable unless `/sa:audit` shows `PASS` or
`PASS-WITH-WAIVERS` **on a matching content hash**. Change any artifact and the gate goes stale — by
content, never by timestamp, so touching a file without changing it doesn't invalidate anything.

`req-auditor` is deliberately **mechanical**: it checks that artifacts agree with each other, never
whether a judgment was good. That's what makes the gate unarguable. Judgment lives in `/sa:review` and
`/sa:estimate-review`, and neither of those blocks anything.

Six checks are **blocking and unwaivable**, each one a defect that would otherwise reach a client:

1. An offer scope line with no traceability
2. A `must` requirement with no estimate and no reasoned deferral
3. A `priced_in: false` risk with no exclusion
4. A broken ID reference between artifacts
5. Offer scope containing a `to_clarify`, unestimated, or unrequested `could` item
6. A price stated with no rate card behind it

---

## Worked example — an inbound TSD

```powershell
/doc-brief  "d:\WORK\Client\Their_TSD_v1.0.docx"
# → optional but recommended: read it before you classify it. Section map, key facts,
#   integration surface, conspicuous gaps. Ask follow-ups against the same agent.

/sa:triage  "d:\WORK\Client\Their_TSD_v1.0.docx"
# → asks 3-5 intake questions, classifies the lane, scaffolds ai/sa/<slug>/

/sa:ingest  <slug>              # TSD → inputs/*.extracted.md
/sa:brief   <slug>              # → re-brief from the extractions, into ai/sa/<slug>/brief.md
                                #   (skip if you already ran /doc-brief above)
/sa:clarify <slug>              # → REQ-IDs, with to_clarify where the TSD is vague
/sa:design  <slug>              # → HLD; integrations marked assumed where no spec exists
/sa:risk    <slug>              # → every assumed integration becomes a scored risk
/sa:estimate <slug>             # → three-point effort; contingency from the register
/sa:estimate-review <slug>      # → optimism bias, lifecycle gaps
/sa:offer   <slug>              # → client-facing content
/sa:audit   <slug>              # → the gate
/sa:package <slug> all          # → DOCX + XLSX under deliverables/
```

Run `/sa:status <slug>` at any point to see the lane, the phase, which artifacts exist, whether the gate
is stale, and the single next command.

**Review between steps.** Each command's output is a draft. The pipeline's value is that a human sees
requirements before design, design before estimate, and estimate before offer — not that it runs
unattended.

### What good looks like on a vague TSD

An inbound TSD with no API specifications and a page of unresolved decisions should *not* produce one
confident number. It should produce a fixed-price Discovery phase, a re-estimate after it, a risk register
naming every unspecified interface, and an offer whose exclusions and client dependencies are explicit.
That's not hedging — it's the more defensible commercial position, and it's what
`ESTIMATION-METHOD.md §5` steers the pipeline toward.

---

## Setup

Optional but recommended before your first priced offer:

```powershell
# Rate card — effort-only output until this exists
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\estimation-data" | Out-Null
Copy-Item "d:\_AI_GIT\estimation-data\rates.yaml.example" `
          "$env:USERPROFILE\.claude\estimation-data\rates.yaml"
# then edit it — placeholder zero rates are treated as "no rate card"
```

A filled-in rate card is commercially sensitive. Keep it in `~\.claude\`, never in this repo — the repo's
`.gitignore` already excludes `estimation-data/rates.yaml`.

For diagram rendering, `mmdc` (`@mermaid-js/mermaid-cli`) must be on `PATH`, otherwise `/sa:package`
reports figures as unrendered rather than silently omitting them.

---

## Deliberate divergences from the reference framework

This pipeline was built after reading `d:\_GEOMANT_GIT\agentic-dev-framework\`. Four things in it were
**not** copied, on purpose:

| Not copied | Why |
|---|---|
| Auto-commit after every command | The reference runs `git add`/`git commit` at the end of `triage` and `package`. That hijacks your git history and conflicts with `CONSTITUTION.md` Articles II and VII. Writing artifacts is the pipeline's job; committing them is yours. |
| `.sa\` at repo root | One engagement per repo. `ai\sa\<slug>\` supports multiple topics in one project. |
| Hardcoded vendor/domain agents | Their `solution-architect` and `project-estimator` bake in one company's platform and market. The schemas and rules were taken; the agents were rewritten generic. |
| Unattended multi-phase autonomy | Their `/dev:auto` runs phases without a human checkpoint. See below. |

Their **slop-check** phrase bank was also left out — the contradiction, citation and locale layers are
genuinely useful and now live in `req-auditor`'s checks 13–15, but the em-dash-density and word-frequency
heuristics produce false positives.

What *was* taken, and improved on: the lane model, the content-hash freshness gate, the JSON-as-source-
of-truth data model, the estimate-critic's quantified heuristics, and the compliance register.

---

## v1 is human-driven — and phase 2 is an addition, not a rewrite

v1 runs one command at a time with human review between. That's the intended shape for now: the
review points *are* the value on commercially binding work.

Three properties were built in so an orchestrator can be added later without touching any agent:

1. **Machine-readable state** — `engagement.json` carries the lane, `STATE.md` carries phase and next.
2. **Deterministic pre/postconditions** — every command declares what it requires and what it writes, and
   stops rather than proceeding on a partial picture.
3. **Content-hash freshness** — an orchestrator can compute exactly which downstream artifacts a change
   invalidated, and re-run only those.

A future `/sa:run <slug>` is then a loop over the lane's sequence, halting at any interactive question, any
`to_clarify` that blocks a `must`, and any gate failure.

**What phase 2 should not do**: run to a client deliverable without a human checkpoint. `/sa:package`'s
gate is a safety property, not a speed bump — `CONSTITUTION.md` Articles III and VII both apply.

---

**Last revised**: 2026-08-12 (v1.1 — added `/sa:brief` / `doc-briefer` and the advisory non-artifact
concept. v1.0 — initial workflow, lane model, and the presales/bid split from internal solution design).
