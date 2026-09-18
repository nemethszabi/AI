"""
sa-framework builders — preflight validation.

Checks that the artifacts a build needs are actually shaped the way ARTIFACT-SCHEMAS.md says,
*before* any document is written, and reports each problem as the thing a person should do about
it rather than as a missing key.

Why this is separate from `req-auditor`. That agent checks whether the artifacts agree with **each
other** — every must-requirement has an estimate line, every offer line traces to something. This
checks whether each artifact matches its own **schema**. They are different failures with
different fixes, and the second one has been slipping through: a live engagement reached version 7
of its workbook with a `rollup` carrying `committed_total`, `platform_unloaded` and
`if_all_options_taken` — none of which are schema fields — because every build was a bespoke script
written against whatever that file happened to contain. The audit passed, because internally it
was consistent. It was consistently wrong.

Findings are graded:

* **error** — the deliverable cannot be built correctly. The build stops.
* **warning** — the deliverable will be built, with something named missing from it.
"""

from __future__ import annotations

THREE_POINT = ("best", "likely", "worst", "pert")

REQUIRED_ROLLUP = {
    "baseline": "the committed (must-priority) scope total",
    "committed": "the figure the offer quotes — baseline + contingency + buffer",
}
OPTIONAL_ROLLUP = ("contingency", "buffer", "optional", "all_options",
                   "by_phase", "by_category", "by_k_category")

# Keys seen in real drifted artifacts, mapped to what they should have been. Naming the
# replacement turns "unknown key" into a one-line fix.
KNOWN_DRIFT = {
    "committed_total": "committed",
    "totals_with_contingency": "committed",
    "if_all_options_taken": "all_options",
    "baseline_unloaded": "baseline",
    "build_delivery": "a `by_phase` entry, not a top-level rollup key",
    "build_delivery_unloaded": "a `by_phase` entry, not a top-level rollup key",
    "platform": "a `by_phase` entry, not a top-level rollup key",
    "platform_unloaded": "a `by_phase` entry, not a top-level rollup key",
    "feature": "a `by_phase` entry, not a top-level rollup key",
    "feature_unloaded": "a `by_phase` entry, not a top-level rollup key",
    "lifecycle": "a `by_phase` entry, not a top-level rollup key",
    "lifecycle_unloaded": "a `by_phase` entry, not a top-level rollup key",
}


def validate(artifacts, types):
    """Return `(errors, warnings)` for the requested deliverable types."""
    errors, warnings = [], []
    if "estimation-pack" in types or "offer" in types:
        _check_estimation(artifacts.get("estimation"), errors, warnings, types)
    if "offer" in types:
        _check_offer(artifacts.get("offer"), errors, warnings)
    return errors, warnings


def _check_estimation(estimation, errors, warnings, types):
    if estimation is None:
        if "estimation-pack" in types:
            errors.append("No estimation.json. Run /sa:estimate before packaging.")
        else:
            warnings.append("No estimation.json — the offer will state no effort figure.")
        return

    rollup = estimation.get("rollup")
    if not isinstance(rollup, dict):
        errors.append(
            "estimation.json has no `rollup` object. Re-run /sa:estimate — every headline figure "
            "is read from there and none is recomputed by the builder."
        )
        return

    drifted = [k for k in rollup if k in KNOWN_DRIFT]
    if drifted:
        lines = [f"  `{k}` should be `{KNOWN_DRIFT[k]}`" for k in sorted(drifted)]
        errors.append(
            "estimation.json's `rollup` uses key names that are not in ARTIFACT-SCHEMAS.md §4.7:\n"
            + "\n".join(lines)
            + "\nThis file predates the schema or was edited by hand. Re-run /sa:estimate to "
            "rewrite it in the current shape — the builder will not guess which invented key "
            "means which standard one."
        )

    for key, meaning in REQUIRED_ROLLUP.items():
        node = rollup.get(key)
        if node is None:
            if not drifted:
                errors.append(
                    f"estimation.json's rollup has no `{key}` — {meaning}. Re-run /sa:estimate."
                )
            continue
        _check_three_point(node, f"rollup.{key}", errors, warnings)

    contingency = rollup.get("contingency")
    if isinstance(contingency, dict):
        if contingency.get("percent") and not contingency.get("decomposition"):
            warnings.append(
                "Contingency has a percentage but no `decomposition`. A percentage that does not "
                "break down into named risks is not a derivation (ESTIMATION-METHOD.md §9.3e); "
                "the workbook will show the figure with nothing behind it."
            )
        if isinstance(contingency.get("amount"), dict):
            _check_three_point(contingency["amount"], "rollup.contingency.amount", errors, warnings)

    for key in ("by_phase", "by_category", "by_k_category"):
        if not rollup.get(key):
            warnings.append(
                f"estimation.json has no `rollup.{key}` — the corresponding breakdown will be "
                "missing from the workbook's Summary and Rollups sheets."
            )

    lines = estimation.get("lines") or []
    if not lines:
        errors.append("estimation.json has no `lines`. There is nothing to itemise.")
        return
    missing_pert = [l.get("id") for l in lines if not ((l.get("ai_assisted") or {}).get("pert"))]
    if missing_pert:
        errors.append(
            f"{len(missing_pert)} estimate line(s) carry no `ai_assisted.pert`: "
            f"{', '.join(str(i) for i in missing_pert[:8])}"
            f"{' …' if len(missing_pert) > 8 else ''}. PERT is the figure every sheet shows."
        )
    missing_k = [l.get("id") for l in lines if not l.get("k_sanity_check")]
    if missing_k and (estimation.get("basis") or {}).get("model") in ("ai-assisted", "both"):
        warnings.append(
            f"{len(missing_k)} line(s) have no `k_sanity_check`. The workbook's "
            "“Why this AI-leverage category” column will be blank for them, which is the column "
            "that makes an implausible compression visible."
        )


def _check_three_point(node, label, errors, warnings):
    holder = node.get("ai_assisted") if isinstance(node.get("ai_assisted"), dict) else node
    if not isinstance(holder, dict):
        errors.append(f"{label} is not a three-point object. Re-run /sa:estimate.")
        return
    missing = [p for p in THREE_POINT if holder.get(p) is None]
    if "pert" in missing:
        errors.append(f"{label} has no stored `pert`. It is the figure every rendered view shows.")
    elif missing:
        warnings.append(f"{label} is missing {', '.join(missing)}.")


def _check_offer(offer, errors, warnings):
    if offer is None:
        errors.append("No offer.json. Run /sa:offer before packaging an offer.")
        return

    untraced = [
        i.get("text", "")[:60]
        for i in ((offer.get("scope") or {}).get("in_scope") or [])
        if not i.get("traces_to")
    ]
    if untraced:
        errors.append(
            f"{len(untraced)} in-scope entries in offer.json carry no `traces_to`. "
            "An offer line with nothing behind it is a scope commitment nobody estimated. "
            f"First: “{untraced[0]}…”"
        )

    if not offer.get("executive_summary"):
        warnings.append("offer.json has no `executive_summary` — the document will open on section 2.")

    solution = offer.get("solution_summary") or {}
    if not (solution.get("principle") or solution.get("text")):
        warnings.append(
            "offer.json's `solution_summary` carries no text — the Solution section will hold only "
            "the diagram and the component table."
        )

    phases = offer.get("delivery_plan") or []
    if phases and not any(p.get("start_week") for p in phases):
        warnings.append(
            "No delivery phase carries `start_week`/`end_week`, so no timeline chart can be drawn "
            "and the Timeline sheet will fall back to whatever `duration` text exists."
        )

    if not offer.get("risks_disclosed"):
        warnings.append("offer.json discloses no risks — the risks table will be absent.")
