# Copilot port notes — standing divergences for the `req-*` / `sa:` family

Read once. Every ported `req-*` agent and every `sa:` command in this branch is subject to everything here,
and none of them restate it — a divergence documented in fourteen places is a divergence that will be
corrected inconsistently in fourteen places.

An agent or command marks **[Copilot]** inline only for a divergence **specific to itself**. The five below
are universal.

**Ported 2026-09-07**, when the standing "doctrine-only" scope decision was lifted and the whole `sa:`
pipeline was brought across. Conformance target: `..\sa-framework\PIPELINE.md §5`.

---

## D1. Config root is `~/.copilot/`, not `~/.claude/`

Every doctrine path in a ported file reads `~/.copilot/`. The four shared documents
(`CONSTITUTION.md`, `AGENT-CONDUCT-BASELINE.md`, `DESIGN-PRINCIPLES-BASELINE.md`,
`sa-framework/`) are byte-identical to the Claude side — same files, copied to a second root, not forks.

Engagement artifacts are **not** tool-scoped: `ai/sa/<slug>/` lives in the project, exactly where the Claude
side writes it. An engagement started in Claude Code can be continued in Copilot CLI and vice versa, because
the artifacts conform to one shared schema. That is the main practical payoff of the port and the reason
`ARTIFACT-SCHEMAS.md` was written tool-agnostic in the first place.

## D2. No `disallowedTools` — read-only is instruction-enforced, and that is weaker

Claude Code lets a read-only agent declare `disallowedTools: Edit, NotebookEdit, Bash`, making the promise
structural (`claude\AGENT-TEMPLATE-BASELINE.md` §1a, `CONSTITUTION.md` Article VI.1). **Copilot CLI's
`.agent.md` frontmatter has no equivalent field.**

The mitigation, applied to every read-only role here (`req-reviewer`, `req-estimate-critic`, `req-auditor`,
`req-slop-detector`, `req-screener`):

- Grant `tools: [write]` only — no `shell` — so the agent structurally cannot run a mutating command. This
  is the one half of the restriction that *is* enforceable, and it is used.
- State the read-only rule explicitly in the agent's own Rules section, naming what it may write (its own
  report, and nothing else).

**Stated plainly rather than papered over**: `write` is not scoped to specific paths on either tool, so
"writes only its own report" remains an instruction on both sides. What Copilot additionally lacks is the
deny-list backstop. This is a real, if narrow, reduction in enforcement and is recorded as such.

`req-auditor` is the sharpest case: its Claude sibling holds `Bash(git hash-object:*), Bash(sha256sum:*)` —
a *scoped* shell grant. Copilot's `shell` grant is all-or-nothing, so this port takes `shell` and carries
the narrowing as a written rule. See that file's own [Copilot] note.

## D3. Dispatch is `@agent-name`, not the `Agent` tool

A `sa:` command here instructs the session to dispatch via `@<agent-name>`; `/agent <name>` selects one
interactively and `/fleet` runs several in parallel. The dispatching session is the main session, so it can
put questions to the human — the half of `AGENT-CONDUCT-BASELINE.md` A7 that matters is unchanged.

**Nested dispatch**: as on the Claude side, no `req-*` agent dispatches another. Orchestration belongs to
the command (`CONSTITUTION.md` Article VI.2).

## D4. No `AskUserQuestion` — same problem, same pattern, different reason

Neither tool gives a dispatched agent a structured way to ask the human. On Claude the tool exists but is
unavailable inside a subagent; on Copilot there is no such tool at all. **The resulting contract is
identical**, so the ported agents need no change:

1. The agent proceeds on the least-committal reading and states the assumption in the artifact.
2. It records the question where the schema provides for it (`to_clarify`, `open_questions`, a `D-NNN`).
3. It repeats genuinely blocking ones under `## Blocking questions` in its returned summary.
4. The command raises them with the human in plain prose.

Step 4 is the [Copilot] difference and it is cosmetic: a plain question instead of a structured prompt.
The obligation (`PIPELINE.md §2.6`) is unchanged, and so is the failure it prevents.

## D5. Model selection is session-level, not per-dispatch — and this one bites

`ARTIFACT-SCHEMAS.md §9` requires the four checking steps to run on a **different model than produced the
work**, selected per invocation. Claude Code passes `model` on the dispatch itself. **Copilot CLI has no
per-dispatch model parameter** — `/model` sets the model for the whole session (`/config model` for the user
default, `--model` at launch).

So on this side the rule is satisfied by a **session switch before dispatching**, and every checking command
here says so explicitly rather than accepting a same-model review by default:

```
/model <a model other than the one that wrote these artifacts>
@req-slop-detector  <slug>
```

Two consequences worth knowing:

- **The switch affects everything else in that session too.** Run a checking step in its own session, or
  switch back after. A command here reminds you.
- **The default is already favourable, but do not rely on it.** This machine's Copilot runs
  `claude-sonnet-5` while the Claude Code side runs Opus, so artifacts authored in Claude Code and checked
  in Copilot CLI are cross-model *by accident of configuration*. That is a fact about today's setup, not a
  guarantee — `/model` is one keystroke away from erasing it. Every checking command still reports which
  model actually ran (`PIPELINE.md §4`).

## D6. The packaging gate cannot refuse — and this port says so

The one capability that genuinely does not survive. `/sa:package` on the Claude side **refuses** to build
without two fresh passing verdicts. Copilot CLI has no mechanism by which a command can hard-stop a session
that has been told to continue.

`copilot\commands\sa\package.md` therefore:

- computes and checks both verdicts exactly as the Claude side does,
- prints a prominent **STOP** block naming every failure, and
- **describes itself as an advisory check, never as a gate.**

Per `PIPELINE.md §3`'s last subsection: a gate that looks like a gate and isn't is worse than an
acknowledged manual check, because it produces the confidence of enforcement with none of the substance.
**If the deliverable is commercially binding, run the packaging step in Claude Code**, where the refusal is
real. That sentence is in the command itself, not only here.
