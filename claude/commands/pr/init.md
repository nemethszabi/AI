---
name: pr:init
description: Scaffold ai/pr/ (config.json, review-guidelines.md, fix-guidelines.md) for a project so /pr:review and /pr:fix can run against it - detects the provider from the git remote and verifies the MCP connection read-only.
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - AskUserQuestion
  - Bash(git -C * remote *)
  - PowerShell(git -C * remote *)
argument-hint: "[project path, optional - defaults to current directory]"
---

> Version: 1.0.0 — 2026-09-18. Initial.

<objective>
`/pr:init` writes the three project files `~/.claude/dev-framework/PR-WORKFLOW.md` §2 describes, so the
generic `pr-reviewer` / `pr-fixer` agents have a provider connection and project-specific guidance to
read. It creates; it never overwrites.
</objective>

<process>
<step name="check-existing">
If `<project>/ai/pr/config.json` exists, report what is there and stop — editing an existing setup is a
manual, reviewed change, not a re-scaffold.
</step>

<step name="detect-provider">
`git -C <project> remote get-url origin`. `dev.azure.com/<org>/<project>/_git/<repo>` or
`<org>.visualstudio.com` → `azure-devops` with organization, project (URL-decoded) and repository filled
in. Anything else → say this version's commands implement Azure DevOps provider calls only; still write
the files with `provider` set to what was detected, so the project-side data is ready.
</step>

<step name="pick-mcp-server">
List the MCP servers available in this session whose tools include a pull-request read call. One
candidate whose configured organization matches → use it. Several or none → ask via `AskUserQuestion`;
with none, write `"mcp_server": "<TODO>"` and print the one-line `claude mcp add --scope user …` shape
the user needs, with a placeholder for the token — never ask for, read, or write the token itself.
</step>

<step name="verify-read-only">
If a server was chosen: call its "who am I" and "get repository" tools. Report the authenticated user and
whether the repository resolves. Never post a test comment from here — write rights are proven by the
first approved post in `/pr:review`.
</step>

<step name="write-files">
- `config.json` per `PR-WORKFLOW.md` §3. `context_files` = every `ai/context/*.md` that exists;
  `fix.build_command` / `test_command` from the project's `CLAUDE.md` or context file if documented, else
  empty strings and a note in the summary.
- `review-guidelines.md` and `fix-guidelines.md` as **skeletons with headings and one-line prompts only**
  (comment language and voice; severity tag format; project hot-spots → pointer to the context file;
  what not to comment on · build/test commands; commit message format; reply format; who sets which
  thread status). Do not invent project rules to fill them — an empty heading is honest, a plausible
  guess is not (`AGENT-CONDUCT-BASELINE.md` D3).
- No `ai/context/` at all → recommend `/scaffold-context` first; the reviewer works without it, but only
  against general soundness.
</step>

<step name="gitignore-advice">
Report whether `ai/` is ignored by the project's `.gitignore`, and say: `config.json` + both guidelines are
safe and useful to commit (no credentials by construction); `ai/pr/results/` holds review prose about
colleagues' code — suggest ignoring it unless the team wants the history. Change no `.gitignore` here.
</step>
</process>

<rules>
- **Create-only.** Never overwrite an existing `ai/pr/` file.
- **No credentials, ever** — not read, not written, not echoed.
- **No invented project rules.** Skeleton headings only.
</rules>
