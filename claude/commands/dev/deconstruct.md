---
name: dev:deconstruct
description: Turn an existing app's UI into a rebuild spec - dispatches dev-ui-analyst against a running URL, screenshots, and/or a source tree, producing ai/context/<slug>-ui-spec.md with every finding marked measured/observed/inferred/gap.
allowed-tools:
  - Read
  - Glob
  - Agent
  - AskUserQuestion
argument-hint: "<url | image path | source path> [more inputs...] [--slug=<name>]"
---

> Version: 1.1.0 — agent-review findings applied, 2026-09-07

<objective>
`/dev:deconstruct <inputs>` produces the spec needed to rebuild an application's interface, by dispatching
`dev-ui-analyst`. Inputs can be mixed freely — a running URL, one or more screenshots, an existing source
tree — and mixing them is the best case, since each covers what the others cannot.

The output is a spec, not code. Feed it to `/dev:build --from-spec=<path>` to actually rebuild.
</objective>

<process>
<step name="resolve-inputs">
Classify each argument: `http(s)://` → live URL; an existing image file → static; an existing directory →
source tree. Resolve `--slug` if given, otherwise derive one from the app name or the URL host.

If nothing resolves to a usable input, stop and say so. Do not dispatch with an app name alone — the agent
would have nothing to analyse and is required to decline.
</step>

<step name="check-authorisation">
For a live URL that is not `localhost`/`127.0.0.1`, confirm with `AskUserQuestion` that the user is
authorised to drive an automated browser against it before dispatching. Analysing someone else's running
application is an outward-facing action, and a rebuild is a use of it that its operator may care about.

**That test is the whole rule — there is no self-owned exemption.** A target the user owns is confirmed in
one keystroke, whereas an exemption would need the command to somehow know whose server it is without
asking, which is exactly the question being skipped. Article VII also forbids carrying one approval to the
next target, so this fires per URL, per run, every time.

If the target needs a login, ask how the agent should authenticate — and take credentials as an
environment-variable reference, never as a literal pasted into the dispatch (Article I).
</step>

<step name="dispatch">
Dispatch `dev-ui-analyst` via `Agent` with every resolved input, the slug, and any auth arrangement. The
agent decides its own mode (LIVE/STATIC/SOURCE/MIXED) from what actually turns out to be reachable.
</step>

<step name="relay">
Return the agent's report. Lead with the **confidence split** — measured/observed/inferred/gap counts — and
the top gaps, because those are what determine whether the spec is ready to build from or still needs a
human. A spec that is mostly `inferred` is a starting point, not a specification, and saying so is more
useful than reporting how many screens were covered.

Put any `## Blocking questions` to the user with `AskUserQuestion`.
</step>
</process>

<rules>
- **Thin dispatcher only.** No `Write`/`Edit`/`Bash`.
- **Confirm before driving a browser against a non-local target**, every time — a prior confirmation for
  one target does not authorise another (Article VII).
- **Never pass a literal credential into the dispatch.** Environment-variable reference or nothing
  (Article I).
- **Never relay the spec as if it were complete.** The confidence split and the gap list lead the summary.
</rules>
