"""Collect Claude Code token usage from session transcripts into the shared usage store.

  python collect_claude.py           all profiles, incremental (only bytes appended since the last run)
  python collect_claude.py --full    re-read every transcript from byte 0
  python collect_claude.py --hook    Stop-hook mode: hook JSON on stdin, collect that session + its subagents

Transcripts are deleted after cleanupPeriodDays (default 30), so the store is the durable copy.
Effort, skill and agent attribution come from per-line fields (effort, attributionSkill, attributionAgent).
"""
import glob, json, os, re, sys, traceback
import usage_lib as U

CMD_RE = re.compile(r'<command-name>\s*/?([^<\s]+)\s*</command-name>')
HOUSEKEEPING = {'clear', 'model', 'usage', 'status', 'rename', 'resume', 'compact', 'effort', 'mcp', 'login',
                'config', 'cost', 'context', 'autocompact'}


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(b.get('text', '') for b in content if isinstance(b, dict) and b.get('type') == 'text')
    return ''


def first_prompt_of(d, content):
    if d.get('isMeta') or d.get('isSidechain'):
        return None
    if isinstance(content, list) and any(isinstance(b, dict) and b.get('type') == 'tool_result' for b in content):
        return None
    txt = text_of(content).strip()
    cmds = CMD_RE.findall(txt)
    if not txt or txt.startswith('<local-command') or 'Caveat:' in txt[:30] or (cmds and all(c in HOUSEKEEPING for c in cmds)):
        return None
    txt = CMD_RE.sub(lambda m: '/' + m.group(1), txt)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', txt)).strip()[:200]


def collect_file(con, cfg, path, account, projects_dir, full=False):
    size = os.path.getsize(path)
    known = con.execute('SELECT pos FROM sources WHERE path=?', (path,)).fetchone()
    pos = 0 if full or not known or known['pos'] > size else known['pos']
    if pos >= size:
        return 0
    with open(path, 'rb') as fh:
        fh.seek(pos)
        data = fh.read()
    data = data[:data.rfind(b'\n') + 1]            # only complete lines; a partial last line waits for next run
    if not data:
        return 0
    rel = os.path.relpath(path, projects_dir).replace('\\', '/')
    proj_dir, is_sub_file = rel.split('/')[0], '/subagents/' in rel
    meta_type = None
    if is_sub_file:
        try:
            meta_type = json.load(open(path[:-6] + '.meta.json', encoding='utf-8')).get('agentType')
        except Exception:
            pass
    first_cwd, reqs, sess = None, {}, {}
    for raw in data.splitlines():
        try:
            d = json.loads(raw)
        except Exception:
            continue
        sid = d.get('sessionId')
        if not sid:
            continue
        first_cwd = first_cwd or d.get('cwd')
        t = d.get('type')
        S = None if is_sub_file else sess.setdefault(sid, dict(tool='claude', session_id=sid, account=account))
        if S is not None:
            S['cwd'] = S.get('cwd') or d.get('cwd')
            S['branch'] = d.get('gitBranch') or S.get('branch')
            if t == 'custom-title':
                S['custom_title'] = d.get('customTitle')
            elif t == 'ai-title':
                S['title'] = d.get('aiTitle')
            elif t == 'cost-state':
                S['tool_cost_usd'] = d.get('totalCostUSD')
            elif t == 'system' and d.get('subtype') == 'compact_boundary':
                S['compactions'] = S.get('compactions', 0) + 1
                if (d.get('compactMetadata') or {}).get('trigger') == 'auto':
                    S['compactions_auto'] = S.get('compactions_auto', 0) + 1
            elif t == 'user' and not S.get('first_prompt'):
                S['first_prompt'] = first_prompt_of(d, (d.get('message') or {}).get('content'))
        if t != 'assistant':
            continue
        msg = d.get('message') or {}
        u, model = msg.get('usage') or {}, msg.get('model')
        if not u or model == '<synthetic>':
            continue
        sub = bool(d.get('isSidechain')) or is_sub_file
        inp, cr, cw = u.get('input_tokens') or 0, u.get('cache_read_input_tokens') or 0, u.get('cache_creation_input_tokens') or 0
        key = f"{msg.get('id')}|{d.get('requestId')}"
        row = dict(tool='claude', req_key=key, account=account, session_id=sid, ts=d.get('timestamp'),
                   model=model, effort=d.get('effort') or '', skill=d.get('attributionSkill') or '',
                   agent=(d.get('attributionAgent') or meta_type or '') if sub else '',
                   run_id=(d.get('agentId') or os.path.basename(path)[:-6]) if sub else '',
                   is_subagent=int(sub), initiator='subagent' if sub else 'main', input=inp,
                   output=u.get('output_tokens') or 0, cache_read=cr, cache_write=cw,
                   cache_write_1h=(u.get('cache_creation') or {}).get('ephemeral_1h_input_tokens') or 0,
                   reasoning=(u.get('output_tokens_details') or {}).get('thinking_tokens'), context=inp + cr + cw)
        if key not in reqs or row['output'] >= reqs[key]['output']:
            reqs[key] = row
    skip = U.excluded(cfg, first_cwd, proj_dir)
    if not skip:
        for S in sess.values():
            S['project'] = U.project_of(S.get('cwd'), proj_dir)
            U.upsert_session(con, S, reset_counters=(pos == 0))
        # attribute every request (subagents included) to the session's launch directory, not wherever
        # the shell had cd'ed to at that moment - otherwise one session splinters into many "projects"
        home = {}
        for r in reqs.values():
            sid = r['session_id']
            if sid not in home:
                s = con.execute("SELECT cwd FROM sessions WHERE tool='claude' AND session_id=?", (sid,)).fetchone()
                home[sid] = (s['cwd'] if s else None) or first_cwd
            r['cwd'], r['project'] = home[sid], U.project_of(home[sid], proj_dir)
        U.upsert_requests(con, list(reqs.values()))
    con.execute('INSERT OR REPLACE INTO sources (path, pos, size) VALUES (?,?,?)', (path, pos + len(data), size))
    return 0 if skip else len(reqs)


def targets(cfg, args):
    roots = U.claude_roots(cfg)
    if '--hook' not in args:
        for acc, root in roots.items():
            pd = os.path.join(root, 'projects')
            for f in glob.glob(os.path.join(pd, '**', '*.jsonl'), recursive=True):
                yield f, acc, pd
        return
    try:
        tp = os.path.abspath(json.load(sys.stdin).get('transcript_path') or '')
    except Exception:
        return
    for acc, root in roots.items():
        pd = os.path.abspath(os.path.join(root, 'projects'))
        if os.path.isfile(tp) and os.path.normcase(tp).startswith(os.path.normcase(pd) + os.sep):
            yield tp, acc, pd
            for f in glob.glob(os.path.join(tp[:-6], 'subagents', '*.jsonl')):
                yield f, acc, pd


def main():
    args = sys.argv[1:]
    cfg = U.load_config()
    con = U.open_store(cfg)
    n = files = 0
    for f, acc, pd in targets(cfg, args):
        files += 1
        n += collect_file(con, cfg, f, acc, pd, full='--full' in args)
        con.commit()
    if '--hook' not in args:
        print(f'claude: {n:,} request rows upserted from {files} transcript files -> {cfg["store"]}')


if __name__ == '__main__':
    if '--hook' in sys.argv:
        try:
            main()
        except Exception:                      # a hook must never disturb the session; log and move on
            os.makedirs(U.LOCAL_DIR, exist_ok=True)
            with open(os.path.join(U.LOCAL_DIR, 'collector-errors.log'), 'a', encoding='utf-8') as fh:
                fh.write(traceback.format_exc() + '\n')
    else:
        main()
