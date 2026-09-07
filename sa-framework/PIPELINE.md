# SA Framework — Pipeline Contract

**Binding** and **tool-agnostic**. Defines what each `sa:` step *does* — its preconditions, the agent it
dispatches, what it writes, how it updates state, and what it must relay — independently of which AI tool
runs it.

Its two siblings govern different axes:

| File | Governs |
|---|---|
| `ARTIFACT-SCHEMAS.md` | **shape** — the JSON every artifact must conform to |
| `ESTIMATION-METHOD.md` | **method** — how numbers are derived and what they may be used for |
| **this file** | **sequence** — which step runs when, on what, and with what obligations |

## Why this file exists

The pipeline is implemented twice — once for Claude Code (`claude\commands\sa\*.md`), once for GitHub
Copilot CLI (`copilot\commands\sa\*.md`) — because the two tools' command formats and dispatch mechanics
are mutually unreadable. Nothing can change that.

What *can* be shared is everything those command files were otherwise going to restate: the lane order, the
preconditions, the gate rules, the `STATE.md` obligations. Before this file, that content was duplicated
across 19 Claude command files; a Copilot port would have made it 38. **Two implementations of one
contract drift; two implementations that both cite one contract do not.**

So: a command file carries argument parsing, dispatch syntax, and its tool's own mechanics. Everything in
the table below it **cites rather than restates**. A command that restates a precondition from here has
created a second source of truth, and that is the defect this file prevents.

**Known debt, stated rather than hidden**: the Claude command files predate this document and still restate
parts of the contract inline — their preconditions, `Next` logic and gate text were written before there was
a shared place to put them. They currently agree with this file, and `copilot\skills\sa-pipeline\SKILL.md`
cites it properly from the start. **Where a Claude command and this file ever disagree, this file wins** and
the command is the defect. Thinning those 19 files to citations is worthwhile but is a separate, mechanical
change; doing it in the same pass that created this document would have meant rewriting a working
implementation and its new specification at once, with nothing stable to check either against.

---

## 1. The step table

`Requires` is a hard precondition unless marked *(soft)* — soft means proceed after saying plainly what
will be weaker. `Phase` is the value written to `STATE.md`; `—` means the step does not set one.

| Step | Requires | Dispatches | Writes | Phase | Next |
|---|---|---|---|---|---|
| `triage` | — | *(none — the command writes directly)* | `engagement.json`, `ENGAGEMENT.md`, `STATE.md`, the folder scaffold | `triage` | `ingest` if inbound files exist, else `clarify` |
| `brief` | one or more readable documents, **or** a bare path | `doc-briefer` | `brief.md` | — | *(unchanged — advisory)* |
| `screen` | a path or slug | `req-ingestor` → `req-analyst` → `req-screener` | `requirements.json` + `screen.md` | per sub-step; the screen itself sets none | *(the bid/no-bid decision — a human's, not a command's)* |
| `ingest` | files to extract | `req-ingestor` | `inputs/*.extracted.md` | `ingest` | `clarify` |
| `clarify` | `engagement.json` *(soft)*, plus ingested files or a description | `req-analyst` | `requirements.json` + `.md` | `clarify` | `estimate` on `rom`, else `design` |
| `design` | `requirements.json` | `req-architect`, then `mermaid-diagram-maker` | `architecture.json` + `.md`, `diagrams/*` | `design` | `review` on `full-design`, else `risk` |
| `review` | `architecture.json` | `req-reviewer` | `review.json` + `.md` | `review` | `design-detail` on `full-design`, else `risk` |
| `design-detail` | `architecture.json`; lane **must** be `full-design`; `review.json` *(soft)* | `req-detailer`, then `mermaid-diagram-maker` | `detailed-design.json` + `.md` | `design-detail` | first missing of `risk` → `estimate` → `audit` |
| `risk` | `architecture.json` (except on `rom`) | `req-risk-officer` | `risk-register.json` + `.md` | `risk` | `estimate` |
| `estimate` | `requirements.json`; `architecture.json` (except on `rom`); `risk-register.json` *(soft)* | `req-estimator` | `estimation.json` + `.md` | `estimate` | `estimate-review`, or `offer` on `rom` |
| `estimate-review` | `estimation.json` | `req-estimate-critic` | `estimate-review.json` + `.md` | `estimate-review` | `offer`, or `estimate` if adjustments are accepted |
| `offer` | `engagement.json`, `requirements.json`; the lane's other artifacts *(soft)* | `req-offer` | `offer.json` + `.md` | `offer` | `audit` |
| `audit` | `engagement.json` | `req-auditor` | `audit/audit-<ts>.md` | `audit` | fix-command on `BLOCKED`; else `slop-check` if no fresh `sa-slop`; else `package` |
| `slop-check` | at least one rendered `.md` or built deliverable | `req-slop-detector` | `audit/slop-<ts>.md` (+ regenerates `audit/extract/`) | `slop-check` | fix-command on `BLOCKED`; else `audit` if no fresh `sa-audit`; else `package` |
| `package` | **both** gates `PASS`/`PASS-WITH-WAIVERS` on a matching `inputs_hash` | *(none — the command builds directly)* | `deliverables/*`, `deliverables/.snapshots/*` | `package` | `status` |
| `status` | `engagement.json` | *(none)* | **nothing — read-only** | — | *(reports one; sets none)* |
| `doc` | `requirements.json` *(soft)* | *(none)* | `package.md` | — *(never advances)* | *(unchanged)* |
| `onepager` | the requested page type's artifacts (`ARTIFACT-SCHEMAS.md §6`) | `req-onepager` | `onepager/<type>-v<NN>.html` + `.pdf` | — | *(unchanged — advisory)* |
| `help` | — | *(none)* | nothing — static reference only | — | — |

Lane sequences are **not** repeated here: `ARTIFACT-SCHEMAS.md §4.1`'s lane table is their single source of
truth, and a second copy is what drifts. This table says what each step *is*; that one says which steps a
given lane *runs*.

---

## 2. Obligations every dispatching step carries

These apply to every step in the table that dispatches an agent, on either tool. A command that skips one
is non-conforming even if it otherwise works.

1. **Resolve the slug explicitly.** An argument naming an existing engagement folder wins; otherwise glob
   for the artifact the step requires — exactly one match uses it, several ask the human which, none stops
   and names the command that would create it. **Never guess between two engagements.**
2. **Check preconditions before dispatching, not after.** A hard precondition missing means stop and name
   the producing step. A soft one missing means say plainly what will be weaker, then proceed — the human
   should choose that knowingly rather than discover it in the output.
3. **Never infer the lane.** No `engagement.json` means no lane. Say so and point at `triage`.
4. **Update `STATE.md` in the canonical shape** (`ARTIFACT-SCHEMAS.md §6`), appending to phase history and
   never rewriting a prior line. `Next` names **exactly one** step.
5. **Relay the agent's own summary**, not a paraphrase of it, plus every file path written.
6. **Surface blocking questions to the human.** A dispatched agent cannot ask on either tool — it proceeds
   on the least-committal reading, records the question in the artifact, and repeats the blocking ones
   under a `## Blocking questions` heading. The dispatching step is the only place those can reach a person.
   Losing them in the transcript is the failure this obligation exists to prevent.
7. **Never commit.** Writing artifacts is the pipeline's job; `git add`/`git commit` is the human's
   (`CONSTITUTION.md` Articles II and VII).
8. **Stay a thin dispatcher.** Never restate an agent's own logic, a threshold from `ESTIMATION-METHOD.md`,
   or a schema rule from `ARTIFACT-SCHEMAS.md`. Cite; don't copy.

---

## 3. The gate contract

One refusal point — `package` — reading two verdicts. Full rationale in `ARTIFACT-SCHEMAS.md §5`; the
operational rules are:

- Each gate emits exactly one fenced `sa-verdict` block. **Match a report to a gate by its `gate:` field**
  (`sa-audit` / `sa-slop`), never by filename. A block with a missing or unrecognized `gate:` counts as a
  missing gate.
- `package` proceeds only when **both** verdicts are `PASS` or `PASS-WITH-WAIVERS` **and** each recorded
  `inputs_hash` matches a freshly computed one. Both gates hash the same input set, so one computation
  serves both comparisons.
- A malformed or missing verdict block is re-requested from the agent **once**. Still malformed → abort
  without updating state. **Never infer a verdict from prose**, and never write one on the agent's behalf.
- Gate reports are append-only. Never overwrite a prior `audit-*.md` or `slop-*.md`, and never delete one
  to make a gate pass.
- A failing gate is a defect to fix, never an obstacle to route around (`CONSTITUTION.md` Article III). The
  remedy is always re-running the step that owns the artifact, never editing a rendered `.md` by hand.

### Where a tool cannot enforce it

A tool whose command layer cannot *refuse* to proceed must say so, loudly and in the command itself, rather
than implying an enforcement it doesn't have. **A gate that looks like a gate and isn't is worse than an
acknowledged manual check**: it produces the confidence of enforcement with none of the substance. Such an
implementation states plainly that the check is advisory-by-mechanism, prints the verdict prominently, and
refuses to describe itself as a gate. See `copilot\README.md` for this framework's live instance of that
problem.

---

## 4. Cross-model review — the tool-agnostic rule

`AGENT-CONDUCT-BASELINE.md` B10 and `ARTIFACT-SCHEMAS.md §9` are binding here. Restated only as it affects
this contract:

The four checking steps — `review`, `estimate-review`, `audit`, `slop-check` — should each run on a
**different model than produced the work under review**, in that order of value (`slop-check` and
`estimate-review` matter most; `audit` least, being mechanical). Every implementation must:

- expose a way to select the model for that step,
- **report which model actually ran**, and
- say so when no override was chosen, naming a suggested one.

*How* a tool selects the model is tool-specific and belongs in its own command files — a per-dispatch
parameter on one tool, a session-level setting on another. That difference does not change the obligation.

---

## 5. Conformance — what "same functionality" means

Two implementations of this contract are equivalent when all of the following hold. This is the checklist a
review uses; it is not a suggestion.

1. Every step in §1 exists, with the same name and the same required/soft precondition split.
2. Each dispatches to the same agent role and writes the same artifacts to the same paths.
3. `STATE.md` transitions are identical — same phase values, same single-`Next` discipline.
4. The gate contract in §3 holds, or its non-enforcement is declared per §3's last subsection.
5. All eight obligations in §2 are honoured.
6. §4's model reporting is present.
7. Every deliberate divergence is **marked in the file itself** and recorded in that branch's `README.md`.

A divergence that is marked and reasoned is conformance. A divergence that is silent is drift, and the
distinction is the whole point of writing this down.

---

**Last revised**: 2026-09-07 (v1.0 — extracted when the `sa:` pipeline was ported to a second tool, at
which point the per-command duplication would have doubled from 19 files to 38. Written tool-agnostic from
the start rather than as a Claude document a port has to reinterpret.)
