# Usage — which entry point when

The commands built on top of this repo's generic agents live in **four different repos** — easy to lose
track of. This is the map. See `README.md` for what's generic (lives here) vs. project-specific (lives in
the project's own `.claude\`), and `dev-framework\DESIGN.md` for why the `dev-*` pipeline is deliberately
lighter than a full wave/gate system.

## Which entry point when

| Situation | Command | Where it lives |
|---|---|---|
| Unfamiliar/new project, no `ai/context/` yet | `/scaffold-context [path]` | Global |
| Need an architecture/sequence/flowchart diagram | `/diagram [what]` | Global |
| **A client document just landed and you need to understand it** | `/sa:brief <path-or-slug>` if it's headed for a bid — works before triage, no engagement needed; `/doc-brief <path>` otherwise | Global |
| **"Can we do this, and roughly what would it cost?" — before deciding whether to bid** | `/sa:screen <path>` — one command, real requirements + a non-quotable band | Global |
| **Inbound TSD/RFP → priced offer** | `/sa:triage` first, then follow the lane it picks | Global |
| New REQ/CR to analyze, in any project or standalone | `/sa:triage` → `/sa:clarify` → … (see `SA-WORKFLOW.md`) | Global |
| Starting from an existing Excel/Word/PDF (RFP, estimate sheet, design doc) | `/sa:ingest <slug> <path>` after `/sa:triage`, before `/sa:clarify` | Global |
| Sanity-check a design before going deeper/committing to it | `/sa:review <slug>` (after `/sa:design`) | Global |
| Need interface/data-model/deployment-level detail, not just the HLD | `/sa:design-detail <slug>` (`full-design` lane) | Global |
| **Score risks + compliance obligations, and set contingency** | `/sa:risk <slug>` (before `/sa:estimate`) | Global |
| **Independent critique of an estimate before it goes out** | `/sa:estimate-review <slug>` | Global |
| **Write the client-facing offer** | `/sa:offer <slug>` → `/sa:audit` → `/sa:package` | Global |
| **Lost track of where an engagement stands** | `/sa:status <slug>` — tells you the single next command | Global |
| A project has no `ai/dev/` yet | `/dev:init [path]` | Global |
| Check a project's current dev-pipeline state | `/dev:status [path]` | Global |
| One-off backend/frontend task, no special process | `/dev:quick <task>` | Global |
| CampaignManager: backend/frontend task | `/dev:quick <task>` (run from that repo) | Global |
| Draft a new agent/skill/legacy-command | `/agent-builder` | Global |
| Draft a new one-time/occasional-use prompt | `prompt-builder` skill | Global |
| Independent check on a drafted agent/skill/command before trusting/copying it | `review-agent` skill (dispatches `agent-reviewer`) | Global |
| Generate/reformat an Excel/Word/PowerPoint document | `office-doc-builder` skill (library, imported by other skills) | Global |
| Read/extract content from an existing Excel/Word file | `office-doc-reader` skill (backs `req-ingestor`; `.pdf` — use the built-in `Read` tool directly) | Global |
| Extraction/generation genuinely needs OCR, patch-editing, or native charts/pivots — beyond what the lightweight skills above do | `document-skills@anthropic-agent-skills` plugin (installed 2026-08-11, user scope — see `SETUP.md` for the per-profile install gotcha) | Plugin, not this repo |
| net8-migration (SCM): bug fix | `/scm:fix [#ID] <bug>` | net8-migration |
| net8-migration (SCM): new requirement | `/scm:req [#ID] <requirement>` | net8-migration |
| net8-migration (SCM): review recent changes | `/scm:review [#ID]` | net8-migration |
| net8-migration (SCM): hosting/IIS question | `/scm:devops-ask <question>` | net8-migration |
| net8-migration (SCM): hosting/config/perf change | `/scm:devops-change <request>` | net8-migration |
| net8-migration (SCM): browser smoke test | `/scm:test [URL] <scenario>` | net8-migration |
| net8-migration (SCM): triage recent `dbo.Logs` errors for a site | `/scm:errors-triage <site> [from-date]` | net8-migration |
| scm-stm-merge: first full analysis pass | `/merge:full-analysis [path]` | scm-stm-merge |
| scm-stm-merge: re-run one phase only | `/merge:requirements` / `db` / `functional` / `code` | scm-stm-merge |

Each project namespace also has its own `:help` (`/scm:help`, `/merge:help`) once it has more than a
couple of commands — static reference, no live analysis. `/sa:help` and `/dev:help` cover the two global
namespaces.

**The `/sa:*` namespace is now 17 commands across three lanes** — too much for one table row. Its full
walkthrough, design rationale, and a worked "inbound TSD → offer" example live in **`SA-WORKFLOW.md`**.
Start there rather than here for any presales/bid work.

## The shape underneath, in one paragraph

One generic agent per role (`dev-backend`, `dev-frontend`, `dev-reviewer`, `dev-browser-tester`,
`solution-analyst`, `mermaid-diagram-maker`, `doc-briefer`, `req-screener`, `req-ingestor`, `req-analyst`,
`req-architect`,
`req-reviewer`, `req-detailer`, `req-risk-officer`, `req-estimator`, `req-estimate-critic`, `req-offer`,
`req-auditor`,
`agent-reviewer` — the meta-level counterpart to `dev-reviewer`, reviewing agent/skill/command/prompt
artifacts themselves rather than application code) — reused
verbatim across every project, never hardcoding a stack fact or project name. Project specificity lives in
two places: the project's own `ai/context/*.md` (facts the agent reads fresh every run) and, where the
*process itself* genuinely differs per project (SCM's Azure DevOps org rule and version-bump discipline;
CampaignManager has neither), a thin project-specific command that injects that process and dispatches to
the generic agent. `scm-stm-merge` is the one deliberate exception — its four agents are fully
project-specific because the domain reasoning (STM/SCM entity collision mapping) is one-time knowledge,
not a reusable role.

## Habits that make it work

- **Restart the session after copying anything new to `~/.claude/`.** Agent/command lists load once at
  session start — see `SETUP.md`'s troubleshooting section.
- **Run `/dev:init` before the first `dev-*` dispatch on a new project.** Every `dev-*` agent refuses to
  proceed without `ai/dev/STATE.md`/`config.json` — this is enforced by `PRINCIPLES.md`, not optional.
- **No gates are wired as blocking anywhere yet.** `/scm:review` and (once built) a generic `/dev:review`
  are on-demand, not automatic. A `dev-backend` task reporting "Build: SUCCESS" is not the same as a
  reviewed task — ask for review explicitly if you want one.
- **The SA pipeline (`/sa:*`) and the dev pipeline (`ai/dev/`) don't talk to each other.** No REQ-ID
  carries over from `/sa:clarify` into a `dev-backend` dispatch automatically — if you want that
  continuity, paste the relevant `REQ-ID`/requirement text into the `/dev:quick`/`/scm:req` task
  description yourself.
- **`/sa:*` artifacts are slugged per-topic** (`ai/sa/<slug>/`) so several REQ/CRs can be in flight in the
  same project without overwriting each other. Every artifact is written **twice**: `<name>.json` is the
  source of truth, `<name>.md` is the rendered version you read. **Never hand-edit a rendered `.md`** — the
  next run regenerates it from the JSON. The only real inputs are free-form text (to `/sa:clarify`) or raw
  files (`.xlsx`/`.docx`/`.pdf`, to `/sa:ingest`).
- **`/sa:triage` picks a lane, and the lane decides the rest.** `rom` (hours, a number for a
  conversation), `offer-sow` (days, a written priced offer — the default for an inbound TSD/RFP), or
  `full-design` (weeks, HLD + LLD + pitch). Re-running triage changes the lane without destroying
  anything. Run `/sa:status` any time to get the single next command for your lane.
- **One command chains, and only one: `/sa:screen`.** It runs scaffold → ingest → clarify → screen
  unattended, because it ends in an internal bid/no-bid call and writes no `estimation.json`/`offer.json` —
  nothing a client could receive. It stops dead there. The rule isn't "never chain", it's **never chain
  across the point where output becomes client-facing**, so `/sa:design` onward stays one at a time.
- **A screening band is not an estimate.** `screen.md`'s number is order-of-magnitude, deliberately wide,
  and **never quotable** — no PERT, no contingency, no compression, no price (`ESTIMATION-METHOD.md` §8).
  `/sa:estimate` is the only route to a number anyone may show a client.
- **One step *does* block: `/sa:package` refuses without a fresh `/sa:audit` PASS.** This is the one
  hard gate in the namespace and it is deliberate — it's the only command that produces something a client
  sees. Freshness is checked by **content hash**, so changing any artifact re-stales the gate and you
  re-run `/sa:audit`. `/sa:review` and `/sa:estimate-review` remain advisory and block nothing.
- **`/sa:doc` and `/sa:offer` are not the same document.** `/sa:doc` is an *internal* consolidation for
  your team. The client-facing path is `/sa:offer` → `/sa:audit` → `/sa:package`. Confusing them is how
  internal risk language reaches a client.
- **Estimates are effort, never price.** With no `rates.yaml` configured you get effort-only output, said
  plainly — never an invented number. See `sa-framework/ESTIMATION-METHOD.md §5` and `SETUP.md` for the
  rate-card step.
- **Never commit is enforced only where a command says so** (SCM's `/scm:fix`/`/scm:req`/
  `/scm:devops-change`). The generic `dev-*` agents and `/dev:quick` have no opinion on commits — that's a
  project-specific mechanic, not a global rule.
