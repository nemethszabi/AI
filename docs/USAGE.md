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
| **Write the client-facing offer** | `/sa:offer <slug>` → `/sa:audit` + `/sa:slop-check` → `/sa:package` | Global |
| **Check a document actually says what the artifacts support**, before it goes out | `/sa:slop-check <slug> --model=<different one>` — ungrounded figures, contradictions, AI tells, flattened diacritics | Global |
| **One page for management / a steering committee** | `/sa:onepager <slug> [summary\|roadmap\|estimate\|timeline\|architecture]` | Global |
| **Lost track of where an engagement stands** | `/sa:status <slug>` — tells you the single next command | Global |
| A project has no `ai/dev/` yet | `/dev:init [path]` | Global |
| Check a project's current dev-pipeline state | `/dev:status [path]` | Global |
| One-off backend/frontend task, no special process | `/dev:quick <task>` | Global |
| CampaignManager: backend/frontend task | `/dev:quick <task>` (run from that repo) | Global |
| **Empty folder → a new .NET demo/prototype app** | `/dev:build "<goal>"` (plans first, you approve the task list, then it builds) — or `/dev:new "<description>"` for just the skeleton | Global |
| **Rebuild an app from its UI** — a running URL, screenshots, or a source tree | `/dev:deconstruct <inputs>` → then `/dev:build --from-spec=<path>` | Global |
| **Many tasks in one go against an existing repo** | `/dev:build "<goal>" --model=<a different one>` | Global |
| Draft a new agent/skill/legacy-command | `/agent-builder` | Global |
| Draft a new one-time/occasional-use prompt | `prompt-builder` skill | Global |
| Independent check on a drafted agent/skill/command before trusting/copying it | `review-agent` skill (dispatches `agent-reviewer`) | Global |
| **Periodic health-and-strategy pass over the whole framework** — is it still in sync, coherent, current, and pointed at the work you actually do? | `/framework-review` (dispatches `framework-strategist`); add `drift`/`doctrine`/`research`/`ideas`/`parity` to narrow it. **It suggested something you want — now what?** See `FRAMEWORK-REVIEW-WORKFLOW.md` for the full report → approve → build → rollout loop | Global |
| **Context is getting large, or stopping for the day** — carry the session over | `/handoff` → `/clear` → `/handoff resume <file>` (it asks to delete the handoff once handled). `/handoff list` shows open ones. Always `<project>/ai/handoff/handoff-YYYYMMDD-HHMM-<slug>.md` | Global |
| **Just changed an agent/skill/command/doctrine or a project's prompting files** — document it, roll it out, back it up | `/doc-sync` (suggested automatically by the `framework-change-flag.py` hook once wired) — four separate approvals: docs → rollout → commit → backup | Global |
| Generate/reformat an Excel/Word/PowerPoint document | `office-doc-builder` skill (library, imported by other skills) | Global |
| Read/extract content from an existing Excel/Word file | `office-doc-reader` skill (backs `req-ingestor`; `.pdf` — use the built-in `Read` tool directly) | Global |
| Extraction/generation genuinely needs OCR, patch-editing, or native charts/pivots — beyond what the lightweight skills above do | `document-skills@anthropic-agent-skills` plugin (installed 2026-08-11, user scope — see `SETUP.md` for the per-profile install gotcha) | Plugin, not this repo |
| development (SCM): bug fix | `/scm:fix [#ID] <bug>` | development |
| development (SCM): new requirement | `/scm:req [#ID] <requirement>` | development |
| development (SCM): review recent changes | `/scm:review [#ID]` | development |
| development (SCM): hosting/IIS question | `/scm:devops-ask <question>` | development |
| development (SCM): hosting/config/perf change | `/scm:devops-change <request>` | development |
| development (SCM): browser smoke test | `/scm:test [URL] <scenario>` | development |
| development (SCM): triage recent `dbo.Logs` errors for a site | `/scm:errors-triage <site> [from-date]` | development |
| scm-stm-merge: first full analysis pass | `/merge:full-analysis [path]` | scm-stm-merge |
| scm-stm-merge: re-run one phase only | `/merge:requirements` / `db` / `functional` / `code` | scm-stm-merge |

Each project namespace also has its own `:help` (`/scm:help`, `/merge:help`) once it has more than a
couple of commands — static reference, no live analysis. `/sa:help` and `/dev:help` cover the two global
namespaces.

**The `/sa:*` namespace is now 19 commands across three lanes** — too much for one table row. Its full
walkthrough, design rationale, and a worked "inbound TSD → offer" example live in **`SA-WORKFLOW.md`**.
Start there rather than here for any presales/bid work.

## The shape underneath, in one paragraph

One generic agent per role (`dev-backend`, `dev-frontend`, `dev-reviewer`, `dev-browser-tester`,
`dev-scaffolder`, `dev-planner`, `dev-ui-analyst`,
`solution-analyst`, `mermaid-diagram-maker`, `doc-briefer`, `req-screener`, `req-ingestor`, `req-analyst`,
`req-architect`,
`req-reviewer`, `req-detailer`, `req-risk-officer`, `req-estimator`, `req-estimate-critic`, `req-offer`,
`req-auditor`, `req-slop-detector`, `req-onepager`,
`agent-reviewer` — the meta-level counterpart to `dev-reviewer`, reviewing agent/skill/command/prompt
artifacts themselves rather than application code; and `framework-strategist`, a tier above that again,
reviewing the whole framework rather than any one project) — reused
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
- **Run `/dev:init` before the first `dev-*` dispatch on a *existing* project.** Every `dev-*` agent
  refuses to proceed without `ai/dev/STATE.md`/`config.json` — enforced by `PRINCIPLES.md`, not optional.
  On a **new** project you don't run it: `dev-scaffolder` (via `/dev:new` or `/dev:build`) writes those
  files itself, along with the `ai/context/` file the implementers read.
- **`/dev:build`'s gate is the plan, not the result.** You see the task list before any code is written —
  that is the cheap moment to catch a misread goal. `--yes` skips it; type it deliberately.
- **No gates are wired as blocking anywhere yet.** `/scm:review` is on-demand, and while `/dev:build` now
  dispatches `dev-reviewer` automatically at the end of a run, its verdict **blocks nothing**. A
  `dev-backend` task reporting "Build: SUCCESS" is not the same as a reviewed task.
- **Review on a different model than wrote the code** (`AGENT-CONDUCT-BASELINE.md` B10) — pass
  `--model=<name>` to `/dev:build`. Same-model review shares the author's blind spots; where you don't pass
  it, the command says so rather than letting that pass as independence.
- **Nothing in `/dev:*` pushes, deploys, provisions, or touches a shared database.** `dev-planner` puts
  that class of work under "needs a human" instead of into the task list, and `/dev:build` halts if a task
  turns out to need one anyway.
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
- **One step *does* block: `/sa:package` refuses without a fresh PASS from *both* gates.** `/sa:audit`
  checks the JSON artifacts agree with each other by ID; `/sa:slop-check` checks the prose a human will read
  is true to them. Two gate inputs, still one refusal point, and it is deliberate — `/sa:package` is the
  only command producing something a client sees. Freshness is checked by **content hash**, so changing any
  artifact re-stales both. `/sa:review` and `/sa:estimate-review` remain advisory and block nothing.
- **Run the independent checks on a different model than wrote the work.** `/sa:review`,
  `/sa:estimate-review`, `/sa:audit` and `/sa:slop-check` all take `--model=`. A reviewer on the author's
  model shares the author's blind spots. Worth it most on `/sa:slop-check` and `/sa:estimate-review`, least
  on `/sa:audit`. It reduces correlated error; it isn't real independence — you still are.
- **The `sa:` pipeline runs on both tools, and engagements are portable between them.** Claude Code has 19
  slash commands; Copilot CLI has the same 19 steps in one `sa-pipeline` skill plus 17 `@`-dispatchable
  agents. `ai/sa/<slug>/` is project-scoped and conforms to one shared schema, so an engagement triaged in
  one can be continued in the other. **Two things differ**: Copilot's packaging step cannot *refuse* (it
  checks and reports, so run binding deliverables in Claude Code), and its model selection is session-level
  (`/model` before dispatching a checking agent). `copilot\PORT-NOTES.md` has all six divergences.
- **`/sa:doc`, `/sa:onepager` and `/sa:offer` are three different documents.** `/sa:doc` is an *internal*
  consolidation for your team; `/sa:onepager` is one dense page for the meeting where nobody read it; the
  client-facing path is `/sa:offer` → `/sa:audit` + `/sa:slop-check` → `/sa:package`. Confusing them is how
  internal risk language reaches a client.
- **Estimates are effort, never price.** With no `rates.yaml` configured you get effort-only output, said
  plainly — never an invented number. See `sa-framework/ESTIMATION-METHOD.md §5` and `SETUP.md` for the
  rate-card step.
- **Never commit is enforced only where a command says so** (SCM's `/scm:fix`/`/scm:req`/
  `/scm:devops-change`). The generic `dev-*` agents and `/dev:quick` have no opinion on commits — that's a
  project-specific mechanic, not a global rule.
