"""Claude Code status line, two rows:

  [scm] scm-stm-merge │ Opus 5 (1M)·medium │ ctx 292k 29% of 1M · handoff advised (>150k) │ +18k/turn
  5h 55% left → 15:51 │ 7d 59% left → Tue 13:41 │ main │ PR #1234 pending │ cache 89% (tools) │ session 18h10 · +156/-23

Row 1 answers "what is this session, and what is it costing?", row 2 "what budget is left, and where am I?"
Identity leads row 1 - profile chip then working folder (moved here from row 2, 2026-09-12: it answers the
same question the chip does, while row 2 is about budget). The two segments that follow are the handoff
decision and nothing else: level then rate - how big the context is, and how fast it is growing.

Cache sits on row 2 (moved 2026-09-12): it is a diagnostic, not a decision. At 96% it says nothing; it
earns attention only when it drops and names a reason, and that is worth a glance, not the primary row.

The folder is the leaf directory, or the last two parts when the leaf is generic
("...\\Mediatel Email replacement\\ai"). Two things are suppressed when they merely restate that folder:
the session name and the git branch - one fact printed twice is worse than a shorter bar. The two
rate-limit windows sit side by side on row 2, because the pair is the decision: "5h fine, week nearly
gone" calls for something different from the reverse.

When the terminal is narrower than a row, segments first shrink to shorter forms and only then drop,
lowest priority first - the context segment and the 5h window never disappear.
COLUMNS is exported by Claude Code before each run.

Deliberately no session $: on a subscription that is a notional API price, not what is billed. Cost lives
in the usage store and the reports (usage_report.py), where it can be compared across tools and models.
The spend-limit window appears only when nearly exhausted; it means nothing on most plans.

settings.json:  "statusLine": {"type": "command", "command": "python D:/_AI_GIT/_scripts/usage/statusline.py",
                               "refreshInterval": 60}
"""
import datetime as dt, json, os, re, sys

# Force UTF-8 both ways: the harness sends UTF-8 JSON, but Python otherwise decodes stdin with the
# machine's ANSI codepage (cp1250 here) unless PYTHONIOENCODING/PYTHONUTF8 happens to be set in the
# spawning environment - which turned accented session names into "KĂ¶ltsĂ©gvetĂ©s".
for _s in (sys.stdin, sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
try:
    import usage_lib as U
    G, LOCAL = U.load_config()['guard'], U.LOCAL_DIR
except Exception:
    G = {'warn_tokens': 150000, 'strong_tokens': 300000}
    LOCAL = os.path.join(os.path.expanduser('~'), '.ai-usage')
STATE_DIR = os.path.join(LOCAL, 'statusline')
GREEN, YELLOW, RED, DIM, RESET = '\033[32m', '\033[33m', '\033[31m', '\033[2m', '\033[0m'
ANSI = re.compile(r'\033\[[0-9;]*m')
SEP = ' │ '


def human(n):
    return f'{n / 1e6:.0f}M' if n >= 1e6 else f'{n / 1000:.0f}k'


def colour(text, col):
    return f'{col}{text}{RESET}' if col and text else text


def seg(priority, col, *variants):
    """One segment, longest form first. `priority` 0 is essential; higher numbers shrink and drop first.
    Segments render in the order given - priority governs degradation only, never position."""
    vs = [colour(v, col) for v in variants if v]
    return (priority, vs) if vs else None


def fit(segments, width):
    """Shrink the least important segment that still has a shorter form; only when nothing can shrink
    any further start dropping, again least important first. Priority 0 survives even if it overflows."""
    items = [s for s in segments if s]
    if not items:
        return ''
    level = [0] * len(items)
    render = lambda: SEP.join(vs[min(l, len(vs) - 1)] for (_, vs), l in zip(items, level))
    while True:
        line = render()
        if len(ANSI.sub('', line)) <= width:
            return line
        shrinkable = [i for i, (_, vs) in enumerate(items) if level[i] < len(vs) - 1]
        if shrinkable:
            level[max(shrinkable, key=lambda i: items[i][0])] += 1
            continue
        if len(items) == 1:
            return render()
        drop = max(range(len(items)), key=lambda i: items[i][0])
        items.pop(drop)
        level.pop(drop)


def window(label, rl, warn_left=30, crit_left=15):
    """('5h 55% left → 18:20', '5h 55% left', '5h 55%', left%) - remaining, NOT used, plus when it comes
    back. GREEN while healthy, yellow at warn_left or below, red at crit_left or below.

    Green matters: this is the only number on the bar that counts DOWN (ctx counts up), so an uncoloured
    "89%" invites being read as 89% consumed and therefore alarming. With green/yellow/red the colour
    carries the meaning and the polarity of the number stops mattering. For the same reason the word
    "left" outlives the reset clock by one degradation step - the bare "5h 89%" form is the ambiguous
    one, so it is the last resort, not the first saving."""
    if not rl or rl.get('used_percentage') is None:
        return None, None, None, 100
    left = 100 - rl['used_percentage']
    short = f'{label} {left:.0f}%'
    mid = short + ' left'
    long = mid
    ts = rl.get('resets_at')
    if ts:
        try:
            t = dt.datetime.fromtimestamp(float(ts))
            long = mid + ' → ' + t.strftime('%a %H:%M' if (t - dt.datetime.now()).total_seconds() > 12 * 3600 else '%H:%M')
        except Exception:
            pass
    col = RED if left <= crit_left else YELLOW if left <= warn_left else GREEN
    return colour(long, col), colour(mid, col), colour(short, col), left


def turn_delta(sid, ctx):
    """How much context the last turn added. The bar re-renders several times per turn, so the last
    non-zero delta is remembered rather than recomputed to zero between renders."""
    if not sid or not ctx:
        return 0
    path = os.path.join(STATE_DIR, f'{sid}.txt')
    prev_ctx = prev_delta = 0
    try:
        prev_ctx, prev_delta = (int(x) for x in open(path, encoding='utf-8').read().split(','))
    except Exception:
        pass
    delta = ctx - prev_ctx if prev_ctx and ctx != prev_ctx else prev_delta
    if ctx != prev_ctx:
        try:
            os.makedirs(STATE_DIR, exist_ok=True)
            open(path, 'w', encoding='utf-8').write(f'{int(ctx)},{int(delta)}')
        except Exception:
            pass
    return delta


GENERIC_LEAF = {'ai', 'src', 'dev', 'app', 'web', 'api', 'client', 'server', 'code', 'docs', 'test', 'tests'}


def folder(path):
    """('scm-stm-merge', 'scm-stm-merge') - the identifying part of the working directory. The leaf alone,
    except when the leaf is a generic name ('...\\Mediatel Email replacement\\ai'), where it says nothing.
    The full path is deliberately not shown: at 50+ characters it would crowd out the reset clocks."""
    if not path:
        return '', ''
    parts = [x for x in path.replace('/', '\\').rstrip('\\').split('\\') if x and not x.endswith(':')]
    if not parts:
        return '', ''
    leaf = parts[-1]
    mid = '\\'.join(parts[-2:]) if leaf.lower() in GENERIC_LEAF and len(parts) > 1 else leaf
    return mid, (mid[:14] + '…' if len(mid) > 14 else mid)


def git_branch(start):
    """Branch name without shelling out - walks up for .git, follows a worktree's gitdir pointer."""
    d = os.path.abspath(start or '.')
    while True:
        g = os.path.join(d, '.git')
        if os.path.exists(g):
            break
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent
    try:
        if os.path.isfile(g):                       # worktree: ".git" is a file pointing at the real dir
            g = os.path.normpath(os.path.join(d, open(g, encoding='utf-8').read().split('gitdir:', 1)[1].strip()))
        head = open(os.path.join(g, 'HEAD'), encoding='utf-8').read().strip()
    except Exception:
        return None
    return head.split('refs/heads/')[-1] if head.startswith('ref:') else head[:7]


def duration(ms, added, removed):
    """('session 18h10 · +1799/-428', 'session 18h10', '18h10') - labelled, so the row reads as prose."""
    t = ''
    if ms:
        m = int(ms // 60000)
        t = f'{m // 60}h{m % 60:02d}' if m >= 60 else f'{m}m'
    edits = f'+{added or 0}/-{removed or 0}' if (added or removed) else ''
    if not t and not edits:
        return '', '', ''
    return (' · '.join(x for x in (f'session {t}' if t else '', edits) if x),
            f'session {t}' if t else edits,
            t or edits)


try:
    d = json.load(sys.stdin)
except Exception:
    print('statusline: no input'); sys.exit(0)
try:
    width = int(os.environ.get('COLUMNS') or 120)
except ValueError:
    width = 120

# ---- row 1: who am I, and how full is the context ----------------------------------------------
profile_name = os.path.basename(os.environ.get('CLAUDE_CONFIG_DIR', '') or '').replace('claude-', '')
chip = f'{DIM}[{profile_name}]{RESET} ' if profile_name else ''

# Identity block: which config root, and which folder. The chip rides on the folder rather than the model,
# so the row opens with "which session am I looking at" before it says anything about cost.
ws, wt = d.get('workspace') or {}, d.get('worktree') or {}
cwd = ws.get('current_dir') or d.get('cwd')
folder_long, folder_short = folder(cwd)
if folder_long:
    place = seg(1, None, chip + folder_long, chip + folder_short)
else:
    place = seg(1, None, chip.rstrip()) if chip else None

model = ((d.get('model') or {}).get('display_name') or '?')
model_short = re.sub(r'\s*\([^)]*\)', '', model)
eff = f"·{(d.get('effort') or {}).get('level')}" if (d.get('effort') or {}).get('level') else ''
fast = ' ⚡' if d.get('fast_mode') else ''
who = seg(2, None, model.replace(' context)', ')') + eff + fast, model_short + eff + fast, model_short)

# The session name earns its place only when it says something the folder doesn't - the same rule the
# branch has always followed. "scm-stm merge" beside "scm-stm-merge" is one fact printed twice.
squash = lambda s: re.sub(r'[^a-z0-9]', '', (s or '').lower())
name = d.get('session_name') or ''
if name and folder_long and squash(name) == squash(folder_long):
    name = ''
name_seg = seg(5, None, name, name[:16] + '…' if len(name) > 16 else name) if name else None

cw = d.get('context_window') or {}
cu = cw.get('current_usage') or {}
size = cw.get('context_window_size') or 0
ctx = sum(cu.get(k) or 0 for k in ('input_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens'))
if not ctx and cw.get('used_percentage') is not None and size:
    ctx = cw['used_percentage'] * size / 100
ctx_seg = growth = None
if ctx:
    pct = f' {ctx / size * 100:.0f}%' if size else ''
    if ctx >= G['strong_tokens']:
        col, tail, mark = RED, f" · handoff now (>{human(G['strong_tokens'])})", '!!'
    elif ctx >= G['warn_tokens']:
        col, tail, mark = YELLOW, f" · handoff advised (>{human(G['warn_tokens'])})", '!'
    else:
        col, tail, mark = GREEN, '', ''
    ctx_seg = seg(0, col, f'ctx {human(ctx)}{pct}{f" of {human(size)}" if size else ""}{tail}',
                  f'ctx {human(ctx)}{pct}{" · handoff" if mark else ""}',
                  f'ctx {human(ctx)}{mark}')
    delta = turn_delta(d.get('session_id'), ctx)
    if delta > 0:                                   # how fast this session is filling up
        growth = seg(3, DIM, f'+{human(delta)}/turn', f'+{human(delta)}')

# The miss reason matters more than the ratio: "tools" means the tool/MCP set moved mid-session and the
# whole prefix was rewritten, which at a large context is the single most expensive event there is.
# Abbreviated so it survives the width budget - the raw names are long enough to get the segment shrunk.
CAUSE_SHORT = {'tools_changed': 'tools', 'ttl_expired': 'ttl', 'system_prompt_changed': 'system',
               'messages_edited': 'edited', 'model_changed': 'model', 'cache_disabled': 'off'}
pc = d.get('prompt_cache') or {}
hr = pc.get('hit_ratio')
cache = None
if hr is not None:
    raw = ((pc.get('last_miss_cause') or {}).get('causes') or [None])[0]
    cause = CAUSE_SHORT.get(raw, (raw or '')[:8])
    body = f'cache {hr:.0%}'
    cache = seg(5, None, f'{body} ({cause})' if cause and hr < 0.98 else body, body, f'c{hr:.0%}')

# ---- row 2: budget left, and where the work is -------------------------------------------------
rls = d.get('rate_limits') or {}
five_long, five_mid, five_short, _ = window('5h', rls.get('five_hour'))
seven_long, seven_mid, seven_short, _ = window('7d', rls.get('seven_day'))
spend_long, spend_mid, spend_short, spend_left = window('spend', rls.get('spend_limit'))
branch = wt.get('branch') or git_branch(cwd)
if branch and folder_long and folder_long.lower() == branch.lower():
    branch = None                               # row 1 already said it
branch_seg = seg(2, None, f"{branch}{f' ({wt['name']})' if wt.get('name') else ''}", branch[:18]) if branch else None
pr = d.get('pr') or {}
pr_seg = None
if pr.get('number'):
    state = pr.get('review_state') or ''
    kind = 'MR' if pr.get('kind') == 'mr' else 'PR'
    pr_seg = seg(3, GREEN if state == 'approved' else RED if state == 'changes_requested' else DIM,
                 f"{kind} #{pr['number']}" + (f' {state}' if state else ''), f"{kind} #{pr['number']}")
dur = duration((d.get('cost') or {}).get('total_duration_ms'),
               (d.get('cost') or {}).get('total_lines_added'),
               (d.get('cost') or {}).get('total_lines_removed'))

print(fit([place, name_seg, who, ctx_seg, growth], width))
row2 = fit([seg(0, None, five_long, five_mid, five_short),
            seg(1, None, seven_long, seven_mid, seven_short),
            branch_seg,
            pr_seg,
            seg(4, None, spend_long, spend_mid, spend_short) if spend_left <= 25 else None,
            cache,
            seg(6, None, *dur)], width)
if row2:
    print(row2)
