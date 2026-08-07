# Design Principles — Baseline

A reusable checklist for bootstrapping a project's own `ai/context/design-principles.md`. This file is
**not binding on any project by itself** — it's a menu to walk through once, per project, when deciding
what should become an enforced rule for that specific codebase. Global, cross-project; stage here, copy
to `~\.claude\DESIGN-PRINCIPLES-BASELINE.md` alongside the agents/commands once reviewed.

Synthesized from two real, previously-validated sources rather than invented from scratch:
`d:\_SCM_GIT\net8-migration\ai\context\scm-context.md §22` (12 non-negotiable SCM rules) and
`d:\_SCM_GIT\net8-migration\ai\prompts\design-architect\design-architect.md`'s own design-principles
section — generalized away from SCM-specific vocabulary (AutoMapper, Club/Customer areas) into the
underlying, stack-agnostic principle each one actually expresses.

---

## How to use this file

1. Run `solution-analyst` (or use an existing context file) — its **§6 "Conventions Observed"** section
   is descriptive input: what the code actually does today.
2. Walk the checklist below, item by item, against those observed conventions. For each:
   - **Applies as-is** → write the project-specific statement into `ai/context/design-principles.md`.
   - **Applies, adapted** → write the project's own concrete version (e.g. "Layer discipline" becomes
     "Controllers → Services → Repositories. No skipping." for a layered .NET app, or "Handlers →
     Use-cases → Adapters" for a hexagonal one).
   - **Doesn't apply** → skip it, don't force-fit.
   - **Missing from this list, but real for this project** → add it (e.g. SCM's payment-orchestration
     rule, §11 below, started life as project-specific before being generalized back into this baseline).
3. **Only explicitly-confirmed items get written.** Nothing is auto-promoted from "observed" to
   "enforced" — same discipline as `CONSTITUTION.md` Article X in the reference framework this pattern
   is drawn from ("patterns proposed for promotion require explicit user approval — never auto-promote").
4. The resulting `ai/context/design-principles.md` is prescriptive, not descriptive — treat edits to it
   as human-gated, not something any agent auto-appends (unlike a living pattern log such as
   `scm-bug-patterns.md`, which is safe to auto-append because it only records observations).

Suggested project-file format — one row per confirmed principle, so provenance stays visible:

```markdown
| # | Principle | Project-specific rule | Source |
|---|---|---|---|
| 1 | Layer discipline | Controllers → Services → Repositories. No skipping. | baseline #1, confirmed as-is |
| 7 | Isolation boundaries | Club and Customer areas do not reference each other. | baseline #7, adapted |
| — | (project-specific, not in baseline) | Payment starts only via IGenericPayment.PaymentTransactionStart(). | added — see §9 payment model |
```

---

## The checklist

### 1. Layer discipline
Dependencies point one way through defined layers (e.g. presentation → application/service →
data-access). No layer calls back up, no layer is skipped to reach one further down.

### 2. Dependency injection over statics
Prefer constructor/interface injection over static accessors, service locators, or global mutable
state. Static access is acceptable only where the framework leaves no alternative (e.g. a templating
layer without DI support) — and should be named as the accepted exception, not silently tolerated.

### 3. One responsibility per component
Each service/module owns one domain concept. No god-objects accumulating unrelated responsibilities as
convenience accretes around them.

### 4. One data-access path per resource
No ad-hoc direct data-store access scattered across the codebase for the same resource — one
repository/access-layer method per aggregate, reused, not re-implemented per call site.

### 5. Boundary types, not internal types, cross layers
The application/service layer speaks in DTOs or equivalent, not raw persistence entities. The
presentation layer speaks in view/request models, not the service layer's DTOs directly. Internal
representations don't leak across a layer boundary.

### 6. Centralize mapping/transformation logic
Object-to-object mapping between layers lives in one defined place (a mapper/profile/adapter layer), not
hand-rolled inline at every call site — so a shape change has one place to update, not many.

### 7. Isolation boundaries between bounded contexts
Distinct functional areas (modules, "areas," bounded contexts, tenant boundaries) don't reference each
other's internals directly. Shared logic moves to an explicitly common layer instead of being duplicated
or cross-referenced.

### 8. Backward compatibility on public contracts
Anything another system or client depends on — APIs, UI contracts, data formats, event schemas — doesn't
regress silently. A breaking change is a deliberate, called-out decision, not a side effect.

### 9. Minimal scope
Do only what was asked. If something else worth fixing is discovered along the way, report it
separately rather than folding it into the current change unasked.

### 10. No premature abstraction
Don't generalize until at least a few (2-3+) concrete cases actually justify the generalization. A
one-off doesn't need a framework built around it.

### 11. Critical paths through one orchestration point
Anything sensitive or hard to undo if done wrong — payments, auth state changes, irreversible external
side effects — has exactly one sanctioned entry point in code. Nothing bypasses it to mutate the
underlying state directly, even for a "simple" case.

### 12. Explicit error handling on domain failures
Known domain-level failure conditions are caught and translated into meaningful, actionable responses —
not swallowed silently, and not surfaced to the caller as an undifferentiated generic failure.

### 13. Consistent, discoverable naming and location conventions
Given a type/concept name, its file location, its test location, and its related artifacts (DTO, mapper,
view) should be predictable from a stated convention — not tribal knowledge.

### 14. Tests as a design discipline, where a test suite exists
New logic ships with a failing-then-passing test where the codebase already has a test culture; note
explicitly if a project has none yet rather than silently skipping the question.

---

## Provenance note

Items 1-2, 5-6, 9-10 map directly to `scm-context.md §22` items 1-2, 5-6, 9-10. Items 3-4, 7-8, 11-12
are the generalized form of SCM items 3-4 (service/repository-per-domain), 7-8 (areas/UI contracts),
11-12 (payment orchestration/domain exceptions). Items 13-14 are additions not present in the SCM
source — 13 generalizes `scm-context.md §17`'s file-path-resolution table into a named principle; 14 was
absent from the SCM source entirely (worth noting as a real gap there, not just an addition here).
