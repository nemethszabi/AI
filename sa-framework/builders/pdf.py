"""
sa-framework builders — field refresh and PDF export.

Solves the one limitation every generated Word document in this framework has carried: a TOC field
that python-docx can insert but cannot populate, because the entries depend on final pagination.
The standing workaround was a sentence in the handover telling the human to open Word and press
Update Field — which works, until the PDF is produced first and ships with the words "No table of
contents entries found."

Where Microsoft Word is installed, this module drives it to do what only Word can: repaginate,
compute the field, save the populated DOCX, and export a PDF. Where Word is absent it says so and
returns, so a Linux or Word-less machine still gets a valid DOCX plus an honest report — never a
silent failure and never a PDF that is missing its contents page.

LibreOffice is used as the fallback when it is on the machine. It refreshes fields on conversion
too, though its pagination differs slightly from Word's, which is reported rather than hidden.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

WORD_PDF_FORMAT = 17  # wdFormatPDF


def available():
    """Report which conversion route this machine can take, without attempting one."""
    route = {"word": False, "libreoffice": None, "reason": ""}
    try:
        import win32com.client  # noqa: F401

        route["word"] = _word_path() is not None
        if not route["word"]:
            route["reason"] = "pywin32 present but Word not found in the registry"
    except ImportError:
        route["reason"] = "pywin32 not installed"
    route["libreoffice"] = shutil.which("soffice") or shutil.which("libreoffice")
    return route


def _word_path():
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"Word.Application\CurVer"):
            return True
    except OSError:
        return None
    except ImportError:
        return None


def refresh_and_export(docx_path, pdf_path=None, update_fields=True):
    """Refresh a DOCX's fields in place and optionally export a PDF.

    Returns a report: `{route, fields_refreshed, docx, pdf, note}`. **Never raises for a missing
    toolchain** — a report saying the TOC is unpopulated is actionable, an exception halfway
    through packaging is not.

    The DOCX is saved back with its fields computed, so the file handed to a human already has its
    contents page filled in rather than depending on them accepting a prompt.
    """
    docx_path = Path(docx_path).resolve()
    pdf_path = Path(pdf_path).resolve() if pdf_path else None
    report = {"route": None, "fields_refreshed": False, "docx": str(docx_path),
              "pdf": None, "note": ""}

    route = available()
    if route["word"]:
        try:
            _via_word(docx_path, pdf_path, update_fields, report)
            return report
        except Exception as exc:  # noqa: BLE001 — fall through to the next route, and say why
            report["note"] = f"Word automation failed ({exc}); "

    if route["libreoffice"] and pdf_path:
        try:
            _via_libreoffice(route["libreoffice"], docx_path, pdf_path, report)
            report["note"] += (
                "Converted with LibreOffice. Its pagination differs slightly from Word's, so page "
                "numbers in the PDF may not match what Word would produce."
            )
            return report
        except Exception as exc:  # noqa: BLE001
            report["note"] += f"LibreOffice conversion failed ({exc}); "

    report["note"] += (
        "No PDF was produced and the table-of-contents field is unpopulated. "
        "Open the DOCX in Word and accept the update-fields prompt (or press Ctrl+A then F9)."
    )
    return report


def _via_word(docx_path, pdf_path, update_fields, report):
    import pythoncom  # type: ignore
    import win32com.client  # type: ignore

    pythoncom.CoInitialize()
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    document = None
    try:
        document = word.Documents.Open(str(docx_path), ReadOnly=False, AddToRecentFiles=False)
        if update_fields:
            # Twice: the first pass inserts the entries, the second fixes the page numbers that
            # inserting them shifted. One pass leaves a TOC whose numbers are off by a page.
            for _ in range(2):
                document.Fields.Update()
                for toc in document.TablesOfContents:
                    toc.Update()
            document.Repaginate()
            report["fields_refreshed"] = True
        document.Save()
        if pdf_path:
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            document.SaveAs(str(pdf_path), FileFormat=WORD_PDF_FORMAT)
            report["pdf"] = str(pdf_path)
        report["route"] = "word"
    finally:
        if document is not None:
            document.Close(SaveChanges=0)
        word.Quit()
        pythoncom.CoUninitialize()


def _via_libreoffice(binary, docx_path, pdf_path, report):
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [binary, "--headless", "--convert-to", "pdf", "--outdir", str(pdf_path.parent), str(docx_path)],
        check=True,
        capture_output=True,
        timeout=180,
    )
    produced = pdf_path.parent / (docx_path.stem + ".pdf")
    if produced != pdf_path and produced.is_file():
        produced.replace(pdf_path)
    report["route"] = "libreoffice"
    report["pdf"] = str(pdf_path)
    report["fields_refreshed"] = True
