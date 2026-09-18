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
| **`copilot\`** | Everything Copilot-CLI-format-specific: `.agent.md` siblings, `AGENTS.md`, `PORT-NOTES.md`. **Full-pipeline tier since 2026-09-07** — 17 agents plus the `sa:` command layer as a `sa-pipeline` skill. Two capability gaps are documented rather than hidden: packaging cannot *refuse*, and read-only cannot be enforced structurally. | `copilot\README.md` |

Why split this way rather than keep everything flat: Claude Code and Copilot CLI use different, mutually
unreadable file formats for agents/commands (frontmatter dialect, dispatch mechanics), so anything
tool-specific has to live somewhere unambiguous — while `CONSTITUTION.md`, both remaining baselines here,
`dev-framework\`, `sa-framework\`, and `skills\` are genuinely prose/data that both tools' agents can read
as-is, so duplicating them per branch would just create drift with no benefit.

**The governing principle, since both branches carry the same pipeline: share the method, separate the
mechanics.** A statement about the *work* — what an artifact must contain, how an estimate is derived, which
step runs when, what a gate means — is shared, byte-identical, cited by both sides. A statement about a
*tool* — frontmatter dialect, dispatch syntax, how a model is selected — is native to its branch. The test
when adding something: would this sentence still be true if the other tool did not exist? If yes it is
shared; if no it belongs in a branch. `sa-framework\PIPELINE.md` exists because applying that test to the
19 `sa:` command files found most of their content on the shared side of it.

## Repository layout — shared doctrine

| Path | What it is |
|---|---|
| `CONSTITUTION.md` | **Binding**, global hard rules (secrets, destructive actions, gates, scope, tool permissions). Every generic agent reads this first. Not a checklist like the two below — this one is live doctrine. |
| `DESIGN-PRINCIPLES-BASELINE.md` | Checklist for drafting a **project's own** `ai/context/design-principles.md` — code/architecture principles (layering, DI, DTOs, isolation boundaries). Not itself binding on any project. |
| `AGENT-CONDUCT-BASELINE.md` | Checklist for drafting a **new agent's own** `<rules>` section — how an agent should behave while working (executor discipline), while reviewing others' work (reviewer discipline), while using persistent memory (memory conduct), or while writing prose a human will send onward (groundedness & slop conduct, section D — added 2026-09-07 alongside B10, which requires an independent review to run on a *different model* than produced the work, since sharing the author's model means sharing the author's blind spots). Not code-architecture rules — see the table in this file for the distinction. |
| `sa-framework\ARTIFACT-SCHEMAS.md` | **Binding** data contract for the `req-*` family and the `/sa:*` namespace — the JSON schema for every artifact, the universal `meta` block, ID conventions, the three-lane model, the canonical `STATE.md` shape, and the content-hash packaging gate, which since 2026-09-07 takes **two** verdicts (`sa-audit` for ID integrity, `sa-slop` for prose integrity) at one refusal point. Also §8 (document profiles — the `templates.yaml` indirection that lets a generic command produce branded output) and §9 (independent review runs on a different model). Records why JSON-as-source-of-truth deliberately reverses `req-analyst` v1.1.0's "stay narrative" rule. Added 2026-08-12. |
| `sa-framework\PIPELINE.md` | **Binding**, **tool-agnostic** pipeline contract for the `sa:` namespace — the step table (preconditions, dispatch target, artifacts, `STATE.md` phase, `Next`), the eight obligations every dispatching step carries, the two-verdict gate contract including what a tool that *cannot* refuse must do instead, the cross-model review rule, and a **conformance checklist** defining what "same functionality" means across two implementations. Extracted 2026-09-07 when the pipeline was ported to Copilot CLI and the per-command duplication would otherwise have doubled from 19 files to 38. Both tools' command layers cite it rather than restating it. Added 2026-09-07. |
| `sa-framework\ESTIMATION-METHOD.md` | **Binding** estimation method for `req-estimator`/`req-estimate-critic`/`req-risk-officer` (and, for §5 only, `req-screener` — §8 records why a screening band is exempt from the derivation machinery and may never be quoted) — PERT and spread rules, the K1–K6 work-type compression factors for AI-assisted delivery, the probability × impact severity matrix and contingency bands, the calibration commitment gate, the effort-is-not-price separation, the commonly-forgotten lifecycle lines, and the `rates.yaml` schema. Codified from the real Netrisk CampaignManager v1/v2 estimates rather than invented. Added 2026-08-12. |
| `dev-framework\PRINCIPLES.md` | **Binding** shared protocol for the `dev-*` role-specialist agent family (state loading, lane discipline, contract discipline, commit/report format, blocked protocol). Scoped to that one family — not global like `CONSTITUTION.md`, not a checklist like the `*-BASELINE.md` files. |
| `dev-framework\DESIGN.md` | Rationale for the `dev-*` family — why it's deliberately lighter than the reference framework's full wave/gate pipeline, the canonical `ai/dev/` state-file schema (incl. `PLAN.md`/`BUILD-LOG.md`), explicit non-goals, and the trigger condition for revisiting them. **Records that trigger #1 fired on 2026-09-07** and what was added in response. Read when deciding whether to extend this family, not at runtime. |
| `dev-framework\STACK-DOTNET.md` | **Binding on `dev-scaffolder`**, advisory to the rest: the house .NET stack profile for demo/prototype apps — solution layout, default choice per concern, what a scaffold must verify before claiming success, and the non-negotiables that survive "it's only a demo". Exists because the `dev-*` family resolves stack facts by *reading a project's context file*, which works for brownfield and breaks entirely on greenfield, where no such file exists yet — without a house default, every generated app is a different stack. Rule 0: versions are **detected** (`dotnet --version`), never asserted from memory. A project's own `ai/context/*.md` outranks it once that exists. Added 2026-09-07. |
| `dev-framework\HANDOFF.md` | **Binding**, **tool-agnostic** session-handoff contract — `ai/handoff/` location and name, file structure, `Status` lifecycle (`open`/`resumed`/`closed`), approval-gated deletion, and a conformance list. Implemented by Claude's `claude\commands\handoff.md` and Copilot's `copilot\skills\handoff\SKILL.md`, so a handoff written in one tool is resumed in the other. Lives in `dev-framework\` because `PRINCIPLES.md` already owns the `ai/` layout and the folder reaches both roots. Added 2026-09-14. |
| `dev-framework\PR-WORKFLOW.md` | **Binding** contract for `pr-reviewer`, `pr-fixer` and the `/pr:*` commands — who may do what (the agents hold **no** PR-provider tool; only the command posts, commits or pushes, and only after a per-run human approval, Articles VI/VII), the project-side `ai/pr/` files (`config.json` naming an MCP server, never a credential; `review-guidelines.md`; `fix-guidelines.md`), the per-run artifacts under `ai/pr/results/PR-<id>/`, the `comments-*.json` / `replies-*.json` schemas, the fixed severity scale, both verdict blocks, the requirement-input rule, and the throwaway PR-head worktree a review reads from. Provider- and stack-agnostic by construction: everything a project knows is data in its own repo. Lives in `dev-framework\` for the same reason `HANDOFF.md` does — that folder already reaches every root. Added 2026-09-18. |
| `dev-framework\BUG-WORKFLOW.md` | **Binding** contract for `bug-analyst`, `bug-fixer` and the `/bug:*` commands — incident to fix in two gated steps: **analyze** (logs + description → unified cross-component timeline, anomalies incl. *expected-but-missing* events, a root cause at one of three honest levels `CONFIRMED` / `HYPOTHESIS` / `INSUFFICIENT EVIDENCE`, and a written fix proposal when the cause is located in code) and **fix** (only the proposal a human approved or amended in that run). Defines the project-side `ai/bug/` data (`config.json` with components, log globs, build commands, protected branches; `log-guide.md`), the customer-data rule that **results never land in a tracked folder** (checked with `git check-ignore`, Article VIII) and that pattern entries carry the mechanism only, and both verdict blocks. Sibling of `PR-WORKFLOW.md`, same design rule: generic agents, project = data. Generalised from a project-specific log-analysis prompt rather than copying it into a project. Added 2026-09-18. |
| `skills\` | Generic skill definitions (`skills\<name>\SKILL.md`, one folder per skill) — the open, cross-tool format, copied to `~\.claude\skills\` and `~\.copilot\skills\` (minus the recorded not-ported list). The canonical form for new reusable, `/name`-invocable work going forward. |
| `estimation-data\` | `rates.yaml.example` only — the rate-card template. A filled-in card is commercially sensitive and gitignored; copy it to the live config root and edit it there. |
| `document-data\` | `templates.yaml.example` only — the document-profile map that tells `/sa:package` which branded `.docx` shell to build into for a given language and locale (`sa-framework\ARTIFACT-SCHEMAS.md` §8). The filled-in `templates.yaml` and the `.docx` files themselves are organization property with machine-specific paths, so both are gitignored and live at `<config-root>\document-data\` — the same indirection as `estimation-data\` and `framework-data\`, and the reason `/sa:package` stays generic while still producing branded output. It sits outside `sa-framework\` specifically because `_scripts\check-sync.ps1` compares that folder byte-for-byte against every live root, so a live-only file inside it would be reported `EXTRA` forever. Added 2026-09-07. |
| `framework-data\` | `scope.yaml.example` only — the scope template `framework-strategist` reads to learn which roots to review on a given machine (staging repo, every live config root, knowledge base, report dir, survey roots, and the hard exclusion list). A filled-in scope file names personal/machine-specific paths, so it's gitignored and lives only at the live config root — same indirection as `estimation-data\`, and the reason the agent itself stays generic. Added 2026-09-05. |
| `_scripts\` | Repo tooling, not rolled out — hook scripts are referenced in place by each root's settings. `check-sync.ps1` (staged-vs-live drift, all four roots) and `install-hooks.ps1` (its `post-commit` hook); `hooks\` — `guard-irreversible-bash.py` (`PreToolUse` on `Bash\|PowerShell`, Articles II/III) and `framework-change-flag.py` (suggests `/doc-sync`), with tests in `hooks\tests\`; `usage\` — the cross-tool token/cost toolkit, status line and context guard (see its own `README.md`). |
| `results\` | Historical only. `SESSION-STATE.md` is the 2026-08-07/08-12 hand-off from when this repo was first built; current session hand-offs follow `dev-framework\HANDOFF.md` instead. |
| `docs\` | Reference documentation that stays in this repo (not copied anywhere) — `GETTING-STARTED.md` (first-time walkthrough for someone new to agentic work), `SETUP.md` (install/verify/troubleshoot, both tools), `USAGE.md` (cross-repo "which entry point when" map), `UPDATING.md` (what's automatic vs. manual when you edit something here, per branch — read before assuming a change is already live), `SA-WORKFLOW.md` (the requirement→offer pipeline: lanes, the five design decisions, a worked example, and what was deliberately not copied from the reference framework), and `FRAMEWORK-REVIEW-WORKFLOW.md` (the periodic framework self-review loop: what the review does and doesn't change itself, how an approved proposal actually gets built and rolled out, and why the tool deliberately can't apply its own findings). |

For the full agent/skill/command inventory, the authoring workflow, and the Claude rollout steps, see
**`claude\README.md`**. For the Copilot branch — its agents, skills, hooks, what is deliberately not ported,
and its rollout — see **`copilot\README.md`**.

## Install / verify / troubleshoot / update

See `docs\SETUP.md` for both tools' install steps, verification checklist, optional plugins, and
troubleshooting. `_scripts\check-sync.ps1` (run manually or via the `post-commit` hook installed by
`_scripts\install-hooks.ps1`) reports drift between what's staged here and what's actually live in each
Claude Code config root. See `docs\UPDATING.md` for what's automatic vs. manual when you change something
here, broken down per branch (shared doctrine / `claude\` / `copilot\`).
