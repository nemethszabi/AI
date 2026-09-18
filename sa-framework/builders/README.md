# sa-framework/builders

Deterministic renderers that turn an engagement's JSON artifacts into the files a client receives.
Governed by `../RENDERING-CONTRACT.md`; run by `/sa:package`.

## Usage

```bash
python build.py <engagement-dir> [--type offer|estimation-pack|all] [--pdf]
                                 [--version NN] [--out DIR] [--dry-run] [--json]
```

A whole engagement builds in a few seconds. Add `--pdf` and it takes about half a minute, because
Word is driven to compute the table-of-contents field and export the PDF.

Exit status is 0 when something usable was produced, even with findings — findings are reported, not
fatal. Non-zero means no deliverable was written and the report says why.

## Modules

| File | Does |
|---|---|
| `build.py` | CLI, artifact loading, version and reference resolution, reporting |
| `validate.py` | Schema preflight — fails in milliseconds with an actionable message |
| `profiles.py` | Render-profile and document-profile resolution, inheritance, section merging |
| `offer_docx.py` | The client offer |
| `estimation_xlsx.py` | The estimation workbook |
| `diagram.py` | Component view and timeline chart, white background, Pillow only |
| `docx_shell.py` | Branded-template handling: placeholders, demo-section removal, version, TOC field |
| `pdf.py` | Field refresh and PDF export via Word, with a LibreOffice fallback |
| `common.py` | Number formatting, config-root resolution, config loading, leak detection |

## Dependencies

`python-docx`, `openpyxl`, `Pillow`. `PyYAML` is used when present and a minimal reader covers the
config subset when it is not. `pywin32` plus Word enables `--pdf`; without them the DOCX is still
produced and the report says the contents page is unpopulated.

Nothing here requires Node, Mermaid or a network connection.

## Testing

```bash
python tests/make_fixture.py          # regenerate the fixture engagement
python build.py tests/fixture --out /tmp/out --pdf
```

The fixture is a realistic invented engagement — 23 estimate lines, five phases, both scope tiers, a
decomposed contingency, a risk register the offer cites. It exercises every diagram tier and every
workbook sheet. No real client material is checked into the framework.

Verify the output rather than the exit code. The specific things worth opening a build to check:

- the effort table's rows add up to the row labelled as their total
- the contents page lists sections starting at 1 and does not list itself
- the component diagram has a white background and no crossing edges
- the workbook's baseline subtotal reconciles to the Summary sheet
- `worst` appears in no sheet and no hidden column

## Adding to this

Extend a module; do not write a one-off script beside an engagement's artifacts. The reason this
package exists is that ad-hoc build scripts accumulated in one engagement folder until there were
eleven of them, each encoding a slightly different idea of what the deliverable should look like.

A client-specific difference is a **render profile**, never a branch in this code. A brand difference
is a **document profile**. If neither fits, the shape being asked for probably belongs in
`RENDERING-CONTRACT.md` first.
