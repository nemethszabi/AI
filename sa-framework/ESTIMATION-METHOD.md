# SA Framework — Estimation Method

**Binding** method for `req-estimator`, `req-estimate-critic`, and `req-risk-officer`. Its counterpart is
`sa-framework\ARTIFACT-SCHEMAS.md` (what the artifacts look like); this file governs **how the numbers are
derived and what they may be used for**.

Not invented. Codified from real estimates produced on this machine — principally the Netrisk
CampaignManager v1/v2 pair (2026-08-10), which established the differentiated-compression model, the
calibration gate, and the pricing separation. Before this file existed, that method lived in a single
`.xlsx` in one project folder and was lost to every other engagement.

---

## 1. Three-point and PERT

Every estimated line carries **best / likely / worst**, and a computed expected value:

```
PERT = (best + 4 × likely + worst) / 6
```

`pert` is **always computed, never typed**. A hand-entered expected value that doesn't satisfy the formula
is a defect.

**Three-point is mandatory** — not "when uncertain". A single-point number on genuinely uncertain work is
false precision, and false precision is what gets signed.

Two spread rules, both checked by `req-estimate-critic`:

- **Degenerate spread**: `likely − best < 0.2 × (worst − best)` means the optimistic case is doing no
  work. Either widen it or justify why the downside is that asymmetric.
- **Implausible confidence**: `worst < 1.5 × best` on anything touching an unconfirmed integration or a
  `to_clarify` requirement. If the inputs are unknown, the range cannot be tight.

Round to sensible precision on output. Carrying `77.00000000000001` into a client document, as an earlier
workbook did, reads as machine output rather than professional judgment.

---

## 2. Delivery models and K-categories

Two delivery models may be estimated. `estimation.json.basis.model` records which.

- **`traditional`** — conventional human delivery. Also serves as the **priced fallback ceiling**: if the
  AI-assisted model underperforms, this is the number the commercial position retreats to.
- **`ai-assisted`** — AI-augmented delivery, derived by dividing traditional figures by a
  **work-type-specific compression factor**, then re-running PERT.
- **`both`** — recommended default for any offer. Quoting both gives a defensible range and makes the
  fallback explicit rather than hidden.

### The compression factors

| K | Work type | Factor | Why this factor |
|---|---|---|---|
| **K1** | CRUD, UI, admin screens, list/detail/export | **÷3–5** | Highest-leverage generation. Well-patterned, verifiable by inspection. |
| **K2** | Business-logic engines, workflow, state machines, data models | **÷3–3.5** | Strong generation, but correctness needs real test design. |
| **K3** | External/third-party integration | **÷~2** | **The external system's behaviour is the constraint, not typing speed.** Undocumented APIs, latency windows, webhook timing — code generation barely helps. |
| **K4** | Test, UAT, stabilisation | **÷~1.5** | Human- and calendar-bound. Deliberately the least compressed line. |
| **K5** | PM, coordination, client meetings | **÷~2** | Bound by other people's availability. |
| **K6** | Documentation | **÷~3** | Compresses well; review still human. |

### The rule that matters most

**Compression is differentiated, never uniform.** The single most common and most expensive misreading is
to take a headline factor and apply it to everything. Calendar time, client decisions, third-party
roadmaps, and UAT windows **do not compress at all.**

State this explicitly in every AI-assisted estimate. The Netrisk v2 register carried it as a named risk
(*"stakeholders generalise the compression to everything"*, rated High/Medium) precisely because it had
already happened once in conversation.

---

## 3. Risk → contingency derivation

### Severity matrix

Severity is **derived** from probability × impact, never asserted:

| | Impact: Low | Impact: Medium | Impact: High |
|---|---|---|---|
| **Probability: High** | Medium | High | **Critical** |
| **Probability: Medium** | Low | Medium | **High** |
| **Probability: Low** | Low | Low | Medium |

### Contingency band

Contingency covers **known unknowns** — the risks in the register. Derive the band from the register's
composition, then adjust with a stated rationale:

| Register composition | Starting band |
|---|---|
| No high or critical risks | 10% |
| 1–2 high, no critical | 12–15% |
| 3+ high, or 1 critical | 15–20% |
| 2+ critical, or a core integration wholly unspecified | 20–25%, **and** say plainly that the estimate is indicative pending discovery |

**Contingency and buffer are separate figures with separate justifications.** Contingency = known
unknowns, from the register. Buffer = unknown unknowns, used sparingly and never as a way to make a
number feel safer without saying why.

Three things are **excluded** from contingency and must instead appear as exclusions in `offer.json`:

1. **Scope change** — handled by change control, not absorbed.
2. **Undecomposed work** — an item too vague to estimate gets `not_estimated` plus a named follow-up
   estimate, never a padded guess.
3. **Business risk** — commercial viability, ROI, adoption. Not the estimator's to price.

Every risk with `priced_in: false` **must** appear as an exclusion. `/sa:audit` checks this.

---

## 4. Calibration and the commitment gate

An AI-assisted estimate is an extrapolation. It must say what it extrapolates from.

`estimation.json.basis.calibration_source` names the empirical baseline. If none exists, that is stated
plainly — an AI-assisted figure with no calibration source is a guess wearing a method's clothing.

### The calibration bias to audit for

The Netrisk baseline recorded ~48,000 LOC delivered in ~2 focused AI-assisted man-days — and the audit
of that figure is more instructive than the figure itself: **it was biased toward greenfield generation
and under-represented the last mile** (orchestrator wiring, import pipelines, end-to-end integration).
Any calibration point drawn from "how fast did we build the new thing" will overstate compression for the
same reason. Check for it explicitly, and say what the baseline excluded.

### The commitment gate

For any AI-assisted estimate above a trivial size, the number is **not committed** until a short
calibration sprint has measured real velocity on real items from *this* engagement.

- **Duration**: ~2 weeks, delivering 2–3 representative items end-to-end (not a spike — genuinely done).
- **Until the gate closes**, quote externally as a **range** with the gate named:
  *"≈160–250 MD, confirmed after a two-week calibration sprint."*
- **After it closes**, re-estimate from measured velocity and commit.

The gate is a commercial instrument, not an engineering nicety: it converts an unbounded estimation risk
into a bounded, two-week, client-visible checkpoint. Offers should present it as a strength.

---

## 5. Pricing is not effort

**`req-estimator` produces effort. It never produces price.**

Effort is an engineering estimate. Price is a commercial decision involving margin, competitive position,
strategic value, payment structure, and risk appetite — none of which are the estimator's to weigh.

This separation matters most under an AI-assisted model, where MD-based pricing against a compressed base
can quietly destroy revenue on work whose *value* to the client is unchanged. Flag that; don't resolve it.

Rules:

- **No rate card found → effort-only output**, stated plainly. Never invent a rate to make a document
  look finished.
- **A rate card found → cost is presented as an arithmetic consequence of effort × rate**, explicitly
  labelled as an input to a pricing decision, not as the price.
- The commercial model itself (fixed price / T&M / phased / value-based) is named in `offer.json` and
  belongs to whoever owns the commercial relationship.

### Recommended commercial shape under high uncertainty

When core integrations are unspecified — the common case for an inbound TSD or RFP:

**Fixed-price a short Discovery phase; re-estimate everything after it.** This is honest, it bounds the
client's initial spend, it converts your largest risk into a paid engagement, and it is far easier to
defend than a single number covering work whose interfaces nobody has seen.

---

## 6. Lifecycle lines commonly forgotten

Check every estimate against this list. Each is either estimated as a line, or explicitly excluded — never
silently absent. `req-estimate-critic` reports any that are neither.

- Environment setup (dev / test / staging)
- Data migration and reconciliation
- Integration testing against the *real* third-party system, not a stub
- Security review, penetration test, remediation
- Accessibility and localisation testing
- UAT support and defect-fix cycles
- Documentation and handover
- Training (end user and administrator)
- Go-live / cutover
- **Hypercare** — the most frequently omitted line of all
- Project management — typically **10–15%** of build effort
- Release, deployment and infrastructure work

---

## 7. Rate card

`req-estimator` looks for a rate card in this order and stops at the first hit:

1. `ai/sa/rates.yaml` (engagement-specific)
2. `ai/context/rates.yaml` (project)
3. `~/.claude/estimation-data/rates.yaml` (personal default)

### Schema

```yaml
# ~/.claude/estimation-data/rates.yaml
version: 1
currency: EUR
unit: man-day            # man-day | hour
as_of: 2026-08-12        # rates older than ~6 months are flagged as stale
source: "internal blended rates — not client-facing"

roles:
  - id: sa
    name: Solution Architect
    rate: 0
  - id: be
    name: Backend Developer
    rate: 0
  - id: fe
    name: Frontend Developer
    rate: 0
  - id: qa
    name: QA Engineer
    rate: 0
  - id: pm
    name: Project Manager
    rate: 0

# Optional. When present, effort is split across roles for costing.
default_role_mix:
  sa: 0.10
  be: 0.35
  fe: 0.25
  qa: 0.20
  pm: 0.10

# Optional, commercial-only. Never applied silently — always shown as a separate line.
margin_percent: null
```

**Rules**: `rate: 0` is a valid placeholder meaning "structure known, rates not supplied" — treat it as
*no rate card* and produce effort-only output rather than a €0 total. A card whose `as_of` is more than
six months old is used but flagged as stale. **A rate card is commercially sensitive: it never appears in
a client-facing deliverable**, only its arithmetic consequences, and only when someone has decided to
show them.

---

**Last revised**: 2026-08-12 (v1.0 — initial codification from the Netrisk CampaignManager v1/v2
estimates and their risk registers).
