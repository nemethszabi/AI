"""UserPromptSubmit hook: warn when the main-thread context passes the handoff thresholds.

Every turn re-sends the whole context, so cost per turn grows with it; in the 2026-08/09 data, requests
above 150k context were half of all requests and ~68% of spend. The warning fires once per threshold
step (warn, then every `repeat_every_tokens` above it), never blocks the prompt, and at the strong level
also asks Claude to suggest a handoff at the next natural break - not mid-task.

settings.json: hooks.UserPromptSubmit -> python D:/_AI_GIT/_scripts/usage/context_guard.py
"""
import json, os, sys

# Hook JSON in and out is UTF-8; without this Python decodes stdin with the machine's ANSI codepage
# whenever PYTHONIOENCODING/PYTHONUTF8 is absent from the spawning environment.
for _s in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    import usage_lib as U
    G = U.load_config()['guard']
    STATE = os.path.join(U.LOCAL_DIR, 'guard')
except Exception:
    G = {'warn_tokens': 150000, 'strong_tokens': 300000, 'repeat_every_tokens': 100000}
    STATE = os.path.join(os.path.expanduser('~'), '.ai-usage', 'guard')


def last_main_context(path):
    size = os.path.getsize(path)
    with open(path, 'rb') as fh:
        fh.seek(max(0, size - 2_000_000))
        lines = fh.read().splitlines()
    for raw in reversed(lines):
        if b'"usage"' not in raw:
            continue
        try:
            d = json.loads(raw)
        except Exception:
            continue
        u = (d.get('message') or {}).get('usage')
        if d.get('type') == 'assistant' and u and not d.get('isSidechain'):
            return (u.get('input_tokens') or 0) + (u.get('cache_read_input_tokens') or 0) + (u.get('cache_creation_input_tokens') or 0)
    return 0


def main():
    hook = json.load(sys.stdin)
    tp, sid = hook.get('transcript_path'), hook.get('session_id') or 'unknown'
    if not tp or not os.path.isfile(tp):
        return
    ctx = last_main_context(tp)
    warn, strong, step = G['warn_tokens'], G['strong_tokens'], G.get('repeat_every_tokens', 100000)
    bucket = 0 if ctx < warn else 1 + int((ctx - warn) // step)
    os.makedirs(STATE, exist_ok=True)
    sf = os.path.join(STATE, f'{sid}.txt')
    try:
        last = int(open(sf).read().strip() or 0)
    except Exception:
        last = 0
    if bucket != last:
        open(sf, 'w').write(str(bucket))
    if bucket <= last:                      # already warned at this level, or context shrank (compaction)
        return
    k = f'{ctx / 1000:.0f}k'
    out = {'systemMessage': f'Context ~{k} tokens - every turn re-sends all of it. At the next natural break: write a '
                            f'handoff (state, decisions, open questions, next step) to a file, /clear, and reload it. '
                            f'/compact is the lossy fallback.'}
    if ctx >= strong:
        out['hookSpecificOutput'] = {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': f'[context-guard] Main-thread context is ~{k} tokens. Finish the current step first; then, '
                                 f'in one line, suggest the user write a handoff file and continue in a fresh session. '
                                 f'Do not stop or shorten the current task because of this note.'}
    print(json.dumps(out))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        pass                                 # never block or break a prompt
