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
| `/sa:audit` | `audit/audit-<ts>.md` — **gate input 1**: do the JSON artifacts agree with each other, by ID? | `req-auditor` |
| `/sa:slop-check` | `audit/slop-<ts>.md` — **gate input 2**: is the prose a human will read grounded, consistent and free of machine-tells? | `req-slop-detector` |
| `/sa:package` | `deliverables/*.docx`, `*.xlsx`, `*.pptx`, built into the branded template | — |
| `/sa:status` | Where you are and the single next command | — |
| `/sa:doc` | `package.md` — **internal** consolidation | — |
| `/sa:onepager` | `onepager/<type>-v<NN>.html` + `.pdf` — a dense single page for management *(advisory)* | `req-onepager` |
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

## Eight design decisions worth understanding

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

### 6. One refusal point, two gate inputs

`/sa:package` refuses to build a client deliverable unless **both** gates show `PASS` or
`PASS-WITH-WAIVERS` **on a matching content hash**. Change any artifact and both go stale — by content,
never by timestamp, so touching a file without changing it doesn't invalidate anything.

There is still exactly **one place that refuses**. What changed on 2026-09-07 is that it reads two
verdicts, because the two check surfaces that don't overlap:

| | `/sa:audit` (`gate: sa-audit`) | `/sa:slop-check` (`gate: sa-slop`) |
|---|---|---|
| Reads | the `.json` artifacts | the rendered `.md` and extracted deliverable text |
| Asks | do these agree with each other, by ID? | is what the human will read true to them? |
| Method | set operations and arithmetic | claim tracing, contradiction scan, pattern/density scan |
| Catches | `REQ-014` is `must` and nothing estimates it | the exec summary quotes "40% faster" and no artifact says so |

The concrete failure this closes: an offer whose every ID resolves — a clean `req-auditor` PASS — while its
executive summary carries an invented benchmark, a phase duration contradicting the delivery plan two pages
later, and the client's name with its diacritics flattened. All four are structurally invisible to an
ID-integrity check, and all four reach the client.

Both agents are deliberately **mechanical or evidenced**: `req-auditor` checks that artifacts agree, never
whether a judgment was good; `req-slop-detector` cites the search it performed rather than asserting that
something "reads like AI". That's what keeps both unarguable. Judgment lives in `/sa:review` and
`/sa:estimate-review`, and neither of those blocks anything.

**Nine `sa-audit` checks are blocking and unwaivable**, each one a defect that would otherwise reach a
client:

1. An offer scope line with no traceability
2. A `must` requirement with no estimate and no reasoned deferral
3. A `priced_in: false` risk with no exclusion
4. A broken ID reference between artifacts
5. Offer scope containing a `to_clarify`, unestimated, or `should`/`could` item (that belongs in
   `scope.optional`, not `in_scope` — decision 5)
6. A price stated with no rate card behind it
7. A `traditional`/`both` delivery model recorded on the `rom` lane (decision 5 forbids it outright)
8. A `0` baseline where no `must` requirement exists — it must be `null` with the reason stated, because a
   quoted commitment of nothing is arithmetically defensible and completely misleading
9. An offer quoting the **all-options** total rather than the committed one — that commits the client to
   every optional item while presenting it as the baseline price

On the `sa-slop` side, blocking is decided by **audience**: an ungrounded quantity, a fabricated specific,
a contradiction between two client-facing figures, or a flattened diacritic in the client's own name blocks
when it appears in `offer.md`, a one-pager, or a built deliverable. The same defect in `architecture.md` is
advisory. A gate that blocked on an internal working note would be a gate people learn to route around.

### 7. The independent checks should run on a different model

Four agents here exist to catch what an earlier agent got wrong — `req-reviewer`, `req-estimate-critic`,
`req-auditor`, `req-slop-detector`. Each enforces independence carefully against reading the author's
*reasoning*, and each, by default, runs on the author's *model*. That is a real gap: the model that found an
assumption reasonable enough to write down is the one least likely to challenge it, and a sentence that felt
right to generate feels right to read.

All four commands take `--model=<sonnet|opus|haiku|fable>`, per-invocation only, and each reports which model
actually ran. Spend it where it pays: `/sa:slop-check` and `/sa:estimate-review` first, `/sa:review` next,
`/sa:audit` last (mechanical checks barely vary by model).

Said honestly, and the doctrine says it too (`ARTIFACT-SCHEMAS.md` §9): sibling models share training
lineage and therefore share some blind spots, so this reduces correlated error rather than delivering real
independence. You remain the reviewer of record, and nothing here may be described as "independently
verified".

### 8. Deliverables build into a branded template

`/sa:triage` resolves a **document profile** from `<config-root>\document-data\templates.yaml` — language
and locale map to a `.docx` shell — and writes it into `engagement.json`. `/sa:package` then *fills* that
template's placeholders and never restyles it, keeping approved boilerplate (confidentiality statements,
disclaimers, company introductions) verbatim.

The template paths live in a gitignored file at the config root rather than in any command, the same
indirection as the rate card, which is what lets a generic pipeline produce organization-branded output
without any command knowing an absolute path. No profile configured means unbranded output — **said out
loud in the relay**, never discovered later in Word.

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
/sa:estimate-review <slug> --model=sonnet
                                # → optimism bias, lifecycle gaps. Note the --model: run the critique
                                #   on something other than what produced the estimate (decision 7).
/sa:offer   <slug>              # → client-facing content
/sa:audit   <slug>              # → gate 1: do the artifacts agree, by ID?
/sa:slop-check <slug> --model=sonnet
                                # → gate 2: is the prose grounded? Ungrounded figures, contradictions,
                                #   AI tells, flattened diacritics. Both gates must pass.
/sa:package <slug> all          # → DOCX + XLSX under deliverables/, in the branded template
/sa:onepager <slug> summary     # → one page for the internal conversation the offer starts
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

## The same pipeline on GitHub Copilot CLI

Since 2026-09-07 this pipeline runs on both tools. Everything above — the lanes, the artifacts, the eight
design decisions, the two-verdict gate — is identical, because the contracts are **one set of files copied
to both config roots**: `ARTIFACT-SCHEMAS.md` (shape), `ESTIMATION-METHOD.md` (method) and `PIPELINE.md`
(sequence, preconditions, gate rules, and a conformance checklist defining what "same functionality" means).

What differs is only the mechanics:

| | Claude Code | Copilot CLI |
|---|---|---|
| Command layer | 19 slash commands (`/sa:*`) | one `sa-pipeline` skill — `~/.copilot/commands/` has no documented discovery behaviour, so 19 files there would silently not exist |
| Agents | 22 in `~/.claude/agents/` | 17 `.agent.md` siblings, dispatched `@req-estimator` |
| Model for a checking step | `--model=` per dispatch | `/model` **before** dispatching — session-level, so switch back after |
| Packaging gate | **refuses** | checks, reports, prints STOP — **advisory, never a gate** |
| Read-only agents | `disallowedTools` enforces it | `write` without `shell`; the rest is a written rule |

**Engagements are portable.** `ai/sa/<slug>/` lives in the project, not in a tool's config, and conforms to
one schema — so an engagement triaged in Claude Code can be clarified in Copilot CLI and packaged back.
That was the deciding argument for porting at all; the honest cost is that a material change to a Claude
`req-*` agent needs the same change in its sibling, and nothing automated enforces that.

**Run commercially binding packaging in Claude Code.** Not a preference — Copilot has no mechanism to
refuse, and a gate that looks like a gate and isn't is worse than an acknowledged manual check.
Full detail: `..\copilot\PORT-NOTES.md`.

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

```powershell
# Document profiles — unbranded deliverables until this exists
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\document-data\templates" | Out-Null
Copy-Item "d:\_AI_GIT\document-data\templates.yaml"   "$env:USERPROFILE\.claude\document-data\"
Copy-Item "d:\_AI_GIT\document-data\templates\*.docx" "$env:USERPROFILE\.claude\document-data\templates\"
# repeat for each config root you use (see claude\README.md's Rollout — there are three)
```

Same reasoning as the rate card: the brand templates and the profile map are organization property with
machine-specific paths, so both are gitignored and live only at the config roots. Without them `/sa:package`
still works — it just builds unbranded, and says so.

For diagram rendering, `mmdc` (`@mermaid-js/mermaid-cli`) must be on `PATH`, otherwise `/sa:package`
reports figures as unrendered rather than silently omitting them.

For one-pager PDFs, `/sa:onepager` uses headless Edge or Chrome — already present on a normal Windows
machine, no install needed. If neither is found the HTML is still written and you print it yourself
(`Ctrl+P` → Landscape → Margins: None → Background graphics: on); the HTML is the artifact, the PDF is a
rendering of it.

---

## Deliberate divergences from the reference framework

This pipeline was built after reading `d:\_GEOMANT_GIT\agentic-dev-framework\`. Four things in it are
still deliberately **not** copied:

| Not copied | Why |
|---|---|
| Auto-commit after every command | The reference runs `git add`/`git commit` at the end of `triage` and `package`. That hijacks your git history and conflicts with `CONSTITUTION.md` Articles II and VII. Writing artifacts is the pipeline's job; committing them is yours. |
| `.sa\` at repo root | One engagement per repo. `ai\sa\<slug>\` supports multiple topics in one project. |
| Hardcoded vendor/domain agents | Their `solution-architect` and `project-estimator` bake in one company's platform and market. The schemas and rules were taken; the agents were rewritten generic. |
| Unattended multi-phase autonomy | Their `/dev:auto` runs phases without a human checkpoint. See below. |

A fifth thing was left out and **has since been reversed** — recorded here rather than quietly edited away,
because the reasoning behind the original omission is a good illustration of how a partly-correct argument
loses a whole capability.

The reference framework's `sa-slop-detector` was not ported when its sibling `sa-completeness-auditor`
became `req-auditor`. The note here said its "contradiction, citation and locale layers now live in
`req-auditor`'s checks 13–15", and that the phrase bank was skipped because "the em-dash-density and
word-frequency heuristics produce false positives."

The second half was right; the first half was not, and it hid the cost:

- `req-auditor` reads **`.json` artifacts**. `sa-slop-detector` read the **rendered prose and the extracted
  deliverable text**. Checks 13–15 catch a phase duration that differs between two JSON fields; they cannot
  see a sentence in the exec summary that no JSON field contains. Those are different surfaces, and calling
  one a home for the other's checks was the error.
- The em-dash objection was specific and correct — em-dash density and sentence length catch competent human
  prose as readily as machine prose. But it was applied to the **entire agent**, discarding the groundedness
  and locale layers along with the two bad heuristics.

The result: for four weeks the pipeline had an ID-integrity gate and no prose-integrity gate at all, and
nothing checked whether a client-facing document said anything the artifacts didn't support.
`req-slop-detector` (2026-09-07) is the port, with the em-dash and sentence-length heuristics deliberately
**still** excluded and that exclusion written into its own rules, so the correct half of the original
objection survives without taking the rest of the agent with it.

What *was* taken, and improved on: the lane model, the content-hash freshness gate, the JSON-as-source-
of-truth data model, the estimate-critic's quantified heuristics, the compliance register, and — belatedly
— the four-layer prose scan.

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
