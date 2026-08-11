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
| New REQ/CR to analyze, in any project or standalone | `/sa:clarify` → `/sa:design` → `/sa:estimate` → `/sa:doc` | Global |
| Starting from an existing Excel/Word/PDF (RFP, estimate sheet, design doc) | `/sa:ingest <slug> <path>` first, then `/sa:clarify <slug>` | Global |
| Sanity-check a design before going deeper/committing to it | `/sa:review <slug>` (after `/sa:design`, before `/sa:design-detail`) | Global |
| Need interface/data-model/deployment-level detail, not just the HLD | `/sa:design-detail <slug>` (after `/sa:design`) | Global |
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

## The shape underneath, in one paragraph

One generic agent per role (`dev-backend`, `dev-frontend`, `dev-reviewer`, `dev-browser-tester`,
`solution-analyst`, `mermaid-diagram-maker`, `req-ingestor`, `req-analyst`, `req-architect`,
`req-reviewer`, `req-detailer`, `req-estimator`,
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
- **`/sa:*` artifacts are slugged per-topic** (`ai/sa/<slug>/`) specifically so you can have several
  REQ/CRs in flight in the same project without them overwriting each other. The slug is just a folder
  name you choose (or `req-analyst` derives one) — every `.md` file under it (`requirements.md`,
  `architecture.md`, `review.md`, `detailed-design.md`, `estimation.md`, `package.md`) is a generated
  *output*, never something you hand-write as input. The only real inputs are free-form text (to
  `/sa:clarify`) or raw files (`.xlsx`/`.docx`/`.pdf`, to `/sa:ingest`).
- **No step in `/sa:*` blocks the next one**, including `/sa:review` — it produces findings, not a
  pass/fail gate. `/sa:estimate` will run even if you skip `/sa:review` entirely. Skip whichever steps a
  small topic doesn't need (most CRs don't need `/sa:ingest` or a separate LLD pass at all).
- **Never commit is enforced only where a command says so** (SCM's `/scm:fix`/`/scm:req`/
  `/scm:devops-change`). The generic `dev-*` agents and `/dev:quick` have no opinion on commits — that's a
  project-specific mechanic, not a global rule.
