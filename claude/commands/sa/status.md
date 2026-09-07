---
name: sa:status
description: Report where an SA engagement stands — lane, phase, artifacts present vs. the lane's expected set, gate freshness, open to_clarify count — and recommend exactly one next command. Read-only.
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
  - AskUserQuestion
argument-hint: "[slug]"
---

> Version: 1.3.0 — minor: reports both gates (`sa-audit` and `sa-slop`) separately with the model each ran
> on, the resolved document profile, and `onepager/` as advisory non-artifact #3
> (`ARTIFACT-SCHEMAS.md` §5, §6, §8, §9). 1.2.0 — `screen.md` reported alongside `brief.md` on its own
> advisory line, per the then two-entry §6 carve-out. 1.1.0 — `brief.md` reported on its own advisory line
> and excluded from `extra`.

<objective>
`/sa:status [slug]` answers "where am I in this engagement?" It reads `ai/sa/<slug>/STATE.md` and
`engagement.json`, compares the artifacts actually present against the set the engagement's lane expects
(`sa-framework/ARTIFACT-SCHEMAS.md` §4.1), checks whether any recorded gate has gone stale by recomputing
the `inputs_hash` per §5, counts open `to_clarify` items, and recommends exactly **one** next command.
Strictly read-only — it never writes, never repairs, and never re-runs a gate on the user's behalf.
</objective>

<process>
<step name="resolve-slug">
Resolve the slug in this order:
1. `$ARGUMENTS` names an existing `ai/sa/<slug>/` → use it.
2. Otherwise glob `ai/sa/*/engagement.json`:
   - exactly one → use it;
   - multiple → list every slug with its lane and phase, and ask via `AskUserQuestion` which one;
   - none → tell the user to run `/sa:triage` first, and stop.

If the folder exists but `engagement.json` is missing, say so and recommend `/sa:triage <slug>` to
(re)initialize it — do not attempt to infer a lane from the other artifacts.
</step>

<step name="read-state">
Read silently — do not echo file contents:
- `ai/sa/<slug>/engagement.json` (required — lane, client, project, `open_questions`)
- `ai/sa/<slug>/STATE.md` (required — phase, last command, next, phase history)
- whichever of `requirements.json`, `architecture.json`, `detailed-design.json`, `review.json`,
  `risk-register.json`, `estimation.json`, `estimate-review.json`, `offer.json` exist
- the most recent `audit/audit-<ts>.md`, if any
- directory listings only for `inputs/`, `diagrams/`, `deliverables/`
</step>

<step name="compute-signals">
Counts and comparisons only — no analysis of content.

- **Lane and phase**: `engagement.lane`; `Phase` from `STATE.md`.
- **Expected artifacts** for the lane, per `ARTIFACT-SCHEMAS.md` §4.1:
  - `rom` → `requirements.json`, `estimation.json`, `offer.json`
  - `offer-sow` → the above plus `architecture.json`, `risk-register.json`, `estimate-review.json`, and
    packaged files under `deliverables/`
  - `full-design` → the above plus `review.json`, `detailed-design.json`, and files under `diagrams/`
  Mark each present or missing. An artifact outside the lane's expected set that exists anyway is listed
  as extra, not as an error. **`brief.md`, `screen.md` and `onepager/` are never `extra`** — all three are
  advisory non-artifacts (`ARTIFACT-SCHEMAS.md` §6), optional on every lane; report each on its own line as
  present or absent, and never as unexpected.
- **Open `to_clarify`**: requirements with `"status": "to_clarify"` in `requirements.json`, plus
  `open_questions[]` entries in `engagement.json` and `requirements.json`, plus any field in
  `engagement.json` still literally valued `to_clarify`. Report the three sub-counts, not one blended
  number.
- **Gate freshness** (§5): recompute the hash over `requirements.json architecture.json estimation.json
  risk-register.json offer.json` — only those that exist, in that fixed order — taking the first 12
  characters of each and joining as `requirements:abc123def456,architecture:...`.

  ```bash
  git hash-object ai/sa/<slug>/requirements.json ai/sa/<slug>/architecture.json
  ```

  Outside a git repo fall back to `sha256sum` (PowerShell equivalent: `Get-FileHash -Algorithm SHA256`).
  Compare the one computed hash against the `inputs_hash:` recorded in **both** gates' latest verdict
  blocks — the newest `audit/audit-*.md` (`gate: sa-audit`) and the newest `audit/slop-*.md`
  (`gate: sa-slop`). Match → `fresh`; differ or absent → `stale`. Report the two separately and never
  blend them into one "gates" line: a fresh audit beside a stale slop scan is the exact state a reader
  needs to see, and an aggregate hides it. Match reports to gates by their `gate:` field, never by
  filename. Content-based, never mtime. Rendered `.md` files, `deliverables/`, `diagrams/`, `onepager/`
  and snapshots are excluded from the hash.
- **Review-model separation**: for each gate and review artifact present, note the `model:` its verdict
  block or report header recorded, if any. Report it beside the verdict — a same-model review is worth
  less than a cross-model one (`ARTIFACT-SCHEMAS.md §9`) and this is the only place a reader sees it
  without opening the report.
- **Staleness of rendered Markdown**: for each `<name>.json` present, note whether the paired `<name>.md`
  is missing. Report it; do not regenerate it.
</step>

<step name="recommend-next">
Recommend exactly one command, first match wins:

1. `engagement.json` missing or unreadable → `/sa:triage <slug>`.
2. A recorded gate verdict is `stale` → re-run that gate before anything downstream.
3. Any `to_clarify` blocking a `must`-priority requirement → `/sa:clarify <slug>`.
4. Otherwise the first missing artifact in the lane's pipeline order (§4.1), mapped to its command:

| Missing | Command | Lanes |
|---|---|---|
| `inputs/` empty, inbound files pending | `/sa:ingest` | all |
| `requirements.json` | `/sa:clarify` | all |
| `architecture.json` | `/sa:design` | `offer-sow`, `full-design` |
| `review.json` | `/sa:review` | `full-design` |
| `detailed-design.json` | `/sa:design-detail` | `full-design` |
| `risk-register.json` | `/sa:risk` | `offer-sow`, `full-design` |
| `estimation.json` | `/sa:estimate` | all |
| `estimate-review.json` | `/sa:estimate-review` | `offer-sow`, `full-design` |
| `offer.json` | `/sa:offer` | all |
| no fresh `sa-audit` verdict | `/sa:audit` | `offer-sow`, `full-design` |
| no fresh `sa-slop` verdict | `/sa:slop-check` | `offer-sow`, `full-design` |
| `deliverables/` empty | `/sa:package` | `offer-sow`, `full-design` |
| everything present | done — or `/sa:doc` for an internal consolidation, `/sa:onepager` for a management page | all |

Skip any row whose lane column doesn't include this engagement's lane. Diagrams have no `/sa:` command —
recommend `/diagram` where the design named diagrams that `diagrams/` doesn't contain.
</step>

<step name="output">
Emit exactly this, no extra commentary. Unknown field → `—`. Do not pad:

```
SA Engagement: <client> — <project>  (<slug>)
Lane:          <rom | offer-sow | full-design>
Phase:         <phase>  ·  last command <last command>
Last update:   <relative, e.g. "2 days ago">

Artifacts (lane expects <n>):
  requirements     <present rev <n> | missing>
  architecture     <present rev <n> | missing | n/a for this lane>
  ...              <one line per expected artifact, in lane pipeline order>
  brief (advisory) <present | not run — /sa:brief>
  screen (advisory)<present | not run — /sa:screen>
  onepager (adv.)  <types and versions present, or "not run — /sa:onepager">
  extra            <any present-but-unexpected artifact, or —>

Open items:
  to_clarify reqs  <n>
  open questions   <n engagement · n requirements>
  unrendered .md   <n or —>

Gates (both required by /sa:package):
  sa-audit:      <PASS | PASS-WITH-WAIVERS | BLOCKED | not-run> (<ts>, <fresh | stale — inputs changed>) [model: <m or —>]
  sa-slop:       <PASS | PASS-WITH-WAIVERS | BLOCKED | not-run> (<ts>, <fresh | stale — inputs changed>) [model: <m or —>]

Document profile: <name → template filename | none — deliverables will be unbranded>

Next: <one command> — <one-line rationale>
```

Add one further line **only when it applies**: if both gates pass but either recorded no `model:`, or
recorded the same model, print
`Note: <gate(s)> ran on the authoring model — consider a cross-model re-run before this goes out.`
Omit it entirely otherwise. A note that prints every time is a note nobody reads.
</step>
</process>

<rules>
- **Read-only.** No `Write`, no `Edit`, no repair, no gate re-run — report the problem and name the command
  that fixes it.
- **Counts, not analysis.** Never re-read requirements to judge their quality or restate design content;
  that is what the `req-*` agents are for.
- **Never guess a lane.** No `engagement.json` means no lane — say so and point at `/sa:triage`.
- **Exactly one recommendation.** A list of things the user could do next is not a recommendation.
</rules>
