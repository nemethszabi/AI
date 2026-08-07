# dev framework — Shared Agent Protocol

Every `dev-*` agent MUST follow this protocol. Read this file first when spawned — before your own
`<role>` instructions, and before touching any file. **Binding**, not a checklist: this is the operational
contract that lets independently-authored specialist agents coordinate through the same state without
stepping on each other.

> **Precedence**: `~/.claude/CONSTITUTION.md` overrides this file if the two ever conflict (secrets,
> destructive actions, gates, scope, tool permissions — those live there, not duplicated here).
> `~/.claude/AGENT-CONDUCT-BASELINE.md` and `AGENT-TEMPLATE-BASELINE.md` govern general conduct and file
> shape respectively — this file is the layer specific to the `dev-*` role-specialist family only.

State-file convention below is `.dev/` (mirrors the reference framework this was adapted from). If the
project you're generating agents for already uses a different convention, change every `.dev/` path in
this file to match — do it once, here, not per-agent.

---

## 1. Load state before anything

```bash
cat .dev/STATE.md 2>/dev/null
cat .dev/config.json 2>/dev/null
```

Internalize: current phase/status, accumulated decisions (they constrain you), open blockers. If `.dev/`
doesn't exist, stop and report "project not initialized" rather than guessing a starting state.

## 2. Stay in your lane

Your task carries an `area` tag matching your role. If you discover work belonging to another area, do
**not** do it — record it under `## Handoffs` in your report (area, description, why) and let the
orchestrator route it. Exception: trivially small touches (a handful of lines) needed to keep the
immediate task coherent are fine; disclose them anyway.

## 3. Contracts are law

`.dev/contracts/` is the source of truth for every interface between areas. Implement against a contract
exactly. If a contract is wrong or insufficient: stop that task, record a `## Contract Issue` in your
report, move to the next independent task. Never silently diverge from a published contract. Only the
area that owns a contract/schema may edit it — every other area treats it as read-only.

## 4. Commit discipline

One commit per completed task. Conventional Commits (`feat:`, `fix:`, `chore:`, `test:`, `refactor:`,
`docs:`, plus `infra:` as a project extension if needed). Reference task/requirement IDs in the body when
the project has them. The destructive/bypass rules (`--no-verify`, force-push, amending others' commits)
are `CONSTITUTION.md` Article II — not restated here, just enforced.

## 5. Quality defaults

- TDD when implementing logic: failing test → implement → green → refactor. Skip only for pure
  config/markup tasks.
- Match existing codebase conventions (naming, structure, error handling) — see the project's own
  `ai/context/design-principles.md` if one exists. Greenfield: follow `.dev/ARCHITECTURE.md`.
- Deviation rule: if the plan says X but reality demands Y, do the smallest correct Y, document it under
  `## Deviations` in your report with rationale — never silently do something other than what was asked.

## 6. Report format

Append your section to the phase's `SUMMARY.md` (create if missing):

```markdown
## [agent-name] — [task IDs] — [date]
**Done:** what was built, files touched, commits made
**Deviations:** (or "none")
**Handoffs:** (or "none")
**Contract issues:** (or "none")
**Notes for gates:** anything a reviewer/QA/security gate should scrutinize
```

Then update `.dev/STATE.md`'s position/decisions if your work changed them. This is the concrete,
dev-family instance of `AGENT-CONDUCT-BASELINE.md` A8 (consistent report format) — use this template
rather than inventing a new shape per agent.

## 7. Blocked protocol

If truly blocked (missing credential, ambiguous requirement with no safe default, a failing dependency
outside your area): stop, write the blocker to `.dev/STATE.md` under `## Blockers`, report it in your
final message. Don't guess on irreversible things — `CONSTITUTION.md` Article VII.

---

**Amendment procedure**: edit this file directly; the git commit message is the change rationale. Takes
effect globally once copied to `~\.claude\dev-framework\PRINCIPLES.md`.
