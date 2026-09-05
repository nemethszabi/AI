---
name: review-agent
description: Independently review a newly drafted or edited agent, skill, command, or one-time prompt file for structural and doctrine compliance, before it's trusted or copied to global. Use after agent-builder or prompt-builder produces a new file, after editing an existing agent/skill/command, or whenever asked to "review this agent", "check this skill before I copy it", "audit this prompt file". Scoped to ONE artifact — for a health-and-strategy pass over the whole framework (sync, doctrine coherence, industry currency, new opportunities), that's framework-review instead.
---

> Version: 1.0.1

# Review Agent

Thin dispatcher to the `agent-reviewer` agent — the independent, read-only reviewer for Claude Code
customization artifacts (as opposed to application code, which `dev-reviewer` covers). Isolation is the
entire point: this must not share the drafting session's own reasoning, so it always dispatches to a
fresh agent context rather than reviewing inline.

## Process

Resolve the target: the file or folder path given in the request, or ask if not provided (for a Skill,
the target is its folder — e.g. `skills\prompt-builder\`, not just `SKILL.md` alone).

Dispatch:

```
Task(subagent_type="agent-reviewer", description="Review drafted artifact", prompt="
Review the artifact at: {resolved target path}.
Follow your own mode-detection and review-dimensions process.
Return your report.")
```

Relay the agent's report back verbatim — do not summarize away the checklist detail or soften a
BLOCKING/REJECTED verdict into something that reads as optional.
