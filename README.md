# _AI_GIT — Cross-tool Agentic Framework

Staging and distribution source for generic, project-agnostic dev/work agents, commands, skills, and
doctrine — shared across every AI coding tool in use on this machine. Files here are drafted, reviewed
manually, then copied into each tool's own live config root (`~\.claude\` for Claude Code, `~\.copilot\`
for GitHub Copilot CLI) — nothing here is live/active in any tool until that copy step happens.

Project-specific agents, commands, and context belong in each project's own repo (its own `.claude\`/
`.github\` and `ai\context\`), never here — see `DESIGN-PRINCIPLES-BASELINE.md`'s and
`AGENT-CONDUCT-BASELINE.md`'s own "how to use" sections for how generic and project-specific artifacts
connect.

**Exclusion**: nothing from `d:\WORK\Private\Költségvetés\` may appear in this repo's content, ever — that
project's material never informs, and is never cited by, anything drafted here.

---

## The three-way split

| Branch | What's there | Detail |
|---|---|---|
| **Shared** (this level) | Doctrine and content genuinely tool-agnostic — binding rules, drafting checklists, the `dev-*`/`req-*` method docs, and skills (already the open, cross-tool `SKILL.md` format both Claude Code and Copilot CLI read natively). | Table below |
| **`claude\`** | Everything Claude-Code-format-specific: agents, legacy commands, `CLAUDE.md`, `AGENT-TEMPLATE-BASELINE.md`. Full-fidelity tier — subagent dispatch, `/sa:*`/`/dev:*` pipelines, the `/sa:audit` blocking gate. | `claude\README.md` |
| **`copilot\`** | Everything Copilot-CLI-format-specific: `.agent.md`/`SKILL.md` twins, `AGENTS.md`. Currently a **doctrine-only scaffold** — empty `agents\`/`skills\`, no `req-*`/`sa:` port yet; that's a deliberate, separate scope decision. | `copilot\README.md` |

Why split this way rather than keep everything flat: Claude Code and Copilot CLI use different, mutually
unreadable file formats for agents/commands (frontmatter dialect, dispatch mechanics), so anything
tool-specific has to live somewhere unambiguous — while `CONSTITUTION.md`, both remaining baselines here,
`dev-framework\`, `sa-framework\`, and `skills\` are genuinely prose/data that both tools' agents can read
as-is, so duplicating them per branch would just create drift with no benefit.

## Repository layout — shared doctrine

| Path | What it is |
|---|---|
| `CONSTITUTION.md` | **Binding**, global hard rules (secrets, destructive actions, gates, scope, tool permissions). Every generic agent reads this first. Not a checklist like the two below — this one is live doctrine. |
| `DESIGN-PRINCIPLES-BASELINE.md` | Checklist for drafting a **project's own** `ai/context/design-principles.md` — code/architecture principles (layering, DI, DTOs, isolation boundaries). Not itself binding on any project. |
| `AGENT-CONDUCT-BASELINE.md` | Checklist for drafting a **new agent's own** `<rules>` section — how an agent should behave while working (executor discipline), while reviewing others' work (reviewer discipline), or while using persistent memory (memory conduct). Not code-architecture rules — see the table in this file for the distinction. |
| `sa-framework\ARTIFACT-SCHEMAS.md` | **Binding** data contract for the `req-*` family and the `/sa:*` namespace — the JSON schema for every artifact, the universal `meta` block, ID conventions, the three-lane model, the canonical `STATE.md` shape, and the content-hash packaging gate. Also records why JSON-as-source-of-truth deliberately reverses `req-analyst` v1.1.0's "stay narrative" rule. Added 2026-08-12. |
| `sa-framework\ESTIMATION-METHOD.md` | **Binding** estimation method for `req-estimator`/`req-estimate-critic`/`req-risk-officer` (and, for §5 only, `req-screener` — §8 records why a screening band is exempt from the derivation machinery and may never be quoted) — PERT and spread rules, the K1–K6 work-type compression factors for AI-assisted delivery, the probability × impact severity matrix and contingency bands, the calibration commitment gate, the effort-is-not-price separation, the commonly-forgotten lifecycle lines, and the `rates.yaml` schema. Codified from the real Netrisk CampaignManager v1/v2 estimates rather than invented. Added 2026-08-12. |
| `dev-framework\PRINCIPLES.md` | **Binding** shared protocol for the `dev-*` role-specialist agent family (state loading, lane discipline, contract discipline, commit/report format, blocked protocol). Scoped to that one family — not global like `CONSTITUTION.md`, not a checklist like the `*-BASELINE.md` files. |
| `dev-framework\DESIGN.md` | Rationale for the `dev-*` family — why it's deliberately lighter than the reference framework's full wave/gate pipeline, the canonical `ai/dev/` state-file schema, explicit non-goals, and the trigger condition for revisiting them. Read when deciding whether to extend this family, not at runtime. |
| `skills\` | Generic skill definitions (`skills\<name>\SKILL.md`, one folder per skill) — the open, cross-tool format, copied to `~\.claude\skills\` and (once approved) `~\.copilot\skills\`. The canonical form for new reusable, `/name`-invocable work going forward. |
| `estimation-data\` | `rates.yaml.example` only — the rate-card template. A filled-in card is commercially sensitive and gitignored; copy it to the live config root and edit it there. |
| `framework-data\` | `scope.yaml.example` only — the scope template `framework-strategist` reads to learn which roots to review on a given machine (staging repo, every live config root, knowledge base, report dir, survey roots, and the hard exclusion list). A filled-in scope file names personal/machine-specific paths, so it's gitignored and lives only at the live config root — same indirection as `estimation-data\`, and the reason the agent itself stays generic. Added 2026-09-05. |
| `docs\` | Reference documentation that stays in this repo (not copied anywhere) — `GETTING-STARTED.md` (first-time walkthrough for someone new to agentic work), `SETUP.md` (install/verify/troubleshoot, both tools), `USAGE.md` (cross-repo "which entry point when" map), `UPDATING.md` (what's automatic vs. manual when you edit something here, per branch — read before assuming a change is already live), and `SA-WORKFLOW.md` (the requirement→offer pipeline: lanes, the five design decisions, a worked example, and what was deliberately not copied from the reference framework). |

For the full agent/skill/command inventory, the authoring workflow, and the Claude rollout steps, see
**`claude\README.md`**. For the Copilot scaffold and its proposed (not-yet-run) rollout, see
**`copilot\README.md`**.

## Install / verify / troubleshoot / update

See `docs\SETUP.md` for both tools' install steps, verification checklist, optional plugins, and
troubleshooting. `_scripts\check-sync.ps1` (run manually or via the `post-commit` hook installed by
`_scripts\install-hooks.ps1`) reports drift between what's staged here and what's actually live in each
Claude Code config root. See `docs\UPDATING.md` for what's automatic vs. manual when you change something
here, broken down per branch (shared doctrine / `claude\` / `copilot\`).
