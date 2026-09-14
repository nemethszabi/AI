---
name: doc-sync
description: Document, roll out and back up a framework or prompting change — four separately approved gates (docs → rollout → commit → backup). Use when the doc-sync hook suggests it, or after any agent/skill/command/doctrine change.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
argument-hint: "[what changed, optional] [--docs-only]"
---

> Version: 1.0.0

<objective>
`/doc-sync` closes the loop that a framework change otherwise leaves open: the change is made, but the
knowledge base still describes the old state, the live config roots still run the old files, and the
backup predates both. It works through four gates in order — **document → roll out → commit → back up** —
and does nothing at any gate without an explicit approval. `--docs-only` stops after the first.

It documents **facts about what changed** (a new command, a renamed folder, a new rule's location, a count);
it never invents doctrine, re-argues a design decision, or rewrites a document's structure. Machine paths
come from `framework-data/scope.yaml`, so this file stays generic.
</objective>

<process>
<step name="load-scope">
Read `framework-data/scope.yaml`: `$CLAUDE_CONFIG_DIR/framework-data/scope.yaml`, else
`~/.claude/framework-data/scope.yaml`. Needed: `staging_repo`, `live_config_roots`, `knowledge_base` +
`knowledge_base_files`, `sync_check_command`, `exclude`, and the optional `doc_sync` block
(`staging_docs`, `project_roots`, `backup_command`).

Missing file → stop and say so. Missing `doc_sync` block → propose one filled from what is already known
(the staging repo's `README.md`/`docs\USAGE.md`/`docs\SETUP.md`, project roots seen in this session, a
backup script if one is named in the knowledge base) and write it only after approval. Never read, cite
or edit anything under an `exclude` path.
</step>

<step name="collect-changes">
Build the change list from, in order:
1. **This conversation** — what was actually created, edited, moved or renamed, and why.
2. The doc-sync hook's session lists — the newest files in `~/.ai-usage/docsync/`.
3. `git -C <staging_repo> status --porcelain` and `git -C <staging_repo> diff --stat` (forward slashes).
4. For each `project_roots` entry touched this session: `git status --porcelain -- .claude ai/prompts
   CLAUDE.md ai/README.md ai/context`.

Classify each change: **global** (staged in the staging repo), **project** (a repo's own `.claude\`/`ai\`),
or **personal** (the knowledge-base folder's own `.claude\`). Drop pure content edits that change nothing
a document states (a typo fix, an appended bug pattern). If nothing remains, say so and stop.
</step>

<step name="map-docs">
For every change, find the documents that state something it made untrue or incomplete:
- **Knowledge base** (`knowledge_base_files`): the inventory (every artifact listed), the overview (layers,
  per-project rows, "last updated" line), the environment file (MCP/profile facts), and any other KB file
  that `Grep` finds naming the changed artifact.
- **Staging docs** (`doc_sync.staging_docs`), and the staging repo's own `claude\README.md` /
  `copilot\README.md` when the change is branch-specific.
- **Project docs**: the project's `ai/README.md`, its `CLAUDE.md`, and its namespace `help` command.

Use `Grep` on the changed artifact's name, old path and old name to find every stale mention; read only the
matching sections. Also check the claim a change most often falsifies: counts ("22 agents"), folder
layouts, and "where does X live" answers.
</step>

<step name="gate-1-document">
Present one changelist, then ask via `AskUserQuestion` — **Apply all** / **Let me pick** / **Skip**:

```
DOC-SYNC — proposed documentation updates
| # | File | Section | Change | Because |
|---|------|---------|--------|---------|
| 1 | …    | …       | …      | <which change made it stale> |
```

Apply the approved rows with `Edit` — minimal, in each document's existing style; update its "Last updated"
line where it has one, naming the change in one clause. Report per file: updated / skipped.
</step>

<step name="gate-2-rollout" condition="global changes exist and --docs-only was not given">
Run `sync_check_command`. From its output and the change list, show exactly which staged files would be
copied to which live roots — **only the changed files**, never a blanket copy — using the destinations and
exclusions in `<staging_repo>\claude\README.md` (Rollout) and, for shared or Copilot files,
`<staging_repo>\copilot\README.md` (Rollout). Read those sections; do not work from memory.

Ask **Roll out** / **Skip**. On approval, copy file by file (`powershell -Command Copy-Item -Force …`,
destination folders created first), then run `sync_check_command` again and report what is in sync and
what is not.

Hook or `settings.json` changes are **never** applied by this step: show the exact JSON to add per root and
ask separately.
</step>

<step name="gate-3-commit" condition="the staging repo has uncommitted changes">
Propose a commit for the **staging repo only**: the file list and a message (subject ≤ 72 characters,
body = the change list in a few lines, plus the attribution lines this session's instructions require).
Ask **Commit** / **Skip**. Never push. Project repositories are never committed by this command — their
owners commit.
</step>

<step name="gate-4-backup" condition="doc_sync.backup_command is set">
Ask **Run backup** / **Skip**. On approval run `backup_command` and report its summary lines (what was
copied where, errors). A failed backup is reported as failed, never as done.
</step>

<step name="report">
```
DOC-SYNC
Changes documented: <n> files — <list>
Rollout:            <done — in sync | skipped | not needed> <any drift left>
Commit:             <sha | skipped | not needed>
Backup:             <done | failed — reason | skipped>
Still open:         <anything declined or not in sync>
```
</step>
</process>

<rules>
- **Four gates, four separate approvals.** An approval covers only its own gate, only this run.
- **Facts only.** Document what changed; never add doctrine, never restructure a document.
- **Only changed files roll out.** No blanket copies; hook/settings changes are shown, never applied.
- **Never push. Never commit a project repository.**
- **Never touch an `exclude` path.**
- **Report truthfully** — a copy or backup that failed or was skipped is said so.
</rules>
