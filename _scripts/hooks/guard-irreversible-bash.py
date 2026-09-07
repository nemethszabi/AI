#!/usr/bin/env python
"""
PreToolUse guard hook for the Bash tool - the structural half of CONSTITUTION.md Articles II and III.

Added 2026-09-05 (framework-review F-12/C-11). Article II ("destructive actions require confirmation
every time") and Article III ("never weaken a gate") were until now enforced only by asking models to
comply. Anthropic's own guidance: an instruction in a doctrine file "is a request, not a guarantee. A
PreToolUse hook that blocks the edit is enforcement."

Deliberately narrow. O-03's warning in that review: a hook that blocks too broadly becomes something you
disable under deadline pressure, which is worse than the instruction. Only these four are matched:

  git push --force      -> ask   (Article II - irreversible for everyone else on the branch)
  git reset --hard      -> ask   (Article II - discards uncommitted work irrecoverably)
  rm -rf                -> ask   (Article II - no undo)
  --no-verify           -> deny  (Article III - its entire purpose is skipping a gate)

"ask" forces the confirmation Article II requires; it does not forbid the command. Only --no-verify is
denied outright, because unlike the others it has no legitimate form - it exists to bypass a check.
--force-with-lease is deliberately NOT matched: it is the safe variant and blocking it would push people
toward plain --force.

Reads the hook payload as JSON on stdin, writes a permission decision as JSON on stdout, always exits 0.
On any parse failure it stays silent and allows - a guard that breaks the Bash tool would be turned off
within a day, and this hook is not the only control in the system.
"""

import json
import re
import sys

# (compiled pattern, decision, human-readable reason)
RULES = [
    (
        re.compile(r"--no-verify\b"),
        "deny",
        "--no-verify skips a commit/push gate. CONSTITUTION.md Article III: never weaken a gate. "
        "Fix what the gate is reporting instead of bypassing it.",
    ),
    (
        re.compile(r"\bgit\s+push\b[^\n]*?(?:--force(?!-with-lease)\b|\s-f\b)"),
        "ask",
        "git push --force rewrites history other clones already have. CONSTITUTION.md Article II "
        "requires explicit confirmation. --force-with-lease is the safer form and is not gated.",
    ),
    (
        re.compile(r"\bgit\s+reset\b[^\n]*?--hard\b"),
        "ask",
        "git reset --hard discards uncommitted work with no undo. CONSTITUTION.md Article II "
        "requires explicit confirmation.",
    ),
    (
        # -rf, -fr, -Rf, and the split -r -f / -f -r forms
        re.compile(r"\brm\s+(?:-[a-zA-Z]*[rR][a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*[rR])[a-zA-Z]*\b"
                   r"|\brm\s+(?:-[rR]\s+-f|-f\s+-[rR])\b"),
        "ask",
        "rm -rf deletes recursively with no undo. CONSTITUTION.md Article II requires explicit "
        "confirmation. Check what the path actually resolves to before approving.",
    ),
]


def main():
    try:
        payload = json.load(sys.stdin)
        command = payload.get("tool_input", {}).get("command", "") or ""
    except Exception:
        return  # fail open - see module docstring

    for pattern, decision, reason in RULES:
        if pattern.search(command):
            json.dump(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": decision,
                        "permissionDecisionReason": reason,
                    }
                },
                sys.stdout,
            )
            return


if __name__ == "__main__":
    main()
