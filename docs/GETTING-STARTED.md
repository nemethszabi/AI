# Getting Started — your first session with agentic work

This is not the reference map (`USAGE.md`) or the install checklist (`SETUP.md`) — it's the "I've never
actually delegated work to an agent before, walk me through it" guide. Read it once, top to bottom, before
your first real run.

---

## The one concept that explains almost everything

Two different things live in this system, and they behave completely differently:

**Slash commands** (`/dev:quick`, `/sa:clarify`, `/scm:fix`, ...) are thin and run **inline, in this same
conversation**. They can ask you a question mid-run (you'll see a real prompt to answer), they can read a
few files themselves, and their whole job is almost always "figure out what's needed, then hand the real
work to an agent."

**Subagents** (`dev-backend`, `req-analyst`, `dev-reviewer`, ...) are the opposite: **isolated and
single-shot**. When a command dispatches one, it starts a fresh instance with no memory of your
conversation so far — only what the command explicitly tells it. It does its work, writes a report in a
fixed format, and hands that report back. It cannot ask you something mid-task the way a command can; if
it hits a genuine ambiguity it either makes the smallest safe assumption and flags it, or stops and reports
the blocker — it never just pauses and waits for you like a normal chat does.

**What this means practically**: you almost never invoke an agent by name yourself. You type a slash
command; the command decides which agent(s) to dispatch and what to tell them. If a report comes back
looking like it's missing context you thought was obvious, it's usually because the *command* didn't pass
that context along — not because the agent ignored something in your head.

---

## Before your first run

1. **Restart your Claude Code session** after anything gets copied to `~/.claude/`. Agent and command
   lists load once, at session start — this is the single most common "why isn't this working" cause (see
   `SETUP.md`'s troubleshooting section).
2. **Verify the install, don't assume it.** Run `/dev:help` and `/sa:help`. Each should print a static
   command reference. If either errors or isn't found, stop here and fix that first — nothing past this
   point will work either.
3. **Pick a real, low-stakes target for your very first try.** Don't debut this on something you're
   nervous about. Something already scaffolded (CampaignManager, net8-migration) or a throwaway test
   folder both work.

---

## Your first 15 minutes, concretely

Do these in order. Each one builds on confidence from the last.

**1. Check a project's status — pure reading, changes nothing.**
```
cd to a project that already has ai/dev/ (e.g. CampaignManager or net8-migration)
/dev:status
```
You should get back a short report: phase, gates (all `false` right now, everywhere), source-of-truth
pointers. If it says "not initialized," that project needs `/dev:init` first — try that instead.

**2. Watch one full read-only round trip.**
```
/scm:devops-ask "what happens if the shared App Pool recycles while a redeploy is in progress?"
```
(or, in any project) `/sa:clarify "<a small, real idea you've been meaning to write down>"`. Nothing gets
written to source code either way — `devops-ask` is read-only by design, and `clarify` only ever writes
`ai/sa/<slug>/requirements.json` plus its rendered `.md`. This is the safest possible way to see a full
dispatch → report cycle without any risk.

Even gentler, if a document just landed on you: `/doc-brief <path-to-a-docx-or-pdf>`. It reads the
document and hands back a section map, the key facts, and where the gaps are — writing nothing but its own
brief file.

**3. Try one real dispatch that actually touches something.**
Pick something genuinely small — a one-line fix, a copy change, anything you could undo by hand in thirty
seconds if you didn't like the result:
```
/dev:quick "<small, specific task>"          # CampaignManager or any ai/dev/-initialized project
/scm:fix "<small, specific bug description>" # net8-migration
```
**Read the report fully before doing anything else** — see the next section for what to actually look at.

---

## What a report is telling you, and how to read one

Every dispatched agent ends with the same shape (this is deliberate — you should be able to read the
bottom of any report from any agent the same way):

- **Done** — what actually happened, files touched, build/test result. Read this against what you asked
  for, not just "did it say SUCCESS."
- **Deviations** — the agent hit something that didn't match the plan and made a judgment call. This is
  not necessarily bad, but it's exactly where you should look closely — did it choose reasonably?
- **Handoffs** — work the agent spotted but deliberately didn't do, because it was out of its lane
  (e.g. `dev-backend` noticing a frontend change is also needed). This is the system working correctly,
  not a failure to be thorough.
- **Contract issues** — the agent found the interface/contract it was told to build against was wrong or
  incomplete, and stopped rather than guessing. Also the system working correctly.
- **Confidence Level** (fix/req-style reports only) — `High` means the root cause was confirmed by
  actually reading the failing code/log; `Medium` means plausible but not fully confirmed; `Low` means
  best-effort from limited evidence. **Treat `Low` as "review this like you wrote it yourself before
  trusting it," not as a soft failure** — the agent is telling you exactly how much scrutiny it thinks the
  result deserves.

If a report doesn't have Deviations/Handoffs/Contract-issues, it should say "none" explicitly — silence on
one of these (as opposed to an explicit "none") is itself worth double-checking.

---

## The safety rails already built in

The `dev-*` side has no mandatory quality gate (see `dev-framework/DESIGN.md` for why) — **you are the
review step there**, every time. The `/sa:*` side has exactly one: `/sa:package` refuses to build a
client-facing document unless `/sa:audit` passed on the current content. That single exception exists
because it's the only command whose output a client sees.

Several other things are already designed to stop and ask rather than silently proceed:

- `/scm:req` and `/scm:devops-change` show you a full design + implementation plan and wait for an
  explicit approve/change/cancel answer before writing any code.
- Anything touching Azure DevOps (posting a comment, changing a work item's state) always shows you the
  exact comment/tag/state change and asks `[y/n]` — every single run, not just the first time.
- No agent in this system ever runs `git commit` or `git add`. You always commit yourself, which is itself
  a built-in checkpoint — nothing lands in history without you looking at the diff first.
- Genuine ambiguity gets asked about via an explicit question (you'll see it as a real prompt), not
  silently guessed — see `AGENT-CONDUCT-BASELINE.md` A7 if you want the underlying rule.

## When something looks wrong

- **The report looks incomplete or off-topic** — most likely the dispatching command didn't pass enough
  context, not that the agent ignored something. Re-run with a more specific task description.
- **You don't trust a change** — don't accept it. Nothing is committed yet at that point; discard by hand
  or ask for `/scm:review` (net8-migration) for an independent second look before you decide.
- **A command or agent seems to not exist** — restart your session first, then check
  `SETUP.md`'s troubleshooting section.

---

## Where to go once this feels normal

- **`USAGE.md`** — the full "which command for which situation" reference across all your projects.
- **`SA-WORKFLOW.md`** — the requirement→offer pipeline end to end: the three lanes, the five design
  decisions worth understanding, and a worked "inbound TSD → priced offer" example. Read this before any
  presales or bid work.
- **`SETUP.md`** — install/troubleshooting detail, including the rate-card step.
- **`dev-framework/DESIGN.md`** — why the `dev-*` side is shaped the way it is, and the specific conditions
  under which it'd be worth adding real gates/wave orchestration later.
- **`sa-framework/ARTIFACT-SCHEMAS.md`** and **`ESTIMATION-METHOD.md`** — the binding doctrine behind the
  `/sa:*` pipeline. Reference material; you don't need it to use the commands.
