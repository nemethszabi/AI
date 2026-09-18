"""
Generate the schema-conforming fixture engagement used to test the builders.

Run from this directory:  python make_fixture.py

The fixture is deliberately realistic rather than minimal: twenty-three estimate lines across five
phases, both scope tiers, a decomposed contingency, a risk register the offer cites, and a
component set that exercises every diagram tier. A two-line fixture proves the code runs; this one
proves the documents are right.

Northwind Telecom is invented. No real client's material is checked into the framework.
"""

import json
from pathlib import Path

HERE = Path(__file__).parent / "fixture"


def meta(artifact):
    return {
        "schema_version": "1.1",
        "artifact": artifact,
        "slug": "northwind-email-replacement",
        "lane": "offer-sow",
        "generated_by": "fixture",
        "generated_at": "2026-09-18T09:00:00Z",
        "revision": 1,
        "supersedes": None,
    }


def pert(best, likely, worst):
    return round((best + 4 * likely + worst) / 6, 1)


def write(name, payload):
    HERE.mkdir(parents=True, exist_ok=True)
    with open(HERE / name, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------- engagement

write("engagement.json", {
    "meta": meta("engagement"),
    "client": "Northwind Telecom",
    "project": "Email Channel Replacement",
    "lane": "offer-sow",
    "industry": "Telecom",
    "counterparty_role": "client",
    "locale": "en-GB",
    "deliverable_language": "English",
    "currency": None,
    "vendor_org": "geomant",
    "document_profile": "geomant-eng",
    "document_ref": "GEO-2026-Northwind-004",
    "file_naming": "<ORG>-<YYYY>-<CLIENT>-<NNN>-<artifact>-v<NN>.<ext>",
    "compliance_flags": ["GDPR"],
})

# --------------------------------------------------------------------------- requirements

REQUIREMENTS = [
    ("Configurable dashboard columns, reorderable and remembered per user", "must"),
    ("Saved filters, private and shareable", "must"),
    ("Full-text search across subject and body as separate scopes", "must"),
    ("Duplicate detection above 90% accuracy, closing high-confidence duplicates automatically", "must"),
    ("Bulk close with a templated customer reply", "must"),
    ("Service-level countdown and overdue highlighting per mailbox", "must"),
    ("Routing on To and CC addresses, not only the sender", "must"),
    ("Negative rule operators for keyword and address groups", "should"),
    ("Export to CSV and XLSX, with a pivot view for supervisors", "must"),
    ("Signature and template variables filled per agent", "could"),
    ("Raise the concurrent open-email limit per agent", "must"),
    ("Real-time wallboard with filtering on every column", "should"),
]
write("requirements.json", {
    "meta": meta("requirements"),
    "requirements": [
        {"id": f"REQ-{i:03d}", "text": text, "priority": priority, "status": "confirmed"}
        for i, (text, priority) in enumerate(REQUIREMENTS, start=1)
    ],
})

# --------------------------------------------------------------------------- architecture

COMPONENTS = [
    ("C-001", "Inbound routing hook", "Integration", "vendor",
     "Web service the mail platform calls for every inbound email; returns queue, priority and tags."),
    ("C-002", "Outbound capture", "Integration", "vendor",
     "Subscribes to Sent Items and correlates each reply to the email it answers."),
    ("C-003", "Routing and duplicate engine", "Solution components", "vendor",
     "Applies keyword, address and similarity rules, and decides what is a duplicate."),
    ("C-004", "Rule administration", "Solution components", "vendor",
     "Web screen where the business maintains keyword groups, address groups and rule order."),
    ("C-005", "Dashboard", "Solution components", "vendor",
     "Search, service-level countdown, saved filters, work list, reports and export."),
    ("C-006", "Email store", "Data", "vendor",
     "Append-only email events with controlled retention and an erasure workflow."),
    ("C-007", "Shared mailboxes", "Channels and sources", "existing",
     "Existing shared mailboxes; customer email arrives and replies leave through them."),
    ("C-008", "Contact centre platform", "Channels and sources", "existing",
     "Existing routing and agent desktop, unchanged by this work."),
]
write("architecture.json", {
    "meta": meta("architecture"),
    "components": [
        {"id": cid, "name": name, "layer": layer, "ownership": ownership,
         "one_liner": one_liner, "status": "active"}
        for cid, name, layer, ownership, one_liner in COMPONENTS
    ],
    "integration_points": [
        {"id": "INT-001", "from": "Contact centre platform", "to": "Inbound routing hook",
         "protocol": "per-rule call"},
        {"id": "INT-002", "from": "Shared mailboxes", "to": "Outbound capture",
         "protocol": "change notification"},
        {"id": "INT-003", "from": "Inbound routing hook", "to": "Routing and duplicate engine",
         "protocol": ""},
        {"id": "INT-004", "from": "Routing and duplicate engine", "to": "Email store", "protocol": ""},
        {"id": "INT-005", "from": "Outbound capture", "to": "Email store", "protocol": ""},
        {"id": "INT-006", "from": "Dashboard", "to": "Email store", "protocol": "read only"},
    ],
})

# --------------------------------------------------------------------------- risk register

RISKS = [
    ("R-001", "The automatic-closure output may close contacts with an unexpected side effect on "
              "the client's own instance", "medium", "high", "high",
     "Live check on the test instance during design; fall back to work-list-only closure.", "medium"),
    ("R-002", "Replies sent by the platform may not appear in the shared mailbox Sent Items folder",
     "medium", "high", "high",
     "Confirm during design; the fallback is a journaling or blind-copy route.", "low"),
    ("R-003", "Reply correlation hit rate falls below expectation on real traffic",
     "medium", "medium", "medium",
     "Header matching with a subject-token fallback; unmatched replies are recorded, not dropped.", "low"),
    ("R-004", "Duplicate accuracy falls below the 90% target on the real corpus",
     "medium", "medium", "medium",
     "Tuning cycles against a representative sample, inside the estimated line.", "medium"),
    ("R-005", "Email volumes are higher than assumed, changing store and search sizing",
     "medium", "low", "low",
     "Volumes requested before design closes; storage sized on the confirmed figure.", "low"),
]
write("risk-register.json", {
    "meta": meta("risk-register"),
    "risks": [
        {"id": rid, "text": text, "probability": p, "impact": i, "severity": s,
         "treatment": t, "residual": r, "owner": "Delivery lead"}
        for rid, text, p, i, s, t, r in RISKS
    ],
    "compliance": [
        {"id": "CMP-001", "obligation": "Lawful basis and retention period for stored email content",
         "source": "GDPR Articles 5 and 6"}
    ],
    "contingency_recommendation": {
        "percent": 15,
        "rationale": "Two high-severity integration risks against a boundary whose behaviour is undocumented.",
    },
})

# --------------------------------------------------------------------------- estimation

LINES = [
    ("L-001", "Solution design: data model, interface contracts, dashboard wireframes, security design",
     ["REQ-001"], ["C-001", "C-005"], "PH-001", "K5", "docs", "baseline", 8, 11, 16,
     "Design is workshop- and decision-paced; AI assists drafting, not agreement."),
    ("L-002", "Inbound routing hook implementing the platform's documented open interface",
     ["REQ-007"], ["C-001"], "PH-002", "K3", "integration", "baseline", 7, 11, 18,
     "The contract shape is generatable; the platform's real behaviour must be discovered on the instance."),
    ("L-003", "Ingest API and email store schema, with retention and erasure",
     ["REQ-009"], ["C-006"], "PH-002", "K2", "build", "baseline", 6, 9, 14,
     "Schema-driven persistence and migrations generate well from the agreed data model."),
    ("L-004", "Outbound capture: change subscription, retrieval and reply correlation",
     ["REQ-009"], ["C-002"], "PH-002", "K3", "integration", "baseline", 6, 9, 15,
     "Subscription plumbing generates; correlation heuristics need tuning against real traffic."),
    ("L-005", "Dashboard shell: sign-on, roles, navigation and grid foundation",
     ["REQ-001"], ["C-005"], "PH-002", "K1", "build", "baseline", 8, 11, 16,
     "A conventional application shell over a standard identity integration."),
    ("L-006", "Environments, deployment pipeline, monitoring and backup",
     ["REQ-009"], ["C-006"], "PH-002", "K2", "infra", "baseline", 4, 6, 9,
     "Pipeline and infrastructure definitions generate from the existing estate pattern."),
    ("L-007", "Configurable dashboard columns, reordering and per-user persistence",
     ["REQ-001"], ["C-005"], "PH-003", "K1", "build", "baseline", 3, 4.5, 7,
     "Standard grid preference storage and retrieval."),
    ("L-008", "Saved filters, private and shareable",
     ["REQ-002"], ["C-005"], "PH-003", "K1", "build", "baseline", 2.5, 4, 6,
     "Conventional create, read, update and delete over a small entity."),
    ("L-009", "Separate subject and body search over the stored corpus",
     ["REQ-003"], ["C-005", "C-006"], "PH-003", "K2", "build", "baseline", 3, 5, 8,
     "Index and query code generate; corpus size and response targets need measurement."),
    ("L-010", "Duplicate detection engine: fingerprint, similarity scoring, threshold policy",
     ["REQ-004"], ["C-003"], "PH-003", "K2", "build", "baseline", 5, 8.5, 14,
     "Scoring code generates; the policy that avoids false positives does not."),
    ("L-011", "Duplicate accuracy validation against a representative sample",
     ["REQ-004"], ["C-003"], "PH-003", "K4", "test", "baseline", 3, 6, 11,
     "A harness generates; sample selection and adjudication cycles are the real cost."),
    ("L-012", "Bulk close with a templated customer reply",
     ["REQ-005"], ["C-005", "C-003"], "PH-003", "K3", "integration", "baseline", 5, 9, 15,
     "Orchestration generates; the supported send route must be established first."),
    ("L-013", "Service-level engine: targets per mailbox, countdown and overdue highlighting",
     ["REQ-006"], ["C-005"], "PH-003", "K2", "build", "baseline", 4, 6.5, 10,
     "Time calculations and their display generate; the targets come from the client."),
    ("L-014", "Routing on To and CC addresses, with address groups",
     ["REQ-007"], ["C-003", "C-004"], "PH-003", "K2", "build", "baseline", 3, 5, 8,
     "Matching logic and its test cases generate from the rule specification."),
    ("L-015", "Rule administration screen: keyword groups, ordering and tags",
     ["REQ-007"], ["C-004"], "PH-003", "K1", "build", "baseline", 4, 6, 9,
     "A conventional administration surface over a known rule model."),
    ("L-016", "Export to CSV and XLSX, with a role-restricted pivot view",
     ["REQ-009"], ["C-005"], "PH-003", "K2", "build", "baseline", 3, 5, 8,
     "Export mapping and pivot scaffolding generate; the permission rules are hand-written."),
    ("L-017", "Integration and load testing against the client's test instance",
     ["REQ-004"], ["C-001"], "PH-004", "K4", "test", "baseline", 5, 8, 13,
     "Test generation compresses authoring, not instance time or defect cycles."),
    ("L-018", "Acceptance-test support and defect fixes",
     ["REQ-001"], ["C-005"], "PH-004", "K5", "test", "baseline", 4, 7, 12,
     "Paced by the client's acceptance window, not by build throughput."),
    ("L-019", "Documentation: administrator guide, user guide and operations runbook",
     ["REQ-001"], ["C-005"], "PH-005", "K2", "docs", "baseline", 3, 4.5, 7,
     "Drafts generate from the design and the built behaviour, then are reviewed."),
    ("L-020", "Production deployment and two weeks of hypercare",
     ["REQ-009"], ["C-006"], "PH-005", "K5", "infra", "baseline", 4, 6, 10,
     "Cutover and hypercare are bound by the calendar and by people."),
    ("L-021", "Project management, reporting and change control",
     ["REQ-001"], ["C-005"], "PH-005", "K5", "pm", "baseline", 8, 12, 18,
     "Coordination scales with the delivery window, not with generated output."),
    ("L-022", "Negative rule operators for keyword and address groups",
     ["REQ-008"], ["C-003"], "PH-003", "K3", "integration", "optional", 2, 4, 7,
     "Operator code generates; the existing parser's semantics must be confirmed first."),
    ("L-023", "Signature and template variables filled per agent",
     ["REQ-010"], ["C-005"], "PH-003", "K3", "integration", "optional", 2, 3.5, 6,
     "No documented injection route; the approach must be proven before it compresses."),
]

lines = []
for lid, item, reqs, comps, phase, k, category, tier, best, likely, worst, why in LINES:
    lines.append({
        "id": lid, "item": item, "category": category,
        "addresses": {"req": reqs, "components": comps, "qa": []},
        "k_category": k, "scope_tier": tier, "phase": phase,
        "ai_assisted": {"best": best, "likely": likely, "worst": worst,
                        "pert": pert(best, likely, worst)},
        "traditional": None, "k_sanity_check": why, "uncertainty": "medium",
        "assumptions": [], "notes": None,
    })


def total(predicate, key):
    return round(sum(l["ai_assisted"][key] for l in lines if predicate(l)), 1)


is_baseline = lambda l: l["scope_tier"] == "baseline"   # noqa: E731
is_optional = lambda l: l["scope_tier"] == "optional"   # noqa: E731

BASELINE = {k: total(is_baseline, k) for k in ("best", "likely", "worst", "pert")}
OPTIONAL = {k: total(is_optional, k) for k in ("best", "likely", "worst", "pert")}
PERCENT = 15
CONTINGENCY = {k: round(v * PERCENT / 100, 1) for k, v in BASELINE.items()}
COMMITTED = {k: round(BASELINE[k] + CONTINGENCY[k], 1) for k in BASELINE}
ALL_OPTIONS = {k: round(COMMITTED[k] + OPTIONAL[k], 1) for k in BASELINE}

PHASE_NAMES = {
    "PH-001": "1. Design",
    "PH-002": "2. Platform build",
    "PH-003": "3. Feature build",
    "PH-004": "4. Test and acceptance",
    "PH-005": "5. Deployment and hypercare",
}
by_phase = []
for phase, name in PHASE_NAMES.items():
    for tier in ("baseline", "optional"):
        group = [l for l in lines if l["phase"] == phase and l["scope_tier"] == tier]
        if group:
            by_phase.append({
                "phase": phase, "name": name, "scope_tier": tier,
                "pert": round(sum(g["ai_assisted"]["pert"] for g in group), 1),
                "likely": round(sum(g["ai_assisted"]["likely"] for g in group), 1),
                "line_count": len(group),
            })

by_category = []
for category in sorted({l["category"] for l in lines}):
    baseline_likely = round(sum(
        l["ai_assisted"]["likely"] for l in lines
        if l["category"] == category and l["scope_tier"] == "baseline"), 1)
    optional_likely = round(sum(
        l["ai_assisted"]["likely"] for l in lines
        if l["category"] == category and l["scope_tier"] == "optional"), 1)
    by_category.append({
        "category": category,
        "baseline_likely": baseline_likely,
        "optional_likely": optional_likely or None,
        "percent_of_baseline": round(baseline_likely / BASELINE["likely"] * 100),
    })

by_k_category = [
    {"k_category": k,
     "baseline_likely": round(sum(
         l["ai_assisted"]["likely"] for l in lines
         if l["k_category"] == k and l["scope_tier"] == "baseline"), 1),
     "line_count": len([l for l in lines if l["k_category"] == k])}
    for k in sorted({l["k_category"] for l in lines})
]

write("estimation.json", {
    "meta": meta("estimation"),
    "basis": {
        "unit": "man-days", "model": "ai-assisted", "model_rationale": None,
        "rate_card": None, "rate_card_note": "No rate card configured — effort-only output.",
        "calibration_source": "Internal delivery of a comparable sidecar, May 2026",
        "commitment_gate": "Figures are committed at signature.",
        "render_worst": False,
    },
    "lines": lines,
    "rollup": {
        "baseline": {"ai_assisted": BASELINE, "traditional": None,
                     "line_count": len([l for l in lines if is_baseline(l)])},
        "contingency": {
            "percent": PERCENT,
            "rationale": "Two high-severity integration risks against a boundary whose behaviour is undocumented.",
            "source_risks": ["R-001", "R-002", "R-004"],
            "decomposition": [
                {"risk": "R-001", "exposure_likely": 8.0,
                 "covers": "Rework if automatic closure behaves differently on the client's instance."},
                {"risk": "R-002", "exposure_likely": 9.5,
                 "covers": "An alternative outbound capture route if replies do not reach Sent Items."},
                {"risk": "R-004", "exposure_likely": 4.6,
                 "covers": "Extra tuning cycles to reach the accuracy target on the real corpus."},
            ],
            "amount": CONTINGENCY,
        },
        "buffer": {"percent": 0, "rationale": None, "amount": None},
        "committed": {"ai_assisted": COMMITTED, "traditional": None,
                      "formula": "baseline + contingency + buffer",
                      "note": "The figure the offer quotes."},
        "optional": {"ai_assisted": OPTIONAL, "traditional": None,
                     "line_count": len([l for l in lines if is_optional(l)]),
                     "items": [l["id"] for l in lines if is_optional(l)],
                     "note": "should/could-priority scope, priced independently and never included above."},
        "all_options": {"ai_assisted": ALL_OPTIONS, "formula": "committed + optional",
                        "note": "Reference only — never the quoted figure."},
        "by_phase": by_phase, "by_category": by_category, "by_k_category": by_k_category,
    },
    "summary": "First estimate for the email channel replacement.",
    "assumptions": [
        {"id": "A-001", "text": "Mailbox creation, licensing and permissions remain with the client.",
         "consequence_if_wrong": "Mailbox administration becomes additional scope, agreed separately."},
        {"id": "A-002", "text": "The contact centre platform exposes its documented open interface for email.",
         "consequence_if_wrong": "The inbound hook has no supported attachment point and the approach is redesigned."},
        {"id": "A-003", "text": "Replies sent by the platform appear in the shared mailbox Sent Items folder.",
         "consequence_if_wrong": "Outbound capture moves to a journaling route, adding integration effort."},
        {"id": "A-004", "text": "The existing hosting estate can carry the new components.",
         "consequence_if_wrong": "New hosting becomes additional scope and moves the schedule."},
        {"id": "A-005", "text": "Email content may be stored under the client's own lawful basis and retention period.",
         "consequence_if_wrong": "The storage design changes and the reporting scope narrows."},
    ],
    "exclusions": [
        {"id": "X-001", "text": "Any direct connection to the contact centre platform's database.",
         "because": "Not a supported integration route."},
        {"id": "X-002", "text": "A replacement agent desktop.",
         "because": "Agents continue to work in the existing desktop."},
        {"id": "X-003", "text": "Voice, chat and social channels.",
         "because": "This engagement covers the email channel only."},
        {"id": "X-004", "text": "Production high availability.",
         "because": "Offered separately once recovery objectives and volumes are confirmed."},
    ],
    "coverage": {"must_total": 9, "must_estimated": 8, "must_unestimated": ["REQ-011"]},
    "not_estimated": [
        {"req": "REQ-011", "item": "Raising the platform's concurrent open-email limit",
         "because": "A platform limit with no development route.",
         "estimable_when": "Never; the workaround is routing configuration."},
        {"req": "REQ-012", "item": "Real-time wallboard with filtering on every column",
         "because": "Named as a separate future development.",
         "estimable_when": "On request, as its own item."},
    ],
})

# --------------------------------------------------------------------------- offer

write("offer.json", {
    "meta": meta("offer"),
    "executive_summary": (
        "Northwind Telecom asked us to replace the capabilities its teams lose by moving email "
        "onto the new contact centre platform. This offer proposes a component that runs alongside "
        "that platform rather than replacing it: agents keep working in the desktop they already "
        "use, while routing, duplicate handling, search and reporting are delivered by new "
        "components beside it.\n\n"
        "The committed effort is stated in section 6. One item, production high availability, is "
        "named and deliberately not priced here, and two capabilities carry no figure at all for "
        "reasons given in section 4."
    ),
    "understanding": (
        "Northwind's email teams compared what they do today with what the new platform provides, "
        "and recorded the gaps feature by feature. Those gaps are working practices, not a wish "
        "list.\n\n"
        "Agents need a dashboard whose columns they choose and keep, filters that survive a logout "
        "and can be shared, and search inside the body of an email rather than only its metadata. "
        "Supervisors need response time and a countdown against a target, plus export and a pivot "
        "from live data.\n\n"
        "The two largest operational asks are duplicate handling and closing a set of emails in "
        "bulk while still sending each customer a proper reply."
    ),
    "solution_summary": {
        "principle": (
            "The existing platform remains the email handling system. Agents draft, send, close and "
            "reopen email exactly where they do today. New components sit beside it: they observe "
            "inbound and outbound email, decide routing and duplicates at arrival, keep their own "
            "store of email events, and present a dashboard with search, reporting and export.\n\n"
            "The new components never read the platform's own database, and they never block a "
            "genuine customer email. If they are unavailable, the platform processes email with its "
            "standard rules."
        ),
        "figure_caption": "Solution architecture — component view",
        "figure_note": (
            "Customer email arrives in the shared mailbox and the platform polls it. For each "
            "routing rule the platform calls the inbound hook, which returns the queue, priority "
            "and tags to apply. The agent handles the email in the desktop, and the reply is "
            "captured from Sent Items and correlated back to the message it answers."
        ),
        "data_protection": (
            "The store holds customer email content. The design includes a per-user access log, "
            "retention periods, an erasure workflow and an audit trail. Northwind defines the "
            "lawful basis and the retention period."
        ),
        "traces_to": ["C-001", "C-003", "C-005", "C-006"],
    },
    "scope": {
        "in_scope": [
            {"work_package": "Design",
             "text": "Data model, interface contracts, dashboard wireframes, security and data-protection design.",
             "traces_to": ["REQ-001"]},
            {"work_package": "Inbound routing hook",
             "text": "Open-interface web service, routing engine, duplicate detection and tag assignment.",
             "traces_to": ["REQ-004", "REQ-007"]},
            {"work_package": "Rule administration",
             "text": "Keyword and address groups, rule ordering, operators and tags, maintained by the business.",
             "traces_to": ["REQ-007"]},
            {"work_package": "Outbound capture",
             "text": "Change subscription on Sent Items, retrieval, and correlation to the inbound email.",
             "traces_to": ["REQ-009"]},
            {"work_package": "Email store",
             "text": "Schema, ingest API, retention and erasure.",
             "traces_to": ["REQ-009"]},
            {"work_package": "Dashboard",
             "text": "Sign-on, roles, grid, columns, service-level engine, filters, search, work list, "
                     "bulk close, reports, export and pivot.",
             "traces_to": ["REQ-001", "REQ-002", "REQ-003", "REQ-005", "REQ-006", "REQ-009"]},
            {"work_package": "Environments",
             "text": "Development, test, acceptance and production on the existing estate, with pipeline, "
                     "monitoring and backup.",
             "traces_to": ["REQ-009"]},
            {"work_package": "Testing",
             "text": "Unit and integration testing against the client's test instance, throughput and "
                     "timeout tests, and duplicate-accuracy validation.",
             "traces_to": ["REQ-004"]},
            {"work_package": "Acceptance, documentation and deployment",
             "text": "Acceptance support, administrator and user guides, operations runbook, production "
                     "release and two weeks of hypercare.",
             "traces_to": ["REQ-001"]},
            {"work_package": "Project management",
             "text": "Planning, reporting, steering and change control across the delivery window.",
             "traces_to": ["REQ-001"]},
        ],
        "optional": [
            {"text": "Negative rule operators for keyword and address groups",
             "traces_to": ["REQ-008"], "effort_md": 4.2},
            {"text": "Signature and template variables filled per agent",
             "traces_to": ["REQ-010"], "effort_md": 3.7},
        ],
        "not_in_figure": [
            {"text": "Raising the concurrent open-email limit per agent",
             "reason": "A platform limit with no development route. The workaround is routing configuration."},
            {"text": "Real-time wallboard with filtering on every column",
             "reason": "Named as separate future development. Can be offered on its own."},
            {"text": "Production high availability",
             "reason": "Offered separately once recovery objectives and volumes are confirmed."},
            {"text": "Annual support and maintenance",
             "reason": "Quoted as a separate line, outside the build total."},
        ],
        "out_of_scope": [
            {"text": "Any direct connection to the contact centre platform's database."},
            {"text": "A replacement agent desktop. Agents continue in the desktop they use today."},
            {"text": "Voice, chat and social channels. This engagement covers email only."},
            {"text": "Migration of historical email from the outgoing system."},
        ],
    },
    "delivery_plan": [
        {"phase": "PH-001", "name": "1. Design", "start_week": 1, "end_week": 3, "weeks": 3,
         "effort_md": 11.3, "deliverables": ["Approved design document set"],
         "commercial_basis": "included in the committed effort"},
        {"phase": "PH-002", "name": "2. Platform build", "start_week": 4, "end_week": 9, "weeks": 6,
         "effort_md": 47.2,
         "deliverables": ["Hook, outbound capture, store and dashboard shell deployed to test"],
         "commercial_basis": "included in the committed effort"},
        {"phase": "PH-003", "name": "3. Feature build", "start_week": 7, "end_week": 14, "weeks": 8,
         "effort_md": 56.7,
         "deliverables": ["Routing, duplicate detection, dashboard features, reports and export"],
         "commercial_basis": "included in the committed effort"},
        {"phase": "PH-004", "name": "4. Test and acceptance", "start_week": 15, "end_week": 18, "weeks": 4,
         "effort_md": 15.5, "deliverables": ["Test report", "Acceptance sign-off"],
         "commercial_basis": "included in the committed effort"},
        {"phase": "PH-005", "name": "5. Deployment and hypercare", "start_week": 19, "end_week": 21,
         "weeks": 3, "effort_md": 22.8,
         "deliverables": ["Production release", "Documentation", "Two weeks of hypercare"],
         "commercial_basis": "included in the committed effort"},
    ],
    "timeline": {
        "total_weeks": 21,
        "note": "The indicative end-to-end duration is 21 weeks from project start to the end of "
                "hypercare. Feature build starts in week 7 and overlaps the platform build. The "
                "timeline assumes the client dependencies in section 7 are met on time. A firm plan "
                "is agreed at the design kick-off.",
    },
    "commercial": {
        "basis": "effort-only",
        "currency": None,
        "figures": {"committed_md": COMMITTED["pert"], "optional_md": OPTIONAL["pert"]},
        "support_md_per_year": 15,
        "note": "Effort is stated in man-days. Converting it to a price is a separate commercial step.",
        "validity_days": 30,
        "terms": [
            "Changes to the scope in section 4 are handled through change control.",
            "Annual support and maintenance starts at the end of hypercare and is quoted per year.",
        ],
    },
    "assumptions": [
        {"id": "A-001", "text": "Mailbox creation, licensing and permissions remain with Northwind.",
         "consequence_if_wrong": "Mailbox administration becomes additional scope, agreed separately."},
        {"id": "A-002", "text": "The contact centre platform exposes its documented open interface for email.",
         "consequence_if_wrong": "The inbound hook has no supported attachment point and the approach is redesigned."},
        {"id": "A-003", "text": "Replies sent by the platform appear in the shared mailbox Sent Items folder.",
         "consequence_if_wrong": "Outbound capture moves to a journaling route, adding integration effort."},
        {"id": "A-004", "text": "The existing hosting estate can carry the new components.",
         "consequence_if_wrong": "New hosting becomes additional scope and moves the schedule."},
        {"id": "A-005", "text": "Email content may be stored under Northwind's own lawful basis and retention period.",
         "consequence_if_wrong": "The storage design changes and the reporting scope narrows."},
    ],
    "exclusions": [
        {"id": "X-001", "text": "Any direct connection to the contact centre platform's database."},
        {"id": "X-002", "text": "A replacement agent desktop."},
        {"id": "X-003", "text": "Voice, chat and social channels."},
    ],
    "client_dependencies": [
        {"id": "D-001", "text": "Application registration and administrator consent for the mailbox subscription.",
         "needed_by": "before the platform build starts, week 4"},
        {"id": "D-002", "text": "Access to a test instance with representative mailboxes and routing rules.",
         "needed_by": "by the end of the design phase, week 3"},
        {"id": "D-003", "text": "A database platform with backup, restore and access arrangements.",
         "needed_by": "by the end of the design phase, week 3"},
        {"id": "D-004", "text": "The lawful basis and retention period for the email store.",
         "needed_by": "before the design phase closes, week 3"},
        {"id": "D-005", "text": "Peak email volumes, mailbox count and concurrent agent numbers.",
         "needed_by": "before the design phase closes, week 3"},
    ],
    "open_questions": [
        {"id": "Q-001", "text": "Does the automatic-closure output close silently, or with an auto-response?",
         "affects": "The behaviour of automatic duplicate closure."},
        {"id": "Q-002", "text": "Which supported source provides contact state changes and closure reasons?",
         "affects": "Whether the status and resolution fields are complete or partial."},
        {"id": "Q-003", "text": "Must search cover attachments, or headers and body only?",
         "affects": "Store size and the search build."},
        {"id": "Q-004", "text": "Should the bulk-close reply be sent from the shared mailbox or through the platform?",
         "affects": "The bulk-close design."},
    ],
    "risks_disclosed": ["R-001", "R-002", "R-004"],
    "sign_off": {"prepared_by": "Solution Architecture", "date": "18 September 2026",
                 "valid_until": "18 October 2026"},
})

print(f"Fixture written to {HERE}")
print(f"  baseline {BASELINE['pert']} + contingency {CONTINGENCY['pert']} "
      f"= committed {COMMITTED['pert']} MD; optional {OPTIONAL['pert']} MD")
