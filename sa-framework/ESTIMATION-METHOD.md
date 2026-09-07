# SA Framework — Estimation Method

**Binding** method for `req-estimator`, `req-estimate-critic`, and `req-risk-officer`. Its counterpart is
`sa-framework\ARTIFACT-SCHEMAS.md` (what the artifacts look like); this file governs **how the numbers are
derived and what they may be used for**.

`req-screener` is bound by **§5 only** (effort is not price; no invented rates) and is deliberately exempt
from the derivation machinery in §§1–4 — see §8.

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

### Rounding, pinned

"Sensible precision" was undefined here until 2026-09-07, which meant every estimate rounded differently and
`req-estimate-critic`'s precision dimension had no threshold to test against. The rule:

| Figure | Precision |
|---|---|
| Per-line `best`/`likely`/`worst` | whole units (man-days), or 0.5 below 5 |
| Per-line `pert` | one decimal |
| Any rollup or total | whole units |
| Percentages (contingency, buffer, PM share) | whole percent |

**Round on output, never in the stored value** — `pert` stays exact in `estimation.json` so the rollup
sums correctly; the rendered `.md` and any deliverable show the rounded form. Rounding a stored value makes
every downstream sum drift by a little, and nobody can then tell whether a total is wrong or merely rounded.

Carrying `77.00000000000001` into a client document, as an earlier workbook did, reads as machine output
rather than professional judgment. So does a total that doesn't equal the sum of the lines above it.

---

## 2. Delivery model and K-categories

`req-estimator` estimates **one delivery model: AI-assisted.** That is how the work is actually going to be
delivered, so that is what gets sized — directly, not by building a hypothetical non-AI estimate first and
discounting it.

`estimation.json.basis.model` **defaults to `"ai-assisted"` and this is normally the only value it takes.**
`traditional` and `both` are opt-in, never the default, and exist only for the rare case where a client or
internal stakeholder explicitly needs a non-AI comparison figure — e.g. a procurement process that
requires a "business as usual" baseline for contrast. `req-estimator` **never produces one unasked** rather
than computing it just because the schema allows it, and records the reason in `basis.model_rationale`.
When it cannot tell whether a comparison figure is wanted, it omits it and raises the question under
`## Blocking questions` in its returned summary; `/sa:estimate` is what puts that to the human, because a
dispatched agent has no `AskUserQuestion` and cannot ask anything itself. A `traditional` figure, when produced, is labelled on its face as a **comparison
figure, not the delivery model being priced** — it is never the number an offer quotes.

**On the `rom` lane, `traditional`/`both` are never produced, full stop** — see §10.

This reverses the framework's original default (`both`, with traditional serving as "the priced fallback
ceiling"). That framing assumed AI-assisted delivery was the exception needing a hedge; it is now the
delivery model being sold, and estimating a parallel legacy figure nobody will use is effort spent
producing a number nobody asked for.

### The K-categories

Every line still carries a `k_category` (`K1`–`K6`) — not to derive the AI-assisted figure by dividing a
constructed traditional number, but because the category is the fastest sanity check available, to the
estimator and to `req-estimate-critic`, that a figure is the right *shape* for the work:

| K | Work type | Typical AI leverage vs. non-AI delivery | Why |
|---|---|---|---|
| **K1** | CRUD, UI, admin screens, list/detail/export | Very high (reference: ÷3–5) | Highest-leverage generation. Well-patterned, verifiable by inspection. |
| **K2** | Business-logic engines, workflow, state machines, data models | High (reference: ÷3–3.5) | Strong generation, but correctness needs real test design. |
| **K3** | External/third-party integration | Low (reference: ÷~2) | **The external system's behaviour is the constraint, not typing speed.** Undocumented APIs, latency windows, webhook timing — generation barely helps. |
| **K4** | Test, UAT, stabilisation | Lowest (reference: ÷~1.5) | Human- and calendar-bound. Deliberately the category to lean on least when a figure feels tight. |
| **K5** | PM, coordination, client meetings | Low (reference: ÷~2) | Bound by other people's availability. |
| **K6** | Documentation | Moderate–high (reference: ÷~3) | Compresses well; review still human. |

The "reference" ratios are what the same class of work has historically cost in non-AI delivery, per the
Netrisk calibration (§4) — kept here as a **sanity band**, not a formula to run every time. Size each
line's AI-assisted best/likely/worst **directly**, informed by the calibration source and the line's own
history if one exists, then check the result against the band for its category. A `K3` integration line
priced as if it carries `K1` leverage, or a `K4` test line compressed as hard as a `K1` screen, is the
single most expensive misreading of this method and is a defect to catch before `req-estimate-critic` does.

Where a `traditional` figure is separately produced (the opt-in case above), the ratio
`traditional.likely / ai_assisted.likely` should land inside its line's band — `req-estimate-critic`
dimension 6 checks this arithmetically when both figures exist, and records it as not checkable when they
don't.

### The rule that matters most

**AI leverage is differentiated, never uniform.** The single most common and most expensive misreading is
to take a headline ratio and apply it to everything. Calendar time, client decisions, third-party
roadmaps, and UAT windows **do not compress at all**, regardless of delivery model — state this explicitly
in every estimate. The Netrisk v2 register carried it as a named risk (*"stakeholders generalise the
compression to everything"*, rated High/Medium) precisely because it had already happened once in
conversation.

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

`estimation.json.basis.calibration_source` names the empirical baseline.

### When there is no calibration source

This is the normal state on a first engagement with a new client, a new stack or a new team, so it needs a
workable answer rather than a refusal. **Produce the estimate**, and do all three of:

1. Set `basis.calibration_source` to the literal string `"none — uncalibrated"`, never to a vague gesture
   at "industry experience". An empty field and a hand-wave are equally unusable; a named absence is
   auditable.
2. **Widen every line's `worst`** to reflect that the compression assumption itself is unverified — the
   uncertainty is in the *method*, not only in the work. A tight range built on an unmeasured compression
   ratio is exactly the false precision §1 exists to prevent.
3. State on the face of the estimate that the figure rests on an unmeasured compression assumption, and
   that the calibration sprint below is therefore not optional but load-bearing.

**This resolves a three-way contradiction that stood until 2026-09-07** and is recorded so it isn't
reintroduced: this section said "state it plainly" (produce), `req-estimator`'s rules said an uncalibrated
figure "is not produced" (refuse), and `req-estimate-critic` dimension 10 scored the absence as a `high`
finding (which presupposes one was produced). Followed literally, the refusal wins and the pipeline cannot
estimate anything for a new client — which is every first engagement. Produce-and-label is the resolution;
the critic's `high` finding stands, because "uncalibrated" is genuinely a serious property of an estimate,
not a clean state.

### The calibration bias to audit for

The Netrisk baseline recorded ~48,000 LOC delivered in ~2 focused AI-assisted man-days — and the audit
of that figure is more instructive than the figure itself: **it was biased toward greenfield generation
and under-represented the last mile** (orchestrator wiring, import pipelines, end-to-end integration).
Any calibration point drawn from "how fast did we build the new thing" will overstate compression for the
same reason. Check for it explicitly, and say what the baseline excluded.

### The commitment gate

For any AI-assisted estimate **at or above 20 man-days baseline Likely**, the number is **not committed**
until a short calibration sprint has measured real velocity on real items from *this* engagement.

The threshold is pinned rather than left as "above a trivial size", which it was until 2026-09-07 and which
was unactionable — an agent cannot apply a judgment nobody defined, and two runs over the same estimate
would disagree about whether the gate applied. 20 MD is roughly where a wrong compression ratio stops being
absorbable inside a single sprint. Below it, record in `basis.commitment_gate` that the gate does not apply
and why; never silently omit the field, because an absent gate and an inapplicable one read identically.

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

## 8. Screening bands are not estimates

`req-screener` (via `/sa:screen`) produces an **order-of-magnitude effort band** to answer "can we do this,
and roughly what would it cost?" before anyone decides to bid. It is not an estimate under this document,
and the distinction is deliberate rather than a shortfall:

| | Screening band | Estimate |
|---|---|---|
| Written by | `req-screener` | `req-estimator` |
| Lands in | `screen.md` (advisory non-artifact) | `estimation.json` + `.md` |
| Method | Rounded range, one or two significant figures | §1 PERT over best/likely/worst per line |
| Contingency | **None** — no register exists yet | §3, derived from the risk register |
| Compression | **None** — no K-categorisation | §2 per-line work-type factors |
| Calibration | **None** | §4, with the commitment gate |
| May be quoted | **Never**, rate card or not | Yes, as effort, per §5 |

Three rules follow, and they bind both agents:

- **A screening band must never be widened, narrowed, or converted into an estimate.** If a real number is
  needed, `/sa:design` → `/sa:risk` → `/sa:estimate` runs from the requirements, not from the band.
- **`req-estimate-critic` never critiques a `screen.md`.** A band with no PERT, no contingency and no
  calibration is not a method violation there — it is the specified output. Critiquing it against §§1–4
  would be a category error, and `screen.md` is outside the artifact set that agent reads.
- **`req-estimator` never treats a band as an input or an anchor.** Reading one before estimating imports
  precisely the optimism the three-point method exists to surface. Estimate from requirements, design and
  register; ignore whatever the screen said.

The reason a deliberately coarse number is allowed to exist at all is that it lives in an advisory
non-artifact nothing cites (`ARTIFACT-SCHEMAS.md` §6) and no deliverable can be built from it. A coarse
number in `estimation.json` would be a defect; the same number in `screen.md` is the honest answer to a
different question.

---

## 9. Scope discipline: bare-minimum baseline, priced optionality

Two independent disciplines, both mandatory on every estimate regardless of lane.

### 9.1 Baseline = `must`-priority only

The estimate's **baseline** is the set of `must`-priority requirements in `requirements.json` — nothing
else. `should`- and `could`-priority requirements are estimated as separate, individually PERT'd
**Optional** line items (`scope_tier: "optional"`) — same rigor, same K-category, same three-point
discipline — but:

- **Excluded from the baseline rollup and from contingency.** Contingency is sized against the baseline's
  own risk profile (§3); blending optional scope into it either overstates the baseline's risk or
  understates the optional item's own.
- **Listed on their own, with their own PERT'd effort**, so a reader can add any of them by an explicit
  decision — never because they rode along silently inside the headline number.
- **Never silently promoted to baseline.** A `should` item the client clearly needs is a signal to send
  back to `req-analyst` for reclassification to `must` — not license for `req-estimator` to fold it in on
  its own judgment. Estimating is not the place to relitigate priority.

The result is a headline number a client can act on immediately, with everything beyond it priced and
visible rather than buried inside it.

### When nothing is `must`

An early or loosely-written requirements list can contain no `must`-priority items at all. Read literally,
the rules above then produce an empty baseline and a headline of zero — a number that is arithmetically
correct and completely misleading, and the kind of output that gets forwarded before anyone reads the
caveat.

**Do not estimate a zero baseline.** Instead:

- Produce the `optional` lines normally — that work is real and sizing it is useful.
- Set the baseline rollup to `null`, not `0`, and state in `basis` that no `must`-priority requirement
  exists, so there is nothing to commit to.
- Raise it under `## Blocking questions` in the returned summary: a requirements list with no `must` is
  almost always a prioritization gap in `req-analyst`'s output, not a genuine finding that the client needs
  nothing.
- **Never promote a `should` to fill the gap.** §9.1's no-silent-promotion rule holds exactly here, where
  the temptation is strongest — reprioritizing is `req-analyst`'s job and the client's, and doing it inside
  the estimator hides a scope decision inside a number.

`0` and `null` are different claims: `0` says "we costed it and it's free", `null` says "there is nothing
here to cost". Only the second is true.

### 9.2 Bare-minimum sizing within the baseline

Every baseline line is sized to the **leanest implementation that still fully satisfies the requirement as
written** — not the most convenient one to build, not one with headroom for a use case nobody asked for,
not "while we're already in this component." Bare-minimum is a discipline on **effort**, never a
discipline on **scope**: it does not mean delivering less than a `must` requirement demands. A requirement
that cannot be met leanly is estimated at whatever it genuinely takes — reducing what a `must` requirement
actually delivers in order to hit a smaller number is scope-cutting, not estimating, and belongs to
`req-analyst` and the client as a requirement-change conversation, never a unilateral move inside
`req-estimator`.

Concretely, for every baseline line:

- Assume the smallest defensible design that meets the requirement — no speculative extensibility, no
  configurability beyond what was asked for, no abstraction built for a second use case that doesn't exist
  yet.
- Record in `notes` what was deliberately kept minimal, so the client can see where headroom was traded
  away and ask for it back as an explicit, priced option if they want it.
- Where a leaner alternative would change *what* the requirement delivers rather than merely *how* it's
  built, that is not a bare-minimum sizing choice — raise it as an assumption, or send it to `req-analyst`.

**Contingency still applies as usual** (§3), sized from the risk register against the bare-minimum
baseline. Bare-minimum sizing tightens the estimate; it does not remove the uncertainty the register
already priced in — the two are not the same lever, and contingency is never shrunk to compensate for
scope already having been trimmed.

---

## 10. The `rom` lane is estimated more strictly than the others

A ROM (rough order of magnitude) figure is produced with the least design and the least risk information
of any lane, and yet tends to anchor client expectations harder than any later, better-informed number —
the first number said out loud is the one people remember. `req-estimator` responds to that with **more**
discipline on `rom`, not less, which runs opposite to what "rough" suggests:

- **Bare-minimum is mandatory, not best-effort, on every line** — §9.2 applies with no exceptions. There is
  no architecture yet to reveal genuine complexity, so the honest response to that ignorance is the
  leanest defensible reading of each requirement, never a comfortable middle figure.
- **`traditional`/`both` are never produced on `rom`, even on explicit request.** A ROM engagement has the
  thinnest basis of any lane for a second delivery model, and offering one invites exactly the
  anchor-shopping a ROM figure exists to foreclose.
- **`likely` is never quietly rounded up "to be safe."** A ROM's job is a tight, honest band, not a padded
  one — uncertainty belongs in the contingency percentage (§3), a number anyone can see and question, not
  folded invisibly into `likely`.
- **State plainly, in `basis`, that the figure was produced without an architecture and without a risk
  register**, and that it will move — often materially — once `/sa:design` and `/sa:risk` exist. A `rom`
  figure that reads as final is a defect regardless of how carefully it was built.
- **Contingency is still derived, never skipped**, even without a register — from whatever unconfirmed
  integrations and assumptions are visible, or from the requirements' own `to_clarify` count, per the
  fallback already described for `req-estimator` in its `load-inputs` step — stated plainly as weaker for
  the missing register.
- **The §9.1 baseline/optional split still applies**, undiluted. A `rom` figure that quietly includes
  `should`/`could` scope in its headline number is the easiest way for a rough number to be mistaken for a
  firm one.

None of this changes the lane table in `ARTIFACT-SCHEMAS.md §4.1` — `rom` still skips `/sa:design` and
`/sa:risk` by design. It changes how tightly `req-estimator` holds itself to §9 *within* that lighter
pipeline, precisely because less rigor upstream is a reason for more discipline at the estimating step, not
less.

---

**Last revised**: 2026-09-07 (v1.3 — four under-specified rules pinned, each of which an agent could not
previously apply consistently: §1 rounding precision (per-line, PERT, rollup, percentages, and round-on-
output-never-in-storage); §4 the no-calibration-source case, resolving a three-way contradiction between
this file, `req-estimator`'s rules and `req-estimate-critic` dimension 10 that, followed literally, made
every first engagement unestimable — produce-and-label, with a widened `worst`, is the resolution; §4 the
commitment gate's threshold, from "above a trivial size" to 20 MD baseline Likely; §9.1 the
no-`must`-requirements case, where the baseline is `null` rather than `0` and the gap goes back to
`req-analyst` rather than being filled by promoting a `should`.
v1.2, 2026-09-03 — §2 rewritten: AI-assisted is now the only delivery model estimated by
default, `traditional`/`both` are opt-in and require a stated reason; added §9 (must-only baseline, priced
optionality, bare-minimum sizing) and §10 (stricter, bare-minimum-mandatory `rom` lane). v1.1 — added §8,
the screening-band carve-out for `req-screener`. v1.0 — initial codification from the Netrisk
CampaignManager v1/v2 estimates and their risk registers).
