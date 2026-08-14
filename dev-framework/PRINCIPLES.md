# dev framework — Shared Agent Protocol

Every `dev-*` agent MUST follow this protocol. Read this file first when spawned — before your own
`<role>` instructions, and before touching any file. **Binding**, not a checklist: this is the operational
contract that lets independently-authored specialist agents coordinate through the same state without
stepping on each other.

> **Precedence**: `~/.claude/CONSTITUTION.md` overrides this file if the two ever conflict (secrets,
> destructive actions, gates, scope, tool permissions — those live there, not duplicated here).
> `~/.claude/AGENT-CONDUCT-BASELINE.md` and `AGENT-TEMPLATE-BASELINE.md` govern general conduct and file
> shape respectively — this file is the layer specific to the `dev-*` role-specialist family only.

State-file convention below is `ai/dev/` — grouped under the same `ai/` root as `ai/context/`,
`ai/prompts/`, `ai/reports/` (the convention already used across these projects), rather than a bare
top-level `.dev/` dot-folder as in the reference framework this was adapted from. If a project you're
generating agents for uses yet another convention, change every `ai/dev/` path in this file to match — do
it once, here, not per-agent.

---

## 1. Load state before anything

```bash
cat ai/dev/STATE.md 2>/dev/null
cat ai/dev/config.json 2>/dev/null
```

Internalize: current phase/status, accumulated decisions (they constrain you), open blockers. If
`ai/dev/` doesn't exist, stop and report "project not initialized" rather than guessing a starting
state.

## 2. Stay in your lane

Your task carries an `area` tag matching your role. If you discover work belonging to another area, do
**not** do it — record it under `## Handoffs` in your report (area, description, why) and let the
orchestrator route it. Exception: trivially small touches (a handful of lines) needed to keep the
immediate task coherent are fine; disclose them anyway.

## 3. Contracts are law

`ai/dev/contracts/` is the source of truth for every interface between areas — unless the project already
has a real, code-level contracts location (e.g. a dedicated contracts/DTOs project); in that case treat
that as the source of truth and record its path in `ai/dev/config.json` instead of duplicating it under
`ai/dev/contracts/`. Implement against a contract
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
  `ai/context/design-principles.md` if one exists. Greenfield, or no existing architecture doc under
  `ai/context/`: follow `ai/dev/ARCHITECTURE.md`.
- Deviation rule: if the plan says X but reality demands Y, do the smallest correct Y, document it under
  `## Deviations` in your report with rationale — never silently do something other than what was asked.
- **Diagnose before fixing.** When the task is a bug/defect rather than new-feature work: before changing
  anything, form a root-cause hypothesis grounded only in what you actually read this run — the error/
  stack trace/log excerpt handed to you, plus the affected code. If the project maintains a bug-patterns
  file under `ai/context/*.md` (commonly named `*-bug-patterns.md`), check it first — apply its documented
  fix directly if a pattern matches, rather than re-deriving one from scratch, and append a new entry
  there (following that file's own format) once you've fixed something not yet documented. State a
  confidence level before implementing, using this fixed scale — also the scale to use for a `Confidence`
  line in your own report format, where one exists:
  - **High (85–100%)** — root cause confirmed by reading the actual code, log, or stack trace, and the
    repro is unambiguous. A match in the project's bug-patterns file further confirms this but isn't
    required — a genuinely novel bug can still be High if the evidence itself is conclusive.
  - **Medium (60–84%)** — plausible but not fully confirmed (e.g. no direct repro, or the code reading is
    inferential rather than a confirmed trace through the actual failure).
  - **Low (<60%)** — inferred from limited evidence, best-effort.

  Base the percentage on evidence quality, not how clean the resulting fix looks. If nothing in the
  available evidence supports a hypothesis, say so and ask for more evidence (repro steps, logs) rather
  than implementing a speculative fix. Before touching code, also weigh blast radius: does the fix affect
  other callers of the changed method/endpoint, a public API surface, auth/session, or payment/money
  handling? If so, read whatever project convention doc covers that area first, and flag the exposure
  under `## Notes for gates`.

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

Then update `ai/dev/STATE.md`'s position/decisions if your work changed them. This is the concrete,
dev-family instance of `AGENT-CONDUCT-BASELINE.md` A8 (consistent report format) — use this template
rather than inventing a new shape per agent.

## 7. Blocked protocol

If truly blocked (missing credential, ambiguous requirement with no safe default, a failing dependency
outside your area): stop, write the blocker to `ai/dev/STATE.md` under `## Blockers`, report it in your
final message. Don't guess on irreversible things — `CONSTITUTION.md` Article VII.

---

**Amendment procedure**: edit this file directly; the git commit message is the change rationale. Takes
effect globally once copied to `~\.claude\dev-framework\PRINCIPLES.md`.

---

**Amendment note (2026-08-07)**: state-file root changed from `.dev/` to `ai/dev/` to keep all
AI-tooling state grouped under the existing `ai/` folder (`ai/context/`, `ai/prompts/`, `ai/reports/`)
instead of adding a new top-level dot-folder. Also clarified that `contracts/` and `ARCHITECTURE.md`
should point at a project's real, pre-existing sources of truth rather than being duplicated under
`ai/dev/` when those already exist in code or in `ai/context/`.

**Amendment note (2026-08-14)**: added the "Diagnose before fixing" quality default (§5), generalizing
discipline that had been living ad hoc inside `net8-migration`'s `/scm:fix` command (confidence bands,
bug-patterns-first, blast-radius check) — `ReaFlow`'s older, pre-agent monolithic fix prompt had
independently reinvented a weaker version of the same thing, which is the drift this closes. Centralized
here rather than duplicated into `dev-backend.md`/`dev-frontend.md` directly, since both already say
"follow PRINCIPLES.md's rules, don't restate them" and inherit this automatically. Bug-fixing commands
(e.g. `/scm:fix`) still own whatever's structurally project-only — DB/log access, issue-tracker
integration, version-bump mechanics — since the dispatched agent's tool grant can't reach those anyway.
