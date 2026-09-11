"""Collect GitHub Copilot CLI token usage from ~/.copilot/session-store.db into the shared usage store.

  python collect_copilot.py

Source table: assistant_usage_events (one row per model request). Copilot's input_tokens already includes
cache reads/writes, so it is split back out here to match the Claude rows. Copilot records its own cost
per request as total_nano_aiu (1 AIU = $0.01, so USD = nano_aiu / 1e11) and premium-request units as
request_multiplier - kept as tool_cost_usd / billed_units.
"""
import os, sqlite3
import usage_lib as U


def main():
    cfg = U.load_config()
    db = os.path.expanduser(cfg.get('copilot_db') or '~/.copilot/session-store.db')
    if not os.path.isfile(db):
        print(f'copilot: no database at {db}')
        return
    src = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    src.row_factory = sqlite3.Row
    con = U.open_store(cfg)
    account = cfg.get('copilot_account') or 'copilot'
    sessions = {r['id']: dict(r) for r in src.execute('SELECT * FROM sessions')}
    first = {r['session_id']: r['user_message'] for r in src.execute(
        'SELECT session_id, user_message FROM turns t WHERE turn_index = '
        '(SELECT MIN(turn_index) FROM turns WHERE session_id = t.session_id)')}
    rows, seen = [], set()
    for e in src.execute('SELECT * FROM assistant_usage_events'):
        s = sessions.get(e['session_id']) or {}
        cwd = s.get('cwd')
        if U.excluded(cfg, cwd):
            continue
        total_in, cr, cw = e['input_tokens'] or 0, e['cache_read_tokens'] or 0, e['cache_write_tokens'] or 0
        sub = e['initiator'] == 'sub-agent' or bool(e['parent_tool_call_id'])
        rows.append(dict(tool='copilot', req_key=str(e['id']), account=account, project=U.project_of(cwd), cwd=cwd,
                         session_id=e['session_id'], ts=e['created_at'], model=e['model'], effort=e['reasoning_effort'] or '',
                         agent='', run_id=(e['agent_id'] or '') if sub else '', skill='', is_subagent=int(sub),
                         initiator=e['initiator'], input=max(total_in - cr - cw, 0), output=e['output_tokens'] or 0,
                         cache_read=cr, cache_write=cw, cache_write_1h=0, reasoning=e['reasoning_tokens'],
                         context=total_in, tool_cost_usd=(e['total_nano_aiu'] or 0) / 1e11,
                         billed_units=e['request_multiplier'], duration_ms=e['duration_ms']))
        seen.add(e['session_id'])
    U.upsert_requests(con, rows)
    for sid in seen:
        s = sessions.get(sid) or {}
        fp = ' '.join((first.get(sid) or '').split())[:200] or None
        U.upsert_session(con, dict(tool='copilot', session_id=sid, account=account, project=U.project_of(s.get('cwd')),
                                   cwd=s.get('cwd'), branch=s.get('branch'), title=s.get('summary'), first_prompt=fp),
                         reset_counters=True)
    con.commit()
    print(f'copilot: {len(rows):,} request rows upserted from {len(seen)} sessions -> {cfg["store"]}')


if __name__ == '__main__':
    main()
