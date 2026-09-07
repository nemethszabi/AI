---
name: scaffold-context
description: Scan a solution folder and draft or update its ai/context/ file via the solution-analyst agent
argument-hint: [path to solution folder, optional — defaults to current directory]
allowed-tools:
  - Agent
  - AskUserQuestion
---

> Version: 1.1.0

<objective>
Bootstrap or refresh a project's `ai/context/` file by delegating to the `solution-analyst` agent — the
generic, project-agnostic scanner that reads an unfamiliar solution and drafts a first-pass context
document for human review.
</objective>

<process>
Resolve the target folder: `$ARGUMENTS` if given, otherwise the current working directory.

```
Agent(subagent_type="solution-analyst", description="Scaffold project context", prompt="
Analyze the solution at: <resolved target folder>.
Detect CREATE vs UPDATE mode per your own mode-detection step and follow your standard process.
Return your report.")
```

Relay the agent's report back to the user as-is — do not summarize away the CREATE/UPDATE distinction or
the confidence caveats it raises.

If the report ends with a `## Blocking questions` section, put those to the user via `AskUserQuestion`
before doing anything else. The agent cannot ask — `AskUserQuestion` does not exist inside a dispatched
agent — so this command is the only place the question can reach a human. In UPDATE mode the agent returns
candidates and writes nothing when it can't tell which context file to update; asking here is what unblocks
it, and the answer is acted on by re-running this command against the chosen root.
</process>
