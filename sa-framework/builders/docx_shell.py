"""
sa-framework builders — branded DOCX shell handling.

Opens a branded template, fills its placeholders, removes the typography samples it ships with,
keeps the approved boilerplate verbatim, and hands the caller a document positioned to receive
engagement content.

The rule this module enforces, from ARTIFACT-SCHEMAS.md §8: **a profile is a shell, never
content.** Fonts, colours, heading numbering, header and footer stay the template's. Nothing here
sets a font or a colour, and that is deliberate — applying a generator's own styling on top of a
branded template is exactly how a document ends up half-branded.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

HEADING_STYLES = {"Title", "Heading 1", "Heading 2", "Heading 3"}


def iter_blocks(doc):
    """Yield the document body's paragraphs and tables in document order."""
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif child.tag == qn("w:tbl"):
            yield Table(child, doc)


def split_sections(doc):
    """Split the body into sections at every Title/Heading paragraph.

    Returns a list of `{"title", "style", "elements"}`. A section owns its heading paragraph and
    every block up to the next heading, so deleting a section removes its body too — a demo
    section whose heading goes but whose three sample paragraphs stay is the common failure here.
    """
    sections, current = [], {"title": None, "style": None, "elements": []}
    for block in iter_blocks(doc):
        is_heading = isinstance(block, Paragraph) and (block.style.name if block.style else "") in HEADING_STYLES
        if is_heading:
            sections.append(current)
            current = {
                "title": block.text.strip(),
                "style": block.style.name,
                "elements": [block._p],
            }
        else:
            current["elements"].append(block._tbl if isinstance(block, Table) else block._p)
    sections.append(current)
    return [s for s in sections if s["elements"]]


def strip_demo_sections(doc, demo_titles):
    """Delete the typography samples the shell ships with. Returns what was removed and what wasn't.

    Matching is on the heading's exact trimmed text. A title listed in the profile but absent from
    the template is reported rather than ignored, because the usual cause is that the template was
    updated and the profile was not — and the visible symptom would otherwise be a sample section
    shipping to a client.
    """
    wanted = {t.strip() for t in (demo_titles or [])}
    removed, seen = [], set()
    for section in split_sections(doc):
        title = (section["title"] or "").strip()
        if title and title in wanted:
            seen.add(title)
            for element in section["elements"]:
                element.getparent().remove(element)
            removed.append(title)
    return {"removed": removed, "not_found": sorted(wanted - seen)}


def fill_placeholders(doc, mapping):
    """Replace `[Placeholder]` tokens everywhere text lives, preserving each run's formatting.

    Covers body paragraphs, tables (including nested), and every section's header and footer. A
    placeholder split across runs by Word's own editing history is rejoined before matching —
    without that, "[Customer Name]" stored as "[Customer " + "Name]" silently survives into the
    client's copy, which is the single most common branding defect.

    Returns the placeholders actually replaced and those left unfilled.
    """
    mapping = {k: ("" if v is None else str(v)) for k, v in (mapping or {}).items()}
    replaced, remaining = set(), set()

    def do_paragraph(paragraph):
        text = paragraph.text
        hits = [k for k in mapping if k in text]
        if not hits:
            return
        for key in hits:
            replaced.add(key)
        if len(paragraph.runs) <= 1:
            new = text
            for key in hits:
                new = new.replace(key, mapping[key])
            if paragraph.runs:
                paragraph.runs[0].text = new
            else:
                paragraph.add_run(new)
            return
        # Multi-run: collapse into the first run, keeping that run's formatting for the whole
        # paragraph. Acceptable because placeholder paragraphs in a shell are single-format by
        # construction; a mixed-format placeholder paragraph would be a template defect.
        new = text
        for key in hits:
            new = new.replace(key, mapping[key])
        paragraph.runs[0].text = new
        for run in paragraph.runs[1:]:
            run.text = ""

    def walk_table(table):
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    do_paragraph(paragraph)
                for nested in cell.tables:
                    walk_table(nested)

    for paragraph in doc.paragraphs:
        do_paragraph(paragraph)
    for table in doc.tables:
        walk_table(table)
    for section in doc.sections:
        for part in (section.header, section.footer, section.first_page_header, section.first_page_footer):
            if part is None:
                continue
            for paragraph in part.paragraphs:
                do_paragraph(paragraph)
            for table in part.tables:
                walk_table(table)

    for key in mapping:
        if key not in replaced:
            remaining.add(key)
    return {"replaced": sorted(replaced), "unfilled": sorted(remaining)}


def set_document_version(doc, version_text):
    """Set the document version consistently everywhere the shell states it.

    The cover carries "Version:  1.0" as literal text and the Document Information table carries it
    again in a cell. They are two places, so they have twice drifted apart: a shipped offer showed
    9.0 on the cover and 1.0 in the table. One function owns both.

    Returns how many places were updated; zero means the shell states no version and the caller
    should say so rather than assume it was handled.
    """
    updated = 0

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text.lower().startswith("version:"):
            if paragraph.runs:
                paragraph.runs[0].text = f"Version:  {version_text}"
                for run in paragraph.runs[1:]:
                    run.text = ""
            updated += 1

    for table in doc.tables:
        for row in table.rows:
            cells = row.cells
            if len(cells) >= 2 and cells[0].text.strip().rstrip(":").lower() == "version":
                cell = cells[1]
                paragraph = cell.paragraphs[0]
                if paragraph.runs:
                    paragraph.runs[0].text = version_text
                    for run in paragraph.runs[1:]:
                        run.text = ""
                else:
                    paragraph.add_run(version_text)
                updated += 1
    return updated


def set_body_outline_level(paragraph):
    """Exclude a heading-styled paragraph from the table of contents.

    Word builds a TOC from outline levels, not from style names, so a "Contents" heading styled as
    Heading 1 lists itself as the first entry. Forcing the paragraph's outline level to body text
    keeps the heading's appearance and removes it from the TOC.
    """
    properties = paragraph._p.get_or_add_pPr()
    # `get_or_add_outlineLvl` inserts the element at its schema-mandated position. Appending it
    # instead produces a `w:pPr` whose children are out of order, which Word silently ignores —
    # the heading then still lists itself, with no error anywhere to explain why.
    properties.get_or_add_outlineLvl().set(qn("w:val"), "9")  # 9 = body text
    return paragraph


def add_toc(doc, levels="1-3"):
    """Append a real Word table-of-contents field.

    LIMITATION, stated rather than hidden: Word computes the entries and page numbers only when the
    field is refreshed — on open, if Word prompts, or via right-click → Update Field. The builder
    cannot pre-render them, because they depend on final pagination. Every caller reports this;
    implying the TOC is already populated is how a client opens a proposal to the words
    "No table of contents entries found."
    """
    paragraph = doc.add_paragraph()
    run = paragraph.add_run()

    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f'TOC \\o "{levels}" \\h \\z \\u'
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Right-click and choose “Update Field” to build the table of contents."
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")

    for element in (begin, instr, separate, placeholder, end):
        run._r.append(element)
    return paragraph


def pick_style(doc, *candidates):
    """Return the first candidate style the template actually defines, else None.

    Templates differ in which table and caption styles they carry. Asking for a style a template
    does not have raises inside python-docx, so every styled call in this package goes through
    here and degrades to the template's default rather than failing the build.
    """
    available = {s.name for s in doc.styles}
    for name in candidates:
        if name in available:
            return name
    return None
