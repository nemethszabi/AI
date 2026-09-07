---
name: sa:slop-check
description: Prose-integrity gate — scans an engagement's rendered Markdown and built deliverables for ungrounded claims, contradictions, AI-tell slop and locale regressions, via req-slop-detector. Emits the second verdict /sa:package requires.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<slug> [--model=sonnet|opus|haiku|fable]"
---

> Version: 1.0.0

<objective>
`/sa:slop-check <slug> [--model=<model>]` runs `req-slop-detector` over `ai/sa/<slug>/`'s rendered Markdown
and the extracted text of anything already built under `deliverables/`, writing a timestamped report to
`ai/sa/<slug>/audit/` that ends with a fenced `sa-verdict` block carrying `gate: sa-slop` and a
content-based `inputs_hash`.

This is the **second input to the one packaging gate**, not a second gate: `/sa:package` refuses without
both `sa-audit` and `sa-slop` at `PASS`/`PASS-WITH-WAIVERS` on a matching hash
(`sa-framework/ARTIFACT-SCHEMAS.md §5`). The two check disjoint surfaces — `/sa:audit` asks whether the JSON
artifacts agree with each other by ID; this asks whether the prose a human will actually read is true to
them. An offer whose every ID resolves can still quote an invented benchmark, and only this command sees it.

**Run it on a different model than wrote the artifacts** — see the `--model` step below.
</objective>

<process>
<step name="parse-model">
Parse `--model=<value>` out of `$ARGUMENTS` wherever it appears; valid values are `sonnet`, `opus`, `haiku`,
`fable`. Reject any other value and ask for a correction rather than silently ignoring it. Strip it from the
remaining arguments before slug resolution.

`--model` is optional but **this is the command where it matters most** (`ARTIFACT-SCHEMAS.md §9`). A model
scanning prose it produced itself is being asked to notice its own habits, and shares exactly the priors
that made every ungrounded sentence feel reasonable when it was written. If no override was given, still
run — but say so plainly in the relay and name a suggested override.
</step>

<step name="resolve-slug">
Same resolution as `/sa:design`: explicit argument if it names an existing `ai/sa/<slug>/`, else glob
`ai/sa/*/engagement.json` (exactly one → use it; multiple → ask via `AskUserQuestion` which topic; none →
tell the user to run `/sa:triage` first).
</step>

<step name="preflight">
Confirm at least one scan target exists: any rendered `.md` under `ai/sa/<slug>/`, or any file under
`deliverables/`. If neither, stop with:

```
Nothing to scan in ai/sa/<slug>/ — no rendered artifacts and no deliverables.
Run /sa:clarify (and the rest of the lane) first, or /sa:package to build something to check.
```

Do not dispatch. An agent given no targets can only produce an empty report or an invented one.
</step>

<step name="compute-inputs-hash">
Compute `inputs_hash` **before dispatching**, per `ARTIFACT-SCHEMAS.md §5` — the same input set and the same
fixed order `/sa:audit` and `/sa:package` use: `git hash-object` over whichever of `requirements.json`,
`architecture.json`, `estimation.json`, `risk-register.json`, `offer.json` exist, first 12 characters each,
joined as `requirements:abc123def456,architecture:...`. Outside a git repo fall back to `sha256sum`
(PowerShell: `Get-FileHash -Algorithm SHA256`).

Content-based, never mtimes. Rendered `.md`, `deliverables/`, `diagrams/`, `onepager/` and snapshots are
excluded from the hash even though this gate reads several of them — §5 records why, and the consequence it
names (a hand-edited `.md` stales neither gate) is intended, not a hole.

Pass the computed hash to the agent; it echoes it verbatim into its verdict block.
</step>

<step name="extract-deliverables">
`req-slop-detector` is read-only with no `Bash` and cannot open OOXML zips. Extract text from every binary
under `deliverables/` into `ai/sa/<slug>/audit/extract/<source-filename>.txt` before dispatching, using
`python-docx` / `openpyxl` / `python-pptx` via a short script per file.

- One `.txt` per source file, named after the source, so a finding maps back unambiguously.
- Rewrite the extracts fresh on every run — `audit/extract/` is regenerable scratch, not evidence
  (`ARTIFACT-SCHEMAS.md §6`), and a stale extract would have the gate pass a document nobody checked.
- If extraction fails for a file, **do not abort**: skip it, and pass its name to the agent so the report
  lists it under `## Not scanned`. A deliverable that went unchecked is reported, never silently treated as
  clean.

Skip this step entirely when `deliverables/` is empty — the pre-package run is the normal case, and scanning
the rendered `.md` alone is the intended behavior then.
</step>

<step name="dispatch">
Dispatch to `req-slop-detector` via `Agent`. Give it the resolved slug and project path, the computed
`inputs_hash`, the list of extracted `.txt` files, the names of any binaries that failed extraction, and the
lane from `engagement.json`. If `--model` was parsed, pass it as the `Agent` dispatch's `model` parameter —
per-invocation only. **Never write a `model:` line into `req-slop-detector.md`'s own frontmatter**: pinning a
reviewer's model makes it wrong the moment the author's model changes, which is the opposite of what §9 is
for.
</step>

<step name="parse-verdict">
Parse **only** the fenced ` ```sa-verdict ` block at the end of the agent's report — never infer a verdict
from prose or a bold line (`AGENT-CONDUCT-BASELINE.md` B7). Validate that `gate:` is `sa-slop`, that
`verdict:` is one of `PASS | PASS-WITH-WAIVERS | BLOCKED`, and that `inputs_hash:` matches the hash you
computed.

If the block is missing or malformed, re-prompt the agent **once** via `SendMessage` ("your report is
missing a valid sa-verdict block — return it again"). If it is still missing or malformed, abort: do not
update `STATE.md`, and do not guess a verdict on the agent's behalf.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md` in the canonical shape from `ARTIFACT-SCHEMAS.md §6`: phase `slop-check`,
last command `/sa:slop-check`, and `Next` set to — first match wins — `/sa:audit` if no fresh passing
`sa-audit` verdict exists, `/sa:package` if both gates now pass, otherwise the specific command that fixes
the first blocking finding. Append to phase history; never rewrite prior lines.
</step>

<step name="relay">
Return the verdict, the per-layer counts (groundedness · contradictions · slop · locale), every blocking
finding one line each with the command that fixes it, anything the agent listed under `## Not scanned`, and
the report path.

State **which model actually ran the scan**. If `--model` was not given, add one line:

```
Scan ran on the session model — the same family that wrote these artifacts.
For a client-facing pass, re-run with --model=<a different one> before /sa:package.
```

That reminder is not decoration: a same-model scan is the case where a fabricated sentence is least likely
to be noticed, because it is exactly what that model would have written (`ARTIFACT-SCHEMAS.md §9`).

Never describe a cross-model pass as "independently verified" — sibling models share training lineage and
therefore share blind spots. It reduces correlated error; it is not a second reviewer.
</step>
</process>

<rules>
- **Thin dispatcher only.** All scanning happens inside `req-slop-detector`; never restate a threshold or a
  pattern from its `<review_dimensions>` here.
- **Never re-interpret the verdict.** Relay it as issued — a gate a dispatcher can soften is not a gate
  (`CONSTITUTION.md` Article III).
- **The command computes the hash and extracts the binaries; the agent stays read-only.** That split is what
  keeps the scanner unable to alter what it scans.
- **Never edit a document to clear a finding.** Fixing a finding means re-running the command that owns the
  artifact — `/sa:offer`, `/sa:estimate`, `/sa:clarify` — so the correction lands in the JSON and the
  rendered `.md` is regenerated from it.
- **Never overwrite a prior slop report**, and never delete one to make a gate pass.
- **Never commit.** Writing artifacts is this pipeline's job; committing them is the human's.
</rules>
