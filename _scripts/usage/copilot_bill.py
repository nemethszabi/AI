"""GitHub Copilot usage for one month, priced the way the company plan actually bills it.

  python copilot_bill.py [--month YYYY-MM] [--plan business|enterprise] [--out FILE.md] [--no-collect]

Since 2026-06-01 every Copilot Business/Enterprise seat bills in GitHub AI Credits: tokens (input, output,
cache) at the model's API list rate, 1 credit = $0.01. The seat price comes back as included credits
(Business $19 -> 1,900) into an org-wide pool; usage above the pool is billed at $0.01 per credit.
Copilot records that charge per request as total_nano_aiu (1e9 nano-AIU = 1 credit), so this reads it as
recorded - no price table. request_multiplier (premium requests) is the retired pre-June billing and is
not used. Code completions are unlimited and never reach the database.
Plans live in usage-config.json (copilot_plans); pick yours with copilot_plan in ~/.ai-usage/config.json.
"""
import argparse, collections as C, datetime as dt, glob, json, os, subprocess, sys
import usage_lib as U

try:                                        # accented session titles must survive printing
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

M = lambda x: f'{x / 1e6:,.1f}M'


def quota_snapshot():
    """Latest premium_interactions quota GitHub sent to Copilot CLI - the entitlement as GitHub sees it."""
    files = sorted(glob.glob(os.path.expanduser('~/.copilot/session-state/*/events.jsonl')),
                   key=os.path.getmtime, reverse=True)
    key = '"quotaSnapshots":'
    for f in files[:20]:
        text = open(f, encoding='utf-8', errors='replace').read()
        i = text.rfind(key)
        if i >= 0:
            try:
                return json.JSONDecoder().raw_decode(text, i + len(key))[0].get('premium_interactions')
            except ValueError:
                pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--month'); ap.add_argument('--plan'); ap.add_argument('--out')
    ap.add_argument('--no-collect', action='store_true')
    a = ap.parse_args()
    if not a.no_collect:
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'collect_copilot.py')],
                       check=False, stdout=subprocess.DEVNULL)
    cfg = U.load_config()
    plan_name = a.plan or cfg.get('copilot_plan') or 'business'
    plan = cfg['copilot_plans'][plan_name]
    credit_usd = cfg.get('copilot_credit_usd', 0.01)

    now = dt.datetime.now(dt.timezone.utc)                     # GitHub bills in UTC calendar months
    y, m = map(int, a.month.split('-')) if a.month else (now.year, now.month)
    start, end = dt.datetime(y, m, 1, tzinfo=dt.timezone.utc), dt.datetime(y + m // 12, m % 12 + 1, 1, tzinfo=dt.timezone.utc)
    con = U.open_store(cfg)
    rows = [dict(r) for r in con.execute('SELECT * FROM requests WHERE tool = ? AND ts >= ? AND ts < ?',
                                         ('copilot', start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))]
    titles = {s['session_id']: s['custom_title'] or s['title'] or s['first_prompt'] or ''
              for s in con.execute("SELECT * FROM sessions WHERE tool = 'copilot'")}
    for r in rows:
        r['credits'] = (r['tool_cost_usd'] or 0) / credit_usd

    used = sum(r['credits'] for r in rows)
    incl = plan['included_credits']
    over = max(used - incl, 0)
    out = [f'# Copilot usage - {start:%Y-%m} (company plan: {plan_name})',
           f'\n{len(rows):,} model requests, {sum(1 for r in rows if r["initiator"] == "user"):,} of them your own prompts, '
           f'{len({r["session_id"] for r in rows})} sessions. Source: Copilot\'s own per-request charge (AI credits), not an estimate.',
           '\n| | AI credits | USD |\n|---|---:|---:|',
           f'| Used this month | {used:,.0f} | ${used * credit_usd:,.2f} |',
           f'| Included with your seat (${plan["seat_usd"]}/month) | {incl:,} | ${incl * credit_usd:,.2f} |',
           f'| Covered by your seat | {min(used, incl):,.0f} | ${min(used, incl) * credit_usd:,.2f} |',
           f'| **Above your seat\'s share** | **{over:,.0f}** | **${over * credit_usd:,.2f}** |',
           f'| **Company cost for you: seat + usage above it** | | **${plan["seat_usd"] + over * credit_usd:,.2f}** |']
    if start <= now < end:
        frac = (now - start) / (end - start)
        proj = used / frac if frac > 0 else used
        out.append(f'\nMonth-end projection at this pace ({frac:.0%} of the month gone): {proj:,.0f} credits, '
                   f'${proj * credit_usd:,.2f} used, ${plan["seat_usd"] + max(proj - incl, 0) * credit_usd:,.2f} company cost.')
    q = quota_snapshot()
    if q:
        cap = 'no per-user cap' if q.get('isUnlimitedEntitlement') else f'{q.get("entitlementRequests")} cap, {q.get("remainingPercentage")}% left'
        out.append(f'\nGitHub quota for your seat: {cap}, overage {"allowed" if q.get("overageAllowedWithExhaustedQuota") else "blocked"}, '
                   f'resets {(q.get("resetDate") or "")[:10]}. Included credits are pooled across the org, so usage above your share '
                   'is billed only once the whole pool runs out; the last row is the worst case.')

    def table(title, keyf, top=None):
        A = C.defaultdict(C.Counter)
        for r in rows:
            k = A[keyf(r)]
            k['n'] += 1; k['prompts'] += r['initiator'] == 'user'
            k['context'] += r['context'] or 0; k['output'] += r['output'] or 0; k['credits'] += r['credits']
        out.append(f'\n### {title}\n| | requests | your prompts | context | output | AI credits | USD | share |\n|---|---:|---:|---:|---:|---:|---:|---:|')
        for k, v in sorted(A.items(), key=lambda kv: -kv[1]['credits'])[:top]:
            out.append(f"| {k} | {v['n']:,} | {v['prompts']:,} | {M(v['context'])} | {M(v['output'])} | {v['credits']:,.0f} | "
                       f"${v['credits'] * credit_usd:,.2f} | {v['credits'] / used:.0%} |" if used else '')

    if rows:
        table('By model', lambda r: r['model'])
        table('By who sent the request (agent tool-call rounds and subagents are billed too)', lambda r: r['initiator'] or '?')
        table('Top 10 sessions', lambda r: ' '.join((titles.get(r['session_id']) or r['session_id']).split())[:70].replace('|', '/'), top=10)
    text = '\n'.join(out) + '\n'
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(text)
        print(f'report: {a.out}')
    else:
        print(text)


if __name__ == '__main__':
    main()
