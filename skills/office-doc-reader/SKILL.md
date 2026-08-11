---
name: office-doc-reader
description: Extract Excel/Word file content to Markdown for an agent to read and cite — the read-side counterpart to office-doc-builder (which only writes/formats). Use when an inbound .xlsx/.xls or .docx file needs its content turned into text before an agent can analyze it, e.g. ingesting a client's existing estimate spreadsheet or design document. Triggers on "read this excel file", "extract this Word document", "ingest this spreadsheet/document", "what's in this .xlsx/.docx".
---

> Version: 1.0.0

# Office Doc Reader

Mechanical extraction only — turns an existing `.xlsx`/`.docx` file into Markdown text so an agent's
`Read` tool (which does not parse spreadsheet/Word internals) can consume it. Does **not** interpret what
the content means — that's the job of whatever agent reads the extracted Markdown afterward.

For `.pdf` files, don't use this skill — Claude's built-in `Read` tool already extracts PDF text directly
(use the `pages` parameter for anything over 10 pages). This skill exists specifically for the two formats
`Read` cannot parse on its own.

## Library layout

```
lib\excel_reader.py   openpyxl — every worksheet → a Markdown table, formulas as last-calculated values
lib\word_reader.py    python-docx — paragraphs + tables in original document order → Markdown, headings preserved
```

Each script is both an importable module (`extract_xlsx_to_markdown(path)` /
`extract_docx_to_markdown(path)`, each returning `(markdown_text, warnings_list)`) and a standalone CLI:

```bash
python lib/excel_reader.py <input.xlsx> <output.md>
python lib/word_reader.py <input.docx> <output.md>
```

## How to use this skill

1. **Run the CLI form via Bash** for a straight file-to-file extraction — this is the common case and
   needs no Python code of your own. Check the script's stdout for a `WARNINGS:` block (e.g. a truncated
   sheet, or a document with no extractable text) and carry those warnings into whatever report you're
   producing — don't silently drop them.
2. **Import the functions instead** only when you need to post-process the text before writing it (e.g.
   prepending a provenance header) rather than writing the raw extraction straight to disk.
3. **Never treat the extraction as authoritative interpretation.** A Markdown table pulled from a
   spreadsheet is still just the spreadsheet's raw cells — whether a given row is a real requirement, a
   stale draft, or a formatting artifact is a judgment call for the downstream agent, not this skill.

## Known limitations (state these explicitly when handing off extracted content)

- **Merged cells** (Excel): openpyxl reports the value only in the merged range's top-left cell; the rest
  of the range reads blank in the extracted table, same as a plain read of the file would show.
- **Images, text boxes, footnotes/endnotes** (Word): not extracted — only body paragraphs and tables. A
  document that relies on these for meaning will read as incomplete.
- **Charts, pivot tables, embedded objects** (Excel): not extracted — only cell values.
- **No OCR.** A scanned document saved as `.docx`/`.xlsx` with no real text layer extracts as empty; the
  script's warning mechanism flags this rather than returning silently blank output.

## When NOT to use this

If the task is *generating* a new formatted Excel/Word/PowerPoint file rather than reading an existing
one, use `office-doc-builder` instead — this skill only reads.

## Escalation path — when this isn't enough

Start here. This skill is a zero-dependency, always-available baseline — no plugin install, no network
fetch, just `openpyxl`/`python-docx` already present in this environment. It covers the common case:
readable text and tables in a normal `.xlsx`/`.docx` file.

If you hit one of its documented limitations for real — a **scanned document with no text layer** (needs
OCR), a **legacy `.doc` binary** (not parseable by `python-docx` at all), or content genuinely requiring
deeper structural fidelity than paragraphs+tables — check whether the `document-skills` plugin
(`anthropic-agent-skills` marketplace, skills `docx`/`xlsx`/`pptx`/`pdf`) is installed and use its matching
skill instead for that one file. It's a heavier, source-available (not open-source) dependency from
Anthropic's own [anthropics/skills](https://github.com/anthropics/skills) repo — worth it specifically for
OCR and edge-case fidelity, not a blanket replacement for this skill's common-case path. Don't reach for it
by default; reach for it when this skill's own warning output tells you why it fell short.

## Rules

- Generic only — never add a hardcoded personal/project fact to either module. Extraction logic stays
  format-specific, not domain-specific.
- Extraction is mechanical and lossy by nature (see limitations above) — always surface warnings rather
  than presenting output as a complete, faithful copy of the source.
