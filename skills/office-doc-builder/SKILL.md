---
name: office-doc-builder
description: Reusable Excel/Word/PowerPoint formatting helpers (openpyxl/python-docx/python-pptx) for generating or reformatting office documents. Use when asked to create a formatted Excel spreadsheet, generate a Word document, build a PowerPoint deck, or make an existing table/document look properly styled — or when another skill needs document-formatting logic instead of rewriting styling boilerplate from scratch. Triggers on "create a formatted excel for X", "generate a word document with X", "build a powerpoint deck about X", "make this table look nice", "add a table of contents to this document".
---

> Version: 1.0.0

# Office Doc Builder

A library of tested, reusable formatting helpers — not a single workflow like `travel-planner`, closer to
a toolbox other scripts (and other skills) import from. The point is the same one that made
`travel-planner` reliable: formatting logic lives in tested code, not re-derived from prose on every
call. Minimize what's LLM-dependent — generate the *content* fresh each time, reuse the *formatting*.

## Library layout

```
lib\excel_helpers.py   openpyxl — styled headers, tables, totals/formulas, highlight cells, freeze panes
lib\word_helpers.py    python-docx — headings, a real TOC field, styled tables, page breaks, default font
lib\pptx_helpers.py    python-pptx — title/content/image slides, widescreen setup, speaker notes
```

Each module is self-contained and independently importable — a script generating only a Word doc doesn't
need to import the Excel or PPTX modules. Read the docstrings at the top of each file and each function's
own docstring before use; they document the exact parameters and any real limitations (e.g. `word_helpers
.add_toc`'s field-code behavior — see below).

## How to use this skill

1. **Don't write raw openpyxl/python-docx/python-pptx styling inline.** Import the relevant helper
   module(s) from this skill's `lib\` folder and call them — write a short script that's mostly *data*,
   with formatting delegated to the library.
2. **Extend the library, don't duplicate it**, when an existing helper is close but not quite right (a new
   color, a new table shape). Add a new function or parameter to the relevant module rather than writing
   one-off styling logic in the calling script — the next document benefits too.
3. **Test the generated file before presenting it as done** — open it programmatically and check the
   specific things that matter for the task (a formula's actual value/formula text, a fill color, that a
   TOC field structure is well-formed) rather than just confirming the save call didn't raise. This
   library's own functions were verified this way before being trusted (see the Q&A log entry this skill
   was built in).
4. **Know the real limitation of `word_helpers.add_toc`**: it inserts a genuine Word TOC field, but Word
   itself computes the actual entries/page numbers only when the field is refreshed inside Word (right-
   click → Update Field, or Word's own "update fields?" prompt on open) — this cannot be pre-rendered by
   the generation script, it depends on final pagination. Always tell the user this when handing over a
   document that used it; don't imply the TOC is already populated.

## When NOT to use this

If the actual hard part of the task is business logic specific to one domain (which categories, what
data goes where, project-specific rules) — build that as its own skill with its own bundled script, the
way `travel-planner` does, and have *that* script import from this library for the low-level formatting
only. This skill is deliberately generic — it should never accumulate project- or domain-specific facts.

## Rules

- Generic only — never add a hardcoded personal/project fact to any module here (a name, a path, a
  business category). If a task needs that, it belongs in the calling script or a domain-specific skill,
  not here.
- Prefer extending an existing function's parameters over adding a near-duplicate function.
- Every new helper function needs a docstring stating its parameters and any real limitation (as
  `add_toc` does) — not just what it does in the easy case.
