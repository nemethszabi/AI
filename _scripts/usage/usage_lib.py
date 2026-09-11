"""Shared pieces of the AI usage toolkit: config, store, pricing, task classification.

Config: usage-config.json next to this file holds generic defaults (no machine paths);
~/.ai-usage/config.json (or $AI_USAGE_CONFIG) overrides it per machine - store path, Claude roots,
cwd->task rules, excluded folders. Store: one SQLite file, one row per model request, tool-agnostic,
so every collector (Claude, Copilot, anything later) fills the same `requests` shape.
Costs are NOT stored for list-priced tools - they are computed at report time from pricing.json, so a
price correction re-prices history without re-collecting (transcripts may be gone by then).
"""
import fnmatch, glob, json, os, re, sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')
LOCAL_DIR = os.path.join(HOME, '.ai-usage')

SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
  tool TEXT NOT NULL, req_key TEXT NOT NULL, account TEXT, project TEXT, cwd TEXT, session_id TEXT,
  ts TEXT, model TEXT, effort TEXT, agent TEXT, run_id TEXT, skill TEXT, is_subagent INTEGER,
  initiator TEXT, input INTEGER, output INTEGER, cache_read INTEGER, cache_write INTEGER,
  cache_write_1h INTEGER, reasoning INTEGER, context INTEGER, tool_cost_usd REAL, billed_units REAL,
  duration_ms INTEGER, PRIMARY KEY (tool, req_key));
CREATE TABLE IF NOT EXISTS sessions (
  tool TEXT NOT NULL, session_id TEXT NOT NULL, account TEXT, project TEXT, cwd TEXT, branch TEXT,
  title TEXT, custom_title TEXT, first_prompt TEXT, compactions INTEGER DEFAULT 0,
  compactions_auto INTEGER DEFAULT 0, tool_cost_usd REAL, PRIMARY KEY (tool, session_id));
CREATE TABLE IF NOT EXISTS sources (path TEXT PRIMARY KEY, pos INTEGER, size INTEGER);
CREATE INDEX IF NOT EXISTS ix_req_session ON requests(tool, session_id);
CREATE INDEX IF NOT EXISTS ix_req_ts ON requests(ts);
"""
REQ_FIELDS = ['tool', 'req_key', 'account', 'project', 'cwd', 'session_id', 'ts', 'model', 'effort', 'agent',
              'run_id', 'skill', 'is_subagent', 'initiator', 'input', 'output', 'cache_read', 'cache_write',
              'cache_write_1h', 'reasoning', 'context', 'tool_cost_usd', 'billed_units', 'duration_ms']


def load_config():
    cfg = json.load(open(os.path.join(HERE, 'usage-config.json'), encoding='utf-8'))
    local = os.environ.get('AI_USAGE_CONFIG') or os.path.join(LOCAL_DIR, 'config.json')
    if os.path.isfile(local):
        cfg.update(json.load(open(local, encoding='utf-8')))
    cfg['store'] = os.path.expanduser(cfg.get('store') or os.path.join(LOCAL_DIR, 'usage.db'))
    cfg['report_dir'] = os.path.expanduser(cfg.get('report_dir') or os.path.dirname(cfg['store']))
    return cfg


def load_pricing():
    return json.load(open(os.path.join(HERE, 'pricing.json'), encoding='utf-8'))


def open_store(cfg):
    os.makedirs(os.path.dirname(cfg['store']), exist_ok=True)
    con = sqlite3.connect(cfg['store'], timeout=30)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def claude_roots(cfg):
    """{account: root}. Explicit `claude_roots` wins; otherwise every ~/.claude or ~/AppData/Local/claude-*
    that has a projects/ folder (one per CLAUDE_CONFIG_DIR profile)."""
    if cfg.get('claude_roots'):
        return {k: os.path.expanduser(v) for k, v in cfg['claude_roots'].items()}
    cands = [os.path.join(HOME, '.claude')] + sorted(glob.glob(os.path.join(HOME, 'AppData', 'Local', 'claude-*')))
    return {('claude' if os.path.basename(p) == '.claude' else os.path.basename(p)): p
            for p in cands if os.path.isdir(os.path.join(p, 'projects'))}


def project_of(cwd, fallback=''):
    if not cwd:
        return fallback
    p = re.sub(r'^[A-Za-z]:', '', cwd.replace('\\', '/')).strip('/')
    return p or fallback


def excluded(cfg, *values):
    pats = [p.lower() for p in cfg.get('exclude_patterns') or []]
    vals = [(v or '').replace('\\', '/').lower() for v in values if v]
    return any(fnmatch.fnmatch(v, p) for v in vals for p in pats)


def upsert_requests(con, rows):
    cols = ','.join(REQ_FIELDS)
    marks = ','.join('?' * len(REQ_FIELDS))
    upd = ','.join(f'{c}=excluded.{c}' for c in REQ_FIELDS[2:])
    # a streamed response is logged as several lines sharing one key; keep the most complete one
    con.executemany(f'INSERT INTO requests ({cols}) VALUES ({marks}) ON CONFLICT(tool, req_key) DO UPDATE SET {upd} '
                    f'WHERE excluded.output >= requests.output', [[r.get(c) for c in REQ_FIELDS] for r in rows])


def upsert_session(con, s, reset_counters=False):
    comp = 'excluded.compactions' if reset_counters else 'sessions.compactions + excluded.compactions'
    comp_a = 'excluded.compactions_auto' if reset_counters else 'sessions.compactions_auto + excluded.compactions_auto'
    con.execute(
        'INSERT INTO sessions (tool, session_id, account, project, cwd, branch, title, custom_title, first_prompt, '
        'compactions, compactions_auto, tool_cost_usd) VALUES (?,?,?,?,?,?,?,?,?,?,?,?) '
        'ON CONFLICT(tool, session_id) DO UPDATE SET account=coalesce(sessions.account, excluded.account), '
        'project=coalesce(sessions.project, excluded.project), cwd=coalesce(sessions.cwd, excluded.cwd), '
        'branch=coalesce(excluded.branch, sessions.branch), title=coalesce(excluded.title, sessions.title), '
        'custom_title=coalesce(excluded.custom_title, sessions.custom_title), '
        'first_prompt=coalesce(sessions.first_prompt, excluded.first_prompt), '
        f'compactions={comp}, compactions_auto={comp_a}, '
        'tool_cost_usd=coalesce(excluded.tool_cost_usd, sessions.tool_cost_usd)',
        [s.get(k) for k in ('tool', 'session_id', 'account', 'project', 'cwd', 'branch', 'title', 'custom_title',
                            'first_prompt')] + [s.get('compactions', 0), s.get('compactions_auto', 0), s.get('tool_cost_usd')])


def list_cost(pricing, r):
    m = (r.get('model') or '').lower()
    mul = pricing['cache_multipliers']
    for p in pricing['models']:
        if p['match'] in m:
            pi = p['input']
            w1h = r.get('cache_write_1h') or 0
            w5 = max((r.get('cache_write') or 0) - w1h, 0)
            return ((r.get('input') or 0) * pi + (r.get('output') or 0) * p['output'] + w5 * pi * mul['write_5m']
                    + w1h * pi * mul['write_1h'] + (r.get('cache_read') or 0) * p.get('cache_read', pi * mul['read'])) / 1e6
    return None


def cost(pricing, r):
    """List-price cost (comparable across tools); tool-reported cost only for models pricing.json lacks."""
    c = list_cost(pricing, r)
    return c if c is not None else (r.get('tool_cost_usd') or 0.0)


TITLE_TAG = re.compile(r'^\s*\[?([a-z]+)\]?\s*:', re.I)


def task_of_request(cfg, skill, agent):
    skill, agent = (skill or '').lower(), (agent or '').lower()
    for rule in cfg['task_rules']:
        if any(skill.startswith(p) for p in rule.get('skill_prefix', [])) or \
                any(agent.startswith(p) for p in rule.get('agent_prefix', [])):
            return rule['task']
    return None


def task_of_title(cfg, title):
    m = TITLE_TAG.match(title or '')
    return m.group(1).lower() if m and m.group(1).lower() in cfg['task_types'] else None


def task_of_cwd(cfg, cwd):
    c = (cwd or '').replace('\\', '/').lower().rstrip('/')
    for rule in cfg.get('cwd_rules') or []:
        if any(fnmatch.fnmatch(c, g.lower()) for g in rule['cwd_glob']):
            return rule['task']
    return None
