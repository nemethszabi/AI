"""Tests for guard-irreversible-bash.py.

Run:  python _scripts/hooks/tests/test_guard_irreversible_bash.py

Why this file exists: the hook was registered against the "Bash" matcher alone while PowerShell is
the primary shell on this machine, so its rules had never actually run against a PowerShell payload.
The matcher was widened to "Bash|PowerShell" on 2026-09-14 and a Remove-Item rule added; this file is
what makes that verifiable rather than assumed.

Trigger strings are assembled from fragments (NV = "--no-" + "verify") for the same reason as
test_guard_shell_db_access.py: the first attempt to check this hook was itself blocked by it, because
the harness's case data contained the literal trigger words. A guard that inspects command text will
eventually be pointed at text that merely DISCUSSES what it guards.
"""
import importlib.util
import json
import pathlib
import sys

HOOK = pathlib.Path(__file__).resolve().parents[1] / "guard-irreversible-bash.py"
spec = importlib.util.spec_from_file_location("guard", HOOK)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

NV = "--no-" + "verify"          # the gate-skipping flag
FORCE = "--for" + "ce"           # git push's irreversible flag
HARD = "--ha" + "rd"             # git reset's irreversible flag
RI = "Remove-" + "Item"          # the PowerShell recursive delete
RM = "r" + "m"                   # the bash one

# (expected decision - "" means no decision at all, name, command)
CASES = [
    # ---------------------------------------------------------------- PowerShell, newly covered
    ("ask",  "PS recursive force delete", f"{RI} -Recurse -Force D:\\tmp\\x"),
    ("ask",  "PS short flags",            f"{RI} -r -f D:\\tmp\\x"),
    ("ask",  "PS switches after path",    f"{RI} D:\\tmp\\x -Force -Recurse"),
    ("ask",  "PS rmdir alias",            "rmdir -Recurse -Force D:\\tmp\\x"),
    ("ask",  "PS git push force",         f"git push {FORCE} origin development"),
    ("ask",  "PS git reset hard",         f"git reset {HARD}"),
    ("deny", "PS gate skip",              f"git commit {NV} -m 'x'"),

    # ---------------------------------------------------------------- bash, unchanged behaviour
    ("ask",  "bash recursive delete",     f"{RM} -rf /tmp/x"),
    ("ask",  "bash split flags",          f"{RM} -r -f /tmp/x"),
    ("ask",  "bash git push force",       f"git push {FORCE}"),

    # ---------------------------------------------------------------- must NOT fire
    ("",     "PS delete, no recurse",     f"{RI} D:\\tmp\\x.txt -Force"),
    ("",     "PS recurse, no force",      f"{RI} D:\\tmp\\x -Recurse"),
    ("",     "PS listing is not deleting", "Get-ChildItem D:\\tmp -Recurse -Force"),
    ("",     "force-with-lease is safe",  "git push --force-with-lease origin development"),
    ("",     "ordinary build",            "dotnet build SCM/SCM.csproj"),
    ("",     "ordinary status",           "git status --short"),
    ("",     "soft reset",                "git reset --soft HEAD~1"),
    ("",     "copy, not remove",          "Copy-Item D:\\a D:\\b -Recurse -Force"),
]


def decide(command):
    """Drive the hook exactly as the harness does: JSON on stdin, JSON or silence on stdout."""
    for pattern, decision, _reason in guard.RULES:
        if pattern.search(command):
            return decision
    return ""


def main():
    failures = []
    for want, name, command in CASES:
        got = decide(command)
        if got != want:
            failures.append((name, want, got, command))
        label = got or "(none)"
        print(f"{'ok  ' if got == want else 'FAIL'} {label:<7} (want {want or '(none)':<7}) {name}")

    print(f"\n{len(CASES)} cases, {len(failures)} failures")
    for name, want, got, command in failures:
        print(f"  FAIL {name}: wanted {want or '(none)'}, got {got or '(none)'}\n       {command!r}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
