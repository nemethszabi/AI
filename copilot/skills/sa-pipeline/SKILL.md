---
name: sa-pipeline
description: Run the lane-driven Solution-Architect requirement-to-offer pipeline — triage an inbound ask into a lane, ingest and clarify it into traceable requirements, design, score risks, estimate, compose a client offer, check it, and package the deliverable. Use when handling an inbound RFP/TSD/change request, deciding whether to bid, producing a priced offer, or building a management one-pager. Triggers on "triage this RFP", "clarify these requirements", "estimate this", "write the offer", "can we do this and what would it cost", "check this document before I send it", "one-pager for management".
---

> Version: 1.0.0

# SA Pipeline — requirement to offer

The Copilot CLI implementation of the `sa:` pipeline. Its Claude Code sibling is 19 slash commands under
`claude\commands\sa\`; here it is one skill plus fourteen `@`-dispatchable agents, because **skills and
agents are Copilot CLI's confirmed extension points** and a per-step command file is not.

> **[Copilot] Why a skill and not 19 commands.** `~/.copilot/commands/*.md` has no documented discovery
> behaviour — it appears in no `copilot --help`, `copilot help commands` or `copilot help config` output as
> of v1.0.82, and the one file staged there predates that check. Building nineteen step files on an
> unverified mechanism would produce a pipeline that silently does not exist. Skills are documented, are
> the open cross-tool standard, and already work here. If custom commands are later confirmed, splitting
> this file is mechanical.

**Read `~/.copilot/sa-framework/PIPELINE.md` before running any step.** It is the binding, tool-agnostic
contract — preconditions, dispatch targets, artifacts, state transitions, the gate rules — shared
byte-for-byte with the Claude side. This file carries only what is Copilot-specific: dispatch syntax,
model switching, and the two places this tool cannot do what the Claude side does.

Standing divergences for the whole family: `~/.copilot/PORT-NOTES.md`.

---

## How a step runs here

1. **Resolve the slug.** An argument naming an existing `ai/sa/<slug>/` wins; otherwise glob for the
   artifact the step requires — one match uses it, several ask the human, none stops and names the
   producing step. Never guess between two engagements.
2. **Check preconditions** from `PIPELINE.md §1` *before* dispatching. Hard precondition missing → stop and
   name the producing step. Soft one missing → say plainly what will be weaker, then proceed.
3. **Dispatch with `@agent-name`.** `/agent <name>` selects one interactively; `/fleet` runs several in
   parallel. Give the agent the slug, the project path, and the lane from `engagement.json`.
4. **Update `ai/sa/<slug>/STATE.md`** in the canonical shape (`ARTIFACT-SCHEMAS.md §6`) — append to phase
   history, never rewrite; `Next` names exactly one step.
5. **Relay the agent's own summary**, plus every file path written.
6. **Raise `## Blocking questions` with the human, in plain prose.** The agent cannot ask
   (`PORT-NOTES.md` D4); this is the only place those reach a person.
7. **Never commit.** Writing artifacts is the pipeline's job; `git add`/`git commit` is the human's.

All eight obligations in `PIPELINE.md §2` apply in full. This list is the Copilot-shaped restatement of
them, not a replacement.

---

## The steps

Lane sequences live in `ARTIFACT-SCHEMAS.md §4.1`; per-step preconditions and outputs live in
`PIPELINE.md §1`. Neither is repeated here — this table maps a step to its dispatch.

| Step | Dispatch | Notes |
|---|---|---|
| **triage** | *(no agent — do it yourself)* | Ask 3–5 lane-classifying questions, then write `engagement.json`, `ENGAGEMENT.md`, `STATE.md` and the folder scaffold. Also resolve the document profile — see *Document profiles* below. |
| **brief** | `@doc-briefer` | Advisory. Takes a bare path with no engagement — the pre-triage form, and the one worth reaching for. |
| **screen** | `@req-ingestor` → `@req-analyst` → `@req-screener` | The bid/no-bid pass. The one chain that runs unattended, because it ends in an internal decision. **Stops dead at the screen** — never continue into design. |
| **ingest** | `@req-ingestor` | Folder scans are one level deep unless recursion was asked for. |
| **clarify** | `@req-analyst` | |
| **design** | `@req-architect`, then `@mermaid-diagram-maker` | Pass the HLD's `Diagrams` section and `ai/sa/<slug>/diagrams/` as the output dir. Skip the second dispatch if none are warranted. |
| **review** | `@req-reviewer` | **Switch model first** — see *Cross-model checking*. |
| **design-detail** | `@req-detailer`, then `@mermaid-diagram-maker` | `full-design` lane only; the agent stops on any other. |
| **risk** | `@req-risk-officer` | Run before estimating — its contingency recommendation is an input. |
| **estimate** | `@req-estimator` | |
| **estimate-review** | `@req-estimate-critic` | **Switch model first.** |
| **offer** | `@req-offer` | |
| **audit** | `@req-auditor` | Gate input 1 — the artifacts agree by id. |
| **slop-check** | `@req-slop-detector` | Gate input 2 — the prose is true to them. **Switch model first.** See *Checking a document* below for the two things you must do before dispatching. |
| **package** | *(no agent — do it yourself)* | See *Packaging* below. **This is where this tool differs most.** |
| **status** | *(no agent)* | Read-only. Report lane, phase, artifacts vs the lane's expected set, **both** gates with the model each ran on, open `to_clarify` counts, and exactly one recommended next step. |
| **doc** | *(no agent)* | Consolidate the JSON artifacts into `package.md` — **internal only**, never sent to a client. Never sets `Phase` or `Next`. Its Effort section reproduces the estimate's summary block — see *The internal package document* below. |
| **onepager** | `@req-onepager` | Then render the PDF yourself — see *One-pagers* below. |
| **help** | *(no agent)* | Point at this file, `PIPELINE.md`, and `docs\SA-WORKFLOW.md`. |

---

## Cross-model checking

`ARTIFACT-SCHEMAS.md §9` requires the four checking steps — `review`, `estimate-review`, `audit`,
`slop-check` — to run on a **different model than produced the work**. A reviewer sharing the author's model
shares the author's blind spots: the sentence that felt reasonable to generate feels reasonable to read.

**[Copilot] Model selection is session-level, not per-dispatch** (`PORT-NOTES.md` D5). There is no
per-agent model parameter, so:

```
/model <a model other than the one that wrote these artifacts>
@req-slop-detector <slug>
```

Two things follow. **The switch affects the whole session** — run a checking step in its own session, or
switch back afterwards. And **do not lean on the default**: this machine's Copilot runs `claude-sonnet-5`
while the Claude Code side runs Opus, so artifacts authored there and checked here are cross-model by
accident of configuration, which `/model` erases in one keystroke.

Priority when you only switch once: `slop-check` and `estimate-review` first, `review` next, `audit` last —
mechanical checks barely vary by model.

**Always report which model actually ran**, and say so when no switch was made. Never call a cross-model
pass "independently verified": sibling models share training lineage, so this reduces correlated error
rather than delivering independence. The human is the reviewer of record.

---

## Checking a document (`slop-check`)

`@req-slop-detector` is read-only with no shell, so **you** must do two things before dispatching:

1. **Compute the `inputs_hash`** per `ARTIFACT-SCHEMAS.md §5` — `git hash-object` over whichever of
   `requirements.json`, `architecture.json`, `estimation.json`, `risk-register.json`, `offer.json` exist,
   first 12 characters each, joined in that fixed order; `sha256sum` outside a git repo. Content-based,
   never mtimes. Pass it in; the agent echoes it verbatim into its verdict block.
2. **Extract any built deliverables** to `ai/sa/<slug>/audit/extract/<source-filename>.txt` using
   `python-docx` / `openpyxl` / `python-pptx`. Rewrite them fresh every run — a stale extract would have the
   check pass a document nobody read. If extraction fails for a file, **do not abort**: pass its name so
   the report lists it under `## Not scanned`. Skip this entirely when `deliverables/` is empty, which is
   the normal pre-package case.

Then parse **only** the fenced ` ```sa-verdict ` block, validating `gate: sa-slop` and that `inputs_hash`
matches what you computed. Missing or malformed → ask the agent once more; still malformed → stop without
updating state and **never infer a verdict from prose**.

---

## Packaging — read this before you use it

**[Copilot] This tool cannot enforce the gate** (`PORT-NOTES.md` D6, `PIPELINE.md §3`). On the Claude side
`/sa:package` *refuses* to build without two fresh passing verdicts. Copilot CLI has no mechanism by which a
skill can hard-stop a session that has been told to continue.

So packaging here does everything the Claude side does **except refuse**:

1. Compute the `inputs_hash` fresh.
2. Read the newest `audit/audit-*.md` and `audit/slop-*.md`, match each by its **`gate:` field** — never by
   filename — and check all four conditions: both verdicts `PASS`/`PASS-WITH-WAIVERS`, both hashes matching.
3. **If any fails, print a prominent STOP block** naming each failure and the step that fixes it, and do not
   proceed unless the human explicitly tells you to.
4. Resolve the document profile and build into the branded template (below).

**Call this an advisory check, never a gate.** A gate that looks like a gate and isn't produces the
confidence of enforcement with none of the substance. **If the deliverable is commercially binding, run the
packaging step in Claude Code**, where the refusal is real.

### The estimation workbook

**Read every total from `estimation.json.rollup`; never recompute one.** The stored figures are the same
ones the estimate document, the offer and the one-pager show — a workbook that recomputes them is a fourth
chance to round one number a fourth way (`ARTIFACT-SCHEMAS.md §4.7`).

- **Tab 1 Summary** — the estimate's own summary block, same rows in the same order
  (`ESTIMATION-METHOD.md §11.1`), each best/likely/worst: Baseline → + Contingency (% and amount) → + Buffer
  → **= Committed total** (visually distinct, labelled *the figure quoted*) → Optional (*not included
  above*) → = If all options taken (**reference only — not a quote**) → Not estimated (`—` with a count,
  never `0`). Arithmetic rows carry **real cell formulas**, so the sum is checkable in the workbook rather
  than asserted by it.
- **Tab 2 Rollups** — `by_phase`, `by_category` (with the **non-build share** as an explicit percentage),
  `by_k_category`. §11.2's three questions, answered without summing the line table.
- **Tab 3 Line items** — one row per `L-`, with REQ/component/QA citations, K-category, category and
  `scope_tier`. Baseline and optional rows visually separated, **never interleaved**, each subtotalling to
  its Tab 1 row.
- **Tab 4 Assumptions & exclusions** · **Tab 5 Coverage matrix** (REQ × component × line).

A `traditional` comparison figure, if one exists, sits in its own column labelled "comparison — not the
delivery model priced" — never merged into one column, never given equal visual weight.

---

## Document profiles

`/sa:package` builds into a branded `.docx` shell when one resolves (`ARTIFACT-SCHEMAS.md §8`).

At **triage**, resolve it once and write `vendor_org`, `document_profile` and `template_path` into
`engagement.json`. Read `~/.copilot/document-data/templates.yaml`; fall back to
`d:/_AI_GIT/document-data/templates.yaml`, and say which you used. Resolution order: an explicit profile
argument or a human-set `template_path` → `deliverable_language` → `locale` → the org's `default_profile`.
No file and no match → all three `null`, and **say once that deliverables will be unbranded**. Silent
unbranded output is the failure this step prevents.

At **package**, fill the template's placeholders and **never restyle it**. Keep `boilerplate_sections`
verbatim — confidentiality statements, disclaimers and company introductions are approved legal and
marketing text, never regenerated, reworded, trimmed or machine-translated. Write engagement content under
`content_sections`, delete `demo_sections`, and **keep anything in none of the three lists**: the cost of an
unexpected extra section is that someone notices; the cost of a silently dropped one is that nobody does.

---

## The internal package document (`doc`)

`package.md`'s **Effort** section reproduces the estimate's own summary block verbatim — same rows, same
order (`ESTIMATION-METHOD.md §11.1`), read straight from `estimation.json.rollup` and never recomputed:
Baseline → + Contingency (% and amount) → + Buffer → **= Committed** → Optional (*not included above*) →
= If all options taken (**reference only, not a quote**) → Not estimated (`—`, never `0`). Then the three
sub-rollups from `by_phase`, `by_category` (with the non-build share as a percentage) and `by_k_category`.

**Lead with Committed, not Baseline.** It is the figure an offer quotes, and an internal document that
leads with the smaller number trains the reader to quote the wrong one.

If `basis.rate_card` is null, state **effort only** — no price, no cost, not even an illustrative one — and
say why (`ESTIMATION-METHOD.md §5`). A rate card, if one was used, never appears here either; only the
arithmetic someone chose to show.

## One-pagers

`@req-onepager` writes self-contained A4-landscape HTML; **you** render the PDF, because the agent has no
shell:

```
msedge --headless=new --disable-gpu --user-data-dir=<a temp dir> \
       --no-pdf-header-footer --print-to-pdf=<out>.pdf "file:///<absolute-path>.html"
```

Four things fail silently if skipped: `--user-data-dir` is **required** (without it the run exits 0 and
writes nothing when a browser profile is in use); **the exit code is not the result** — poll for the output
file up to ~15s rather than trusting it; `--no-pdf-header-footer` suppresses browser furniture that
otherwise prints over the layout; and the input must be a `file:///` URL with an absolute path and forward
slashes. Fall back to Chrome; if neither exists, **do not fail** — the HTML is the artifact, so name its
path and tell the human to print it (`Ctrl+P` → Landscape → Margins: None → Background graphics: on).

Then verify the PDF is **one page**. A two-page result means the layout overflowed — report it and re-run;
never hand over a "one-pager" that is two pages.

---

## Shared conventions

- **JSON is the truth; the `.md` is rendered from it in the same run** and never hand-edited.
- **`inputs/` is immutable** once written. `audit/extract/` is regenerable scratch and is not.
- **IDs are stable forever** — never renumbered, never reused; a dropped item becomes `withdrawn`.
- **Three advisory non-artifacts**: `brief.md`, `screen.md`, `onepager/*`. No JSON, no ids, cited by
  nothing, excluded from `inputs_hash`, never a phase, and never reported as unexpected. The test for
  membership: **does anything refuse on it?** If yes it is a gate output, which is why `audit/slop-*.md`
  is not one.
- **A screening band is not an estimate and is never quotable** (`ESTIMATION-METHOD.md §8`).
- **Effort is not price.** No rate card means effort-only output, said plainly; a rate card never appears in
  anything client-facing, only the arithmetic someone chose to show.
- **One place for the numbers.** Every rendered estimate leads with a single summary table carrying every
  headline figure and its arithmetic — baseline, + contingency, + buffer, **= committed** (the figure an
  offer quotes), optional (*not included above*), = if all options taken (**reference only, never a
  quote**), not estimated (`—`, never `0`). Then three sub-rollups: by phase, by work type with the
  non-build share as a percentage, and by K-category. A reader must never add two sections together to
  answer "what does this cost?" (`ESTIMATION-METHOD.md §11`). Every rollup is three-point and is **stored**
  in `estimation.json.rollup`, so the offer, the XLSX, `doc` and the one-pager all read the same figures
  rather than each recomputing them.
- **Internal vs client-facing are different documents.** `doc` → `package.md` is for your team; `onepager`
  is for the meeting; the client path is `offer` → `audit` + `slop-check` → `package`. Never send
  `package.md` to a client.
- **Engagements are portable.** `ai/sa/<slug>/` conforms to one shared schema, so an engagement started in
  Claude Code continues here and vice versa (`PORT-NOTES.md` D1). That portability is the main payoff of
  this port.
