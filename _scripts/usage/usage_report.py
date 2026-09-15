"""Cross-tool AI usage report from the shared store (runs the collectors first unless --no-collect).

  python usage_report.py [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--tool claude|copilot]
                         [--out FILE.md] [--stdout] [--no-collect]

Task type per request: its own skill/agent rule -> session title tag ("sa: ...", set via /rename)
-> the session's dominant classified type -> cwd rule -> "generic". Rules live in usage-config.json.
Costs are list-price estimates (pricing.json) so tools and models compare on one scale; the tool's own
figure is shown alongside where it records one.
"""
import argparse, collections as C, datetime as dt, os, statistics, subprocess, sys
import usage_lib as U

try:                                        # report text is UTF-8 regardless of the console codepage
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

M = lambda x: f'{x / 1e6:,.1f}M'


def hit(a):
    d = a['cache_read'] + a['cache_write'] + a['input']
    return f"{a['cache_read'] / d * 100:.0f}%" if d else '-'


def agg(rows, keyf):
    A = C.defaultdict(C.Counter)
    for r in rows:
        a = A[keyf(r)]
        for f in ('input', 'output', 'cache_read', 'cache_write', 'context', 'cost'):
            a[f] += r[f] or 0
        a['tool_cost'] += r['tool_cost_usd'] or 0
        a['billed'] += r['billed_units'] or 0
        a['n'] += 1
        a.setdefault('sessions', set()).add((r['tool'], r['session_id']))
    return A


def table(out, title, A, key_hdr, top=None, sort_by_cost=True, extra=()):
    hdr = [key_hdr, 'req', 'sessions', 'context', 'output', 'cache hit', 'est $', '$/req'] + [e[0] for e in extra]
    out.append(f'\n### {title}\n| ' + ' | '.join(hdr) + ' |\n|' + '---|' + '---:|' * (len(hdr) - 1))
    items = sorted(A.items(), key=(lambda kv: -kv[1]['cost']) if sort_by_cost else (lambda kv: str(kv[0])))
    for k, a in items[:top]:
        k = ' / '.join(str(x) for x in k) if isinstance(k, tuple) else k
        cells = [k, f"{a['n']:,}", f"{len(a['sessions']):,}", M(a['context']), M(a['output']), hit(a),
                 f"{a['cost']:,.2f}", f"{a['cost'] / a['n']:.3f}"] + [e[1](a) for e in extra]
        out.append('| ' + ' | '.join(cells) + ' |')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--since'); ap.add_argument('--until'); ap.add_argument('--tool'); ap.add_argument('--out')
    ap.add_argument('--stdout', action='store_true'); ap.add_argument('--no-collect', action='store_true')
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    if not a.no_collect:
        for c in ('collect_claude.py', 'collect_copilot.py'):
            subprocess.run([sys.executable, os.path.join(here, c)], check=False)
    cfg, pricing = U.load_config(), U.load_pricing()
    con = U.open_store(cfg)
    where, params = ['1=1'], []
    if a.since: where.append('ts >= ?'); params.append(a.since)
    if a.until: where.append('ts < ?'); params.append(a.until)
    if a.tool: where.append('tool = ?'); params.append(a.tool)
    rows = [dict(r) for r in con.execute(f'SELECT * FROM requests WHERE {" AND ".join(where)}', params)]
    sess = {(s['tool'], s['session_id']): dict(s) for s in con.execute('SELECT * FROM sessions')}
    if not rows:
        print('no usage rows in range'); return
    for r in rows:
        r['cost'] = U.cost(pricing, r)
        r['own_task'] = U.task_of_request(cfg, r['skill'], r['agent'])
    by_sess = C.defaultdict(list)
    for r in rows:
        by_sess[(r['tool'], r['session_id'])].append(r)
    sess_task = {}
    for k, rs in by_sess.items():
        s = sess.get(k) or {}
        t = U.task_of_title(cfg, s.get('custom_title') or s.get('title'))
        if not t:
            w = C.Counter()
            for r in rs:
                if r['own_task']: w[r['own_task']] += r['cost']
            t = w.most_common(1)[0][0] if w else (U.task_of_cwd(cfg, s.get('cwd') or rs[0]['cwd']) or 'generic')
        sess_task[k] = t
    for r in rows:
        r['task'] = r['own_task'] or sess_task[(r['tool'], r['session_id'])]
        r['month'] = (r['ts'] or '')[:7]

    first, last = min(r['ts'] for r in rows)[:10], max(r['ts'] for r in rows)[:10]
    total = sum(r['cost'] for r in rows)
    out = [f'# AI usage report - {first} .. {last}',
           f'\nGenerated {dt.datetime.now():%Y-%m-%d %H:%M} from `{cfg["store"]}`. {len(rows):,} requests, '
           f'{len(by_sess):,} sessions, est. **${total:,.2f}** at list prices (pricing.json, verified {pricing.get("verified")}). '
           'Copilot $ is its own recorded AI-credit charge, which is what the company seat is billed since 2026-06-01 '
           '(`copilot_bill.py` shows it against the plan). Claude $ is a notional API list price - a subscription '
           'does not bill per token - so compare it *relatively*.']
    tool_cost = ('tool $', lambda x: f"{x['tool_cost']:,.2f}" if x['tool_cost'] else '-')
    billed = ('AI credits', lambda x: f"{x['tool_cost'] * 100:,.0f}" if x['tool_cost'] else '-')
    table(out, 'By tool', agg(rows, lambda r: r['tool']), 'tool', extra=(tool_cost, billed))
    table(out, 'By tool / model / effort', agg(rows, lambda r: (r['tool'], r['model'], r['effort'] or '-')), 'tool / model / effort',
          extra=(tool_cost, billed))
    table(out, 'By task type / tool / model', agg(rows, lambda r: (r['task'], r['tool'], r['model'])), 'task / tool / model')

    # per-session comparison: what does one session of task X cost on tool/model Y
    S = C.defaultdict(list)
    for k, rs in by_sess.items():
        mc = C.Counter()
        for r in rs: mc[r['model']] += r['cost']
        S[(sess_task[k], k[0], mc.most_common(1)[0][0])].append(sum(r['cost'] for r in rs))
    out.append('\n### Cost per session, by task type / tool / dominant model\n| task / tool / model | sessions | median $ | mean $ | max $ |\n|---|---:|---:|---:|---:|')
    for k, v in sorted(S.items(), key=lambda kv: (kv[0][0], -statistics.median(kv[1]))):
        out.append(f'| {" / ".join(k)} | {len(v)} | {statistics.median(v):,.2f} | {statistics.mean(v):,.2f} | {max(v):,.2f} |')

    table(out, 'By account', agg(rows, lambda r: (r['tool'], r['account'])), 'tool / account')
    table(out, 'By project (top 15)', agg(rows, lambda r: r['project'] or '?'), 'project', top=15)
    table(out, 'Main thread vs subagents', agg(rows, lambda r: (r['tool'], 'subagent' if r['is_subagent'] else 'main')), 'tool / thread')
    subs = [r for r in rows if r['is_subagent']]
    if subs:
        runs = lambda x: f"{len(x['runs']):,}"
        A = agg(subs, lambda r: (r['tool'], r['agent'] or '(unnamed)'))
        for r in subs:
            A[(r['tool'], r['agent'] or '(unnamed)')].setdefault('runs', set()).add(r['run_id'])
        table(out, 'Subagent types (top 25)', A, 'tool / agent', top=25,
              extra=(('runs', runs), ('$/run', lambda x: f"{x['cost'] / max(len(x['runs']), 1):,.2f}")))
    sk = [r for r in rows if r['skill']]
    if sk:
        table(out, 'Skills / commands (top 25)', agg(sk, lambda r: (r['tool'], r['skill'])), 'tool / skill', top=25)
    table(out, 'By month', agg(rows, lambda r: (r['month'], r['tool'])), 'month / tool', sort_by_cost=False)

    out.append('\n### Top 15 sessions\n| # | tool | project | start | title / first prompt | req | max ctx | est $ | tool $ |\n|---|---|---|---|---|---:|---:|---:|---:|')
    ranked = sorted(by_sess.items(), key=lambda kv: -sum(r['cost'] for r in kv[1]))[:15]
    for i, (k, rs) in enumerate(ranked, 1):
        s = sess.get(k) or {}
        label = (s.get('custom_title') or s.get('title') or s.get('first_prompt') or '').replace('|', '/')[:90]
        tc = s.get('tool_cost_usd')
        out.append(f"| {i} | {k[0]} | {rs[0]['project']} | {min(r['ts'] for r in rs)[:10]} | {label} | {len(rs)} | "
                   f"{max(r['context'] for r in rs) // 1000}k | {sum(r['cost'] for r in rs):,.2f} | {f'{tc:,.2f}' if tc else '-'} |")

    g = cfg['guard']
    out.append('\n### Signals')
    for lim in (g['warn_tokens'], g['strong_tokens'], 500_000):
        big = [r for r in rows if r['context'] > lim]
        out.append(f"- Requests with context > {lim // 1000}k: {len(big):,} ({len(big) / len(rows):.0%}), "
                   f"est ${sum(r['cost'] for r in big):,.2f} ({sum(r['cost'] for r in big) / total:.0%} of spend)")
    comp = [s for k, s in sess.items() if k in by_sess]
    out.append(f"- Compactions: {sum(s['compactions'] or 0 for s in comp)} (auto {sum(s['compactions_auto'] or 0 for s in comp)})")
    mains = {k: sum(1 for r in rs if not r['is_subagent']) for k, rs in by_sess.items()}
    for lim in (100, 200):
        L = [k for k, n in mains.items() if n > lim]
        out.append(f"- Sessions with > {lim} main-thread requests: {len(L)}, est ${sum(sum(r['cost'] for r in by_sess[k]) for k in L):,.2f}")
    eff = C.Counter()
    for r in rows:
        eff[r['effort'] or '-'] += r['cost']
    out.append('- Spend by effort level: ' + ', '.join(f'{k} ${v:,.2f}' for k, v in eff.most_common()))
    unpriced = {r['model'] for r in rows if U.list_cost(pricing, r) is None}
    if unpriced:
        out.append(f"- Priced from the tool's own figure (not in pricing.json): {', '.join(sorted(unpriced))}")

    text = '\n'.join(out) + '\n'
    if a.stdout:
        sys.stdout.reconfigure(encoding='utf-8'); print(text)
    else:
        path = a.out or os.path.join(cfg['report_dir'], f'usage-report-{dt.date.today():%Y%m%d}.md')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w', encoding='utf-8').write(text)
        print(f'report: {path}')


if __name__ == '__main__':
    main()
