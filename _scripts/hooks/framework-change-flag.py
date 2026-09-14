"""PostToolUse hook: notice when a session edits framework or prompting files, and ask Claude - once per
session - to suggest /doc-sync at the next natural break.

Why a hook and not an instruction: a written "remember to document" rule is exactly the kind of thing a long
session forgets, and long sessions are where framework edits pile up. The hook never blocks, never edits
anything, and fires its reminder once; every further matching path is only appended to the session's list,
which /doc-sync reads.

What counts (path contains, case-insensitive, forward slashes):
  - the staging repo named by `staging_repo` in framework-data/scope.yaml (except its results/ and logs)
  - any `/.claude/` folder (agents, commands, skills, CLAUDE.md, settings.json) - not settings.local.json
  - any `/ai/prompts/`, and any file named CLAUDE.md, CONSTITUTION.md or *-BASELINE.md
Never counted: the knowledge base itself (`knowledge_base` in scope.yaml - editing docs must not re-trigger
a doc sync), ai/handoff/, ai/reports/, ai/results/, ai/design/, ai/dev/.

Claude Code  - settings.json: hooks.PostToolUse -> matcher "Edit|Write|MultiEdit|NotebookEdit"
               -> python "D:/_AI_GIT/_scripts/hooks/framework-change-flag.py"
Copilot CLI  - ~/.copilot/hooks/framework-change-flag.json (staged at copilot/hooks/), event postToolUse.
               Added 2026-09-14. Payload is camelCase (toolName, toolArgs, sessionId), there is no matcher,
               so the tool filter is done here; output is a top-level additionalContext. /doc-sync is
               Claude-only, so the Copilot reminder says to finish the change from Claude Code.
Session lists: ~/.ai-usage/docsync/<session_id>.txt
"""
import json, os, re, sys

for _s in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

STATE = os.path.join(os.path.expanduser('~'), '.ai-usage', 'docsync')
NEVER = ('/ai/handoff/', '/ai/reports/', '/ai/results/', '/ai/design/', '/ai/dev/', 'settings.local.json',
         '/_scripts/sync-check.log', '/__pycache__/')


def norm(p):
    return os.path.expandvars(str(p)).replace('\\', '/').rstrip('/').lower()


def scope_values():
    """staging_repo and knowledge_base from scope.yaml, without a YAML dependency."""
    roots = [os.environ.get('CLAUDE_CONFIG_DIR') or '', os.path.join(os.path.expanduser('~'), '.claude')]
    for r in roots:
        f = os.path.join(r, 'framework-data', 'scope.yaml') if r else ''
        if f and os.path.isfile(f):
            vals = {}
            for line in open(f, encoding='utf-8', errors='replace'):
                m = re.match(r'^(staging_repo|knowledge_base):\s*["\']?(.+?)["\']?\s*$', line)
                if m:
                    vals[m.group(1)] = norm(m.group(2))
            return vals
    return {}


def counts(path, scope):
    p = norm(path)
    if any(n in p for n in NEVER):
        return False
    kb = scope.get('knowledge_base')
    if kb and p.startswith(kb + '/'):
        return False
    staging = scope.get('staging_repo')
    if staging and p.startswith(staging + '/') and '/results/' not in p:
        return True
    name = p.rsplit('/', 1)[-1]
    return ('/.claude/' in p or '/ai/prompts/' in p or name in ('claude.md', 'constitution.md')
            or name.endswith('-baseline.md'))


COPILOT_WRITE_TOOLS = ('edit', 'create', 'write')    # Copilot's view tool also carries a path - never count it


def read_payload(hook):
    """(path, session_id, tool) from either tool's payload; path is None when nothing was written."""
    if 'toolName' in hook:                  # Copilot CLI
        if str(hook.get('toolName', '')).lower() not in COPILOT_WRITE_TOOLS:
            return None, None, 'copilot'
        args = hook.get('toolArgs') or {}
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {}
        path = args.get('path') or args.get('file_path') or args.get('filePath') if isinstance(args, dict) else None
        return path, hook.get('sessionId'), 'copilot'
    ti = hook.get('tool_input') or {}       # Claude Code
    return ti.get('file_path') or ti.get('notebook_path'), hook.get('session_id'), 'claude'


def main():
    hook = json.load(sys.stdin)
    path, session, tool = read_payload(hook)
    if not path or not counts(path, scope_values()):
        return
    os.makedirs(STATE, exist_ok=True)
    sf = os.path.join(STATE, f"{session or 'unknown'}.txt")
    first = not os.path.isfile(sf)
    seen = set() if first else set(open(sf, encoding='utf-8').read().splitlines())
    if path not in seen:
        with open(sf, 'a', encoding='utf-8') as fh:
            fh.write(path + '\n')
    if not first:
        return
    if tool == 'copilot':
        print(json.dumps({'additionalContext': (
            f'[doc-sync] This session changed a framework/prompting file ({path}). Do not interrupt the current '
            f'task. When it reaches a natural end, suggest once, in one line: make sure the change is staged in '
            f'the staging repo (never only at ~/.copilot), then run /doc-sync from Claude Code to document, roll '
            f'out, commit and back it up - Copilot CLI has no /doc-sync.')}))
    else:
        print(json.dumps({'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': f'[doc-sync] This session changed a framework/prompting file ({path}). Do not '
                                 f'interrupt the current task. When it reaches a natural end, suggest once, in one '
                                 f'line: run /doc-sync to update the knowledge base, roll out and back up.'}}))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass                                 # never block or break a tool call
