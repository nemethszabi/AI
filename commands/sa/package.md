---
name: sa:package
description: Build the client-facing deliverable (DOCX/XLSX/PPTX) from an engagement's JSON artifacts. Refuses to run without a fresh PASS from /sa:audit.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - Skill
  - Agent
argument-hint: "<slug> [offer|estimation-pack|hld|lld|pitch|all] [--mode=auto|regenerate|patch]"
---

> Version: 1.0.0

<objective>
`/sa:package <slug> [type] [--mode=]` renders `ai/sa/<slug>/`'s JSON artifacts into the actual
client-facing files under `ai/sa/<slug>/deliverables/`.

This is the only command in the namespace that produces something a client sees, so it is the only one
with a hard gate: `/sa:audit` must show `PASS` or `PASS-WITH-WAIVERS` on a **matching `inputs_hash`**
(`sa-framework/ARTIFACT-SCHEMAS.md §5`). Refusing to build from stale artifacts is correct behavior —
per `CONSTITUTION.md` Article III the fix is to re-run the gate, never to weaken it.
</objective>

<process>
<step name="resolve-args">
Resolve the slug as `/sa:design` does. Then parse `$ARGUMENTS`:

**`type`** — `offer` (default), `estimation-pack`, `hld`, `lld`, `pitch`, or `all`. For `all`, build what
the lane in `engagement.json` calls for:

| Lane | `all` builds |
|---|---|
| `rom` | `offer` (light) |
| `offer-sow` | `offer` + `estimation-pack` |
| `full-design` | `offer` + `estimation-pack` + `hld` + `lld` + `pitch` |

**`--mode=`** — `auto` (default), `regenerate`, or `patch`. Resolve `auto` to a concrete mode now (see
`resolve-mode`) and report which was chosen.
</step>

<step name="gate-check">
Compute `inputs_hash` fresh, per `ARTIFACT-SCHEMAS.md §5`: `git hash-object` over whichever of
`requirements.json`, `architecture.json`, `estimation.json`, `risk-register.json`, `offer.json` exist,
first 12 characters each, joined in that fixed order. Outside a git repo, fall back to `sha256sum`.
Content-based — **never** mtimes. Exclude rendered `.md`, `deliverables/`, `diagrams/` and snapshots.

Read the newest `ai/sa/<slug>/audit/audit-*.md` and its fenced ```` ```sa-verdict ```` block. Both must
hold:

1. `verdict` is `PASS` or `PASS-WITH-WAIVERS`.
2. Its recorded `inputs_hash` matches the one just computed.

If either fails, print and **abort**:

```
Cannot package — gate failed or stale:
  Audit: <verdict or "no audit found"> @ <timestamp>
         <hash match | STALE — artifacts changed since the audit>

Run /sa:audit <slug>, then retry.
```
</step>

<step name="read-context">
Read `engagement.json` for `deliverable_language`, `locale`, `currency`, `template_path` and
`file_naming` (default `<ORG>-<YYYY>-<CLIENT>-<NNN>-<artifact>-v<NN>.<ext>`). Read every
`ai/sa/<slug>/*.json` artifact the requested types need.
</step>

<step name="render-diagrams">
If `ai/sa/<slug>/diagrams/*.mmd` exist and their `.png` is missing or older, render via `mmdc`. If `mmdc`
isn't installed, skip with a warning and note that affected figures will be referenced but absent — never
silently omit a figure the document's text refers to.
</step>

<step name="resolve-mode">
For each requested type find the highest existing `v<NN>` in `deliverables/`.

- `regenerate` → always build fresh.
- `patch` → requires both a prior version **and** its snapshot at
  `deliverables/.snapshots/<type>-v<NN>.json`. Missing either → fall back to `regenerate` and say so.
- `auto` → `patch` when a prior version and its snapshot both exist, else `regenerate`.

**Capability constraint, stated honestly**: the first-party `office-doc-builder` skill only ever writes
fresh files — it cannot patch an existing document in place. Real patch mode therefore requires the
`document-skills` plugin (`docx`/`xlsx`/`pptx`), per that skill's own escalation path. If `patch` is
requested and the plugin isn't available, fall back to `regenerate` and tell the user plainly that
comments, tracked changes and manual formatting in the prior version will not carry over.
</step>

<step name="build-regenerate" condition="mode == regenerate">
Use the `office-doc-builder` skill's `lib\` helpers — import them, don't write raw
openpyxl/python-docx/python-pptx styling inline.

- **`offer`** → DOCX from `offer.json`, sections in the order of `req-offer`'s own output template.
- **`estimation-pack`** → XLSX from `estimation.json` + `rates.yaml` if one was used:
  Tab 1 Summary (best/likely/worst, contingency and buffer shown separately) ·
  Tab 2 Line items (one row per `L-`, with its REQ/component/QA citations and K-category) ·
  Tab 3 Assumptions & exclusions · Tab 4 Coverage matrix (REQ × component × line).
  Where both delivery models were estimated, show them side by side — never merge them into one column.
- **`hld`** → DOCX from `architecture.json`. **`lld`** → DOCX from `detailed-design.json`.
- **`pitch`** → PPTX, 8–12 slides: Title · Their objectives · Our understanding · Solution · Delivery ·
  Investment · Risks & controls · Next steps.

Write to `deliverables/` under the engagement's naming convention.
</step>

<step name="build-patch" condition="mode == patch">
Diff the current artifacts against `deliverables/.snapshots/<type>-v<NN>.json` to produce a concrete
change list. Map each change to a section/table/cell, apply the minimal edit via the `document-skills`
plugin preserving surrounding formatting and tracked changes, recompute derived totals and coverage
tables, and append a revision-history row.

Save as `v<NN+1>`. **Never overwrite a prior version.**

If a delta can't be mapped cleanly to a location, skip it and report:
`"Delta X cannot be patched safely — re-run this type with --mode=regenerate."` A half-patched
deliverable is worse than a clean regenerate.
</step>

<step name="verify-output">
Open each generated file programmatically and check what actually matters before calling it done — that
totals carry the values `estimation.json` holds, that diacritics survived the round-trip, that no figure
reference points at a diagram that failed to render. A save call that didn't raise is not verification.

If the document uses a Word TOC field, tell the user it populates only when Word refreshes the field —
don't imply it's already filled in.
</step>

<step name="save-snapshot">
Write `deliverables/.snapshots/<type>-v<NN>.json` bundling the artifacts that drove this build, so the
next `patch` run has a baseline. Never delete an old snapshot — each pairs with its version.
</step>

<step name="update-state">
Update `STATE.md` in the canonical shape from `sa-framework/ARTIFACT-SCHEMAS.md §6`: phase `package`,
last command `/sa:package`, next `/sa:status`. Record what was built, at which version, via which mode in
the appended phase-history line. Append; never rewrite prior lines.
</step>

<step name="relay">
Report each file built with its version and size, the mode used, the locale, diagrams rendered, any
deltas skipped, and any verification finding.
</step>
</process>

<rules>
- **No build without a fresh gate PASS.** Refusal is correct, not pedantic — and the remedy is re-running
  `/sa:audit`, never relaxing the check (`CONSTITUTION.md` Article III).
- **Freshness is content-based.** Packaging's own outputs never re-stale the gate that permitted them.
- **Never overwrite a versioned deliverable** — increment `v<NN>`.
- **Patch never forces an unsafe edit.** Unmappable deltas are reported and skipped.
- **Say what didn't work.** A missing `mmdc`, an unavailable plugin, a skipped delta or a lost diacritic is
  reported plainly — never papered over to make the run look clean.
- **Never commit.** Deliverables are the human's to review and commit.
- **A rate card never appears in a client-facing file** — only the arithmetic consequences someone chose
  to show (`ESTIMATION-METHOD.md §7`).
</rules>
