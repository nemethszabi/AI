# dev framework — House .NET Stack Profile

**Binding on `dev-scaffolder`.** Advisory to every other `dev-*` agent: once a project has its own
`ai/context/*.md`, that file's *observed* conventions win over this one's defaults — an agent implementing
into an existing codebase follows the codebase (`PRINCIPLES.md` §5), not this profile.

This file exists because the `dev-*` family is deliberately stack-generic: every agent pulls stack facts
from the target project's own context files and hardcodes none. That works for brownfield work and breaks
completely on greenfield, where there is no context file and no code to observe. Without a house profile,
every new demo app gets whatever stack the model reached for that day, and "vibe coding" produces a pile of
mutually inconsistent skeletons instead of a set of apps that look like one person built them.

Scope: **.NET full-stack demo and prototype applications.** Not a rule for client production work, where
the client's own standards win, and not a constraint on any existing repo.

---

## Rule 0 — versions are detected, never asserted

**No agent may write a framework version, SDK version, or package version into a project from memory.**
Run the tool and record what it actually reported:

```bash
dotnet --version          # SDK actually in use
dotnet --list-sdks        # what's available to pick from
dotnet --list-runtimes    # what can actually run
```

Target the newest **LTS** the installed SDK supports unless the ask names a version. Record the resolved
version in the project's own `ai/context/<slug>-context.md` §3 and in `ai/dev/config.json`. A version
number that entered a project without a command behind it is a defect even when it happens to be right
(`AGENT-CONDUCT-BASELINE.md` D2) — and here it is a defect that fails the build rather than just
misinforming a reader.

The same rule covers NuGet packages: add them with `dotnet add package <name>` and let the tool resolve the
version. Never hand-write a `<PackageReference Version="...">` from memory.

---

## 1. Solution layout

Two shapes. Pick the smaller one unless the ask genuinely needs the larger.

**Compressed — the default for a demo app** (one API, one UI, one test project):

```
<Name>.sln
src/<Name>.Api/          ASP.NET Core host: endpoints, DTOs, EF Core DbContext, domain types
src/<Name>.Web/          frontend (omit entirely if the demo is API-only or Blazor-hosted-in-Api)
tests/<Name>.Tests/      xUnit
README.md                how to run it, in two commands or fewer
```

**Layered — only when the ask involves more than one consumer, a real domain, or a stated architecture
requirement:**

```
<Name>.sln
src/<Name>.Api/              host + endpoints + DTOs only
src/<Name>.Domain/           entities, value objects, domain services — no project references out
src/<Name>.Infrastructure/   EF Core DbContext, repositories, external clients
src/<Name>.Web/              frontend
tests/<Name>.UnitTests/
tests/<Name>.IntegrationTests/
```

**Do not scaffold the layered shape "so it can grow later."** A four-project solution for a demo CRUD app
is the single most common way this profile gets misapplied — `DESIGN-PRINCIPLES-BASELINE.md` #10 argues
against building for a hypothetical, and a demo's whole value is that a human can read all of it.

## 2. Default choices

| Concern | Default | Deviate when |
|---|---|---|
| API style | ASP.NET Core **Minimal APIs**, endpoints grouped one static class per feature, registered via an extension method | The ask names MVC, or the demo rebuilds something controller-shaped |
| Frontend | **Blazor** (Server for a demo — no API hop, no WASM download, simplest to run) | The ask names React/Vue/Angular, or a rebuild target's UI is that framework — then **React + TypeScript + Vite** |
| Styling | Blazor: isolated `.razor.css` per component. React: **Tailwind** | The rebuild target has its own design system to match |
| Data access | **EF Core**, code-first, migrations committed | The ask names Dapper/raw SQL, or there is no persistence at all |
| Database | **SQLite** file, created and seeded on startup | The ask names SQL Server/Postgres — then still local, still disposable |
| Validation | Built-in `DataAnnotations` + a minimal-API filter | Rules outgrow attributes → FluentValidation |
| Logging | **Serilog** to console, structured | The ask needs sinks/correlation |
| Configuration | `appsettings.json` + `appsettings.Development.json` + **user-secrets** for anything secret | Never — see §4 |
| Auth | **None.** A demo gets no login screen unless the ask asks for one | The ask asks. Then ASP.NET Core Identity, or the target's real scheme. **Never hand-rolled crypto or hand-rolled token validation** |
| Tests | **xUnit**, `WebApplicationFactory<T>` for endpoint tests | The ask names another runner |
| API docs | OpenAPI via the built-in ASP.NET Core support, exposed in Development only | — |
| Local orchestration | Plain `dotnet run` | The demo genuinely needs multiple processes (API + separate SPA dev server + a container DB) → **.NET Aspire**, but only after confirming the workload is actually installed. Do not pick Aspire and then discover it is missing |
| Source control | `git init` + one initial local commit, with a .NET `.gitignore` | Never a remote, never a push — Article VII |

**Verify before choosing, don't assume:** Aspire, EF tooling (`dotnet-ef`), and Tailwind's toolchain are all
optional installs on a given machine. Check for the tool, and if it is absent, either install it as an
explicit, reported step or pick the default that does not need it. Discovering a missing workload halfway
through a scaffold is how a "working skeleton" turns into a broken one.

## 3. What a scaffold must produce before it reports success

A skeleton nobody can run is worth less than no skeleton, because it looks finished. Every scaffold ends
with a **vertical slice that actually executes**:

1. `dotnet build` succeeds with **no warnings introduced by the scaffold itself**.
2. The app starts and serves at least one real route — a health endpoint plus one feature endpoint that
   returns seeded data, not a template placeholder.
3. If there is a UI: one page that renders that real data, reachable from the app's start URL.
4. `dotnet test` runs and passes with at least one meaningful test — one that would fail if the endpoint
   broke. A test asserting `true == true` is worse than no test project.
5. `README.md` states the exact commands to build, run, and test, and the URL the app listens on.

Report the actual command output for 1, 2 and 4. "The build should succeed" is not a build result
(`CONSTITUTION.md` Article IV).

## 4. Non-negotiables that survive "it's only a demo"

Demo status relaxes architecture. It relaxes nothing below.

- **No secrets in committed files** — not in `appsettings.json`, not in a connection string, not in a
  seeded user record, not in the README. User-secrets or environment variables (Article I).
- **No EF migration run against anything but a local, disposable database.** `dotnet ef database update`
  pointed at a shared or remote connection string is a destructive action requiring explicit confirmation
  (Article II).
- **No disabled analyzer, no skipped test, no `<NoWarn>` added to make a build go green** (Article III).
- **No `--force`, no `git push`, no cloud provisioning, no container registry, no deployment.** A demo app
  is local until a human says otherwise (Article VII).
- **No seeded PII.** Seed data is obviously synthetic — `Ada Lovelace`, not a real name pulled from
  anywhere (Article VIII).

## 5. Rebuild mode — when the app is reconstructed from an existing one

When scaffolding from a `ui-spec` produced by `dev-ui-analyst`, or from an existing source tree:

- **The original's stack does not override this profile.** Observing that the original was Angular + Java
  is an input to the *spec*, not a reason to scaffold Angular + Java. Rebuild in the house stack unless the
  ask explicitly says to match the original's technology.
- **The original's UI *does* override this profile's styling defaults.** Layout, spacing, colour and
  component structure come from the spec — that is the entire point of a rebuild.
- **Never reproduce the original's credentials, seeded personal data, branding assets, or copyrighted
  content** into the rebuild. Reconstruct structure and behaviour; substitute placeholder content.

---

**Amendment procedure**: edit this file directly; the git commit message is the change rationale. Takes
effect once copied to `~\.claude\dev-framework\STACK-DOTNET.md`.

**Added 2026-09-07** — alongside `dev-scaffolder`, `dev-planner`, `dev-ui-analyst` and `/dev:build`. The
gap this closes: the `dev-*` family could not start a project from zero, because every agent in it resolves
stack facts by reading a context file that greenfield does not have. See `DESIGN.md`'s amendment record.
