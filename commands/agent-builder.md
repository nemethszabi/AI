---
name: agent-builder
description: Interactively draft a new Claude Code agent and/or its companion command, following this repo's established conventions (generic-vs-project placement, naming, tool-permission discipline, XML-vs-Markdown body style) and consulting CONSTITUTION.md / AGENT-CONDUCT-BASELINE.md / DESIGN-PRINCIPLES-BASELINE.md as applicable.
argument-hint: [one-line description of the new agent/command's purpose — will ask if omitted]
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Draft a new, correctly-structured agent (`.claude\agents\*.md`) and/or command
(`.claude\commands\*.md`), staying in this conversation rather than delegating to an isolated subagent —
prompt-drafting is iterative (plan → draft → review → fix), and an isolated agent that reports once and
disappears loses that loop. This command exists to make the house conventions built up in this repo
mechanical to apply, not something to re-derive from memory each time.
</objective>

<process>

<step name="intake">
From `$ARGUMENTS`, or by asking if omitted: what is the new agent/command for? Get a one- or two-sentence
description of its job before proceeding — do not start drafting from a vague request.
</step>

<step name="classify">
Resolve, asking via `AskUserQuestion` only for whichever of these aren't already obvious from the intake
description:

- **Agent, command, or both?** A read-and-report job with real internal process (like
  `solution-analyst`) is an agent. A thin dispatcher, or something that only makes sense typed by name
  (`/scaffold-context`), is a command. Many real cases are both — an agent plus a thin command that
  invokes it, same shape as `solution-analyst` + `scaffold-context`.
- **Generic or project-specific?** Apply the tell from the review doc (§10): does the draft need to
  contain a fact that only makes sense in one repo — an absolute path, an org name, a stack fact, a
  build command? If yes → project-specific. If it only discovers facts at runtime from wherever it's
  invoked → generic. If genuinely unclear, ask directly rather than guessing.
- **If project-specific**: which project/repo? Its own `.claude\agents\` / `.claude\commands\` is the
  target, not this repo.
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
4. `d:\WORK\AI\results\claude-prompting-system-review.md` §10 (generic/specific decision rule), §13
   (naming conventions table) — for placement and file-naming, not duplicated into this file to avoid
   drift between the two.
</step>

<step name="design-summary">
For anything beyond a trivial, unambiguous request, present a short summary before writing any file —
mirroring the plan-then-approve pattern already used in this repo (`solution-analyst` went through this
exact loop):

```
## Draft plan: <name>

Type: agent | command | both
Scope: generic (~\.claude\) | project-specific (<repo>\.claude\)
Role: executor | reviewer | dispatcher
Tools: <list, with one-line justification for each — least privilege, not convenience>
Conventions applied: <which of CONSTITUTION / AGENT-CONDUCT / DESIGN-PRINCIPLES sections, or "none — no
  code-architecture surface">
Body style: XML | Markdown (state which, and why — XML only if the draft needs to embed example
  Markdown output, per the collision rule already established in this repo)
```

Wait for explicit go-ahead before drafting. Skip this step only for something genuinely small and
unambiguous (the user should be able to tell when a plan step is overkill; when in doubt, show it).
</step>

<step name="draft">
Write the file(s):

- **Naming**: kebab-case. Generic agent → `<role>.md`, no project prefix. Project agent →
  `<project-prefix>-<role>.md`. Commands mirror the same rule, optionally namespaced under a subfolder
  (`commands\<namespace>\<verb>.md` → `/namespace:verb`) once there's more than one command in a related
  family — a single standalone command stays flat.
- **Frontmatter**: agents use `tools:` (comma list). Commands use `allowed-tools:` (YAML list). Match
  whichever file type is being written — they are not interchangeable keys.
- **Tool list**: minimum the role actually needs. No `Edit` unless the agent modifies existing files. No
  `Task`/`Agent` on a leaf-level specialist — orchestration belongs in the calling command, not a
  leaf agent, unless the whole point of this one is to orchestrate others.
- **Body**: Markdown headers by default. Switch to XML tags only if the draft embeds an example Markdown
  output block (avoids the outer/inner heading collision) — state this decision in the design summary
  above, don't silently pick one.
- **Placement**: generic → this repo's `agents\` or `commands\` (staged, not live until copied to
  `~\.claude\` — say so in the report). Project-specific → the target repo's own `.claude\agents\` or
  `.claude\commands\` directly (no staging step for those — they're only ever relevant to that one repo).
</step>

<step name="self-check">
Before reporting done:
- If XML tags were used, verify every opening tag has exactly one matching closing tag (a stray or
  missing tag is a real, previously-caught defect class in this repo — check with a tool-assisted count,
  not by eye).
- Frontmatter key correctness (`tools:` vs `allowed-tools:`) matches the file type actually written.
- Naming matches the convention for its generic/project-specific classification.
</step>

<step name="report">
```
## Built: <name>

Files: <path(s) written>
Type: agent | command | both
Scope: generic (staged in this repo — not live until copied to ~\.claude\) | project-specific (already
  live in its own repo's .claude\)
Conventions consulted: <list; note explicitly if CONSTITUTION.md was skipped because it doesn't exist
  yet>
Still needs: <manual review; copy-to-global step if generic; a test run if this is meant to be invoked
  soon>
```
</step>

</process>
