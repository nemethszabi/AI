---
name: diagram
description: Create Mermaid diagrams (architecture/sequence/flowchart/class/state/deployment/ER) via the mermaid-diagram-maker agent
argument-hint: [what to diagram, optional — defaults to whatever architecture/design is already in the conversation]
allowed-tools:
  - Agent
  - AskUserQuestion
---

> Version: 1.1.0

<objective>
Create one or more Mermaid diagrams by delegating to the `mermaid-diagram-maker` agent — the generic,
project-agnostic diagram specialist that writes `.mmd` files and renders them to `.png`.
</objective>

<process>
Resolve what to diagram: `$ARGUMENTS` if given, otherwise whatever architecture/design has already been
discussed or defined in the current conversation.

```
Agent(subagent_type="mermaid-diagram-maker", description="Create diagram(s)", prompt="
Create diagram(s) for: <resolved input>.
Follow your standard process (assess, plan, create, render, verify, report).
Return your report.")
```

Relay the agent's report back to the user as-is — file paths and what each diagram covers, not a
paraphrase.

If the report ends with a `## Blocking questions` section, put those to the user via `AskUserQuestion`.
The agent cannot ask — `AskUserQuestion` does not exist inside a dispatched agent — so it marks uncertain
elements in the diagram and hands the questions here instead. Re-run this command with the answers to get
a diagram without the `?` markers.
</process>
