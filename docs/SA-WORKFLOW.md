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

## Before the lanes — the bid/no-bid screen

Not every inbound document deserves a pipeline. The first question is usually asked in a corridor: *"can we
do this, and roughly what would it cost?"* — and the answer needs to be good enough to decide **whether to
invest days in an offer**, not good enough to send anyone.

```
/sa:screen "d:\WORK\Client\Their_RFP.docx"
```

One command, four steps — scaffold → ingest → clarify → screen — producing two files with deliberately
different standing:

| Output | Standing | Why |
|---|---|---|
| `requirements.json` | **Real** | The artifact every later step cites, and the most expensive thing to re-derive. If you bid, `/sa:design` picks it up as-is. |
| `screen.md` | **Advisory** | Feasibility verdict, named blockers, an order-of-magnitude effort band. Nothing cites it, no deliverable is built from it, and it is excluded from `inputs_hash`. |

It writes **no `estimation.json` and no `offer.json`** — and that omission is the entire reason a
multi-step command is acceptable here. A coarse number sitting in the file an offer is generated from is a
defect waiting to be signed; the same number in `screen.md` is an honest answer to a different question
(`ESTIMATION-METHOD.md` §8).

**Depth of pass and lane are independent axes.** A screen is *not* the `rom` lane. `rom` is a statement
about an engagement's commercial weight; a screen is a statement about how deep this particular sweep goes.
The largest RFP in the pipeline still starts with someone asking whether to bid it, so `/sa:screen` runs on
any lane and on none — and it deliberately does *not* make you commit to a lane first, since that would
invert the question you're asking.

The verdict is one of four, and two of them are "no": `can-do`, `can-do-if` (with the conditions listed as
things someone must go get), `probably-not`, and `cannot-assess` — the honest outcome when a document is too
thin to judge. A screen that cannot say no has no value, so none of the four is ever softened into another.

The band is **never quotable**, rate card or not. `screen.md` says so in its own header, not just in the
report. `req-estimator` never reads it as an anchor, and `req-estimate-critic` never critiques it — a band
with no PERT, no contingency and no calibration isn't a method violation, it's the specification.

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
| `/sa:screen` | `requirements.json` (real) + `screen.md` — feasibility verdict and a non-quotable effort band *(the bid/no-bid pass)* | `req-screener` |
| `/sa:triage` | `engagement.json` + `ENGAGEMENT.md` + `STATE.md`, and the lane | — |
| `/sa:brief` | `brief.md` — a comprehension read of the inbound documents, from a slug **or a bare path** *(advisory)* | `doc-briefer` |
| `/sa:ingest` | `inputs/*.extracted.md` from Excel/Word/PDF | `req-ingestor` |
| `/sa:clarify` | `requirements.json` — REQ-IDs, priority, status, source | `req-analyst` |
| `/sa:design` | `architecture.json` — HLD, components, NFRs, integrations, phasing | `req-architect` |
| `/sa:review` | `review.json` — narrative critique of the design | `req-reviewer` |
| `/sa:design-detail` | `detailed-design.json` — LLD *(full-design lane only)* | `req-detailer` |
| `/sa:risk` | `risk-register.json` — scored risks + compliance register | `req-risk-officer` |
| `/sa:estimate` | `estimation.json` — three-point best/likely/worst **AI-assisted** effort per line; `must`-only bare-minimum baseline with contingency, `should`/`could` priced separately as Optional; stricter on `rom` | `req-estimator` |
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
rule.

**It takes a bare path, not just a slug** — `/sa:brief "…\Their_TSD.docx"` works with no engagement in
existence, which is the pre-triage form and the one worth reaching for, since the lane call is what needs
the read. `/doc-brief <path>` is the same agent for documents unrelated to any bid.

Because it is advisory it never appears in a `STATE.md` `Next`. So the practical choice is: triage blind,
or brief first. `/sa:triage` and `/sa:ingest` both *offer* it — triage when it classified documents you
hadn't read, ingest when no `brief.md` exists yet — but neither runs it and neither treats it as a phase.
Nothing is lost by skipping it: the lane is reversible, so a brief that changes the picture is answered by
re-running `/sa:triage`.

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

### 4. AI-assisted is the delivery model, not a discount applied to one

`req-estimator` sizes AI-assisted effort **directly** — it no longer builds a hypothetical traditional
estimate and divides it down. `estimation.json.basis.model` defaults to, and normally stays, `ai-assisted`;
a `traditional`/`both` comparison figure is opt-in only, requires a stated reason, and is never produced on
`rom` (`ESTIMATION-METHOD.md §2`). Each line still carries a `K1`–`K6` work-type category, but it's now a
**sanity band**, not a division mechanic: UI/CRUD carries very high AI leverage, external integration and
UAT/coordination carry the least, and a number that doesn't fit its category's band is a defect to catch
before it ships.

The most expensive misreading of an AI-assisted estimate is generalising one headline leverage ratio to
everything. Calendar time, client decisions, third-party roadmaps and UAT windows **do not compress**.
Every estimate says this out loud, and the offer repeats it.

The figure also stays **uncommitted** until a short calibration sprint measures real velocity on real items
from *this* engagement. Until then it's quoted as a range with the gate named. Present that as a strength —
it converts an unbounded estimation risk into a bounded, client-visible checkpoint.

### 5. Baseline is must-only and bare-minimum; everything else is priced but optional

`req-estimator` sizes two tiers, never blended (`ESTIMATION-METHOD.md §9`):

- **Baseline** — every `must`-priority requirement, sized to the *leanest implementation that still fully
  satisfies it*. Bare-minimum is a discipline on effort, never on scope — a `must` is never under-delivered
  to hit a smaller number; that's a requirement-change conversation, not an estimating one. Contingency
  (decision 2) applies here, and only here.
- **Optional** — every `should`/`could`-priority requirement, estimated with the same rigor but excluded
  from the baseline total, its own contingency, and any commitment. It's listed, priced, and addable by an
  explicit client decision, never folded silently into the headline number.

**On the `rom` lane this is enforced harder, not lighter** (`ESTIMATION-METHOD.md §10`): bare-minimum is
mandatory on every line with no exceptions, a `traditional`/`both` comparison is refused even on request,
and `likely` is never rounded up "to be safe" — the first number said out loud tends to anchor a client's
expectations harder than any later, better-informed one, so the response to having the least information of
any lane is more estimating discipline, not less.

### 6. One hard gate, in one place

`/sa:package` refuses to build a client deliverable unless `/sa:audit` shows `PASS` or
`PASS-WITH-WAIVERS` **on a matching content hash**. Change any artifact and the gate goes stale — by
content, never by timestamp, so touching a file without changing it doesn't invalidate anything.

`req-auditor` is deliberately **mechanical**: it checks that artifacts agree with each other, never
whether a judgment was good. That's what makes the gate unarguable. Judgment lives in `/sa:review` and
`/sa:estimate-review`, and neither of those blocks anything.

Seven checks are **blocking and unwaivable**, each one a defect that would otherwise reach a client:

1. An offer scope line with no traceability
2. A `must` requirement with no estimate and no reasoned deferral
3. A `priced_in: false` risk with no exclusion
4. A broken ID reference between artifacts
5. Offer scope containing a `to_clarify`, unestimated, or `should`/`could` item (that belongs in
   `scope.optional`, not `in_scope` — decision 5)
6. A price stated with no rate card behind it
7. A `traditional`/`both` delivery model recorded on the `rom` lane (decision 5 forbids it outright)

---

## Worked example — an inbound TSD

```powershell
/sa:brief   "d:\WORK\Client\Their_TSD_v1.0.docx"
# → optional but recommended: read it before you classify it. Section map, key facts,
#   integration surface, conspicuous gaps. Takes a bare path — no engagement needed yet.
#   Follow-ups go to the same agent via SendMessage, which still holds the full text.

/sa:triage  "d:\WORK\Client\Their_TSD_v1.0.docx"
# → asks 3-5 intake questions, classifies the lane, scaffolds ai/sa/<slug>/
#   Offers /sa:brief here if you classified without having read the document.

/sa:ingest  <slug>              # TSD → inputs/*.extracted.md
/sa:brief   <slug>              # → re-brief from the extractions, into ai/sa/<slug>/brief.md
                                #   (skip if you already briefed the raw file above)
/sa:clarify <slug>              # → REQ-IDs, with to_clarify where the TSD is vague
/sa:design  <slug>              # → HLD; integrations marked assumed where no spec exists
/sa:risk    <slug>              # → every assumed integration becomes a scored risk
/sa:estimate <slug>             # → AI-assisted three-point effort; must-only baseline + priced optional;
                                #   contingency from the register
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

**`/sa:screen` is the one deliberate exception, and where it draws its line is the whole argument.** It
chains four steps unattended because it terminates in an *internal* bid/no-bid decision — nothing it writes
can be built into a client deliverable, since it produces no `estimation.json` and no `offer.json`. It stops
dead at the screen and will not run `/sa:design` onward even if asked. So the rule isn't "never chain"; it's
**never chain across the point where output becomes something a client receives**. Everything from
`/sa:design` to `/sa:package` stays one command at a time, because that's where the compounding happens: a
misread requirement becomes a design, becomes a number, becomes a signature.

Treat `/sa:screen` as the proving ground for the orchestrator below — it validates the chaining mechanics on
the case where being wrong costs a conversation rather than a bid.

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

**Last revised**: 2026-09-03 (v1.4 — decision 4 rewritten and decision 5 added for the estimation-doctrine
update: AI-assisted is now the only delivery model estimated by default (`traditional`/`both` opt-in,
never on `rom`), and the baseline is `must`-only and bare-minimum, with `should`/`could` priced separately
as Optional and `rom` held to a stricter standard (`ESTIMATION-METHOD.md §2, §9, §10`). The blocking-checks
list grew from six to seven (the new `rom` model-restriction check) and item 5's wording widened from
`could` to `should`/`could`. v1.3 — added `/sa:screen` / `req-screener`: the bid/no-bid pass, the
depth-vs-lane distinction, advisory non-artifact #2, and the "never chain across the client boundary" rule
that scopes it. v1.2 — documented `/sa:brief`'s bare-path pre-triage form, the
`SendMessage` follow-up route, and the triage/ingest *offer* that makes an advisory command discoverable
without making it a phase. v1.1 — added `/sa:brief` / `doc-briefer` and the advisory non-artifact concept.
v1.0 — initial workflow, lane model, and the presales/bid split from internal solution design).
