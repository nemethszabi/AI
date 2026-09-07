---
name: sa:package
description: Build the client-facing deliverable (DOCX/XLSX/PPTX) from an engagement's JSON artifacts, into the branded template a document profile resolves. Refuses to run without a fresh PASS from BOTH gates — /sa:audit (the artifacts agree by ID) and /sa:slop-check (the prose is grounded).
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

> Version: 2.0.0 — major: the gate now requires **two** verdicts (`sa-audit` and the new `sa-slop`), and
> builds into a branded template when a document profile resolves (`ARTIFACT-SCHEMAS.md §5, §8`).

<objective>
`/sa:package <slug> [type] [--mode=]` renders `ai/sa/<slug>/`'s JSON artifacts into the actual
client-facing files under `ai/sa/<slug>/deliverables/`, inside the engagement's branded document profile
where one applies (`sa-framework/ARTIFACT-SCHEMAS.md §8`).

This is the only command in the namespace that produces something a client sees, so it is the only one
with a hard gate — and that one gate now reads **two** verdicts, both of which must show `PASS` or
`PASS-WITH-WAIVERS` on a **matching `inputs_hash`** (§5):

| Verdict | From | Checks |
|---|---|---|
| `sa-audit` | `/sa:audit` | do the JSON artifacts agree with each other, by ID? |
| `sa-slop` | `/sa:slop-check` | is the prose a human will read grounded, consistent and free of machine-tells? |

Two gate **inputs**, still one refusal point. Neither substitutes for the other: an offer whose every ID
resolves can still quote an invented benchmark, and an offer with beautiful prose can still be missing a
`must` requirement. §5 records the split. Refusing to build from stale artifacts is correct behavior — per
`CONSTITUTION.md` Article III the fix is to re-run the gate, never to weaken it.
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

Read the newest `ai/sa/<slug>/audit/audit-*.md` **and** the newest `ai/sa/<slug>/audit/slop-*.md`, and take
the fenced ```` ```sa-verdict ```` block from each. Match them by their `gate:` field — `sa-audit` and
`sa-slop` — never by filename or by prose. A block with no `gate:`, or with an unrecognized one, counts as a
missing gate; never guess which gate a report belongs to.

All four conditions must hold:

1. `sa-audit` `verdict` is `PASS` or `PASS-WITH-WAIVERS`.
2. Its recorded `inputs_hash` matches the one just computed.
3. `sa-slop` `verdict` is `PASS` or `PASS-WITH-WAIVERS`.
4. Its recorded `inputs_hash` matches too.

Both gates hash the same input set, so one computation serves both comparisons.

If any fails, print and **abort**:

```
Cannot package — gate failed or stale:
  Audit (sa-audit): <verdict or "not run"> @ <timestamp>
                    <hash match | STALE — artifacts changed since the audit>
  Slop  (sa-slop):  <verdict or "not run"> @ <timestamp>  [ran on: <model>]
                    <hash match | STALE — artifacts changed since the scan>

Run <the failing command(s)>, then retry.
```

Name only the gates that actually failed — telling someone to re-run a gate that passed teaches them to
skim the message. When `sa-slop` passed but ran on the same model that wrote the artifacts, add one advisory
line (not a refusal): `slop scan ran on <model>, same family as the author — consider
/sa:slop-check <slug> --model=<other> before this goes out` (`ARTIFACT-SCHEMAS.md §9`).
</step>

<step name="read-context">
Read `engagement.json` for `deliverable_language`, `locale`, `currency`, `vendor_org`, `document_profile`,
`template_path` and `file_naming` (default `<ORG>-<YYYY>-<CLIENT>-<NNN>-<artifact>-v<NN>.<ext>`). Read every
`ai/sa/<slug>/*.json` artifact the requested types need.
</step>

<step name="resolve-template">
Resolve the branded shell for every DOCX type (`offer`, `hld`, `lld`), per `ARTIFACT-SCHEMAS.md §8`:

1. `engagement.json.template_path` is set and the file exists → use it. `/sa:triage` already resolved it.
2. Otherwise read `<config-root>/document-data/templates.yaml` — resolving `<config-root>` by
   `ARTIFACT-SCHEMAS.md §8`'s chain (`$CLAUDE_CONFIG_DIR`, then `~/.claude`, then the staged repo copy;
   never assume `~/.claude`, since three redirected roots exist) — find `engagement.json.document_profile`
   (or resolve it fresh by `deliverable_language` → `locales` → the org's `default_profile`), and use that
   profile's `template`, resolved relative to the yaml's own directory.
3. No `templates.yaml`, no matching profile, or a `template:` that doesn't resolve → build **unbranded**,
   and say so explicitly in the relay. Silent unbranded output is the failure this step exists to prevent —
   a document that quietly lost the client's branding looks like carelessness, and nobody notices until it
   has been sent.

`<ORG>` in `file_naming` comes from the org's `doc_id_prefix`; fall back to the vendor org's name in caps
only if no profile resolved.

**A profile is a shell, never content.** When one resolves, the rules in §8 bind this command absolutely:

- **Fill the template's placeholders; never restyle it.** Replace `[Document Title]`, `[Customer Name]`,
  `[Date]`, `[REF-YYYY-NNN]`, `[Author Name]` and the profile's other mapped placeholders from
  `engagement.json`. Fonts, colours, heading numbering, header and footer stay the template's. Do not apply
  `office-doc-builder`'s own styling on top of a branded template — that is precisely how a branded document
  ends up half-branded.
- **Keep `boilerplate_sections` verbatim.** Confidentiality statements, disclaimers and company
  introductions are approved legal and marketing text. Never regenerate, never reword, never translate them
  on the fly, and never trim them to save a page.
- **Write the engagement's content under `content_sections`**, and **delete `demo_sections`** — heading and
  body — since those are typography samples shipped with the shell.
- **Anything in none of the three lists is kept.** An unlisted section is a section somebody added
  deliberately; the cost of an unexpected extra section is that someone notices, the cost of a silently
  dropped one is that nobody does.
- **`deliverable_language` selects the profile; it does not authorize translation.** If the artifacts are in
  one language and the profile is another, stop and say so — a machine-translated client document is a
  decision for the human, not a side effect of packaging.

Patching a template in place needs the `document-skills` plugin, same constraint as `resolve-mode` below.
When it isn't available, `python-docx` can still open the template, fill placeholders and append content —
say in the relay which route was taken, since the two differ in what they preserve.
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
openpyxl/python-docx/python-pptx styling inline. **Where a template resolved, open it and fill it; apply the
helpers' styling only to content the template has no style for**, per `resolve-template` above.

- **`offer`** → DOCX from `offer.json`, sections in the order of `req-offer`'s own output template, written
  under the profile's `content_sections` where one applies.
- **`estimation-pack`** → XLSX from `estimation.json` + `rates.yaml` if one was used. **Read every total
  from `rollup`; never recompute one** (`ARTIFACT-SCHEMAS.md §4.7`) — the stored figures are the same ones
  the estimate document, the offer and the one-pager show, and a workbook that recomputes them is a fourth
  chance to round one number a fourth way.

  **Tab 1 Summary** — the estimate's own summary block, same rows in the same order
  (`ESTIMATION-METHOD.md §11.1`), each as best/likely/worst: Baseline → + Contingency (% and amount) →
  + Buffer → **= Committed total** (visually distinct, labelled *the figure quoted*) → Optional (labelled
  *not included above*) → = If all options taken (labelled **reference only — not a quote**) → Not
  estimated (`—` with a count, never `0`). Arithmetic rows carry real cell formulas, so the sum is
  checkable in the workbook rather than asserted by it.
  **Tab 2 Rollups** — by delivery phase, by work type (with the **non-build share** as an explicit
  percentage), by K-category. §11.2's three questions, answered without summing the line table.
  **Tab 3 Line items** — one row per `L-`, with REQ/component/QA citations, K-category, category and
  `scope_tier`. Baseline and optional rows visually separated, **never interleaved**, each subtotalling to
  its Tab 1 row.
  **Tab 4 Assumptions & exclusions** · **Tab 5 Coverage matrix** (REQ × component × line).

  If a `traditional` comparison figure exists (opt-in only, per `ESTIMATION-METHOD.md §2`), show it
  alongside `ai_assisted` in its own column, labelled "comparison — not the delivery model priced" —
  never merged into one column and never given equal visual weight to the AI-assisted figure.
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

Also report, every time: **which document profile was used, or that the build was unbranded and why**, and
**which model each gate ran on**. Both are things a reader would otherwise assume went well.

If `onepager/` is empty and this was an `offer` build, mention `/sa:onepager <slug> summary` — the
management page for the internal conversation the offer is about to start.
</step>
</process>

<rules>
- **No build without a fresh PASS from BOTH gates.** Refusal is correct, not pedantic — and the remedy is
  re-running `/sa:audit` and/or `/sa:slop-check`, never relaxing the check (`CONSTITUTION.md` Article III).
- **Gates are matched by their `gate:` field**, never by filename. A verdict block without one is a missing
  gate, not a gate to guess at.
- **A branded template is filled, never restyled**, and its `boilerplate_sections` are preserved verbatim
  (`ARTIFACT-SCHEMAS.md §8`).
- **Unbranded output is announced, never silent.** No profile resolved is a sentence in the relay, not an
  omission the reader discovers in Word.
- **Freshness is content-based.** Packaging's own outputs never re-stale the gate that permitted them.
- **Never overwrite a versioned deliverable** — increment `v<NN>`.
- **Patch never forces an unsafe edit.** Unmappable deltas are reported and skipped.
- **Say what didn't work.** A missing `mmdc`, an unavailable plugin, a skipped delta or a lost diacritic is
  reported plainly — never papered over to make the run look clean.
- **Never commit.** Deliverables are the human's to review and commit.
- **A rate card never appears in a client-facing file** — only the arithmetic consequences someone chose
  to show (`ESTIMATION-METHOD.md §7`).
</rules>
