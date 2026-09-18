---
name: sa:revise
description: Apply a change to an engagement that already has artifacts — architecture rework, a scope cut, a re-estimate — re-running only the steps the change actually invalidates, archiving what it supersedes, and recording why. The path for the fifth revision of a live bid, instead of hand-patching JSON.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - Agent
argument-hint: "<slug> \"<what changed and why>\" [--from=clarify|design|risk|estimate|offer] [--only]"
---

> Version: 1.0.0 — new. Written after an engagement reached its nineteenth estimation revision with nine
> `.bak` files beside the live artifact, five ad-hoc `_rev6_patch*.py` scripts in the engagement folder,
> a `__pycache__` directory, and no record anywhere of why revision 17 differed from revision 16.

<objective>
`/sa:revise <slug> "<change>"` applies a change to an engagement whose artifacts already exist, and does
the three things that were being done by hand:

1. **Works out what the change actually invalidates** — and re-runs only that, in dependency order.
2. **Archives what it supersedes** into `history/`, rather than leaving `.bak` files beside the live file.
3. **Records why**, in `CHANGELOG.md`, so the fifth revision of a bid can be explained to the person who
   has to defend its number.

The pipeline was built for a first pass. Every command assumes it is producing an artifact, not amending
one. That gap is where the mess came from: re-running `/sa:estimate` from scratch felt too expensive, so
people hand-edited `estimation.json` instead, which broke it against its own schema, which meant the
workbook had to be built by a bespoke script, which meant the next change had to be hand-patched too.

**This command never edits an artifact directly.** It decides what to re-run and dispatches the agent that
owns each one. An artifact hand-edited outside its owning agent is exactly how one engagement's `rollup`
ended up carrying `committed_total`, `platform_unloaded` and `if_all_options_taken` — none of which are
schema fields, and none of which any builder can interpret.
</objective>

<process>
<step name="resolve-and-read">
Resolve the slug as `/sa:design` does. Read `engagement.json` for the lane, and `STATE.md` for the current
phase. No `engagement.json` means no engagement to revise: say so and point at `/sa:triage`.

Read the **change note** from `$ARGUMENTS`. It is required. A revision with no stated reason is the thing
this command exists to stop — nine backups and no changelog is what "I'll remember why" looks like a month
later.
</step>

<step name="classify-the-change">
Decide the **entry point** — the earliest artifact the change touches. `--from=` states it explicitly;
otherwise classify from the change note:

| The change is about | Entry point |
|---|---|
| what the client asked for; a requirement added, cut, or re-prioritised | `clarify` |
| how it is built; a component added or withdrawn; an approach replaced | `design` |
| a new or reassessed risk; a contingency argument | `risk` |
| sizing only — the scope and design are unchanged | `estimate` |
| wording, positioning, what is disclosed; no numbers move | `offer` |

State the classification and the reasoning **before acting**, in one line. Getting this wrong is
recoverable; getting it wrong silently is not.

When the note spans two entry points — "drop the HDX component and re-size the dashboard" — take the
**earlier** one. Re-running a step that did not need it costs a few minutes. Skipping one that did leaves
two artifacts describing different solutions, and nothing downstream notices.
</step>

<step name="derive-the-cascade">
From the entry point, the steps to re-run are that step and everything downstream of it **on this lane**
(`ARTIFACT-SCHEMAS.md §4.1`). Downstream order is fixed:

```
clarify → design → risk → estimate → offer
```

with `review` after `design` and `design-detail` after `review` on the `full-design` lane, and `design`,
`risk` and `review` skipped entirely on `rom`.

`--only` restricts the run to the entry point alone. It is for the case where you already know the
downstream artifacts are unaffected — a wording fix in the offer, say. **Report what it skipped**, by
name, so a stale downstream artifact is a decision on the record rather than an oversight.

Print the plan and the reason, then proceed:

```
Revising <slug> — <change note>
  Entry point : estimate  (sizing only; scope and design unchanged)
  Re-running  : estimate → estimate-review → offer
  Unchanged   : requirements, architecture, risk-register
  Gates       : both will go stale and must be re-run before /sa:package
```
</step>

<step name="archive">
Before anything is rewritten, copy each artifact the cascade will touch into
`ai/sa/<slug>/history/<artifact>-r<NN>.json`, where `NN` is the `meta.revision` currently in the file.

`history/`, not a `.bak` beside the live file. The difference is not tidiness. A `.bak` sits in the same
glob as the artifact it shadows, so every tool that scans the folder sees both, every agent that resolves
"the estimation file" can find the wrong one, and nine of them in one directory makes the live file harder
to identify, not easier.

Never overwrite a file already in `history/` — a revision number is a fact about what was sent.
</step>

<step name="dispatch">
Dispatch each step in cascade order, exactly as its own command would, and **wait for each to finish
before starting the next**. Each agent reads the artifact it owns, merges the change, and writes both the
JSON and its rendered Markdown.

Give the dispatched agent the change note itself, verbatim, plus the entry point's reasoning. An agent
told "re-estimate" produces a different result from one told "re-estimate: the client withdrew the
wallboard and accepts a configuration workaround for the open-email limit" — the second can tell which
lines should move and which must not.

Every agent **increments `meta.revision` and sets `supersedes`** (`ARTIFACT-SCHEMAS.md §2`). Check that it
did. A re-run that leaves `revision` unchanged has produced an artifact that cannot be told apart from the
one it replaced.

Relay each agent's own summary and any blocking questions as you go, rather than collecting them to the
end. A revision pass can take several minutes, and a blocking question surfaced at the end is a question
that was answerable five steps ago.
</step>

<step name="changelog">
Append one entry to `ai/sa/<slug>/CHANGELOG.md`, creating it if absent:

```markdown
## r<NN> — <ISO date>

**Change**: <the note, verbatim>
**Entry point**: <step> — <why>
**Re-ran**: <steps>
**Effect on the committed figure**: <before> MD → <after> MD (<delta>), or "unchanged"
**Superseded**: history/<artifact>-r<NN>.json, …
```

The effort line matters most and is the one most often missing. A bid that moved from 263 to 184 man-days
across nineteen revisions needs to be explicable one revision at a time, because somebody will eventually
be asked why — and the honest answer has to come from a record, not a reconstruction.

Append; never rewrite a prior entry.
</step>

<step name="update-state">
Update `STATE.md` in the canonical shape (`ARTIFACT-SCHEMAS.md §6`): phase = the last step re-run, last
command `/sa:revise`, next `/sa:audit`. Append to phase history; never rewrite a prior line.
</step>

<step name="relay">
Report, in this order:

1. The change note and the entry point, with its reasoning.
2. Each step re-run, with the agent's own summary.
3. **The effort delta** — the committed total before and after, or "unchanged". This is the first thing
   anyone asks and the last thing a transcript usually makes findable.
4. What was archived.
5. Any blocking question a dispatched agent raised.
6. **That both gates are now stale**, and that `/sa:audit` and `/sa:slop-check` must be re-run before
   `/sa:package`. They are content-hashed, so this happens automatically — but say it, because the next
   step someone reaches for after a revision is the rebuild.
</step>
</process>

<rules>
- **Never edit an artifact directly.** Dispatch the agent that owns it. A hand-edited artifact breaks
  against its own schema, and everything downstream then needs hand-editing too — which is the failure
  mode this command exists to end.
- **Never write a one-off patch script** in an engagement folder. If the same edit is needed repeatedly,
  that is a change to an agent or to `sa-framework/builders/`, made once.
- **Never leave `.bak` files beside a live artifact.** Superseded revisions go in `history/`.
- **A change note is mandatory.** No note, no revision.
- **The cascade is derived, never assumed.** State the entry point and the reasoning before acting.
- **`--only` reports what it skipped**, by name.
- **Never renumber IDs.** A requirement that is dropped becomes `"status": "withdrawn"`, never removed —
  downstream artifacts already cite it (`ARTIFACT-SCHEMAS.md §3`).
- **Never touch `deliverables/`.** A document that was sent is a fact about the past. The next build takes
  the next version number.
- **Never commit.**
</rules>

<notes>
**Running a fast requirement-to-estimate pass.** That is not this command — it is the `rom` lane, which
exists precisely for it: `/sa:triage` classifying to `rom`, then `ingest → clarify → estimate → offer` with
no design, risk or review step (`ARTIFACT-SCHEMAS.md §4.1`, and `ESTIMATION-METHOD.md §10` on the stricter
sizing that lane requires). Use `/sa:revise` when artifacts already exist and something about them has
changed.

**Housekeeping.** An engagement folder should contain artifacts, `inputs/`, `audit/`, `diagrams/`,
`deliverables/`, `history/` and `CHANGELOG.md`. Anything else — `__pycache__/`, `_patch_*.py`,
`*.bak`, a hand-written edit list — is residue from a revision made without this command, and is safe to
delete once its content is reflected in an artifact. Say so when you see it; do not delete it silently.
</notes>
