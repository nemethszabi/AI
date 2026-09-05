---
name: framework-review
description: Review the whole agentic AI framework itself — audit it against its own doctrine, check staged-versus-live sync across every config root, research what has changed in industry practice, reconcile the tracked gap register, propose new agentic use cases for professional and personal work, and produce a dated report with a ranked, human-gated changelist. Use for a periodic health-and-strategy pass on the framework, or when asked to "review my AI setup", "what should I improve in my agent framework", "is my Claude setup still current", "what else could I automate with agents". Not for reviewing one drafted agent or skill — that is review-agent.
---

> Version: 1.0.0

# Framework Review

Dispatches the `framework-strategist` agent to review the agentic framework as a system and propose where
it should go next. The agent reads the doctrine, the whole artifact roster, every live config root and the
knowledge base in its own context window, then researches current practice on the web. That is a large
read, which is exactly why it runs in a subagent rather than inline: the calling session keeps its context
for acting on the findings.

Run it periodically, not continuously. Monthly is a reasonable starting cadence; the agent recommends its
own next interval at the end of each report.

## What it is not

`review-agent` checks one newly drafted artifact for structural and doctrine compliance and returns a
verdict on it. This skill never does that. It checks whether the whole set is coherent, honestly
documented, actually rolled out, current against the platform, and pointed at the work you really do.

When the review finds a single artifact that needs a structural check, it says so and you run
`review-agent` on that artifact. When it proposes something new, you build it with `agent-builder`. This
skill deliberately builds nothing itself.

## Usage

```
/framework-review                      full review, the default
/framework-review drift                staged-versus-live sync only
/framework-review doctrine             doctrine and roster coherence only
/framework-review research             industry delta only
/framework-review ideas                opportunity brainstorm only
/framework-review parity               second-tool migration status only
```

## Before the first run

The agent takes every path it touches from a scope file, so no machine's paths live inside the agent.
Copy the template into **your tool's own live config root** and fill it in once. This skill lives in the
shared cross-tool layer, so the root differs by tool: Claude Code uses `CLAUDE_CONFIG_DIR` when set and
otherwise the default `.claude` root, while Copilot CLI uses its own `.copilot` root. The block below is
the Claude-side form.

```powershell
$root = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { "$env:USERPROFILE\.claude" }
New-Item -ItemType Directory -Force "$root\framework-data" | Out-Null
Copy-Item "{repo}\framework-data\scope.yaml.example" "$root\framework-data\scope.yaml"
```

Writing it to the wrong tool's root fails silently rather than loudly: the agent simply reports it could
not resolve the scope and runs reduced.

Then edit it. The entries that matter most:

| Entry | Why it matters |
|---|---|
| `live_config_roots` | List every root a session might run under. Checking only one is how a rollout gap goes unnoticed for weeks. |
| `knowledge_base_files` | The only files the agent may edit directly, and only to correct facts it verified this run. |
| `exclude` | Hard, absolute. The agent never reads, cites, or reasons about anything under these, and never proposes removing one. |
| `report_dir` | Where the dated report lands. |

Without the file the agent still runs. It bootstraps what it can from the environment and the global
instruction file, reports which roots it could not resolve, and — on an attended run only — offers to
write the scope file from your answers. An unattended run never stops to ask; it reports and continues
reduced.

## How to run it

1. Resolve the mode from the argument, defaulting to a full review.
2. Dispatch `framework-strategist` with the mode and whether the run is attended. Say explicitly when the
   run is unattended or backgrounded, so the agent writes proposals instead of stopping to ask.
3. Relay the summary. The agent's full report is not shown to the user, so surface the numbers that
   change what they do: findings by severity, what was applied and to which files, the top proposed
   changes, the top opportunities, and the report path.
4. If drift was found, show the rollout command. Do not run it. Promotion to a live config root is a
   deliberate human step by design, and the agent is forbidden from performing it.

## What the agent may and may not change

This split is the safety model of the whole skill, so keep it visible when relaying results.

| Bucket | What happens |
|---|---|
| Applied | Verified factual corrections to the living knowledge-base files only. A wrong count, a stale path, a candidate that is now adopted, a tracked gap now resolved. |
| Proposed | A concrete before and after for a doctrine file, agent, skill, command or setting. Written into the report, never applied by the agent, even if you approve it mid-run. Approval routes it back to the calling session, which makes the edit in the open. |
| Build | New artifacts. Routed to `agent-builder`, never drafted by this agent — **and built into the layer the agent names**. A personal-work artifact never goes into the shared dev/work repo, no matter how reusable its shape looks, and the fact that a dev/work builder tool drafts it does not make its output dev/work (Constitution Article IX). |

## Follow-up questions

The report is the start of the conversation, not the end. Once the agent has read the framework, send
further questions to that same agent with `SendMessage` — it still holds every file it read and answers
with citations. A new dispatch would re-read the whole framework and re-fetch every source for nothing.

Good follow-ups: expand one finding, draft the exact before and after for a proposed change, argue against
an opportunity you think is wrong, or ask which single change would pay off most this month.

If the agent's session is gone, the fallback is the report itself plus targeted `Grep` against the roots
it names, rather than a full re-dispatch.

## Reading the report

Reports accumulate in the configured directory as `framework-review-YYYYMMDD.md`, one per run. They are
meant to be compared: the gap-register reconciliation and the closing summary block exist so a later run
can see what actually moved since the last one. Do not hand-edit an old report to reflect later changes —
write the change into the framework and let the next run observe it.

The closing summary block is scannable, not a gate. Nothing consumes it and nothing blocks on it. This
skill produces advice, and every real change stays a human decision.
