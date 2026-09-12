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
| `tools:` | comma list, agents only | — | Minimum the role needs — see `AGENT-CONDUCT-BASELINE.md` A6. **Never grant `AskUserQuestion` to an agent** — see the note below the table |
| `allowed-tools:` | — | YAML list, commands only | Different key name from `tools:` — confirmed distinct, not a typo |
| `argument-hint` | — | optional, commands only | e.g. `[path, optional]` |
| `color` | optional | — | Cosmetic only; doesn't gate behavior |
| `model` | optional | — | **Pin by tier, and never pin a reviewer** (rule revised 2026-09-12, replacing the older blanket "don't pin a model by default"). Mechanical → Sonnet; Worker/author with a gate behind it → Sonnet; Judgment (design, estimation, planning) → leave inheriting. **Gates and reviewers must never carry a `model:` pin at all** — independence requires the *caller* to pick a different model than wrote the work (`AGENT-CONDUCT-BASELINE.md` B10), and a pin can silently make reviewer and author the same model. That is a correctness bug, not a cost decision. Per-agent table and measured $/run: `d:\WORK\AI\knowledge-base\token-economy.md` §6 |
| `memory` | optional | — | `user` (`~/.claude/agent-memory/<name>/`), `project` (`.claude/agent-memory/<name>/`) or `local` (`.claude/agent-memory-local/<name>/`). Only when cross-session learning has real value — see `AGENT-CONDUCT-BASELINE.md`'s Memory conduct section first. Prefer `project`/`local` for anything project-bound; `user` leaks one project's facts into every other session |
| `disallowedTools` | optional | — | Deny-list applied *after* `tools:`/inheritance. This is how a read-only agent's promise becomes structural instead of a sentence in `<rules>` |
| `permissionMode` | optional | — | `default` \| `acceptEdits` \| `auto` \| `dontAsk` \| `bypassPermissions` \| `plan` \| `manual`. **Never `bypassPermissions` on an agent that writes** — that deletes Article II's confirmation requirement wholesale |
| `maxTurns` | optional | — | Positive integer. Cheap circuit-breaker for survey/scanning agents that could otherwise loop |
| `skills` | optional | — | Skills preloaded into the agent's context at startup. This is the mechanism `AGENT-CONDUCT-BASELINE.md:12-17` calls the "natural next step" — conduct doctrine can now actually be *read at runtime*, not just consulted while drafting |
| `mcpServers` | optional | — | Server names or inline definitions, scoped to this agent. Prefer this over hardcoding a wall of `mcp__<server>__*` tool names in `tools:` |
| `hooks` | optional | — | Lifecycle hooks scoped to this one agent — the per-agent form of the guard hook in §1a |
| `background` | optional | — | `true`/`false`. Fits long read-only reviews whose output the caller doesn't need inline |
| `effort` | optional | — | `low` \| `medium` \| `high` \| `xhigh` \| `max`. Set low on mechanical scanners — this moves cost and quality more than `model` does, and it is the only tier dial a gate or reviewer may carry. **Unset already means `high`**, and effort has **no per-dispatch override** (the dispatch tool takes `model`, not `effort` — verified 2026-09-12), so writing `high` explicitly buys nothing while permanently removing your only lever. Set a value only when you want something *other* than the default. Not supported on Haiku 4.5 |
| `isolation` | optional | — | `worktree` — runs the agent in its own git worktree. For editing agents whose diff you want quarantined |
| `initialPrompt` | optional | — | Auto-submitted as the first user turn when the agent runs as a *main session*. Irrelevant for dispatch-only agents |
| `experimental` | optional | — | Map with `cacheTtl`: `5m` or `1h`. Worth setting only on an agent re-invoked repeatedly in one session via `SendMessage` |

Field list verified against <https://code.claude.com/docs/en/sub-agents>, 2026-09-05. Before adding a field
here, check it there — this table was 11 fields stale for long enough that every agent in the roster was
drafted without them.

> **`AskUserQuestion` does not exist inside a dispatched agent.** Only the main session can call it.
> Granting it in an agent's `tools:` line produces `Error: No such tool available` at the exact moment the
> agent tried to stop and ask — which is the worst possible moment for an undefined behavior. Found the
> hard way on 2026-09-05: **nine** agents declared it, every one of them dispatch-only.
>
> The pattern that works, and the one to draft into any new agent that has something to ask:
> 1. The agent proceeds under the **safest / least irreversible** reading rather than stalling, and states
>    that assumption in the artifact it writes.
> 2. It records the question durably where the artifact schema already provides for it (`to_clarify`,
>    `open_questions`, a `D-NNN` ID).
> 3. It repeats the genuinely blocking ones in its returned summary under a `## Blocking questions`
>    heading (`## Decisions needed` for a review/strategy agent).
> 4. **The dispatching command or skill** — which does run in the main session — puts those to the human
>    with `AskUserQuestion`. Every dispatcher of such an agent must carry that step and grant the tool,
>    or the question dies in the transcript.
>
> A command or skill may grant `AskUserQuestion` freely. An agent may not.

## 1a. Structural enforcement — prefer a field over a sentence

`CONSTITUTION.md` Article VI.1 already sets the standard: a restriction is "enforced by the tool list
itself, not by instruction alone." The fields above extend that standard to rules previously left to model
compliance. Anthropic's own guidance is the same — an instruction like "never edit `.env`" in a doctrine
file "is a request, not a guarantee. A `PreToolUse` hook that blocks the edit is enforcement."

When drafting, ask which of the agent's `<rules>` are actually *promises* and move each to its mechanism:

| The rule says | Enforce it with |
|---|---|
| "read-only — never edits anything" | `tools:` minimum **plus** `disallowedTools: Write, Edit, NotebookEdit` |
| "never runs git state-changing commands" | `disallowedTools: Bash`, or a `PreToolUse` hook if `Bash` is genuinely needed |
| "never promotes/installs anything to a live root" | `disallowedTools` on the writing tool, since a path rule can't be expressed in `tools:` |
| "always confirms before a destructive action" (Article II) | a `PreToolUse` hook at the root — see `_scripts\hooks\` |
| "no agent spawns another agent" (Article VI.2) | `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "1"` in `settings.json` `env` — the platform default is **3** |

An agent whose `<rules>` block concedes its own rules are "instruction-enforced, not tool-enforced" is
telling you a field is missing. Write the field, then leave the sentence in as documentation of intent.

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
