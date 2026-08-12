---
name: sa:brief
description: Produce a structured comprehension brief of an engagement's inbound documents via doc-briefer — the pre-triage read that /sa:triage deliberately doesn't do. Advisory only; writes brief.md and touches no pipeline artifact or state.
allowed-tools:
  - Read
  - Write
  - Bash
  - Grep
  - Glob
  - Agent
argument-hint: "<slug-or-path> [--out <path>] [--recursive]"
---

> Version: 1.0.0

<objective>
`/sa:brief <slug-or-path>` dispatches `doc-briefer` to read an engagement's inbound documents and write
`ai/sa/<slug>/brief.md` — a structured comprehension brief covering what the document is, its section map,
the business problem, key facts and constraints, the integration surface, conspicuous gaps, and where to
read closely.

It exists because of a real hole in the lane model: `/sa:triage` asks the human to commit to `rom`,
`offer-sow` or `full-design` — the choice that determines the entire downstream pipeline — while its own
rules forbid it from reading the inbound material ("Do not copy, summarize or rewrite it; record its path…
No analysis here"), and `/sa:ingest` is likewise forbidden from interpreting what it extracts. The first
interpreted output in the pipeline is `/sa:clarify`, two steps after the lane was already chosen. This
command fills that gap without weakening either rule.

**Advisory, not a phase.** It writes no JSON, updates no `STATE.md`, and produces nothing any other
artifact cites. Run it before `/sa:triage`, after `/sa:ingest`, or never — the pipeline behaves identically
either way.
</objective>

<process>
<step name="resolve-input">
Parse `$ARGUMENTS` as `<slug-or-path> [--out <path>] [--recursive]`.

- **A slug** (matches an existing `ai/sa/<slug>/`) → read `inputs/INDEX.md` and the `*.extracted.md` files
  it lists. If `inputs/` is empty or absent, say so and recommend `/sa:ingest <slug> <path>` first — then
  offer to proceed against a raw path instead rather than stopping dead.
- **A file or folder path** → the common pre-triage case, where no engagement exists yet. Proceed against
  the path directly. Do not scaffold anything; `/sa:triage` owns engagement creation.
- **Empty** → if exactly one `ai/sa/*/engagement.json` exists, use that slug. Otherwise ask for a slug or
  a path.

Resolve the output path: `--out` if given; otherwise `ai/sa/<slug>/brief.md` for a slug, or a `-brief.md`
file beside the first source document when running against a bare path.
</step>

<step name="dispatch">
Dispatch the `doc-briefer` agent with: the resolved source paths (or the engagement's `inputs/` extractions),
the resolved output path, and whether `--recursive` was passed.

If `ai/sa/<slug>/engagement.json` exists, pass the client, project and `compliance_flags` as orienting
context only — the brief describes what the document says, and an engagement's own metadata must never be
presented as something the document stated.

Dispatch once. Never dispatch `req-analyst`, `req-architect` or any other pipeline agent from here — this
command produces a brief and nothing else.
</step>

<step name="report">
Relay the agent's summary, then print:

```
Briefed <n> document(s) for <slug or path>.
<n> sections — <n> requirement / <n> background / <n> boilerplate.
<n> integrations named, <n> actually specified · <n> conspicuous gaps.
Warnings: <list, or none>
Written: <brief path>

Next: <the recommendation — see below>
```

`Next` is `/sa:triage <path>` when no engagement exists yet, `/sa:ingest <slug> <path>` when the engagement
has no extracted inputs, and `/sa:clarify <slug>` otherwise. Add one line noting that follow-up questions
can go to the same `doc-briefer` agent while it still holds the document.
</step>
</process>

<rules>
- **Never writes a pipeline artifact.** No `*.json`, no rendered pipeline `.md`, no `audit/`, no
  `deliverables/`. Only `brief.md` at the resolved output path.
- **Never updates `STATE.md`.** "brief" is not a value in the phase enum (`ARTIFACT-SCHEMAS.md` §6), and
  writing one would make `/sa:status` report a phase the lane model doesn't contain. The brief's absence
  from pipeline state is deliberate, not an oversight.
- **`brief.md` is excluded from the packaging gate.** It carries no IDs, nothing cites it, and it is not
  part of `/sa:package`'s `inputs_hash` (`ARTIFACT-SCHEMAS.md` §5). Re-running `/sa:brief` never stales a
  gate.
- **Never writes into `inputs/`.** Immutable after `/sa:ingest` — the agent extracts to a temp directory
  when it has to extract at all.
- **Never re-extracts what `/sa:ingest` already extracted.** Existing `inputs/*.extracted.md` are the
  source; they carry provenance headers this command must not duplicate or contradict.
- **Never produces requirements.** No REQ-IDs, no priorities, no design, no estimate, no risk scores. If
  the user wants those, name `/sa:clarify` and stop.
- **Never commits.** No `git add`, `git commit` or `git push` — `CONSTITUTION.md` Articles II and VII.
- **Re-running is non-destructive to everything but the brief itself**, which is regenerated wholesale.
</rules>
