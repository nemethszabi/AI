---
name: pr:help
description: Static reference for the pr: command namespace. No live analysis, no project context read.
allowed-tools: []
---

> Version: 1.0.0 — 2026-09-18. Initial.

<reference>
# `pr:` commands — generic pull-request review and fix

Global — works in any project that has `ai/pr/config.json`. Contract and rationale:
`~/.claude/dev-framework/PR-WORKFLOW.md`.

| Command | Purpose |
|---|---|
| `/pr:init [path]` | Scaffold `ai/pr/` — provider connection (`config.json`) + skeleton review/fix guidelines. Create-only. |
| `/pr:review <PR>` | Fetch PR + threads → PR-head checkout → `pr-reviewer` (cold) → report + proposed line comments → **you approve** → post. |
| `/pr:fix <PR>` | Fetch open threads → `pr-fixer` fixes on the source branch, builds, tests → **you approve** commit / push / replies, each separately. |
| `/pr:help` | This reference. |

`<PR>` is a number (`28548`), `#28548`, or the PR's URL. Run from inside the repo, or give the repo path
as the first argument.

## `/pr:review` options
| Option | Effect |
|---|---|
| `--req=<file.md>` / `--req="text"` | The requirement to review against. Without it: PR description + linked work items only — the report says that this confirms code-matches-description, not description-matches-need. |
| `--model=<name>` | Model for the reviewer. Use a different one than wrote the code. |
| `--no-post` | Produce files, never offer posting. |
| `--only-report` | Report only; no comment list. |

## `/pr:fix` options
| Option | Effect |
|---|---|
| `--threads=<id,id>` | Only these threads. |
| `--from-review` | Fix the newest local `/pr:review` comment list instead of provider threads (self-review loop; posts nothing). |
| `--include-resolved` | Also consider threads not in active/pending status. |
| `--model=<name>` | Model for the fixer. |

## Where things are
| Path (in the project) | What |
|---|---|
| `ai/pr/config.json` | Provider, MCP server **name**, org/project/repo, context files, related repos, build/test commands. Never a credential. |
| `ai/pr/review-guidelines.md` | Project-specific: what to check, comment voice, severity tags. |
| `ai/pr/fix-guidelines.md` | Project-specific: build/test, commit message, reply + thread-status etiquette. |
| `ai/pr/results/PR-<id>/` | Every run's files: `pr-`, `threads-`, `requirement-`, `review-`, `comments-`, `fix-`, `replies-`, `posted-<ts>`. |
| `ai/context/*.md` | Project context both agents read first. |

## Safety model
- The agents hold **no** PR-provider tool. Only the command posts, and only what you approved in that run.
- `/pr:review` never touches your working tree: it reviews a throwaway detached worktree of the PR head.
- `/pr:fix` refuses to start unless the tree is clean and on the PR's source branch. It never stashes,
  switches, force-pushes or skips hooks.
- The tooling never votes on a PR. The verdict is advice to you.
- Severity: `blocker` · `major` · `minor` · `nit` · `question`. Verdict is derived from the counts.

## Typical loops
| Situation | Do |
|---|---|
| Asked to review a colleague's PR | `/pr:review 28548 --req=<spec.md> --model=<other>` → read report → approve comments |
| Author pushed fixes | `/pr:review 28548` again — existing threads are not re-raised; "still present at head" is reported |
| Your own PR got comments | `/pr:fix 28548` → approve commit/push → approve replies → `/pr:review 28548 --no-post --model=<other>` |
| Before opening your PR for review | `/pr:review <id> --no-post` → `/pr:fix <id> --from-review` |

This command performs no live analysis — it only prints the reference above.
</reference>
