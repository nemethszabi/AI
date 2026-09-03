# Agent & Command Template — Baseline

A reusable skeleton for the **file structure** of a new agent or command — frontmatter fields, section
tags, tone. Distinct from `AGENT-CONDUCT-BASELINE.md`, which governs *behavior*; this file governs
*shape*. Global, cross-project — draft here, copy to `~\.claude\AGENT-TEMPLATE-BASELINE.md` alongside the
other baselines.

Synthesized from real files, not invented: `claude\agents\solution-analyst.md` (this repo), and
`dev-reviewer.md`, `mermaid-diagram-maker.md`, `sa-completeness-auditor.md` (via
`commands/sa/audit-deliverable.md`'s invocation contract) from
`d:\_GEOMANT_GIT\agentic-dev-framework\`.

---

## How to use this file

Walk it once per new agent/command, top to bottom. Skip a piece only if it genuinely doesn't apply —
don't force-fit ceremony onto a two-line dispatcher command (see `claude\commands\scaffold-context.md` for
what a minimal command looks like).

---

## 1. Frontmatter

| Field | Agents | Commands | Notes |
|---|---|---|---|
| `name` | kebab-case, no project prefix if generic | kebab-case; may include namespace (`sa:help`) | See `README.md`'s generic-vs-project rule |
| `description` | One paragraph: what it does + when to use it. Add `Use PROACTIVELY when...` if it should be auto-invoked without being asked by name. | One line: what running it produces | This is the *only* thing the orchestrator sees before deciding to invoke it — write for that, not for a human skimming |
| `tools:` | comma list, agents only | — | Minimum the role needs — see `AGENT-CONDUCT-BASELINE.md` A6 |
| `allowed-tools:` | — | YAML list, commands only | Different key name from `tools:` — confirmed distinct, not a typo |
| `argument-hint` | — | optional, commands only | e.g. `[path, optional]` |
| `color` | optional | — | Cosmetic only; doesn't gate behavior |
| `model` | optional | — | Set only when the role genuinely needs a specific tier (e.g. a cheap high-volume scanner vs. a judgment-heavy critic) — don't pin a model by default |
| `memory: user` | optional | — | Only when cross-session, cross-project learning has real value — see `AGENT-CONDUCT-BASELINE.md`'s Memory conduct section before adding this |

## 2. Section skeleton — agents

```
<role>
  Identity in 1-2 sentences. Then: "First action: ..." — the concrete first step, always including
  reading ~/.claude/CONSTITUTION.md if the agent is generic/global (see solution-analyst.md).
</role>

<mode_detection>   -- only if the agent branches its whole approach on discovered state
  (e.g. CREATE vs UPDATE). Omit entirely if the agent always does one thing.
</mode_detection>

<process>
  <step name="...">...</step>   -- one per real phase of work, imperative, in execution order
  ...
</process>

<review_dimensions> / <findings_discipline>   -- reviewer/gate agents only, see AGENT-CONDUCT-BASELINE
  section B. Ranked-by-severity checklist + how a finding must be evidenced.
</review_dimensions>

<output_template>   -- only if the agent writes a file with a fixed shape
  The literal template, so output is diffable across runs.
</output_template>

<rules>
  Bullet list, bold lead phrase per rule, one sentence each. Hard constraints only — behavior already
  covered by CONSTITUTION.md or AGENT-CONDUCT-BASELINE.md doesn't need restating here, just what's
  specific to this agent's own job.
</rules>

<memory>   -- only if `memory: user` is set in frontmatter
  What belongs in cross-session memory vs. what must stay project-local. See AGENT-CONDUCT-BASELINE.md.
</memory>

<output>
  The exact deliverable and what gets returned to the caller. For a gate/reviewer agent, this is where
  the fenced verdict-block contract (AGENT-CONDUCT-BASELINE B7) gets specified.
</output>
```

## 3. Section skeleton — commands

```
<objective>   -- one paragraph: what this command produces, and which agent (if any) it delegates to
</objective>

<process>
  Resolve arguments ($ARGUMENTS / explicit path), then either the command's own steps, or an Agent(...)
  invocation of the agent it dispatches to. (The dispatch tool is named `Agent`; earlier revisions of
  this file said `Task(...)`, which was stale — grant `Agent` in `allowed-tools`, not `Task`.) Keep this thin — a command that routes to an agent should
  not re-describe that agent's own logic (see README.md's generic/project-specific decision rule: the
  specificity lives in the agent, not the dispatcher).
</process>
```

A `<namespace>:help` command (once a namespace exists — see `README.md`) is the one exception: it has no
`<process>`, just a `<reference>` block of static text and an explicit instruction not to add live
analysis. See `commands/sa/help.md` in the reference framework.

### Follow-up questions to an already-dispatched agent — `SendMessage`

A dispatch is **not** necessarily single-shot. An `Agent(...)` call returns an agent id, and
`SendMessage(to: <id>)` resumes that same agent **with its context intact** — the documents it read, the
code it walked, the reasoning it did. Verified live 2026-08-12 during the `doc-briefer` review, when the
`agent-reviewer` dispatch returned a resumable id.

Use it when the agent's value is in what it *holds*, not just what it returned — a document-comprehension
agent answering follow-ups from the source, a reviewer asked to expand on one finding. Re-dispatching
instead makes it re-read everything from scratch, at full token cost, with no memory of the first pass.

Two rules:
- **A command that promises follow-up Q&A must say `SendMessage`, not "ask it again."** The distinction is
  load-bearing and invisible to the user otherwise.
- **Always document the fallback.** Agent sessions don't live forever. Name what to do when the id is
  gone — usually re-reading the artifact the agent already wrote, plus targeted `Grep`, rather than a full
  re-dispatch.

First implemented in `agents/doc-briefer.md` + `skills/doc-brief/SKILL.md`.

## 4. Tone

- Imperative, not descriptive: "Read the diff" not "The agent should read the diff."
- Concrete over abstract: a named file path, a named tool call, a literal template — not "appropriate
  documentation" or "relevant checks."
- One responsibility per agent. If a task is structurally a different job, the agent says so and stops
  (`AGENT-CONDUCT-BASELINE.md` A9) rather than stretching to cover it.
- No filler sentences that restate the obvious from the section tag itself.

## 5. Naming

Not duplicated here — see `d:\WORK\AI\results\claude-prompting-system-review.md §13` for the full
generic-vs-project naming table (kebab-case, prefix rules, doctrine-file ALL-CAPS convention). Keeping it
in one place so this file and that one don't drift apart.
