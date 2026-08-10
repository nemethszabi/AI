---
name: prompt-builder
description: Draft a new one-time or occasional-use prompt with proper context-loading and structure, saved under a project's ai/prompts/{topic}/ folder for future reuse. Use when the user wants to save a prompt for reuse later, or asks to "make this a reusable prompt", "draft a one-time prompt for X", "save this as a prompt I can run again". Do NOT use for anything that will actually recur often, or that needs isolation/tool-restriction/autonomy/proactive-triggering — that's agent-builder's job (this skill checks for that and redirects rather than complying blindly).
---

# Prompt Builder

Draft a new, well-structured one-time/occasional-use prompt file — the lighter-weight artifact type
below Skills and Agents (see `d:\WORK\AI\knowledge-base\claude-prompting-kb.md` §1–2 for the full
decision tree). Stays inline in this conversation rather than delegating — drafting is iterative.

## Step 1 — Sanity check: is this genuinely one-time?

Before anything else, check whether the request actually describes a **recurring** need in disguise —
"I'll want to run this every time X happens" is a Skill, not a one-time prompt. If the description
suggests real recurrence, isolation needs, or tool-restriction needs, say so explicitly and point at
`agent-builder` instead of proceeding. Don't silently comply with "make this a one-time prompt" for
something that isn't one.

## Step 2 — Gather inputs

From the request, or by asking directly for whichever isn't already clear:

1. **Purpose** — one- or two-sentence description of what this prompt does. Don't start drafting from a
   vague request.
2. **Target location** — which project's `ai/prompts/{topic}/` this lands in. Default to the current
   working directory's project; ask if it should go somewhere else (e.g. running this from
   `d:\WORK\AI` while drafting something meant for a different repo).
3. **Topic slug** — short kebab-case name for the folder/file. Derive from the purpose if not given
   explicitly, but confirm before writing — naming matters (see the naming conventions table in
   `d:\WORK\AI\results\claude-prompting-system-review.md` §13).

## Step 3 — Discover context

Scan the target project's `ai/context/` folder, if it exists, and propose which file(s) this prompt
should instruct the reader to load first — don't make the user type paths from memory. Every existing
prompt in this style (`scm-dev-fix-core.md`, `run-sonar-fix.md`, etc.) opens with exactly this pattern:
"Read the project's context file, then...".

## Step 4 — Decide structure

Ask (or infer, confirming before drafting) each of these — don't default all of them to "no" just
because that's simpler:

- **Runtime parameters?** Does *invoking* this prompt later need fill-in-the-blank values (a repo name,
  a PR number, a date range)? If yes, draft a parameter block at the top using curly-brace placeholders,
  same shape as `run-sonar-fix.md`'s `REPO_ROOT`/`REPO_NAME`/`PROJECT_NAME`/`PR_ID`.
- **Approval gate?** Read-only/report-only task, or does it modify things with real blast radius? If the
  latter, it needs a phased Understand → Design → Plan → **approve** → Implement → Report structure —
  the single highest-leverage pattern in this whole framework
  (`d:\WORK\AI\results\claude-prompting-system-review.md` §5.3) — don't skip it by default for anything
  with write/mutate potential. Cross-check against `CONSTITUTION.md` Article II (destructive/irreversible
  actions) if the target project has one.
- **Output/report format?** Does this end in a saved, dated `ai/reports/` file (existing convention), or
  just an inline answer with nothing worth persisting?

## Step 5 — Draft

Write the file at `{target-location}\ai\prompts\{topic-slug}\{topic-slug}-core.md` (or a flat
`{topic-slug}.md` if the prompt is simple enough not to need a separate run-file). Plain Markdown headers
only — no XML/angle-bracket tags anywhere in this body, including for fill-in-the-blank placeholders: use
curly braces (`{like-this}`) instead, matching this framework's own existing prompt convention. That's a
hard constraint for this file type (same as any other Skill), not a style choice.

## Step 6 — Report

```
## Built: {topic-slug}

File: path written
Target project: repo name
Context files referenced: list, or "none"
Runtime parameters: list, or "none — no parameters needed"
Approval gate: yes, phased / no, read-only
Output: saved to ai/reports/... , or inline only
```
