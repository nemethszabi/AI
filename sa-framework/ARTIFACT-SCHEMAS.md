# SA Framework — Artifact Schemas

**Binding** shared data contract for the `req-*` agent family and the `/sa:*` command namespace. Scoped
to that pipeline — not global like `CONSTITUTION.md`, not a drafting checklist like the `*-BASELINE.md`
files. Every `req-*` agent reads this after `CONSTITUTION.md`.

Its counterpart is `sa-framework\ESTIMATION-METHOD.md` (how numbers are derived). This file governs
*shape*; that one governs *method*.

---

## 1. Why JSON at all

Every SA artifact is written **twice**: a `.json` file (source of truth) and a rendered `.md` file
(what humans read). The Markdown is generated *from* the JSON in the same agent run — never
hand-maintained separately, never the other way round.

This dual-output rule exists for four concrete capabilities, not for tidiness:

1. **Gate freshness by content hash.** `/sa:package` refuses to build a client deliverable from stale
   inputs. Hashing a rendered narrative is useless — hashing a normalized JSON is exact.
2. **Deliverable generation.** `estimation.json` becomes an XLSX with real cells; parsing a Markdown
   table back into numbers is lossy and fragile.
3. **Cross-artifact validation.** "Every `must` requirement has an estimate line" is a set operation
   over IDs, not a prose reading.
4. **Patch-mode document editing.** Diffing two JSON snapshots yields a precise change list; diffing
   two prose documents does not.

**This reverses an earlier explicit decision.** `req-analyst` v1.1.0 carried the rule *"Stay narrative,
lightweight. This is not a REQ-ID-traceable JSON extraction pipeline with formal gates."* That rule was
correct while the pipeline terminated in an internal `package.md`. It stopped being correct once the
pipeline had to terminate in a **client-facing, commercially binding** document. The rule is retired
deliberately, not by oversight.

**Cost, stated honestly**: every agent now maintains two representations of the same content, and they
can drift. The mitigation is mandatory: **render the Markdown from the JSON you just wrote, in the same
run, never from memory of what you intended to write.**

---

## 2. Universal `meta` block

Every artifact JSON begins with the same `meta` object. No exceptions.

```json
{
  "meta": {
    "schema_version": "1.0",
    "artifact": "requirements",
    "slug": "ams-osiguranje-client-portal",
    "lane": "offer-sow",
    "generated_by": "req-analyst",
    "generated_at": "2026-08-12T14:30:00Z",
    "revision": 1,
    "supersedes": null
  },
  "...": "artifact-specific payload follows"
}
```

| Field | Rule |
|---|---|
| `schema_version` | `"1.0"` for this document. Bump on any breaking change here, never per-artifact. |
| `artifact` | One of: `engagement`, `requirements`, `architecture`, `detailed-design`, `review`, `risk-register`, `estimation`, `estimate-review`, `offer`. |
| `slug` | Matches the `ai/sa/<slug>/` folder name. |
| `lane` | Copied from `engagement.json`. `rom` \| `offer-sow` \| `full-design`. |
| `generated_by` | The agent name that wrote it. |
| `generated_at` | ISO 8601 UTC. |
| `revision` | Integer, starts at 1, increments on each re-run that changes content. |
| `supersedes` | Previous `revision` number, or `null` on first write. |

**Every agent increments `revision` and sets `supersedes` on any re-run that changes content.** This is a
universal obligation, not one each agent restates — `req-auditor` check 7 fails a second run that leaves
`revision` at 1.

**Every agent reads the `.json` when merging on a re-run, never the rendered `.md`.** The Markdown is
lossy by design: it omits fields no human needs to read (`source_ref`, `depends_on`, `notes`). Merging
from it silently drops them.

---

## 3. ID conventions

Stable, never renumbered, never reused. A deleted item is marked `"status": "withdrawn"`, not removed —
downstream artifacts may already cite it.

| Prefix | Artifact | Example |
|---|---|---|
| `REQ-NNN` | requirements | `REQ-001` |
| `C-NNN` | architecture components | `C-007` |
| `QA-NNN` | quality attributes / NFRs | `QA-003` |
| `INT-NNN` | integration points | `INT-002` |
| `R-NNN` | risks | `R-018` |
| `CMP-NNN` | compliance obligations | `CMP-004` |
| `L-NNN` | estimation line items | `L-014` |
| `PH-NNN` | delivery phases | `PH-001` |
| `F-NNN` | review findings | `F-003` |
| `A-NNN` | assumptions | `A-005` |
| `X-NNN` | exclusions | `X-002` |
| `D-NNN` | client dependencies / decisions required | `D-001` |

---

## 4. Artifact schemas

### 4.1 `engagement.json` — written by `/sa:triage`

The only artifact a command writes directly rather than an agent. Everything downstream reads it.

```json
{
  "meta": { "...": "artifact: engagement" },
  "client": "AMS Osiguranje a.d.o.",
  "project": "Client Portal",
  "lane": "offer-sow",
  "lane_rationale": "Written priced offer needed; multi-day turnaround; no LLD requested yet.",
  "industry": "Insurance",
  "counterparty_role": "prospect",
  "locale": "sr-RS",
  "deliverable_language": "English",
  "currency": "EUR",
  "template_path": null,
  "file_naming": "<ORG>-<YYYY>-<CLIENT>-<NNN>-<artifact>-v<NN>.<ext>",
  "delivery_model_intent": "both",
  "commercial_size": "to_clarify",
  "turnaround": "2026-08-19",
  "incumbent_platform": "Aquarius, amso.biz, EOS",
  "compliance_flags": ["GDPR", "ZZPL-RS", "PII", "health-data"],
  "inbound_sources": ["inputs/AMS_Osiguranje_TSD_02_Client_Portal_v1.0.docx.extracted.md"],
  "open_questions": ["Phase 1 product scope undecided (TSD P-01)"]
}
```

`delivery_model_intent` is `traditional` | `ai-assisted` | `both` | `to_clarify`. It is set at triage
because `req-risk-officer` runs *before* `req-estimator` and needs to know whether the AI-delivery
calibration and compression-misreading risks apply — there is no `estimation.json` to read at that point.

`lane` drives rigor and deliverables everywhere downstream:

| Lane | Pipeline | Deliverables |
|---|---|---|
| `rom` | ingest → clarify → estimate → offer | offer (light) |
| `offer-sow` | ingest → clarify → design → risk → estimate → estimate-review → offer → **audit** → package | offer DOCX + estimation XLSX |
| `full-design` | all of the above → review → design-detail → diagrams → **audit** → package | + HLD, LLD, pitch deck |

`audit` is never optional on a lane that packages — `/sa:package` refuses without it (§5). This table is
the single source of truth for lane sequence; commands cite it rather than restating it, because a
restated pipeline is what drifts.

**Lane is reversible.** Re-running `/sa:triage` updates `engagement.json` in place; it never re-scaffolds
over existing artifacts. When genuinely ambiguous, classify **up one tier** and say why.

### 4.2 `requirements.json` — `req-analyst`

```json
{
  "meta": { "...": "artifact: requirements" },
  "summary": "One paragraph: what this REQ/CR is about, who asked, why.",
  "requirements": [
    {
      "id": "REQ-001",
      "description": "Authenticated policyholders can view active policies and expiry dates.",
      "priority": "must",
      "status": "confirmed",
      "source": "TSD §4.2 Dashboard Element 'Active policies'",
      "source_ref": "inputs/AMS_TSD.extracted.md:147",
      "notes": null,
      "depends_on": ["REQ-004"],
      "compliance_flags": ["PII"]
    }
  ],
  "open_questions": [
    { "id": "D-001", "question": "Is Phase 1 scope AO+Casco or Casco+Travel Health?", "blocks": ["REQ-012"], "source": "TSD §10 P-01" }
  ],
  "context_used": ["ai/context/foo-context.md"],
  "ingested_sources": ["inputs/AMS_TSD.extracted.md"]
}
```

| Field | Allowed values / rule |
|---|---|
| `priority` | `must` \| `should` \| `could`. Reflects the **requester's** framing, never the analyst's opinion. |
| `status` | `confirmed` \| `inferred` \| `to_clarify` \| `withdrawn`. |
| `source` | Human-readable citation. Mandatory for `confirmed`. |
| `source_ref` | `file:line` where available. |
| `depends_on` | Array of `REQ-ID`. Empty array, not `null`, when none. |
| `compliance_flags` | Subset of `engagement.compliance_flags`. Propagates to `req-risk-officer`. |

**Merge rule on re-run**: keep every existing `id` exactly as numbered; never renumber; never downgrade a
status a human has upgraded. New findings get new sequential IDs. Record what changed in `summary`.

### 4.3 `architecture.json` — `req-architect`

```json
{
  "meta": { "...": "artifact: architecture" },
  "approach": {
    "chosen": "Portal-in-front-of-record-systems with an integration gateway",
    "alternatives": [
      { "name": "Extend Aquarius directly", "score": 2, "rejected_because": "Vendor dependency; no public-facing tier." }
    ],
    "decision_criteria": ["time-to-value", "regulatory containment", "integration risk"]
  },
  "components": [
    { "id": "C-001", "name": "Portal Web App", "responsibility": "Serbian-language customer journeys", "tech": "to_clarify", "addresses": ["REQ-001"], "layer": "experience" }
  ],
  "quality_attributes": [
    { "id": "QA-001", "attribute": "availability", "target": "99.5% business hours", "status": "to_clarify", "addressed_by": ["C-001"] }
  ],
  "integrations": [
    { "id": "INT-001", "system": "Aquarius", "direction": "read", "pattern": "REST via internal gateway", "confidence": "assumed", "confirmations_needed": ["endpoint spec", "auth model"] }
  ],
  "phasing": [
    { "id": "PH-000", "name": "Discovery", "duration_weeks_likely": 3, "entry_criteria": [], "exit_criteria": ["D-001 closed"], "delivers": [] }
  ],
  "data_flow": "Narrative or step list.",
  "deployment_topology": "Narrative.",
  "traceability": [ { "req": "REQ-001", "components": ["C-001"], "qa": [] } ],
  "assumptions": [ { "id": "A-001", "text": "AMS exposes Aquarius via an internal gateway.", "confidence": "low", "if_wrong": "INT-001 effort doubles." } ],
  "open_questions": [ { "id": "D-011", "question": "Which identity provider fronts the portal?", "blocks": ["C-002"], "raised_by": "architecture" } ],
  "risks_raised": ["Integration specs absent for all four core systems"]
}
```

`integrations[].confidence` is `confirmed` \| `assumed` \| `unknown`. **Any `assumed` or `unknown`
integration must produce a corresponding risk in `risk-register.json`** — `req-risk-officer` enforces
this, and `/sa:audit` checks it.

`risks_raised` is a prose hand-off list only. The scored register lives in `risk-register.json`; the
architect never scores risks.

`open_questions` uses the **shared** `D-` namespace from §3 — the architect continues the sequence
`requirements.json` started rather than opening a local one, so `req-offer` and `req-auditor` can treat
questions from either source identically when building client dependencies.

### 4.4 `detailed-design.json` — `req-detailer`

Full-design lane only.

```json
{
  "meta": { "...": "artifact: detailed-design" },
  "components": [
    { "id": "C-001", "interfaces": [ { "name": "GET /api/policies", "inputs": "...", "outputs": "...", "errors": "..." } ], "config": [], "notes": "" }
  ],
  "data_model": [ { "entity": "PortalCase", "fields": [], "owner_system": "portal" } ],
  "key_flows": [ { "name": "Claim submission", "steps": [] } ],
  "deployment_detail": {},
  "open_questions": []
}
```

Component `id`s **must** already exist in `architecture.json`. The detailer never invents a component and
never re-litigates the HLD's approach — disagreement goes in `open_questions`.

### 4.5 `review.json` — `req-reviewer`

```json
{
  "meta": { "...": "artifact: review" },
  "scope_reviewed": ["architecture.json@rev2", "detailed-design.json@rev1"],
  "summary": "Two-sentence overall read.",
  "findings": [
    { "id": "F-001", "severity": "high", "area": "traceability", "finding": "REQ-014 has no component.", "evidence": "architecture.json traceability[]", "recommendation": "Add a component or mark REQ-014 out of scope." }
  ],
  "coverage": { "requirements_total": 42, "requirements_traced": 39, "must_untraced": ["REQ-014"] }
}
```

`severity` is `high` \| `medium` \| `low`. **No PASS/FAIL verdict** — this pipeline's design review is
deliberately gate-free, an explicit and documented divergence from `AGENT-CONDUCT-BASELINE.md` B7. The
*packaging* gate (§5) is where refusal happens, not here.

### 4.6 `risk-register.json` — `req-risk-officer`

```json
{
  "meta": { "...": "artifact: risk-register" },
  "risks": [
    {
      "id": "R-001",
      "risk": "No API specification exists for any of the four core systems.",
      "category": "integration",
      "probability": "high",
      "impact": "high",
      "severity": "critical",
      "affects": ["REQ-012", "INT-001", "L-014"],
      "treatment": "reduce",
      "mitigation": "Fixed-price Discovery phase to obtain specs before Phase 2 is priced.",
      "owner": "to_clarify",
      "residual": "medium",
      "priced_in": true,
      "contingency_note": "Drives the +5% integration band."
    }
  ],
  "compliance": [
    { "id": "CMP-001", "regime": "GDPR", "obligation": "Lawful basis for processing JMBG.", "applies_because": "REQ-003 collects national ID.", "status": "open", "blocking_deliverable": false, "owner": "client" }
  ],
  "contingency_recommendation": { "percent": 15, "rationale": "Derived from 1 critical + 3 high risks; see §3 of ESTIMATION-METHOD.md." },
  "top_watchlist": ["R-001", "R-004", "R-007"]
}
```

`severity` is **derived, not asserted** — from the probability × impact matrix in
`ESTIMATION-METHOD.md §3`. `treatment` is `avoid` \| `reduce` \| `transfer` \| `accept`.
`priced_in: false` means the risk is explicitly **not** covered by contingency and must therefore appear
as an exclusion in `offer.json`.

### 4.7 `estimation.json` — `req-estimator`

```json
{
  "meta": { "...": "artifact: estimation" },
  "basis": {
    "unit": "man-days",
    "model": "both",
    "rate_card": null,
    "rate_card_note": "No rate card found — effort-only output.",
    "calibration_source": "Netrisk CM v2 (2026-08-10)",
    "commitment_gate": "2-week calibration sprint before any figure is committed."
  },
  "lines": [
    {
      "id": "L-001",
      "item": "Adaptive form engine",
      "category": "build",
      "addresses": { "req": ["REQ-005"], "components": ["C-003"], "qa": [] },
      "k_category": "K2",
      "traditional": { "best": 18, "likely": 26, "worst": 40, "pert": 26.3 },
      "ai_assisted": { "best": 6, "likely": 9, "worst": 14, "pert": 9.3 },
      "uncertainty": "medium",
      "assumptions": ["A-002"],
      "notes": ""
    }
  ],
  "rollup": {
    "traditional": { "best": 0, "likely": 0, "worst": 0 },
    "ai_assisted": { "best": 0, "likely": 0, "worst": 0 },
    "contingency_percent": 15,
    "contingency_rationale": "From risk-register.json contingency_recommendation.",
    "buffer_percent": 0,
    "totals_with_contingency": {}
  },
  "summary": "What changed since the previous revision, or the estimate's headline on a first run.",
  "assumptions": [ { "id": "A-002", "text": "..." } ],
  "exclusions": [ { "id": "X-001", "text": "Online payment integration.", "because": "TSD §2.3 out of scope." } ],
  "coverage": { "must_total": 21, "must_estimated": 21, "must_unestimated": [] },
  "not_estimated": [ { "req": "REQ-030", "because": "Blocked on D-001; separate estimate after decomposition." } ]
}
```

`model` is `traditional` \| `ai-assisted` \| `both`. `k_category` is `K1`–`K6` per
`ESTIMATION-METHOD.md §2`; `null` for zero-effort lines. `pert` is **computed**, never typed by hand:
`(best + 4×likely + worst) / 6`.

An item that genuinely cannot be estimated goes in `not_estimated` with a reason — never as a guessed
line, and never silently folded into "misc".

### 4.8 `estimate-review.json` — `req-estimate-critic`

```json
{
  "meta": { "...": "artifact: estimate-review" },
  "findings": [
    { "id": "F-001", "dimension": "optimism-bias", "severity": "high", "finding": "L-014 spread is degenerate.", "evidence": "likely-best = 2; 0.2*(worst-best) = 4.4", "recommendation": "Widen worst or justify." }
  ],
  "lifecycle_gaps": ["hypercare", "data migration"],
  "recommended_adjustments": [ { "line": "L-014", "field": "worst", "from": 20, "to": 30, "because": "..." } ],
  "revised_totals": { "likely": 0 },
  "verdict_note": "Advisory. This artifact never blocks packaging on its own."
}
```

### 4.9 `offer.json` — `req-offer`

The client-facing artifact. Everything in it must trace to another artifact — **`req-offer` invents
nothing**.

```json
{
  "meta": { "...": "artifact: offer" },
  "executive_summary": "",
  "understanding": "Our reading of the client's need, in their language.",
  "scope": {
    "in_scope": [ { "text": "", "traces_to": ["REQ-001"] } ],
    "out_of_scope": [ { "text": "", "traces_to": ["X-001"] } ]
  },
  "solution_summary": { "text": "", "traces_to": ["C-001"] },
  "delivery_plan": [ { "phase": "PH-000", "name": "Discovery", "duration": "2-3 weeks", "deliverables": [], "commercial_basis": "fixed-price" } ],
  "commercial": {
    "basis": "effort-only",
    "currency": null,
    "figures": {},
    "note": "No rate card configured; pricing is a management decision — see ESTIMATION-METHOD.md §5.",
    "validity_days": 30
  },
  "assumptions": [ { "id": "A-001", "text": "", "consequence_if_wrong": "" } ],
  "exclusions": [ { "id": "X-001", "text": "" } ],
  "client_dependencies": [ { "id": "D-001", "text": "", "needed_by": "before Phase 2 pricing" } ],
  "risks_disclosed": ["R-001"],
  "sign_off": { "prepared_by": "", "date": "", "valid_until": "" }
}
```

**Every `in_scope` entry carries a non-empty `traces_to`.** An offer line with nothing behind it is a
scope commitment nobody estimated — the single most expensive defect this pipeline exists to prevent.

---

## 5. Freshness and the packaging gate

`/sa:package` computes an `inputs_hash` over the artifacts that drive the requested deliverable:

```bash
git hash-object requirements.json architecture.json estimation.json risk-register.json offer.json
```

First 12 characters of each, joined as `requirements:abc123def456,architecture:...`, in that fixed order,
including only files that exist. Fall back to `sha256sum` outside a git repo.

**Content-based, never mtime.** A file touched but unchanged must not invalidate a gate; a file changed
in place must.

Rendered `.md` files, `deliverables/`, `diagrams/` and snapshots are **excluded** from the hash — packaging
its own output must not re-stale the gate that permitted it.

`/sa:audit` writes its verdict as a fenced block:

````
```sa-verdict
verdict: PASS
inputs_hash: requirements:abc123def456,estimation:789abc012def
generated_at: 2026-08-12T14:30:00Z
```
````

`/sa:package` refuses unless the verdict is `PASS` or `PASS-WITH-WAIVERS` **and** the recorded
`inputs_hash` matches a freshly computed one. Refusal is correct behavior, not pedantry — per
`CONSTITUTION.md` Article III, the fix is to re-run the gate, never to weaken it.

---

## 6. Directory layout

```
ai/sa/<slug>/
  ENGAGEMENT.md          engagement.json          ← /sa:triage
  STATE.md                                        ← every command updates
  inputs/                                         ← /sa:ingest (immutable)
  requirements.md        requirements.json        ← req-analyst
  architecture.md        architecture.json        ← req-architect
  detailed-design.md     detailed-design.json     ← req-detailer
  review.md              review.json              ← req-reviewer
  risk-register.md       risk-register.json       ← req-risk-officer
  estimation.md          estimation.json          ← req-estimator
  estimate-review.md     estimate-review.json     ← req-estimate-critic
  offer.md               offer.json               ← req-offer
  audit/                 audit-<ts>.md            ← /sa:audit
                         WAIVERS.md               ← human-authored; Rationale + Approved-by + Date
  diagrams/              *.mmd  *.png             ← mermaid-diagram-maker
  deliverables/          *.docx *.xlsx *.pptx     ← /sa:package
    .snapshots/          <type>-v<NN>.json
```

`inputs/` is **immutable** — never edited after ingest. Rendered `.md` files are **generated** — never
hand-edited, because the next agent run overwrites them from JSON.

### `STATE.md` — canonical shape

Written by `/sa:triage`, updated by **every** subsequent command. One shape, so `/sa:status` and any
future orchestrator can parse it:

```markdown
# State — <slug>

- **Lane**: `<rom | offer-sow | full-design>`
- **Phase**: <triage | ingest | clarify | design | review | design-detail | risk | estimate |
  estimate-review | offer | audit | package>
- **Last command**: `/sa:<command>`
- **Last update**: <ISO 8601 UTC>
- **Next**: <exactly one recommended command>

## Phase history
- <YYYY-MM-DD HH:MM UTC> — <phase> — <one-line what happened>
```

**Append to phase history; never rewrite or drop prior lines.** `Next` names exactly one command — an
orchestrator needs a single edge, and a human needs an unambiguous instruction.

---

## 7. Designed for phase-2 orchestration

v1 is human-driven: one command per step, with human review between. It is deliberately built so an
orchestrator can be added later **without rewriting any agent**. Three properties make that possible, and
they must be preserved by anything added to this pipeline:

1. **Machine-readable state.** `engagement.json` carries `lane`; `STATE.md` carries `phase` and `next`.
   An orchestrator reads the lane table in §4.1 and knows the whole command sequence.
2. **Deterministic pre/postconditions.** Every command declares which artifacts it requires and which it
   writes. Missing precondition → stop and name it; never proceed on a partial picture.
3. **Content-hash freshness.** An orchestrator can compute exactly which downstream artifacts are stale
   after a change, and re-run only those.

A future `/sa:run <slug>` is then a loop over the lane's sequence, stopping at any `AskUserQuestion`, any
`to_clarify` that blocks a `must`, or any gate failure. **Do not add autonomous multi-phase execution
without a human checkpoint** — `CONSTITUTION.md` Articles VII and III both apply, and the reference
framework's `/dev:auto` is exactly the pattern this one declines to copy.

---

**Last revised**: 2026-08-12 (v1.0 — initial schema set, created alongside the lane model and the
presales/bid split from internal solution design).
