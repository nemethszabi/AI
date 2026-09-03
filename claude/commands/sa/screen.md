---
name: sa:screen
description: Answer "can we do this, and roughly what would it cost?" in one command — scaffolds, extracts, clarifies and screens in sequence, producing real requirements plus an advisory, non-quotable screen.md. The bid/no-bid pass, before anyone commits to an offer.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<path-or-slug> [--lane <rom|offer-sow|full-design>] [--client <name>] [--dry-run]"
---

> Version: 1.0.0

<objective>
`/sa:screen <path-or-slug>` answers the two questions that get asked before anyone decides to bid — **can
we do this, and roughly what would it cost?** — by running the pipeline's shallow front half in one
command: scaffold → extract → clarify → screen.

It produces **real** `requirements.json` (the artifact every later step cites, and the most expensive thing
to re-derive) and an **advisory** `screen.md` carrying the feasibility verdict and a deliberately coarse,
explicitly non-quotable effort band. It writes no `estimation.json` and no `offer.json`, so nothing it
leaves behind can be mistaken for — or built into — a client deliverable.

**This is the one place in the namespace where commands run in sequence without a human between them**, and
it earns that because it terminates in an internal decision input rather than in something a client
receives. Everything past the bid/no-bid decision stays one-command-at-a-time.

**Depth of pass and lane are independent.** A screen is not the `rom` lane. `rom` is a statement about an
engagement's commercial weight; a screen is a statement about how deep *this sweep* goes, and the biggest
RFP in the pipeline still starts with someone asking whether to bid it. So `/sa:screen` runs on any lane,
and on none.
</objective>

<process>
<step name="resolve-input">
Parse `$ARGUMENTS` as `<path-or-slug> [--lane <lane>] [--client <name>] [--dry-run]`.

- **A slug** (matches an existing `ai/sa/<slug>/`) → screen that engagement. Reuse whatever is already
  there; never re-scaffold and never re-ingest what `inputs/` already holds.
- **A file or folder path** → the common case, where nothing exists yet.
- **A free-form description with no file** → also valid; skip the ingest step entirely and clarify from the
  text, exactly as `/sa:clarify` does.
- **Empty** → ask for a path, a slug, or a description. Never guess at a document from the working
  directory's contents.

With `--dry-run`, print the sequence this invocation would run, which steps it would skip and why, and stop
without dispatching anything.
</step>

<step name="scaffold">
Skip entirely if the slug already has `engagement.json`.

Otherwise dispatch `/sa:triage`'s scaffolding with intake **reduced to the minimum**: client, project and
slug only. Do **not** run triage's full 3–5 question intake, and do not press the user on the lane — the
whole reason they are screening is that they haven't decided whether this is worth an offer, so asking them
to commit to a lane first inverts the question.

Record the lane as triage's provisional classification (or `--lane` if given), and say plainly in the
report that it is provisional. This is safe because the lane is documented as reversible and re-running
`/sa:triage` updates it in place — and because `req-screener` ends its own output with the lane the
requirements actually look like, which is better evidence than a guess made before reading them.
</step>

<step name="ingest">
Skip when the input was a free-form description, or when `inputs/` already holds extractions for the files
given.

Otherwise dispatch `req-ingestor` for the resolved paths, exactly as `/sa:ingest` does. `inputs/` is
immutable once written, here as everywhere.
</step>

<step name="clarify">
Dispatch `req-analyst` for a **real** `requirements.json` + `requirements.md`. Full quality, not a sketch —
these carry forward into the offer if the decision is to bid, and a shallow requirements list is the one
shortcut that would poison everything downstream.

One instruction differs from `/sa:clarify`: **prefer recording `to_clarify` over asking the user.** On a
screen the unanswered questions *are* part of the deliverable — "here is what nobody has told us yet" is
half of what the person deciding needs. Reserve `AskUserQuestion` for something that would change the
feasibility verdict itself, not for detail that only sharpens a number this pass isn't producing anyway.
</step>

<step name="screen">
Dispatch `req-screener` with the resolved slug and project path. It reads `requirements.json`, plus
`brief.md` and `inputs/` if present, and writes `screen.md`.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md` for the steps that genuinely ran — phases `triage`, `ingest` and `clarify`,
appended to phase history as usual, since those wrote real artifacts.

**Do not record a `screen` phase.** It isn't a value in the phase enum, and `screen.md` is an advisory
non-artifact (`ARTIFACT-SCHEMAS.md` §6). Set `Next` to what the pipeline would say after `clarify` — the
lane's next command — and let the report, not the state file, carry the bid/no-bid recommendation.
</step>

<step name="report">
Relay `req-screener`'s summary, then print:

```
Screened <client> / <project> (<slug>) — <n> requirements, <n> to_clarify.
Can we do it?   <verdict> — <one line>
Rough effort:   <n>–<n> person-days (order of magnitude, NOT quotable)
Blockers:       <n> · Decision-relevant unknowns: <n>
Looks like:     <lane> lane
Written:        requirements.json (real) · screen.md (advisory)

If we bid: /sa:triage <slug> to confirm the lane, then /sa:design.
If we don't: nothing here is a deliverable and nothing cites screen.md.
```

State which steps were skipped and why. If `req-screener` returned `cannot-assess`, lead with that and name
what would have to be answered — do not bury it under a band.

Follow-up questions about the screen go to that same `req-screener` agent via `SendMessage` to the agent id
this dispatch returned, which still holds the requirements and extractions in context. If that session is
gone, re-read `screen.md` and `requirements.md` and `Grep` the extractions rather than re-dispatching
(`AGENT-TEMPLATE-BASELINE.md` §3).
</step>
</process>

<rules>
- **Writes no `estimation.json` and no `offer.json`.** Not a draft, not a placeholder, not under another
  name. This is the whole reason a multi-step command is acceptable here: it cannot leave behind anything a
  client deliverable could be built from. A number that needs to be quotable is `/sa:estimate`'s output,
  reached one command at a time.
- **Never runs `/sa:design`, `/sa:risk`, `/sa:estimate`, `/sa:offer`, `/sa:audit` or `/sa:package`.** The
  sequence stops at the screen, always. If the user asks this command to keep going, name the next command
  and stop — the human checkpoint at the bid/no-bid decision is the point, not an obstacle
  (`ARTIFACT-SCHEMAS.md` §7, `CONSTITUTION.md` Articles III and VII).
- **The band is never quotable and never becomes a price.** `screen.md` says so on its face; the report
  repeats it. No rate card is read here even if one exists.
- **`screen.md` follows the §6 advisory carve-out in full** — no JSON, no IDs, excluded from `inputs_hash`,
  no `STATE.md` phase, and never `extra` in `/sa:status`.
- **Halt and report rather than assume.** If `req-analyst` raises something that changes feasibility, or a
  precondition is genuinely missing, stop at that step and say where it stopped and why. A partial screen
  with its boundary stated is useful; a complete-looking screen built over a gap is not.
- **Requirements are real; everything else here is provisional.** Say that in the report every time, so the
  next person to open the folder knows which of the two files they can trust.
- **Never commit.**

`req-screener`'s own rules — the verdict enum, the banding discipline, the no-PERT boundary, citation
requirements — live in `agents\req-screener.md` and are deliberately not restated here
(`AGENT-TEMPLATE-BASELINE.md` §3).
</rules>
