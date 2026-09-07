---
name: sa:onepager
description: Compose a dense single-page management one-pager (summary / roadmap / estimate / timeline / architecture) from an engagement's artifacts, via req-onepager — self-contained A4-landscape HTML, rendered to PDF. Advisory; gates nothing.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<slug> [summary|roadmap|estimate|timeline|architecture|all] [--lang=<language>] [--model=sonnet|opus|haiku|fable] [--no-pdf]"
---

> Version: 1.0.0

<objective>
`/sa:onepager <slug> [type]` composes a one-page landscape document for people who will not read the full
artifacts — a manager, a sales lead, a steering committee — via `req-onepager`, writing self-contained HTML
to `ai/sa/<slug>/onepager/<type>-v<NN>.html` and rendering it to a matching `.pdf`.

Five page types, each a fixed layout over a specific artifact set: `summary` (the ask, the number, the
decisions), `roadmap` (what ships when, and what each package is worth), `estimate` (where the number comes
from, line by line), `timeline` (when it lands and what must be true by when), `architecture` (who does
what, and where the chain can break). Default is `summary`.

**Advisory — this gates nothing and nothing is built from it** (`sa-framework/ARTIFACT-SCHEMAS.md §6`). It
is not exempt from groundedness, though: every figure cites the artifact it came from, an untraceable figure
is printed as a named gap rather than filled, and `/sa:slop-check` scans the output as client-facing text.
</objective>

<process>
<step name="parse-args">
Parse and strip, in any order, before slug resolution:

- **`type`** — `summary` (default), `roadmap`, `estimate`, `timeline`, `architecture`, or `all`.
- **`--lang=<language>`** — the page's language. Optional; defaults to
  `engagement.json.deliverable_language`. Worth reaching for: a management one-pager is frequently wanted in
  your own working language even when the client-facing offer is in another, and only you know which meeting
  this page is for.
- **`--model=<value>`** — `sonnet` | `opus` | `haiku` | `fable`. Optional, per-invocation only. Composition
  is judgment-heavy (what to lead with, what to merge when it doesn't fit), so a stronger model is worth it
  on a page going to a steering committee. Reject an invalid value rather than ignoring it.
- **`--no-pdf`** — write the HTML and skip rendering. Use it when iterating on content.
</step>

<step name="resolve-slug">
Same resolution as `/sa:design`: explicit argument if it names an existing `ai/sa/<slug>/`, else glob
`ai/sa/*/engagement.json` (exactly one → use it; multiple → ask via `AskUserQuestion` which topic; none →
tell the user to run `/sa:triage` first).
</step>

<step name="check-preconditions">
Check the requested type's required artifacts against `req-onepager`'s own table:

| Type | Requires |
|---|---|
| `summary` | `engagement.json`, `requirements.json` |
| `roadmap` | `estimation.json` |
| `estimate` | `estimation.json`, `requirements.json` |
| `timeline` | `architecture.json` (with `phasing[]`) |
| `architecture` | `architecture.json` |

Missing → stop and name the command that produces it (`/sa:clarify`, `/sa:estimate`, `/sa:design`). Do not
dispatch: a page composed around a hole is the one output of this pipeline most likely to be shown to
someone who cannot tell.

For `all`, report which types will be composed and which are skipped for missing artifacts, then proceed
with the composable ones.
</step>

<step name="dispatch">
Dispatch to `req-onepager` via `Agent`. Give it the resolved slug and project path, the page type(s), the
resolved language and where it came from, and the config root so it can find
`document-data/templates.yaml` for the brand palette and document-ID prefix. If `--model` was parsed, pass
it as the `Agent` dispatch's `model` parameter — per-invocation only, never written into the agent's own
frontmatter.
</step>

<step name="render-pdf" condition="not --no-pdf">
Render each HTML the agent wrote to a sibling `.pdf` using headless Chromium. Verified working on this
machine 2026-09-07 with Edge; the flags matter and are not interchangeable:

```bash
"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --headless=new --disable-gpu \
  --user-data-dir="<a temp dir>" \
  --no-pdf-header-footer \
  --print-to-pdf="<out>.pdf" "file:///<absolute-path-to>.html"
```

Four things learned the hard way, all of which produce a silent failure if skipped:

1. **`--user-data-dir` is required.** Without it the run exits `0` and writes nothing when a normal browser
   profile is already in use.
2. **The exit code is not the result.** Edge returns before the file is flushed. **Poll for the output file**
   (up to ~15s) and treat the run as failed only if it never appears — never report success on exit code
   alone.
3. **`--no-pdf-header-footer`** suppresses the browser's own URL/date furniture, which otherwise prints over
   the layout.
4. **The input must be a `file:///` URL with an absolute path**, forward slashes, drive letter included.

Fall back to Chrome at `C:/Program Files/Google/Chrome/Application/chrome.exe` if Edge is absent. If neither
exists, **do not fail the command** — the HTML is the real artifact. Say plainly that no Chromium was found,
name the HTML path, and tell the user to open it and print to PDF (`Ctrl+P` → Save as PDF → Landscape →
Margins: None → Background graphics: on).
</step>

<step name="verify-output">
Confirm each PDF exists and is non-trivial (> 5 KB), then check the one thing that actually breaks: **that it
is a single page.** A two-page PDF means the HTML overflowed and the layout is wrong, not merely long.

Report a multi-page result plainly and tell the user to re-run — never hand over a "one-pager" that is two
pages. If `--no-pdf` was passed, skip this step and say the fit was not verified, since fit can only be
checked by rendering.
</step>

<step name="update-state">
Update `ai/sa/<slug>/STATE.md`: set `Last command` to `/sa:onepager` and the current timestamp, and append
one phase-history line naming the type(s) and version(s) written.

**Leave `Phase` and `Next` exactly as they were.** `onepager` is not a value in the §6 phase enum and this
command advances nothing — it is an advisory non-artifact, like `/sa:brief` and `/sa:screen`, and making the
pipeline look further along because someone printed a page would be a lie about state. If `Next` is empty,
set it to `/sa:status <slug>`.
</step>

<step name="relay">
Return, per page composed: the type, both file paths, the page language and whether it came from `--lang` or
`deliverable_language`, whether a brand profile resolved and which, and the basis line naming the artifacts
and revisions the page was built from.

Then relay the two things the reader needs before taking this into a room:

- **Every figure the agent printed as a gap**, with the artifact that would fill it. These are the questions
  the page will get asked.
- **Anything merged or trimmed to make it fit**, so nobody assumes the page is the complete line list.

If the agent's summary ends with a `## Blocking questions` section, put those to the user via
`AskUserQuestion` — the usual ones are which audience the page is for (and therefore its language) and
whether a cost figure may appear at all. The agent cannot ask: `AskUserQuestion` does not exist inside a
dispatched agent.

Finally, if `offer.json` exists and no fresh `sa-slop` verdict does, mention that `/sa:slop-check <slug>`
also scans one-pagers as client-facing text — worth running before this page leaves the building.
</step>
</process>

<rules>
- **Thin dispatcher only.** All composition and layout happens inside `req-onepager`; this command resolves
  arguments, renders the PDF, and verifies the fit.
- **Advisory, and it stays advisory.** Never set `Phase`, never set `Next` to itself, never let a one-pager
  satisfy a precondition for anything (`ARTIFACT-SCHEMAS.md §6`).
- **Never overwrite a prior version** — `v<NN>` increments. The version someone carried into a meeting has
  to stay recoverable.
- **The HTML is the artifact; the PDF is a rendering.** A missing Chromium is a warning, never a failure.
- **Never report a multi-page PDF as a one-pager.**
- **Effort, not price** — a cost figure appears only when a rate card was used, labelled as arithmetic on
  effort × rate, and the rate card itself never appears (`ESTIMATION-METHOD.md §5, §7`).
- **Never commit.** Writing artifacts is this pipeline's job; committing them is the human's.
</rules>
