"""
sa-framework builders — estimation workbook.

The internal-and-client-shareable counterpart to the offer. Where the offer states one number, the
workbook is where every number can be checked one line at a time.

Three rules shape it:

1. **Management first, detail after.** Sheet 1 answers "what does this cost and what is it made
   of?" without scrolling. Everything else supports that answer.
2. **Read stored figures; never recompute a total.** Every headline comes from `estimation.json`'s
   `rollup` (ARTIFACT-SCHEMAS.md §4.7). Arithmetic *rows* carry real cell formulas so a reader can
   check the sum in the workbook, but the builder never substitutes its own arithmetic for a
   stored figure.
3. **The spread lives here, not in the offer.** Line items show best, likely and PERT. `worst` is
   written nowhere — no column, no hidden column — unless `basis.render_worst` is true
   (ESTIMATION-METHOD.md §11.5). A hidden column is one unhide away from the anchoring that rule
   exists to prevent.
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from common import DASH, md, pct, render_worst, rollup_figure

HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
TITLE_FONT = Font(bold=True, size=14)
SUB_FONT = Font(italic=True, size=10, color="555555")
QUOTED_FILL = PatternFill("solid", fgColor="FFF2CC")
REF_FILL = PatternFill("solid", fgColor="F2F2F2")
SECTION_FONT = Font(bold=True, size=11)
THIN = Side(style="thin", color="D0D0D0")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
NUM = "#,##0.0"


class WorkbookBuilder:
    def __init__(self, artifacts, render_profile):
        self.a = artifacts
        self.rp = render_profile
        self.cfg = render_profile.get("xlsx") or {}
        self.findings = []
        self.wb = Workbook()
        self.wb.remove(self.wb.active)

    def note(self, message):
        self.findings.append(message)

    @property
    def estimation(self):
        return self.a.get("estimation") or {}

    @property
    def rollup(self):
        return self.estimation.get("rollup") or {}

    # ----------------------------------------------------------------- build

    def build(self, out_path):
        known = {
            "summary": self.t_summary,
            "how_to_read": self.t_how_to_read,
            "rollups": self.t_rollups,
            "line_items": self.t_line_items,
            "timeline": self.t_timeline,
            "assumptions": self.t_assumptions,
            "risks": self.t_risks,
            "not_estimated": self.t_not_estimated,
            "coverage": self.t_coverage,
            "client_row_coverage": self.t_client_row_coverage,
        }
        for tab in self.cfg.get("tabs") or []:
            builder = known.get(tab)
            if not builder:
                self.note(f"Render profile asks for unknown workbook tab '{tab}' — skipped.")
                continue
            builder()
        if not self.wb.sheetnames:
            raise ValueError("No sheets were produced — check the render profile's `xlsx.tabs`.")

        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        self.wb.save(str(out_path))
        return out_path

    # ----------------------------------------------------------------- helpers

    def sheet(self, title, widths=None):
        ws = self.wb.create_sheet(title[:31])
        if widths:
            for i, width in enumerate(widths, start=1):
                ws.column_dimensions[get_column_letter(i)].width = width
        return ws

    def title_block(self, ws, title, subtitle=None):
        ws["A1"] = title
        ws["A1"].font = TITLE_FONT
        if subtitle:
            ws["A2"] = subtitle
            ws["A2"].font = SUB_FONT
        return 4

    def header_row(self, ws, row, headers):
        for col, text in enumerate(headers, start=1):
            cell = ws.cell(row=row, column=col, value=text)
            cell.fill = HEADER_FILL
            cell.font = HEADER_FONT
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            cell.border = BORDER
        if self.cfg.get("freeze_headers", True):
            ws.freeze_panes = ws.cell(row=row + 1, column=1)
        return row + 1

    def data_rows(self, ws, row, rows, number_cols=()):
        for values in rows:
            for col, value in enumerate(values, start=1):
                cell = ws.cell(row=row, column=col, value=value)
                cell.border = BORDER
                cell.alignment = WRAP
                if col in number_cols and isinstance(value, (int, float)):
                    cell.number_format = NUM
            row += 1
        return row

    # ----------------------------------------------------------------- tabs

    def t_summary(self):
        """Management view: the waterfall, then what the money is made of."""
        ws = self.sheet("Summary", [46, 16, 52])
        engagement = self.a.get("engagement") or {}
        row = self.title_block(
            ws,
            f"{engagement.get('client') or 'Engagement'} — {engagement.get('project') or 'Estimate'}",
            "Effort in man-days. Every figure below is the PERT expected value. "
            "Best and likely are on the Line items sheet.",
        )

        rollup = self.rollup
        contingency = rollup.get("contingency") or {}
        buffer_ = rollup.get("buffer") or {}
        optional = rollup.get("optional") or {}
        not_estimated = self.estimation.get("not_estimated") or []

        row = self.header_row(ws, row, ["Summary row", "PERT (MD)", "What it means"])
        first = row

        entries = [
            ("Baseline before contingency", rollup_figure(rollup, "baseline"),
             "Committed (must-priority) scope, sized at the leanest defensible effort."),
            (f"+ Contingency ({pct(contingency.get('percent'))})", rollup_figure(rollup, "contingency.amount"),
             contingency.get("rationale") or "Derived from the named risks in the risk register."),
            ("+ Buffer", rollup_figure(rollup, "buffer.amount"),
             buffer_.get("rationale") or "No separate buffer."),
        ]
        for label, value, meaning in entries:
            ws.cell(row=row, column=1, value=label).border = BORDER
            # A zero or absent buffer is shown as an em dash, never left blank: "there is no
            # separate buffer" and "nobody filled this in" must not look the same
            # (ESTIMATION-METHOD.md §11.1, §11.4). Excel's SUM ignores the text cell.
            cell = ws.cell(row=row, column=2, value=value if value is not None else DASH)
            cell.number_format = NUM
            cell.border = BORDER
            if value is None:
                cell.alignment = Alignment(horizontal="right")
            ws.cell(row=row, column=3, value=meaning).alignment = WRAP
            ws.cell(row=row, column=3).border = BORDER
            row += 1

        # The quoted figure. A real formula, so the sum is checkable in the workbook.
        committed = rollup_figure(rollup, "committed")
        ws.cell(row=row, column=1, value="= COMMITTED TOTAL — the figure quoted").font = Font(bold=True)
        cell = ws.cell(row=row, column=2, value=f"=SUM(B{first}:B{row - 1})")
        cell.number_format = NUM
        cell.font = Font(bold=True)
        for col in (1, 2, 3):
            ws.cell(row=row, column=col).fill = QUOTED_FILL
            ws.cell(row=row, column=col).border = BORDER
        ws.cell(row=row, column=3, value="This is the number the offer states.").alignment = WRAP
        committed_row = row
        row += 2

        ws.cell(row=row, column=1, value="Optional — NOT included above").border = BORDER
        c = ws.cell(row=row, column=2, value=rollup_figure(rollup, "optional"))
        c.number_format = NUM
        c.border = BORDER
        ws.cell(row=row, column=3, value=optional.get("note") or
                "should/could-priority scope, priced independently and added only if selected.").alignment = WRAP
        optional_row = row
        row += 1

        ws.cell(row=row, column=1, value="= If all options taken").border = BORDER
        c = ws.cell(row=row, column=2, value=f"=B{committed_row}+B{optional_row}")
        c.number_format = NUM
        c.border = BORDER
        for col in (1, 2, 3):
            ws.cell(row=row, column=col).fill = REF_FILL
        ws.cell(row=row, column=3, value="REFERENCE ONLY — not a quote.").alignment = WRAP
        row += 1

        ws.cell(row=row, column=1, value="Not estimated").border = BORDER
        # An em dash with a count, never 0: zero means measured as zero, and an unestimated item
        # shown as zero silently claims it is free.
        ws.cell(row=row, column=2, value=DASH if not_estimated else 0).border = BORDER
        ws.cell(row=row, column=3, value=(
            f"{len(not_estimated)} item(s) with no figure — see the Not estimated sheet."
            if not_estimated else "Nothing was left unestimated."
        )).alignment = WRAP
        row += 3

        # What the figure is made of — the management breakdown.
        #
        # Labelled "baseline", not "committed", and deliberately so: these rows sum to the
        # baseline, because contingency is derived against the baseline as a whole rather than
        # apportioned across phases. A breakdown that sums to one number under a heading naming a
        # different one is the misreading ESTIMATION-METHOD.md §11.1 exists to prevent.
        row = self._summary_breakdown(
            ws, row, "Baseline effort by delivery phase (before contingency)",
            self._phase_rows(), "Phase",
            footer=("+ contingency and buffer as above = the committed total. "
                    "Contingency is derived against the baseline as a whole, not split by phase."),
        )
        category_rows, category_footer = self._category_rows()
        row = self._summary_breakdown(
            ws, row, "Baseline effort by work type (before contingency)",
            category_rows, "Work type", footer=category_footer,
        )

        basis = self.estimation.get("basis") or {}
        ws.cell(row=row, column=1, value="Basis").font = SECTION_FONT
        row += 1
        for label, value in [
            ("Delivery model", basis.get("model")),
            ("Unit", basis.get("unit")),
            ("Rate card", basis.get("rate_card") or basis.get("rate_card_note") or "None applied"),
            ("Calibration source", basis.get("calibration_source") or DASH),
        ]:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=value)
            ws.cell(row=row, column=2).alignment = WRAP
            row += 1
        return ws

    def _summary_breakdown(self, ws, row, heading, rows, label_header, footer=None):
        """A labelled breakdown with a live subtotal, so the column can be checked against itself."""
        if not rows:
            self.note(f"No data for the summary breakdown “{heading}”.")
            return row
        ws.cell(row=row, column=1, value=heading).font = SECTION_FONT
        row += 1
        row = self.header_row(ws, row, [label_header, "PERT (MD)", "Share of the baseline"])
        first = row
        total = sum(v for _, v, _ in rows if isinstance(v, (int, float))) or 1
        for label, value, _note in rows:
            ws.cell(row=row, column=1, value=label).border = BORDER
            cell = ws.cell(row=row, column=2, value=value)
            cell.number_format = NUM
            cell.border = BORDER
            share = ws.cell(row=row, column=3,
                            value=(value / total) if isinstance(value, (int, float)) else None)
            share.number_format = "0%"
            share.border = BORDER
            row += 1
        ws.cell(row=row, column=1, value="Subtotal").font = Font(bold=True)
        subtotal = ws.cell(row=row, column=2, value=f"=SUM(B{first}:B{row - 1})")
        subtotal.number_format = NUM
        subtotal.font = Font(bold=True)
        row += 1
        if footer:
            ws.cell(row=row, column=1, value=footer).font = SUB_FONT
            row += 1
        return row + 2

    def _phase_rows(self):
        rows = []
        for phase in self.rollup.get("by_phase") or []:
            if (phase.get("scope_tier") or "baseline") != "baseline":
                continue
            value = phase.get("pert") if phase.get("pert") is not None else phase.get("likely")
            rows.append([phase.get("name") or phase.get("phase"), value, phase.get("line_count")])
        return rows

    def _category_rows(self):
        """By work type. Returns `(rows, footer)`.

        The non-build share is returned as a footer, not as a row. A summary line sitting inside
        the data range is inside the subtotal formula too, and the next person who gives it a value
        double-counts it without noticing.
        """
        rows = []
        build_total = other_total = 0.0
        for entry in self.rollup.get("by_category") or []:
            value = entry.get("baseline_likely")
            category = entry.get("category")
            rows.append([category, value, None])
            if isinstance(value, (int, float)):
                if category == "build":
                    build_total += value
                else:
                    other_total += value
        footer = None
        if rows and (build_total + other_total):
            share = other_total / (build_total + other_total)
            footer = (
                f"Non-build share of the baseline: {pct(share * 100)} — design, testing, "
                "documentation, infrastructure and project management. This is the first thing "
                "anyone senior checks, so it is stated rather than left to be added up."
            )
        return rows, footer

    def t_how_to_read(self):
        """The explainer sheet. Without it, K2 and PERT are private vocabulary."""
        ws = self.sheet("How to read", [26, 92])
        row = self.title_block(ws, "How to read this workbook",
                               "Definitions for the figures and codes used on the other sheets.")

        blocks = [
            ("Man-day (MD)", "One person working one full day. All effort in this workbook is in man-days. "
                             "Effort is not price: converting man-days to a cost is a separate commercial step."),
            ("Three-point estimate", "Each line is estimated three times, not once: best (everything goes right), "
                                     "likely (the realistic case), and worst (several things go wrong at once). "
                                     "Estimating a single number hides how confident the estimate actually is."),
            ("PERT", "The expected value used everywhere in this workbook and quoted in the offer. "
                     "PERT = (best + 4 × likely + worst) ÷ 6. It weights the likely case heavily while still "
                     "letting the two tails move the result, so it is more honest than the likely case alone "
                     "and far less alarming than the worst case."),
            ("Why worst is not shown", "Worst is calculated and checked on every line, but it is not printed. "
                                       "It is a tail, not a forecast — the case where several independent things "
                                       "all go badly at once. Printed beside the committed figure it gets read as "
                                       "“the real number”. The uncertainty it represents is carried openly by the "
                                       "contingency percentage instead."),
            ("Baseline", "The committed scope only: every must-priority requirement, sized at the leanest "
                         "defensible effort that still delivers it properly."),
            ("Contingency", "A percentage added to the baseline, derived from the named risks in the risk "
                            "register — not a round number chosen for comfort. The Risks sheet lists what it buys."),
            ("Committed total", "Baseline + contingency + buffer. The one figure the offer quotes."),
            ("Optional", "Should- and could-priority scope. Priced so it can be chosen, never included in the "
                         "committed total, and never assumed."),
            ("Scope tier", "Every line is either baseline (committed) or optional. No line is both, and the two "
                           "are never interleaved in a table."),
            ("Not estimated", "Work that was discussed and deliberately carries no figure, with the reason. "
                              "Shown as a dash, never as zero — zero would claim it is free."),
        ]
        row = self.header_row(ws, row, ["Term", "What it means"])
        row = self.data_rows(ws, row, blocks)
        row += 2

        ws.cell(row=row, column=1, value="AI-leverage categories (K1–K6)").font = SECTION_FONT
        row += 1
        ws.cell(row=row, column=1, value=(
            "Delivery is AI-assisted. How much that compresses a given piece of work depends on what "
            "the work is, so every line carries a category recording the expected leverage, plus a "
            "one-sentence justification on the Line items sheet. The categories exist so an implausible "
            "compression is visible to a reader rather than buried in a total."
        ))
        ws.cell(row=row, column=1).alignment = WRAP
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        row += 2

        row = self.header_row(ws, row, ["Category", "Typical work, and why the leverage is what it is"])
        row = self.data_rows(ws, row, [
            ("K1 — high leverage",
             "Conventional, well-patterned work: CRUD screens, standard persistence, grid preferences, "
             "boilerplate. Generated from an existing schema or contract and then reviewed."),
            ("K2 — good leverage",
             "Familiar work with project-specific judgment: schema-driven columns, export and mapping code, "
             "reporting projections. Generatable in bulk, with real decisions to make about behaviour."),
            ("K3 — limited leverage",
             "Integration against a system whose behaviour must be discovered: third-party contracts, "
             "undocumented semantics, protocol edge cases. Code generates; the knowledge does not."),
            ("K4 — little leverage",
             "Work whose cost is measurement and iteration rather than typing: accuracy tuning, performance "
             "work, adjudicating real-world samples. A harness can be generated; the cycles cannot."),
            ("K5 — none",
             "Work paced by other people: workshops, client decisions, UAT windows, approvals, steering."),
            ("K6 — negative",
             "Work AI-assisted delivery makes harder rather than easier, if the engagement has any. "
             "Rare, and always justified per line."),
        ])
        row += 1
        ws.cell(row=row, column=1, value=(
            "Calendar time is not compressed by any of this. AI-assisted delivery reduces build effort. "
            "It does not shorten client decisions, third-party dependencies or UAT windows."
        )).font = SUB_FONT
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        return ws

    def t_rollups(self):
        """The three sub-rollups, answering the three questions always asked."""
        ws = self.sheet("Rollups", [40, 16, 16, 14])
        row = self.title_block(ws, "Rollups",
                               "Three views of the same lines: what ships when, how much is not build "
                               "work, and whether the AI-leverage mix is plausible.")

        ws.cell(row=row, column=1, value="By delivery phase — what ships when").font = SECTION_FONT
        row += 1
        row = self.header_row(ws, row, ["Phase", "PERT (MD)", "Scope tier", "Lines"])
        row = self.data_rows(ws, row, [
            [p.get("name") or p.get("phase"),
             p.get("pert") if p.get("pert") is not None else p.get("likely"),
             p.get("scope_tier") or "baseline",
             p.get("line_count")]
            for p in self.rollup.get("by_phase") or []
        ], number_cols=(2,))
        row += 2

        ws.cell(row=row, column=1, value="By work type — how much of this is not build work").font = SECTION_FONT
        row += 1
        row = self.header_row(ws, row, ["Work type", "Baseline (MD)", "Optional (MD)", "% of baseline"])
        categories = self.rollup.get("by_category") or []
        row = self.data_rows(ws, row, [
            [c.get("category"), c.get("baseline_likely"), c.get("optional_likely"),
             (c.get("percent_of_baseline") / 100) if c.get("percent_of_baseline") is not None else None]
            for c in categories
        ], number_cols=(2, 3))
        for r in range(row - len(categories), row):
            ws.cell(row=r, column=4).number_format = "0%"
        non_build = sum(
            c.get("baseline_likely") or 0 for c in categories if c.get("category") != "build"
        )
        total = sum(c.get("baseline_likely") or 0 for c in categories)
        if total:
            ws.cell(row=row, column=1, value="Non-build share of the baseline").font = Font(bold=True)
            cell = ws.cell(row=row, column=4, value=non_build / total)
            cell.number_format = "0%"
            cell.font = Font(bold=True)
            row += 1
        row += 2

        ws.cell(row=row, column=1, value="By AI-leverage category — is the mix plausible").font = SECTION_FONT
        row += 1
        row = self.header_row(ws, row, ["Category", "Baseline (MD)", "Lines", ""])
        row = self.data_rows(ws, row, [
            [k.get("k_category"), k.get("baseline_likely"), k.get("line_count"), None]
            for k in self.rollup.get("by_k_category") or []
        ], number_cols=(2,))
        ws.cell(row=row + 1, column=1, value="Category definitions are on the How to read sheet.").font = SUB_FONT
        return ws

    def t_line_items(self):
        """Every line, separately, so it can be checked one by one."""
        show_worst = render_worst(self.estimation)
        if show_worst:
            self.note("basis.render_worst is true, so a `worst` column was written. "
                      "Confirm the engagement owner actually asked for it.")
        ws = self.sheet("Line items", [11, 46, 22, 16, 10, 8, 12, 12, 10, 10, 10, 10, 52])
        row = self.title_block(
            ws, "Estimate line items",
            "Baseline first, optional second, never interleaved. "
            + ("Best, likely, worst and PERT shown." if show_worst
               else "Best, likely and PERT shown; worst is calculated and checked but not printed."),
        )

        headers = ["ID", "Item", "Requirements", "Components", "Phase", "K", "Work type",
                   "Scope tier", "Best", "Likely"]
        if show_worst:
            headers.append("Worst")
        headers += ["PERT", "Why this AI-leverage category"]
        row = self.header_row(ws, row, headers)

        lines = self.estimation.get("lines") or []
        baseline = [l for l in lines if (l.get("scope_tier") or "baseline") == "baseline"]
        optional = [l for l in lines if (l.get("scope_tier") or "baseline") == "optional"]

        for group_name, group in (("Baseline (committed)", baseline), ("Optional (not committed)", optional)):
            if not group:
                continue
            cell = ws.cell(row=row, column=1, value=group_name)
            cell.font = SECTION_FONT
            cell.fill = REF_FILL
            row += 1
            first = row
            for line in group:
                effort = line.get("ai_assisted") or {}
                addresses = line.get("addresses") or {}
                values = [
                    line.get("id"),
                    line.get("item"),
                    ", ".join(addresses.get("req") or []),
                    ", ".join(addresses.get("components") or []),
                    line.get("phase"),
                    line.get("k_category"),
                    line.get("category"),
                    line.get("scope_tier") or "baseline",
                    effort.get("best"),
                    effort.get("likely"),
                ]
                if show_worst:
                    values.append(effort.get("worst"))
                values += [effort.get("pert"), line.get("k_sanity_check")]
                row = self.data_rows(ws, row, [values],
                                     number_cols=tuple(range(9, 13 if show_worst else 12)))
            pert_col = get_column_letter(12 if show_worst else 11)
            ws.cell(row=row, column=2, value=f"Subtotal — {group_name}").font = Font(bold=True)
            cell = ws.cell(row=row, column=(12 if show_worst else 11),
                           value=f"=SUM({pert_col}{first}:{pert_col}{row - 1})")
            cell.number_format = NUM
            cell.font = Font(bold=True)
            row += 2

        ws.cell(row=row, column=2, value=(
            "Each subtotal is a live formula, so the arithmetic can be checked here rather than "
            "taken on trust. The baseline subtotal reconciles to the Summary sheet's baseline row."
        )).font = SUB_FONT
        ws.auto_filter.ref = None
        return ws

    def t_timeline(self):
        offer = self.a.get("offer") or {}
        phases = offer.get("delivery_plan") or []
        if not phases:
            self.note("No delivery plan in offer.json — the Timeline sheet was skipped.")
            return None
        ws = self.sheet("Timeline", [34, 12, 12, 10, 14, 58])
        row = self.title_block(ws, "Delivery timeline",
                               "Indicative. A firm plan is agreed at kick-off once client dependencies are met.")
        row = self.header_row(ws, row, ["Phase", "Start week", "End week", "Weeks", "Effort (MD)", "Deliverable"])
        rows = []
        for phase in phases:
            start, end = phase.get("start_week"), phase.get("end_week")
            rows.append([
                phase.get("name"),
                start,
                end,
                (end - start + 1) if (start and end) else phase.get("duration"),
                phase.get("effort_md"),
                "; ".join(phase.get("deliverables") or []) or phase.get("deliverable"),
            ])
        row = self.data_rows(ws, row, rows, number_cols=(5,))
        timeline = offer.get("timeline") or {}
        if timeline.get("total_weeks"):
            ws.cell(row=row, column=1, value="Indicative end-to-end").font = Font(bold=True)
            ws.cell(row=row, column=4, value=timeline["total_weeks"]).font = Font(bold=True)
            ws.cell(row=row, column=6, value=timeline.get("note") or "").alignment = WRAP
        return ws

    def t_assumptions(self):
        ws = self.sheet("Assumptions", [12, 16, 74, 56])
        row = self.title_block(ws, "Assumptions and exclusions",
                               "An assumption that proves wrong changes the estimate. "
                               "An exclusion is work this estimate does not cover at all.")
        row = self.header_row(ws, row, ["ID", "Type", "Statement", "If it proves wrong / why excluded"])
        rows = []
        for item in self.estimation.get("assumptions") or []:
            rows.append([item.get("id"), "Assumption", item.get("text"),
                         item.get("consequence_if_wrong") or ""])
        for item in self.estimation.get("exclusions") or []:
            rows.append([item.get("id"), "Exclusion", item.get("text"), item.get("because") or ""])
        if not rows:
            self.note("estimation.json carries no assumptions or exclusions.")
        self.data_rows(ws, row, rows)
        return ws

    def t_risks(self):
        register = self.a.get("risk_register")
        if not register:
            self.note("No risk-register.json — the Risks sheet was skipped.")
            return None
        ws = self.sheet("Risks", [11, 60, 13, 12, 12, 58, 20])
        contingency = self.rollup.get("contingency") or {}
        row = self.title_block(
            ws, "Risk register",
            f"Contingency of {pct(contingency.get('percent'))} "
            f"({md(rollup_figure(self.rollup, 'contingency.amount'), unit=True)}) is derived from these risks.",
        )
        row = self.header_row(ws, row, ["ID", "Risk", "Probability", "Impact", "Severity",
                                        "Treatment", "Residual"])
        self.data_rows(ws, row, [
            [r.get("id"), r.get("text") or r.get("title"), r.get("probability"), r.get("impact"),
             r.get("severity"), r.get("treatment") or r.get("mitigation"), r.get("residual")]
            for r in register.get("risks") or []
        ])

        decomposition = contingency.get("decomposition") or []
        if decomposition:
            row = ws.max_row + 3
            ws.cell(row=row, column=1, value="What the contingency buys").font = SECTION_FONT
            row += 1
            row = self.header_row(ws, row, ["Risk", "Exposure (MD)", "Covers", "", "", "", ""])
            self.data_rows(ws, row, [
                [d.get("risk"), d.get("exposure_likely"), d.get("covers"), None, None, None, None]
                for d in decomposition
            ], number_cols=(2,))
        else:
            self.note("Contingency carries no decomposition — a percentage that does not decompose "
                      "into named risks is not a derivation (ESTIMATION-METHOD.md §9.3e).")
        return ws

    def t_not_estimated(self):
        items = self.estimation.get("not_estimated") or []
        ws = self.sheet("Not estimated", [18, 56, 56, 46])
        row = self.title_block(ws, "Not estimated",
                               "Discussed, real, and deliberately carrying no figure. "
                               "Shown as a dash everywhere, never as zero.")
        row = self.header_row(ws, row, ["Reference", "Item", "Why there is no figure", "Estimable when"])
        if not items:
            ws.cell(row=row, column=1, value="Nothing was left unestimated.")
            return ws
        self.data_rows(ws, row, [
            [i.get("req") or i.get("ref"), i.get("item") or i.get("text"),
             i.get("because"), i.get("estimable_when") or ""]
            for i in items
        ])
        return ws

    def t_coverage(self):
        requirements = self.a.get("requirements")
        if not requirements:
            self.note("No requirements.json — the Coverage sheet was skipped.")
            return None
        ws = self.sheet("Coverage", [14, 62, 12, 14, 26, 24, 18])
        coverage = self.estimation.get("coverage") or {}
        row = self.title_block(
            ws, "Requirement coverage",
            f"{coverage.get('must_estimated', DASH)} of {coverage.get('must_total', DASH)} "
            "must-priority requirements carry an estimate line.",
        )
        row = self.header_row(ws, row, ["Requirement", "Text", "Priority", "Status",
                                        "Components", "Estimate lines", "Coverage"])

        by_req = {}
        for line in self.estimation.get("lines") or []:
            for rid in ((line.get("addresses") or {}).get("req") or []):
                by_req.setdefault(rid, []).append(line.get("id"))
        components_by_req = {}
        for component in ((self.a.get("architecture") or {}).get("components") or []):
            for rid in component.get("addresses") or component.get("traces_to") or []:
                components_by_req.setdefault(rid, []).append(component.get("id"))

        rows = []
        for requirement in requirements.get("requirements") or []:
            rid = requirement.get("id")
            lines = by_req.get(rid, [])
            rows.append([
                rid,
                requirement.get("text"),
                requirement.get("priority"),
                requirement.get("status"),
                ", ".join(components_by_req.get(rid, [])),
                ", ".join(lines),
                "covered" if lines else "untraced",
            ])
        self.data_rows(ws, row, rows)
        untraced = [r for r in rows if r[6] == "untraced" and r[2] == "must"]
        if untraced:
            self.note(f"{len(untraced)} must-priority requirement(s) have no estimate line: "
                      + ", ".join(r[0] for r in untraced))
        return ws

    def t_client_row_coverage(self):
        """Source-workbook row → estimate line. Rendered only when the engagement carries the map."""
        mapping = ((self.a.get("requirements") or {}).get("client_rows")
                   or (self.a.get("offer") or {}).get("client_rows"))
        if not mapping:
            self.note("Render profile asks for client row coverage, but no `client_rows` map exists "
                      "in requirements.json or offer.json. Sheet skipped.")
            return None
        ws = self.sheet("Client rows", [16, 12, 66, 12, 26, 18])
        row = self.title_block(ws, "Source workbook row coverage",
                               "Every row of the client's own requirement workbook, and where it landed.")
        row = self.header_row(ws, row, ["Sheet", "Row", "Text", "Cluster", "Estimate lines", "Treatment"])
        self.data_rows(ws, row, [
            [m.get("sheet"), m.get("row"), m.get("text"), m.get("cluster"),
             ", ".join(m.get("lines") or []), m.get("treatment")]
            for m in mapping
        ])
        return ws
