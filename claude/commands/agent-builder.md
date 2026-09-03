---
name: agent-builder
description: Interactively draft a new Claude Code agent, skill, and/or legacy command, following this repo's established conventions (generic-vs-project placement, naming, tool-permission discipline, XML-vs-Markdown body style, the no-XML-tags rule for Skills) and consulting CONSTITUTION.md / AGENT-CONDUCT-BASELINE.md / DESIGN-PRINCIPLES-BASELINE.md as applicable.
argument-hint: [one-line description of the new agent/skill/command's purpose — will ask if omitted]
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
---

> Version: 1.0.2 — patch: added the Article IX personal-vs-generic classify check (real mistake caught
> live — `travel-planner` was first drafted into `_AI_GIT` before being corrected). 1.0.1 added the
> Command-vs-Skill self-consistency note (`agent-reviewer` finding). 1.0.0 was the first tracked version.

<objective>
Draft a new, correctly-structured agent (`.claude\agents\*.md`), skill (`.claude\skills\*\SKILL.md`),
and/or legacy command (`.claude\commands\*.md`), staying in this conversation rather than delegating to
an isolated subagent — prompt-drafting is iterative (plan → draft → review → fix), and an isolated agent
that reports once and disappears loses that loop. This command exists to make the house conventions built
up in this repo mechanical to apply, not something to re-derive from memory each time.

This file itself remains a legacy Command, not a Skill, purely because it predates Skills and was updated
in place rather than converted — a Skill would preserve the same inline-iteration property equally well
(per this file's own `classify` step), so there's no principled Command-vs-Skill argument here, just
history. Converting it is a reasonable future step, not yet done — noted honestly rather than inventing a
rationale that doesn't hold up against this file's own stated criteria (`agent-reviewer` finding,
2026-08-10).

For a lighter-weight, non-repeating prompt that doesn't need any of this machinery — no tool grant, no
scope classification, no self-check — use `skills\prompt-builder\SKILL.md` instead. This command is for
things that will be invoked repeatedly as a named artifact.
</objective>

<process>

<step name="intake">
From `$ARGUMENTS`, or by asking if omitted: what is the new agent/skill/command for? Get a one- or
two-sentence description of its job before proceeding — do not start drafting from a vague request.
</step>

<step name="classify">
Resolve, asking via `AskUserQuestion` only for whichever of these aren't already obvious from the intake
description:

- **Agent, skill, or command?**
  - **Agent**: needs an isolated context window (bias avoidance / fresh-eyes review), enforced tool
    restriction beyond what a single conversation turn provides, autonomous multi-step tool use, or
    proactive auto-delegation matched by its own `description`.
  - **Skill** (default for anything that isn't an agent): explicit `/name` invocation, optionally also
    auto-triggered by its own `description`, runs inline in the current conversation unless authored to
    dispatch into a subagent. This is the canonical form for new work going forward — commands are a
    legacy path Claude Code still runs but isn't developing further.
  - **Command** (legacy — rare, don't default here out of habit): only for something small enough that a
    skill's folder structure is pure overhead, and you're confident it will never need bundled resources
    or auto-triggering.
  - Many real cases are both — an agent plus a thin skill/command that invokes it, same shape as
    `solution-analyst` + `scaffold-context`.
- **Generic or project-specific?** Apply the tell from the review doc (§10): does the draft need to
  contain a fact that only makes sense in one repo — an absolute path, an org name, a stack fact, a
  build command? If yes → project-specific. If it only discovers facts at runtime from wherever it's
  invoked → generic. If genuinely unclear, ask directly rather than guessing.
  **Personal-life content (travel, health, finance, hobbies, or similar — anything not dev/work) is
  always project-specific to `d:\WORK\AI`, never generic, even if it looks reusable/global in shape** —
  `CONSTITUTION.md` Article IX. Check this *before* defaulting to "generic" just because there's only one
  user of the whole framework; that reasoning applies to *scope* (global-feeling, personal), not to
  *placement* (still never `_AI_GIT`).
- **If project-specific**: which project/repo? Its own `.claude\agents\` / `.claude\skills\` /
  `.claude\commands\` is the target, not this repo — including `d:\WORK\AI\.claude\` for personal-life
  output, per the rule above.
- **Executor or reviewer role?** (agents only) An executor does work (reads, analyzes, drafts, sometimes
  writes). A reviewer checks someone else's work and should be read-only by tool permissions, not just
  by instruction.
- **Does it touch target-code architecture?** (agents that modify or design code, not ones that just
  read/report) If yes, `DESIGN-PRINCIPLES-BASELINE.md` is relevant to its `<role>`/`<process>`; if it
  never touches code shape, skip it.
</step>

<step name="consult-conventions">
Read, in this order, whatever exists (skip silently if a file doesn't exist yet — note the gap in the
final report rather than failing):

1. `CONSTITUTION.md` (this repo's root) — binding, always relevant if present.
2. `AGENT-CONDUCT-BASELINE.md` (this repo's root) — always. Use the Executor section or the Reviewer
   section per the `classify` step's answer, not both.
3. `DESIGN-PRINCIPLES-BASELINE.md` (this repo's root) — only if `classify` flagged architecture-touching.
4. `d:\WORK\AI\knowledge-base\claude-prompting-kb.md` §1–2 (artifact-type decision tree) and
   `d:\WORK\AI\results\claude-prompting-system-review.md` §10 (generic/specific decision rule), §13
   (naming conventions table) — for placement and file-naming, not duplicated into this file to avoid
   drift between the two.

No dedicated Skill baseline file exists yet — the conventions below are folded directly into this
command's own `draft` step. Only worth extracting to its own `*-BASELINE.md` once the same skill-specific
rule ends up duplicated across 3+ drafted skills (same threshold already applied to every other doctrine
file in this repo).
</step>

<step name="design-summary">
For anything beyond a trivial, unambiguous request, present a short summary before writing any file —
mirroring the plan-then-approve pattern already used in this repo (`solution-analyst` went through this
exact loop):

```
## Draft plan: <name>

Type: agent | skill | command (legacy) | combination
Scope: generic (~\.claude\) | project-specific (<repo>\.claude\)
Role: executor | reviewer | dispatcher
Tools: <list, with one-line justification for each — least privilege, not convenience>
Conventions applied: <which of CONSTITUTION / AGENT-CONDUCT / DESIGN-PRINCIPLES sections, or "none — no
  code-architecture surface">
Body style: Markdown only if Skill (XML/angle-bracket tags are forbidden in SKILL.md — spec-level
  prompt-injection constraint, not a style choice) | XML or Markdown if agent/command (XML only if the
  draft needs to embed an example Markdown output block, per the collision rule already established here)
```

Wait for explicit go-ahead before drafting. Skip this step only for something genuinely small and
unambiguous (the user should be able to tell when a plan step is overkill; when in doubt, show it).
</step>

<step name="draft">
Write the file(s):

- **Naming**: kebab-case throughout.
  - Generic agent → `claude\agents\<role>.md`, no project prefix. Project agent →
    `<repo>\.claude\agents\<project-prefix>-<role>.md`.
  - Generic skill → `skills\<role>\SKILL.md` (shared, repo root — a folder, not a flat file — the folder
    name matches the skill's own `name:` frontmatter field). Project skill →
    `<repo>\.claude\skills\<project-prefix>-<role>\SKILL.md`.
  - Legacy commands mirror the agent naming rule, optionally namespaced under a subfolder
    (`claude\commands\<namespace>\<verb>.md` → `/namespace:verb`) once there's more than one command in a
    related family — a single standalone command stays flat.
- **Frontmatter**:
  - Agents use `tools:` (comma list).
  - Commands use `allowed-tools:` (YAML list).
  - Skills' `SKILL.md` requires only `name` + `description` — everything else (tool restrictions, model,
    execution environment) is optional per the open Agent Skills spec; verify current optional field
    names against Anthropic's own skill docs at draft time rather than assuming a specific key here.
  - These are not interchangeable — match whichever file type is actually being written.
- **The `description` field is the actual trigger for a Skill** — not the name, not the slash form. Write
  it to describe *when this should fire*, not just what it does; a vague description is the most common
  reason a skill silently never auto-triggers. Commands' `description` is documentation only, no such
  requirement.
- **No XML/angle-bracket tags anywhere in a Skill's body** — hard spec constraint (prompt-injection
  risk if untrusted tags could inject instructions before the skill loads), not a style preference like
  the XML-vs-Markdown choice for agents/commands. Plain Markdown headers only.
- **Bundled resources** (Skills only): if the skill's job benefits from scripts, templates, or reference
  docs loaded on demand rather than always in context, put them in the same folder alongside `SKILL.md`
  and reference them by relative path — this is the progressive-disclosure mechanism the folder shape
  exists for. Don't inline something long into `SKILL.md` itself if it's only needed in a minority of
  invocations.
- **Tool list**: minimum the role actually needs. No `Edit` unless the agent modifies existing files. No
  `Task`/`Agent` on a leaf-level specialist — orchestration belongs in the calling skill/command, not a
  leaf agent, unless the whole point of this one is to orchestrate others (and note: this repo's own
  `CONSTITUTION.md` Article VI.2 forbids an agent spawning another agent regardless — orchestration must
  live in the skill/command layer, never inside an agent's own definition).
- **Body**: Markdown headers by default for everything; XML tags remain an option for agent/command
  bodies only, and only if the draft embeds an example Markdown output block (avoids the outer/inner
  heading collision) — state this decision in the design summary above, don't silently pick one. Never
  XML for a Skill body, no exception.
- **Placement**: generic → this repo's `claude\agents\`, `skills\` (shared, repo root), or
  `claude\commands\` (staged, not live until copied to `~\.claude\` — say so in the report).
  Project-specific → the target repo's own
  `.claude\agents\`, `.claude\skills\`, or `.claude\commands\` directly (no staging step for those —
  they're only ever relevant to that one repo).
- **Versioning**: add a `> Version: 1.0.0` line near the top of the body (right after frontmatter) for
  agents, skills, and commands — not needed for one-time prompts (`prompt-builder`'s territory). On an
  edit to an existing file rather than a first draft, bump it: patch for wording/quality fixes, minor for
  new steps/capabilities, major for a structural rewrite. No separate changelog file — the version number
  plus this repo's own `results\SESSION-STATE.md` dated entries are enough at this scale.
</step>

<step name="self-check">
Before reporting done:
- If XML tags were used (agent/command only), verify every opening tag has exactly one matching closing
  tag (a stray or missing tag is a real, previously-caught defect class in this repo — check with a
  tool-assisted count, not by eye).
- If a Skill was drafted: grep `SKILL.md`'s body for any `<` outside of a fenced code block or Markdown
  table — zero should remain. This is a hard constraint, not a judgment call.
- If a Skill was drafted: re-read its `description` field and confirm it states *when* to trigger, not
  just what the skill does.
- A `> Version: 1.0.0` line is present (or correctly bumped, if this was an edit).
- Frontmatter key correctness (`tools:` vs `allowed-tools:` vs Skill's `name`+`description`) matches the
  file type actually written.
- Naming matches the convention for its generic/project-specific classification, and a Skill's folder
  name matches its own `name:` field.
</step>

<step name="report">
```
## Built: <name>

Files: <path(s) written>
Type: agent | skill | command (legacy) | combination
Scope: generic (staged in this repo — not live until copied to ~\.claude\) | project-specific (already
  live in its own repo's .claude\)
Conventions consulted: <list; note explicitly if CONSTITUTION.md was skipped because it doesn't exist
  yet>
Still needs: <a review-agent pass before trusting/copying (dispatch skills\review-agent\SKILL.md);
  copy-to-global step if generic (skills copy to ~\.claude\skills\, same as agents/commands — see this
  repo's README Rollout section); a test run if this is meant to be invoked soon>
```
</step>

</process>
