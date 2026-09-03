---
name: sa:brief
description: Produce a structured comprehension brief of an engagement's inbound documents via doc-briefer — the pre-triage read that /sa:triage deliberately doesn't do. Advisory only; writes brief.md and touches no pipeline artifact or state.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
argument-hint: "<slug-or-path> [--out <path>] [--recursive]"
---

> Version: 1.1.0 — minor: follow-up Q&A now names `SendMessage` and its fallback explicitly, per
> `AGENT-TEMPLATE-BASELINE.md` §3; the `<slug-or-path>` bare-path form documented in `<objective>`.

<objective>
`/sa:brief <slug-or-path>` dispatches `doc-briefer` to read an engagement's inbound documents and write
`ai/sa/<slug>/brief.md` — a structured comprehension brief covering what the document is, its section map,
the business problem, key facts and constraints, the integration surface, conspicuous gaps, and where to
read closely.

It exists because of a real hole in the lane model: `/sa:triage` asks the human to commit to `rom`,
`offer-sow` or `full-design` — the choice that determines the entire downstream pipeline — while its own
rules forbid it from *interpreting or summarizing* the inbound material ("Do not copy, summarize or rewrite
it; record its path… No analysis here"), and `/sa:ingest` is likewise forbidden from interpreting what it
extracts. Triage may read; it may not tell you what the document means. So the first interpreted output in
the pipeline is `/sa:clarify` — two steps after the lane was already chosen. This command fills that gap
without weakening either rule.

**Advisory, not a phase.** It writes no JSON, updates no `STATE.md`, and produces nothing any other
artifact cites. Run it before `/sa:triage`, after `/sa:ingest`, or never — the pipeline behaves identically
either way.

**Both argument forms work, and the path form is the point.** `/sa:brief <slug>` briefs an existing
engagement's extracted inputs; `/sa:brief <path>` briefs a raw file or folder with **no engagement yet** —
which is the pre-triage case this command was built for, since the lane call is what needs the read. The
path form neither creates nor requires `ai/sa/<slug>/`.

`/doc-brief <path>` is the same underlying agent for documents unrelated to any engagement. Prefer
`/sa:brief` once a document is headed for a bid, even before triage: the brief then lands in the
engagement folder as soon as one exists, instead of beside the source file.
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
has no extracted inputs, and `/sa:clarify <slug>` otherwise.

Then add one line telling the user that follow-up questions go to that **same** `doc-briefer` agent via
`SendMessage` to the agent id this dispatch returned — it still holds the full document text and answers
with section citations. Say `SendMessage`, not "ask it again": a fresh `Agent` call re-extracts and
re-reads everything at full token cost with no memory of the first pass
(`AGENT-TEMPLATE-BASELINE.md` §3).

If that agent session is gone, name the fallback rather than silently re-dispatching: read the `brief.md`
just written, and `Grep` the extracted Markdown at the path the agent reported. Re-dispatch only when the
question genuinely needs the whole document re-read.
</step>
</process>

<rules>
- **This command writes nothing at all** — enforced by its tool grant, which has no `Write` or `Edit`. It
  resolves inputs, dispatches, and reports; `doc-briefer` writes the brief. No `*.json`, no rendered
  pipeline `.md`, no `audit/`, no `deliverables/`, no `inputs/`.
- **Never updates `STATE.md`.** "brief" is not a value in the phase enum, and writing one would make
  `/sa:status` report a phase the lane model doesn't contain. This is the advisory-command carve-out
  recorded in `ARTIFACT-SCHEMAS.md` §6 — cite it there; don't re-argue it here.
- **`brief.md` is excluded from the packaging gate.** It carries no IDs and nothing cites it, so it is not
  part of `/sa:package`'s `inputs_hash` (`ARTIFACT-SCHEMAS.md` §5). Re-running `/sa:brief` never stales a
  gate.
- **Never dispatches a second agent.** One `doc-briefer` call. Requirements, design, risk and estimate work
  belong to their own commands — name the right one (`/sa:clarify` first) and stop.
- **Never commits.** No `git add`, `git commit` or `git push` — `CONSTITUTION.md` Articles II and VII.
- **Re-running is non-destructive to everything but the brief itself**, which is regenerated wholesale.

`doc-briefer`'s own rules — extraction limits, `inputs/` immutability, the no-requirements boundary,
one-level folder scanning — live in `agents\doc-briefer.md` and are deliberately not restated here
(`AGENT-TEMPLATE-BASELINE.md` §3: the specificity lives in the agent, not the dispatcher).
</rules>
