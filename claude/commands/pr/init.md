---
name: pr:init
description: Scaffold ai/pr/ (config.json, review-guidelines.md, fix-guidelines.md, mcp.example.json) for a project so /pr:review and /pr:fix can run against it - detects the provider from the git remote and verifies the MCP connection read-only.
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - AskUserQuestion
  - Bash(git -C * remote *)
  - Bash(git -C * rev-parse *)
  - Bash(git -C * check-ignore *)
  - PowerShell(git -C * remote *)
  - PowerShell(git -C * rev-parse *)
  - PowerShell(git -C * check-ignore *)
argument-hint: "[project path, optional - defaults to current directory]"
---

> Version: 1.0.0 — 2026-09-18. Initial (revised after agent-review round 2).

<objective>
`/pr:init` writes the project files `~/.claude/dev-framework/PR-WORKFLOW.md` §2 describes, so the
generic `pr-reviewer` / `pr-fixer` agents have a provider connection and project-specific guidance to
read. It creates; it never overwrites.
</objective>

<process>
<step name="resolve-target">
`<project>` = the argument if given, else the current directory. `git -C <project> rev-parse
--show-toplevel`; not a repository → say so and stop. Use the top level as `<project>` from here on.
</step>

<step name="check-existing">
Glob `<project>/ai/pr/`. If `config.json` exists, report what is there and stop — editing an existing setup
is a manual, reviewed change, not a re-scaffold. Otherwise note, **per file**, which of `config.json`,
`review-guidelines.md`, `fix-guidelines.md`, `mcp.example.json` already exist; those are left untouched in
`write-files`.
</step>

<step name="detect-provider">
`git -C <project> remote get-url origin`. **First strip any `user[:secret]@` from the URL** — before
parsing it, printing it or writing it anywhere; an embedded PAT in a remote URL is reported as "the remote
URL carries credentials — remove them from the remote" (Article I.3) without the value.
`dev.azure.com/<org>/<project>/_git/<repo>` or `<org>.visualstudio.com/<project>/_git/<repo>` →
`azure-devops` with organization, project (URL-decoded) and repository filled in. Anything else → say this
version's commands implement Azure DevOps provider calls only; still write the files with `provider` set to
what was detected, so the project-side data is ready.
</step>

<step name="pick-mcp-server">
From the tools available in this session, list the MCP servers whose tools include a pull-request read
call. **Never read `~/.claude.json`, any `.mcp.json` or any other MCP config file** — they hold tokens.
For each candidate, learn its organization from a read call (its "list organizations" or "who am I"
tool), not from its config. One candidate whose organization matches → use it. Several or none → ask via
`AskUserQuestion`. With none, write `"mcp_server": "<TODO>"` and print the per-user setup — the token
lives in a user environment variable, never in shell history, on a command line or in a file:
1. Set the variable without echoing the token (PowerShell):
   `$t = Read-Host 'PAT' -MaskInput; [Environment]::SetEnvironmentVariable('<TOKEN_VAR>', $t, 'User'); Remove-Variable t`
   — then open a new terminal.
2. `claude mcp add-json --scope user <server-name> '<the mcpServers.<server-name> object from
   ai/pr/mcp.example.json, as one line>'` — **single quotes**, so neither Bash nor PowerShell expands
   `${<TOKEN_VAR>}`; the stored entry must keep the literal `${…}`.
3. `/mcp` shows the server connected.
Never ask for, read, or write the token itself.
</step>

<step name="verify-read-only">
If a server was chosen: call its "who am I" and "get repository" tools. Report the authenticated user and
whether the repository resolves. Never post a test comment from here — write rights are proven by the
first approved post in `/pr:review`.
</step>

<step name="write-files">
Only files noted as absent in `check-existing`; `Write` creates `ai/pr/`.
- `config.json` per `PR-WORKFLOW.md` §3, every key present: `default_target_branch` from the provider's
  repository default branch (else `git -C <project> rev-parse --abbrev-ref origin/HEAD`, else `""`);
  `context_files` = every `ai/context/*.md` that exists; `related_repositories: []`; `review` with the §3
  defaults (`max_inline_comments: 15`, `post_summary_comment: true`, `build_in_review: false`);
  `fix.build_command` / `test_command` from the project's `CLAUDE.md` or context file if documented, else
  empty strings and a note in the summary.
- `review-guidelines.md` and `fix-guidelines.md` as **skeletons with headings and one-line prompts only**
  (comment language and voice; severity tag format; project hot-spots → pointer to the context file;
  what not to comment on · build/test commands; commit message format; reply format; who sets which
  thread status). Do not invent project rules to fill them — an empty heading is honest, a plausible
  guess is not (`AGENT-CONDUCT-BASELINE.md` D3).
- `mcp.example.json` — the chosen or placeholder server name, its public shape and the setup steps from
  `pick-mcp-server`, with the token only as `${<TOKEN_VAR>}`. No credential, by construction.
- No `ai/context/` at all → recommend `/scaffold-context` first; the reviewer works without it, but only
  against general soundness.
</step>

<step name="gitignore-advice">
Check with `git -C <project> check-ignore ai/pr/results/x ai/bug/results/x` whether the results folders
are ignored. Say: `config.json`, both guidelines and `mcp.example.json` are safe and useful to commit (no
credentials by construction); `ai/pr/results/` holds review prose about colleagues' code and
`ai/bug/results/` customer data — advise these two lines for the project's `.gitignore` unless already
ignored:
```
ai/pr/results/
ai/bug/results/
```
Change no `.gitignore` here — the human adds them.
</step>

<step name="relay">
Report: the project root, the provider and org/project/repository detected (URL with credentials
stripped), the MCP server chosen or `<TODO>` with the setup lines, the read-only check result, each file
as **written** or **already existed — left untouched**, the empty build/test commands if any, the
`.gitignore` advice, and the next step: fill the two guidelines, then `/pr:review <id> --no-post`.
</step>
</process>

<rules>
- **Create-only, per file.** Never overwrite an existing `ai/pr/` file.
- **No credentials, ever** — not read, not written, not echoed; the remote URL is stripped before use and
  no MCP config file is opened.
- **No invented project rules.** Skeleton headings only.
- **Never edit a `.gitignore`.** Advise the lines; the human adds them.
</rules>
