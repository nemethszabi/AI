"""Claude Code status line: profile, model/effort, context size (colour-coded against the guard
thresholds), session cost, cache hit ratio and 5-hour rate-limit use.

settings.json:  "statusLine": {"type": "command", "command": "python D:/_AI_GIT/_scripts/usage/statusline.py"}
"""
import json, os, sys

sys.stdout.reconfigure(encoding='utf-8')
try:
    import usage_lib as U
    G = U.load_config()['guard']
except Exception:
    G = {'warn_tokens': 150000, 'strong_tokens': 300000}
GREEN, YELLOW, RED, DIM, RESET = '\033[32m', '\033[33m', '\033[31m', '\033[2m', '\033[0m'

try:
    d = json.load(sys.stdin)
except Exception:
    print('statusline: no input'); sys.exit(0)

parts = []
profile = os.path.basename(os.environ.get('CLAUDE_CONFIG_DIR', '') or '').replace('claude-', '')
model = (d.get('model') or {}).get('display_name') or '?'
effort = (d.get('effort') or {}).get('level')
parts.append((f'{DIM}[{profile}]{RESET} ' if profile else '') + model + (f'·{effort}' if effort else ''))

cw = d.get('context_window') or {}
cu = cw.get('current_usage') or {}
ctx = sum(cu.get(k) or 0 for k in ('input_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens'))
if not ctx and cw.get('used_percentage') is not None and cw.get('context_window_size'):
    ctx = cw['used_percentage'] * cw['context_window_size'] / 100
if ctx:
    col = RED if ctx >= G['strong_tokens'] else YELLOW if ctx >= G['warn_tokens'] else GREEN
    hint = ' handoff?' if ctx >= G['warn_tokens'] else ''
    parts.append(f'{col}ctx {ctx / 1000:.0f}k{hint}{RESET}')

c = (d.get('cost') or {}).get('total_cost_usd')
if c is not None:
    parts.append(f'${c:,.2f}')
hr = (d.get('prompt_cache') or {}).get('hit_ratio')
if hr is not None:
    parts.append(f'cache {hr:.0%}')
rl = ((d.get('rate_limits') or {}).get('five_hour') or {}).get('used_percentage')
if rl is not None:
    parts.append(f'5h {rl:.0f}%')
agent = (d.get('agent') or {}).get('name')
if agent:
    parts.append(f'agent {agent}')
print(' │ '.join(parts))
