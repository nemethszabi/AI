---
name: scaffold-context
description: Scan a solution folder and draft or update its ai/context/ file via the solution-analyst agent
argument-hint: [path to solution folder, optional — defaults to current directory]
allowed-tools:
  - Task
---

<objective>
Bootstrap or refresh a project's `ai/context/` file by delegating to the `solution-analyst` agent — the
generic, project-agnostic scanner that reads an unfamiliar solution and drafts a first-pass context
document for human review.
</objective>

<process>
Resolve the target folder: `$ARGUMENTS` if given, otherwise the current working directory.

```
Task(subagent_type="solution-analyst", description="Scaffold project context", prompt="
Analyze the solution at: <resolved target folder>.
Detect CREATE vs UPDATE mode per your own mode-detection step and follow your standard process.
Return your report.")
```

Relay the agent's report back to the user as-is — do not summarize away the CREATE/UPDATE distinction or
the confidence caveats it raises.
</process>
