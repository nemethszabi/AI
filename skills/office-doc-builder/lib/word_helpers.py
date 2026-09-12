"""
Reusable python-docx formatting helpers - generalized so future Word-generating skills/scripts don't
re-derive the same boilerplate each time.

Requires: python-docx (pip install python-docx). Note the import name is "docx", not "python_docx".
"""

import os
import re

from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT


def add_heading_styled(doc, text, level=1):
    """Thin wrapper over doc.add_heading - exists so every heading in a generated document goes through
    one place, in case a consistent style tweak is needed later across many scripts."""
    return doc.add_heading(text, level=level)


def add_toc(doc):
    """Inserts a real Word TOC field (not a static list of headings). IMPORTANT LIMITATION, not a bug:
    Word computes TOC page numbers/entries only when the field is refreshed inside Word itself - python-
    docx cannot pre-render the final content, since that depends on final pagination. The field is
    inserted correctly and will show a placeholder until the user opens the document in Word and does
    Right-click -> Update Field (or press F9, or Word will often prompt automatically on open with
    'This document contains fields that may refer to other files... update?'). Always tell the user this
    when handing over a document that used this helper - don't imply the TOC is already populated.
    """
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    r_element = run._r

    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")

    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = 'TOC \\o "1-3" \\h \\z \\u'

    fld_separate = OxmlElement("w:fldChar")
    fld_separate.set(qn("w:fldCharType"), "separate")

    placeholder = OxmlElement("w:t")
    placeholder.text = "Right-click and choose Update Field to generate the table of contents."

    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")

    r_element.append(fld_begin)
    r_element.append(instr_text)
    r_element.append(fld_separate)
    r_element.append(placeholder)
    r_element.append(fld_end)
    return paragraph


def add_table_styled(doc, headers, rows, style="Light Grid Accent 1", markdown=False,
                     font_pt=None, repeat_header=True, col_widths_cm=None):
    """Adds a table with a header row (bold) plus data rows, using one of Word's built-in table styles
    by name (default: a clean grid style available in the default template).

    headers: list of strings. rows: list of lists of cell values (converted to str).
    markdown: if True, cell text is parsed for inline markdown (**bold**, *italic*, `code`, links) via
        add_markdown_runs instead of being inserted literally. Header cells stay bold either way.
    font_pt: if set, applies this point size to every run in the table - useful for wide tables that
        would otherwise overflow the page.
    repeat_header: if True, marks the header row to repeat at the top of each page the table spans.
        Word only honors this for tables that actually break across pages.
    col_widths_cm: optional list of column widths in centimetres, one per column. Word ignores cell
        widths unless autofit is off, so this also disables autofit. Pass None to let Word size them.

    Returns the created table.
    """
    table = doc.add_table(rows=1, cols=len(headers))
    try:
        table.style = style
    except KeyError:
        # Style name not present in this template - fall back to the default rather than raising,
        # since the table content itself still matters more than the exact style name matching.
        pass
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        _fill_cell(header_cells[i], h, markdown=markdown, bold=True)
    for row_values in rows:
        cells = table.add_row().cells
        for i, v in enumerate(row_values):
            if i < len(cells):
                _fill_cell(cells[i], v, markdown=markdown)
    if col_widths_cm:
        table.autofit = False
        for row in table.rows:
            for i, w in enumerate(col_widths_cm):
                if i < len(row.cells):
                    row.cells[i].width = Cm(w)
    if font_pt:
        set_table_font_size(table, font_pt)
    if repeat_header:
        set_repeat_table_header(table.rows[0])
    return table


def _fill_cell(cell, value, markdown=False, bold=False):
    """Writes a value into a table cell, replacing the cell's existing empty paragraph. Supports
    multi-line cell content by splitting on newline into separate paragraphs."""
    text = "" if value is None else str(value)
    paragraph = cell.paragraphs[0]
    for i, line in enumerate(text.split("\n")):
        p = paragraph if i == 0 else cell.add_paragraph()
        if markdown:
            add_markdown_runs(p, line, bold=bold)
        else:
            run = p.add_run(line)
            run.bold = bold


def set_table_font_size(table, size_pt):
    """Applies a point size to every run in an existing table, including cells added later only if
    called after they exist. Runs with no explicit size inherit the style otherwise."""
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(size_pt)


def set_repeat_table_header(row):
    """Marks a table row as a header row that repeats on each page the table spans. LIMITATION: Word
    applies this only when the table actually breaks across a page boundary, and never for rows after
    the first contiguous block of header rows."""
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)
    return row


def set_cell_shading(cell, hex_color):
    """Sets a table cell's background fill. hex_color: 'RRGGBB' without the leading '#'."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color.lstrip("#"))
    tc_pr.append(shd)
    return cell


def add_page_break(doc):
    doc.add_page_break()


def set_default_font(doc, name="Calibri", size_pt=11):
    """Sets the document's Normal style font - affects all text using the default style, applied once
    near the top of a generation script rather than per-run."""
    style = doc.styles["Normal"]
    style.font.name = name
    style.font.size = Pt(size_pt)


def center_paragraph(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

def set_margins(doc, top_cm=2.0, bottom_cm=2.0, left_cm=2.0, right_cm=2.0, section_index=None):
    """Sets page margins in centimetres. section_index=None applies to every section in the document."""
    sections = doc.sections if section_index is None else [doc.sections[section_index]]
    for s in sections:
        s.top_margin = Cm(top_cm)
        s.bottom_margin = Cm(bottom_cm)
        s.left_margin = Cm(left_cm)
        s.right_margin = Cm(right_cm)


def content_width_in(doc, section_index=0):
    """Usable text width in inches (page width minus left/right margins) - the correct max width for a
    full-bleed image, since python-docx will happily insert one wider than the page."""
    s = doc.sections[section_index]
    return (s.page_width - s.left_margin - s.right_margin) / 914400.0


def content_height_in(doc, section_index=0):
    """Usable text height in inches (page height minus top/bottom margins)."""
    s = doc.sections[section_index]
    return (s.page_height - s.top_margin - s.bottom_margin) / 914400.0


def add_page_number_footer(doc, text_prefix="", section_index=None):
    """Adds a centred 'prefix N' page-number field to the section footer. The number is a real Word
    PAGE field, so it renumbers correctly; like any field it is computed by Word, not by this script."""
    sections = doc.sections if section_index is None else [doc.sections[section_index]]
    for s in sections:
        p = s.footer.paragraphs[0] if s.footer.paragraphs else s.footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if text_prefix:
            p.add_run(text_prefix)
        run = p.add_run()
        for kind, val in (("begin", None), ("instr", "PAGE"), ("end", None)):
            if kind == "instr":
                el = OxmlElement("w:instrText")
                el.set(qn("xml:space"), "preserve")
                el.text = val
            else:
                el = OxmlElement("w:fldChar")
                el.set(qn("w:fldCharType"), kind)
            run._r.append(el)
    return doc


def add_horizontal_rule(doc):
    """A thin full-width rule, drawn as an empty paragraph with a bottom border (Word has no native
    horizontal-rule object in the python-docx API)."""
    p = doc.add_paragraph()
    p_pr = p._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "BFBFBF")
    borders.append(bottom)
    p_pr.append(borders)
    p.paragraph_format.space_after = Pt(6)
    return p


def add_caption(doc, text, italic=True, size_pt=9, color="808080"):
    """A centred small-grey caption paragraph, for use under a figure or table."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.italic = italic
    run.font.size = Pt(size_pt)
    run.font.color.rgb = RGBColor.from_string(color)
    return p


def add_image_fitted(doc, path, max_width_in, max_height_in=None, center=True):
    """Inserts a picture scaled to fit inside a width/height box, preserving aspect ratio. python-docx
    scales the other dimension automatically when only one is given, so this adds the second pass that
    catches tall images which would otherwise overflow the page. Returns the InlineShape, or None if
    the file is missing (missing images are skipped rather than raising, so one broken path doesn't
    abort a long document build)."""
    if not os.path.isfile(path):
        return None
    p = doc.add_paragraph()
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    shape = run.add_picture(path, width=Inches(max_width_in))
    if max_height_in and shape.height > Inches(max_height_in):
        ratio = Inches(max_height_in) / float(shape.height)
        shape.height = Inches(max_height_in)
        shape.width = int(shape.width * ratio)
    return shape


def add_hyperlink(paragraph, text, url, color="0563C1", underline=True):
    """Adds a real clickable external hyperlink run. python-docx has no public API for this, so the
    relationship is created directly on the part. Returns the w:hyperlink element."""
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), r_id)
    run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    if color:
        c = OxmlElement("w:color")
        c.set(qn("w:val"), color)
        r_pr.append(c)
    if underline:
        u = OxmlElement("w:u")
        u.set(qn("w:val"), "single")
        r_pr.append(u)
    run.append(r_pr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    run.append(t)
    link.append(run)
    paragraph._p.append(link)
    return link


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

_INLINE_RE = re.compile(
    r"(?P<strike>~~(?P<strike_t>.+?)~~)"
    r"|(?P<bold>\*\*(?P<bold_t>.+?)\*\*)"
    r"|(?P<code>`(?P<code_t>[^`]+)`)"
    r"|(?P<link>\[(?P<link_t>[^\]]*)\]\((?P<link_u>[^)]*)\))"
    r"|(?P<ital>\*(?!\*)(?P<ital_t>(?:[^*\n]|\*\*[^*\n]*\*\*)+?)\*(?!\*))",
    re.S,
)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_IMAGE_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
_HR_RE = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
_BULLET_RE = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_NUM_RE = re.compile(r"^(\s*)\d+[.)]\s+(.*)$")
_QUOTE_RE = re.compile(r"^\s*>\s?(.*)$")
_TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:\-|]+\|[\s:\-|]*$")


def add_markdown_runs(paragraph, text, bold=False, italic=False, code=False, strike=False,
                      code_font="Consolas", code_color="C7254E"):
    """Parses inline markdown in `text` and appends the corresponding runs to `paragraph`.

    Supports **bold**, *italic*, `code`, ~~strikethrough~~ and [label](url) links, including nesting
    (e.g. a link inside bold). Underscore emphasis is deliberately NOT supported: identifiers such as
    campaign_id would otherwise be mangled, which is the more common case in technical documents.
    The bold/italic/code/strike arguments set the starting state and are what makes nesting work.
    """
    if not text:
        return paragraph
    pos = 0
    for m in _INLINE_RE.finditer(text):
        if m.start() > pos:
            _add_plain_run(paragraph, text[pos:m.start()], bold, italic, code, strike,
                           code_font, code_color)
        if m.group("bold") is not None:
            add_markdown_runs(paragraph, m.group("bold_t"), True, italic, code, strike,
                              code_font, code_color)
        elif m.group("strike") is not None:
            add_markdown_runs(paragraph, m.group("strike_t"), bold, italic, code, True,
                              code_font, code_color)
        elif m.group("code") is not None:
            _add_plain_run(paragraph, m.group("code_t"), bold, italic, True, strike,
                           code_font, code_color)
        elif m.group("link") is not None:
            url = m.group("link_u") or ""
            label = m.group("link_t") or url
            if url.startswith(("http://", "https://", "mailto:")):
                add_hyperlink(paragraph, label, url)
            else:
                # Relative/in-repo path: keep it readable as text rather than making a dead link.
                _add_plain_run(paragraph, label, bold, italic, True, strike, code_font, code_color)
        elif m.group("ital") is not None:
            add_markdown_runs(paragraph, m.group("ital_t"), bold, True, code, strike,
                              code_font, code_color)
        pos = m.end()
    if pos < len(text):
        _add_plain_run(paragraph, text[pos:], bold, italic, code, strike, code_font, code_color)
    return paragraph


def _add_plain_run(paragraph, text, bold, italic, code, strike, code_font, code_color):
    if not text:
        return
    run = paragraph.add_run(text)
    run.bold = bold or None
    run.italic = italic or None
    if strike:
        run.font.strike = True
    if code:
        run.font.name = code_font
        # East-Asian font attribute must be set too or Word may substitute for non-ASCII runs.
        r_pr = run._r.get_or_add_rPr()
        r_fonts = r_pr.find(qn("w:rFonts"))
        if r_fonts is None:
            r_fonts = OxmlElement("w:rFonts")
            r_pr.append(r_fonts)
        r_fonts.set(qn("w:eastAsia"), code_font)
        if code_color:
            run.font.color.rgb = RGBColor.from_string(code_color)
    return run


def split_markdown_row(line):
    """Splits one markdown table row into cell strings, honouring backslash escapes and inline code
    spans. A naive line.split('|') breaks on any row containing a pipe inside a `code span`, silently
    shifting every column after it - which is why this exists."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, buf, in_code, i = [], "", False, 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s):
            buf += s[i + 1]
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
            buf += ch
            i += 1
            continue
        if ch == "|" and not in_code:
            cells.append(buf.strip())
            buf = ""
            i += 1
            continue
        buf += ch
        i += 1
    cells.append(buf.strip())
    return cells


def _is_structural(line):
    s = line.strip()
    if not s:
        return True
    return bool(
        _HEADING_RE.match(s)
        or _IMAGE_RE.match(s)
        or _HR_RE.match(s)
        or _BULLET_RE.match(line)
        or _NUM_RE.match(line)
        or _QUOTE_RE.match(line)
        or s.startswith("|")
    )


def add_markdown(doc, md_text, base_dir=None, heading_offset=0, table_style="Light Grid Accent 1",
                 table_font_pt=9, image_captions=False, max_image_height_in=None,
                 skip_first_heading=False, code_font="Consolas", quote_shading="F2F2F2"):
    """Renders a Markdown string into an existing python-docx Document.

    Handles: ATX headings, paragraphs (with soft-wrapped lines joined), pipe tables, images, bullet and
    numbered lists, blockquotes, horizontal rules, and all inline markup add_markdown_runs supports.

    base_dir: directory that relative image paths resolve against (defaults to the process cwd).
    heading_offset: added to every heading level, for nesting a whole document under a parent heading.
        Levels are clamped to Word's 1-9 range.
    image_captions: if True, an image's alt text is emitted as a caption below it. Off by default
        because many documents already write their own caption line after the image.
    max_image_height_in: cap on image height; defaults to ~85% of the usable text height.
    skip_first_heading: drops the document's first heading line, for when the caller supplies its own
        title.

    NOT supported, by design: fenced code blocks, nested/multi-level lists (all bullets render at one
    level), reference-style links, footnotes and inline HTML. Raise these only if a document needs them.
    """
    base_dir = base_dir or os.getcwd()
    width_in = content_width_in(doc)
    if max_image_height_in is None:
        max_image_height_in = content_height_in(doc) * 0.85

    lines = md_text.replace("\r\n", "\n").split("\n")
    i, n = 0, len(lines)
    seen_heading = False

    while i < n:
        raw = lines[i]
        stripped = raw.strip()

        if not stripped:
            i += 1
            continue

        m = _HEADING_RE.match(stripped)
        if m:
            if skip_first_heading and not seen_heading:
                seen_heading = True
                i += 1
                continue
            seen_heading = True
            level = max(1, min(9, len(m.group(1)) + heading_offset))
            h = doc.add_heading("", level=level)
            add_markdown_runs(h, m.group(2).strip(), code_font=code_font, code_color=None)
            i += 1
            continue

        m = _IMAGE_RE.match(stripped)
        if m:
            alt, path = m.group(1), m.group(2).strip()
            full = path if os.path.isabs(path) else os.path.join(base_dir, path.replace("/", os.sep))
            shape = add_image_fitted(doc, full, width_in, max_image_height_in)
            if shape is None:
                add_caption(doc, "[missing image: %s]" % path)
            elif image_captions and alt:
                add_caption(doc, alt)
            i += 1
            continue

        if _HR_RE.match(stripped):
            add_horizontal_rule(doc)
            i += 1
            continue

        if stripped.startswith("|"):
            block = []
            while i < n and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            _render_table(doc, block, table_style, table_font_pt, code_font)
            continue

        m = _QUOTE_RE.match(raw)
        if m:
            parts = []
            while i < n and _QUOTE_RE.match(lines[i]):
                parts.append(_QUOTE_RE.match(lines[i]).group(1).strip())
                i += 1
            _render_quote(doc, " ".join(p for p in parts if p), code_font, quote_shading)
            continue

        m = _BULLET_RE.match(raw)
        if m:
            text, i = _gather_continuation(lines, i, m.group(2))
            p = doc.add_paragraph(style="List Bullet")
            add_markdown_runs(p, text, code_font=code_font)
            continue

        m = _NUM_RE.match(raw)
        if m:
            text, i = _gather_continuation(lines, i, m.group(2))
            p = doc.add_paragraph(style="List Number")
            add_markdown_runs(p, text, code_font=code_font)
            continue

        text, i = _gather_continuation(lines, i, stripped)
        p = doc.add_paragraph()
        add_markdown_runs(p, text, code_font=code_font)

    return doc


def _gather_continuation(lines, i, first):
    """Joins a soft-wrapped markdown block: consumes following lines until a blank or structural line,
    returning the joined text and the new index."""
    parts = [first]
    i += 1
    while i < len(lines) and not _is_structural(lines[i]):
        parts.append(lines[i].strip())
        i += 1
    return " ".join(p for p in parts if p), i


def _render_quote(doc, text, code_font, shading):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    p_pr = p._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "18")
    left.set(qn("w:space"), "8")
    left.set(qn("w:color"), "A6A6A6")
    borders.append(left)
    p_pr.append(borders)
    if shading:
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), shading.lstrip("#"))
        p_pr.append(shd)
    add_markdown_runs(p, text, italic=True, code_font=code_font)
    return p


def _render_table(doc, block, style, font_pt, code_font):
    rows = [split_markdown_row(l) for l in block if not _TABLE_SEP_RE.match(l.strip())]
    if not rows:
        return None
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    headers, body = rows[0], rows[1:]
    table = add_table_styled(doc, headers, body, style=style, markdown=True, font_pt=font_pt)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table
