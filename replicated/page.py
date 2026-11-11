"""Render docs/index.html: one static, self-contained page (inline SVG, no dependencies, no network).

Reads the thesis snapshot and recomputes everything, so the page cannot drift from the build.
"""
from __future__ import annotations

import html
import json
import math
from pathlib import Path

from . import build, checks, compare, metrics

ROOT = Path(__file__).resolve().parent.parent
E = html.escape
REPO_URL = "https://github.com/noegng/near-hackathon"  # empty makes the page link relatively

CSS = """
:root{color-scheme:light;--serif:Charter,"Bitstream Charter","Iowan Old Style","Palatino Linotype",Georgia,serif;--sans:system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
--surface:#faf9f6;--panel:#f0eee8;--text:#161614;--text2:#55534d;--muted:#8a8880;--grid:#e2dfd6;--s1:#2a78d6;--s2:#eb6834;--good:#0a7d0a;--crit:#c43131}
@media (prefers-color-scheme:dark){:root{color-scheme:dark;--surface:#161615;--panel:#232321;--text:#eeece6;--text2:#bdbbb1;--muted:#8f8d85;--grid:#33322e;--s1:#4a94ea;--s2:#e0683a;--good:#4fbf4f;--crit:#ef6b6b}}
*{box-sizing:border-box}body{margin:0;background:var(--surface);color:var(--text);font:17px/1.6 var(--serif);-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
main{max-width:1040px;margin:0 auto;padding:28px 24px 64px}
.mast{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px 24px;font:600 .72rem/1.3 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--text2);padding-bottom:12px;border-bottom:1px solid var(--text);margin-bottom:52px}
.mast b{color:var(--text)}
h1{font-size:clamp(2.1rem,5.2vw,3.5rem);line-height:1.04;letter-spacing:-.022em;font-weight:600;margin:0 0 24px;max-width:17em}
.lede{font-size:1.28rem;line-height:1.45;max-width:36em;margin:0}
p{margin:10px 0;max-width:38em}.note{font:.82rem/1.55 var(--sans);color:var(--text2);max-width:60em}
a{color:inherit;text-decoration-color:var(--muted);text-decoration-thickness:1px;text-underline-offset:3px}a:hover{text-decoration-color:currentColor}
code{font:.82em ui-monospace,"SF Mono",Menlo,Consolas,monospace;background:var(--panel);padding:2px 5px;border-radius:3px;white-space:nowrap}
.keys{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:0 32px;margin:52px 0 0}
.key{border-top:2px solid var(--text);padding:12px 0 22px}.key b{display:block;font:600 2.3rem/1.1 var(--serif);letter-spacing:-.015em;font-variant-numeric:lining-nums tabular-nums}
.key span{display:block;font:.84rem/1.45 var(--sans);color:var(--text2);margin-top:8px}
section{margin-top:76px;border-top:1px solid var(--grid);padding-top:18px}
.kicker{font:600 .72rem/1 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0}
h2{font-size:1.8rem;line-height:1.18;letter-spacing:-.012em;font-weight:600;margin:10px 0 12px;max-width:22em}
h3{font:600 .95rem/1.3 var(--sans);margin:0 0 3px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr));gap:36px 44px;margin-top:8px}
figure{margin:26px 0 0}figcaption{font:.84rem/1.45 var(--sans);color:var(--text2);margin-bottom:10px;max-width:46em}
svg{display:block;width:100%;height:auto;overflow:visible}svg text{fill:var(--text2);font:12px var(--sans);font-variant-numeric:tabular-nums}
svg .strong{fill:var(--text);font-weight:600}.gridl{stroke:var(--grid);stroke-width:1}.hit{fill:transparent;cursor:crosshair}
.dot{opacity:0;pointer-events:none}.hit:hover+.dot{opacity:1}
.legend{display:flex;gap:20px;flex-wrap:wrap;font:.82rem/1.3 var(--sans);color:var(--text2);margin:14px 0 4px}.legend i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:7px}
.legend i.dia{border-radius:0;transform:rotate(45deg)}
table{border-collapse:collapse;width:100%;font:.86rem/1.45 var(--sans);font-variant-numeric:tabular-nums;margin-top:18px}
th,td{text-align:left;padding:9px 16px 9px 0;border-bottom:1px solid var(--grid);vertical-align:top}th:last-child,td:last-child{padding-right:0}
th{font-size:.72rem;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);font-weight:600;border-bottom-color:var(--text);white-space:nowrap}
td.n,th.n{text-align:right;white-space:nowrap}td:first-child{white-space:nowrap}
details{margin:14px 0;border-top:1px solid var(--grid);padding-top:12px}summary{cursor:pointer;font:600 .86rem/1.3 var(--sans)}summary:hover{color:var(--s1)}
.st{font-weight:600;white-space:nowrap}.st.ok::before{content:"\\2713  ";color:var(--good)}.st.bad::before{content:"\\2717  ";color:var(--crit)}.st.wait::before{content:"\\25CB  ";color:var(--muted)}
.scroll{overflow-x:auto}
footer{margin-top:84px;border-top:1px solid var(--text);padding-top:18px;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px 40px;font:.82rem/1.6 var(--sans);color:var(--text2)}
footer b{display:block;font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:4px}footer p{margin:0}
#tip{position:fixed;pointer-events:none;background:var(--text);color:var(--surface);padding:6px 9px;border-radius:4px;font:.78rem/1.35 var(--sans);display:none;z-index:9;max-width:260px}
@media (max-width:560px){body{font-size:16px}.mast{margin-bottom:36px}section{margin-top:56px}.key b{font-size:2rem}}
"""

JS = """
const tip=document.getElementById('tip');
document.addEventListener('mousemove',e=>{const t=e.target.closest('[data-tip]');if(!t){tip.style.display='none';return}
tip.textContent=t.dataset.tip;tip.style.display='block';const w=tip.offsetWidth;
tip.style.left=Math.min(e.clientX+14,innerWidth-w-8)+'px';tip.style.top=(e.clientY+14)+'px'});
"""


def money(v: float) -> str:
    a = abs(v)
    return f"${v / 1e9:.1f}B" if a >= 1e9 else f"${v / 1e6:.0f}M" if a >= 1e6 else f"${v / 1e3:.0f}K" if a >= 1e3 else f"${v:.0f}"


def count(v: float) -> str:
    a = abs(v)
    return f"{v / 1e6:.1f}M" if a >= 1e6 else f"{v / 1e3:.0f}K" if a >= 1e3 else f"{v:.0f}"


def nice_max(v: float) -> float:
    """Axis top at or above v whose quarters are round, so the four tick labels need no rounding."""
    import math
    if v <= 0:
        return 1.0
    mag = 10 ** math.floor(math.log10(v))
    for step in (1.2, 1.6, 2, 2.4, 3.2, 4, 4.8, 6, 8, 12):
        if v <= step * mag * (1 + 1e-9):
            return step * mag
    return 12 * mag


def spread(ys: list[float], gap: float) -> list[float]:
    """Move label positions apart until neighbours are at least `gap` apart, keeping their order and centre."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    out = list(ys)
    for a, b in zip(order, order[1:]):
        if out[b] - out[a] < gap:
            out[b] = out[a] + gap
    shift = (math.fsum(out) - math.fsum(ys)) / len(ys)
    return [y - shift for y in out]


MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def month_label(day: str) -> str:
    """'2026-11-11' -> 'Nov 26'."""
    return f"{MONTHS[int(day[5:7]) - 1]} {day[2:4]}"


def line_chart(xlabels: list[str], series: list[tuple[str, str, list[float]]], fmt, w=460, h=230) -> str:
    """series: (name, css color var, values). One shared y axis from zero."""
    L, R, T, B = 48, 96 if len(series) > 1 else 16, 12, 26
    top = nice_max(max(max(v) for _, _, v in series))
    n = len(xlabels)
    X = lambda i: L + (w - L - R) * i / (n - 1)
    Y = lambda v: T + (h - T - B) * (1 - v / top)
    o = [f'<svg viewBox="0 0 {w} {h}" role="img">']
    for k in range(5):
        v = top * k / 4
        o.append(f'<line class="gridl" x1="{L}" x2="{w - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text x="{L - 6}" y="{Y(v) + 4:.1f}" text-anchor="end">{fmt(v)}</text>')
    for i in (0, n // 2, n - 1):
        o.append(f'<text x="{X(i):.1f}" y="{h - 6}" text-anchor="{"start" if i == 0 else "end" if i == n - 1 else "middle"}">{E(xlabels[i])}</text>')
    ends = spread([Y(v[-1]) for _, _, v in series], 15)
    for (name, col, vals), ly in zip(series, ends):
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
        o.append(f'<polyline points="{pts}" fill="none" stroke="var({col})" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        if len(series) > 1:
            o.append(f'<text class="strong" x="{X(n - 1) + 8:.1f}" y="{ly + 4:.1f}">{E(name)}</text>')
    for name, col, vals in series:
        for i, v in enumerate(vals):
            o.append(f'<circle class="hit" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="{max(4, min(10, (w - L - R) / n / 2)):.1f}" data-tip="{E(name)}, {E(xlabels[i])}: {fmt(v)}"/>'
                     f'<circle class="dot" cx="{X(i):.1f}" cy="{Y(v):.1f}" r="4" fill="var({col})" stroke="var(--surface)" stroke-width="2"/>')
    return "".join(o) + "</svg>"


def bar_chart(labels: list[str], vals: list[float], fmt, w=940, h=240) -> str:
    L, R, T, B = 44, 8, 18, 26
    top = nice_max(max(vals))
    n = len(vals)
    slot = (w - L - R) / n
    bw = min(40, slot - 2)
    Y = lambda v: T + (h - T - B) * (1 - v / top)
    o = [f'<svg viewBox="0 0 {w} {h}" role="img">']
    for k in range(5):
        v = top * k / 4
        o.append(f'<line class="gridl" x1="{L}" x2="{w - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text x="{L - 6}" y="{Y(v) + 4:.1f}" text-anchor="end">{fmt(v)}</text>')
    hi = max(range(n), key=lambda i: vals[i])
    for i, v in enumerate(vals):
        x = L + slot * i + (slot - bw) / 2
        y, r = Y(v), min(4, max(0, (Y(0) - Y(v)) / 2))
        o.append(f'<path d="M{x:.1f},{Y(0):.1f}V{y + r:.1f}q0,-{r} {r},-{r}h{bw - 2 * r:.1f}q{r},0 {r},{r}V{Y(0):.1f}z" fill="var(--s1)" data-tip="{E(labels[i])}: {fmt(v)}"/>')
        if i in (hi, n - 1):
            o.append(f'<text class="strong" x="{x + bw / 2:.1f}" y="{y - 5:.1f}" text-anchor="middle">{fmt(v)}</text>')
        if i % 2 == (n - 1) % 2:
            o.append(f'<text x="{x + bw / 2:.1f}" y="{h - 6}" text-anchor="middle">{E(labels[i])}</text>')
    return "".join(o) + "</svg>"


def strip(rows: list[dict], w=940) -> str:
    """One row per quantity, each on its own scale from zero: team numbers as circles, ours as diamonds."""
    L, R, rh = 270, 60, 58
    h = rh * len(rows) + 8
    o = [f'<svg viewBox="0 0 {w} {h}" role="img">']
    for k, r in enumerate(rows):
        y = rh * k + 34
        top = nice_max(max(r["teams"] + [v for _, v in r["ours"]]))
        X = lambda v: L + (w - L - R) * v / top
        o.append(f'<text class="strong" x="0" y="{y - 4}">{E(r["label"])}</text><text x="0" y="{y + 11}">{len(r["teams"])} team numbers</text>')
        o.append(f'<line class="gridl" x1="{L}" x2="{w - R}" y1="{y}" y2="{y}"/><text x="{L - 8}" y="{y + 4}" text-anchor="end">0</text><text x="{w - R + 8}" y="{y + 4}">{r["fmt"](top)}</text>')
        last_x, level = None, 0
        for v, who in sorted(zip(r["teams"], r["who"])):
            # numbers closer than a dot's width stack upwards, so three teams quoting one figure show as three dots
            level = level + 1 if last_x is not None and X(v) - last_x < 9 else 0
            if level == 0:
                last_x = X(v)
            o.append(f'<circle cx="{last_x:.1f}" cy="{y - 7 - 11 * level}" r="6" fill="var(--s1)" stroke="var(--surface)" stroke-width="2" data-tip="{E(who)}: {r["fmt"](v)}"/>')
        for name, v in r["ours"]:
            x = X(v)
            o.append(f'<path d="M{x:.1f},{y}l7,7l-7,7l-7,-7z" fill="var(--s2)" stroke="var(--surface)" stroke-width="2" data-tip="Ours, {E(name)}: {r["fmt"](v)}"/>')
    return "".join(o) + "</svg>"


def table(head: list[str], rows: list[list[str]], num_cols=()) -> str:
    th = "".join(f'<th class="{"n" if i in num_cols else ""}">{E(h)}</th>' for i, h in enumerate(head))
    body = "".join("<tr>" + "".join(f'<td class="{"n" if i in num_cols else ""}">{c}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def render(snapshot: str) -> str:
    res = metrics.compute(build.load_raw(snapshot))
    m = {k: v["value"] for k, v in res["metrics"].items()}
    rep = compare.run(snapshot)
    chk = checks.evaluate(res)
    s, fam = rep["summary"], {}
    for c in rep["claims"]:
        fam.setdefault(c["family"], []).append(c)
    pct = lambda v: f"{v:.1f}%"
    mult = lambda v: f"{v:.1f}x"

    def fam_row(f, label, fmt, ours):
        return {"label": label, "fmt": fmt, "teams": [c["claimed"] for c in fam[f]], "who": [c["project"] for c in fam[f]],
                "ours": [(n, m[i]) for n, i in ours]}

    strips = [
        fam_row("issuance_cover", "Issuance offset by Intents revenue", pct,
                [("360 days, on chain", "wallet_growth_cover_of_net_issuance_pct_360d"), ("30 days, on chain", "wallet_growth_cover_of_net_issuance_pct_30d"), ("90 days, on chain", "wallet_growth_cover_of_net_issuance_pct_90d")]),
        fam_row("burn_cover", "Issuance offset by fee burn", lambda v: f"{v:.2f}%",
                [("30 days", "burn_cover_of_net_issuance_pct_30d"), ("90 days", "burn_cover_of_net_issuance_pct_90d"), ("365 days", "burn_cover_of_net_issuance_pct_365d")]),
        fam_row("breakeven_multiple", "Growth needed to offset issuance", mult,
                [("90 days", "breakeven_multiple_90d"), ("30 days", "breakeven_multiple_30d"), ("365 days", "breakeven_multiple_365d")]),
        fam_row("intents_fees_30d", "Intents gross fees, 30 days", money, [("snapshot day", "intents_fees_30d")]),
        fam_row("price_yoy", "NEAR price change over a year", lambda v: f"+{v:.0f}%", [("day to day", "price_yoy"), ("30-day means", "price_yoy_30d_avg")]),
    ]
    wk = res["series"]["weekly_30d_means"]
    wv = res["series"]["wallets_vs_reported"]
    steps = res["series"]["wallet_cover_steps"]
    near = lambda v: f"{v / 1e6:.1f}M"

    status_cls = {"HOLDS": "ok", "HIT": "ok", "FAILS": "bad", "MISS": "bad", "PENDING": "wait"}
    unit = lambda c: {"%": "%", "x": "x"}.get(res["metrics"][c["metric"]]["unit"], "")
    check_rows = [[E(c["id"]), E(c["statement"]), E(c.get("due", "now")), f'{c["value"]:.3g}{unit(c)}',
                   f'<span class="st {status_cls[c["status"]]}">{c["status"].capitalize()}</span>'] for c in chk]
    claim_rows = [[E(c["family"]), E(c["project"]), compare.fmt(c["claimed"], c["unit"]), compare.fmt(c["best_dated"]["ours"], c["unit"]),
                   f'{c["best_dated"]["gap"]:.1%}', E(c["best_dated"]["status"]), f'<a href="{E(c["url"])}">quote</a>']
                  for c in sorted(rep["claims"], key=lambda c: (c["family"], c["claimed"]))]
    lo, hi = m["wallet_growth_cover_of_net_issuance_pct_360d"], m["wallet_growth_cover_of_net_issuance_pct_90d"]

    repo = f'<a href="{REPO_URL}">{E(REPO_URL.split("//")[-1])}</a>' if REPO_URL else "the repository"
    thesis = REPO_URL + "/blob/main/THESIS.md" if REPO_URL else "../THESIS.md"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NEAR, replicated</title><meta name="description" content="{s['claims']} published NEAR numbers recomputed from raw data, and the investment thesis that survives."><style>{CSS}</style></head><body><main>
<div class="mast"><span><b>NEAR, replicated</b> &middot; a replication study</span><span>NEAR Hackathon, Investment Thesis track &middot; data to {E(res['asof'])}</span></div>
<h1>About thirty teams measured NEAR. Do their numbers agree?</h1>
<p class="lede">We recomputed {s['claims']} numbers published by {s['sources']} of them from raw public data, kept what replicates, and built one thesis on it: NEAR is a growth bet on Intents revenue that today offsets {lo:.0f}% to {hi:.0f}% of new supply, and that revenue can be counted on chain.</p>
<div class="keys">
<div class="key"><b>{s['best_dated']['reproduced']} of {s['claims']}</b><span>published numbers are within 5% of our recomputation ({s['at_snapshot']['reproduced']} on the snapshot day itself)</span></div>
<div class="key"><b>{lo:.0f}&ndash;{hi:.0f}%</b><span>of net issuance is offset by captured Intents revenue, depending on the window</span></div>
<div class="key"><b>{m['revenue_wallets_near'] / 1e6:.2f}M</b><span>NEAR held by the three revenue wallets, read from an archival node; the total has never fallen</span></div>
<div class="key"><b>{m['growth_multiple_to_offset_issuance_90d']:.1f}&times;</b><span>growth in captured revenue needed before issuance is offset</span></div>
</div>
<p class="note" style="margin-top:8px">Snapshot {E(snapshot)}. Every figure on this page is generated by <code>python3 -m replicated.page</code> from raw data committed with its hashes. The full argument, with the evidence against, is in <a href="{thesis}">THESIS.md</a>.</p>

<section><p class="kicker">1 &middot; Replication</p>
<h2>Where the teams disagree, it is the definition</h2>
<p>Each row has its own scale starting at zero. Circles are numbers published by other teams; diamonds are our recomputation under different, equally defensible definitions. The circles spread about as widely as the diamonds do.</p>
<div class="legend"><span><i style="background:var(--s1)"></i>Published by a team</span><span><i class="dia" style="background:var(--s2)"></i>Our recomputation, per definition</span></div>
<figure>{strip(strips)}</figure></section>

<section><p class="kicker">2 &middot; Revenue</p>
<h2>The revenue is on chain, and it is all still there</h2>
<p>Reported revenue does not have to be taken on trust. It arrives as NEAR in three wallets, and their balances at past block heights can be read from any archival node.</p>
<div class="grid2">
<figure><h3>Revenue wallets against reported revenue</h3><figcaption>NEAR held by the three wallets at 30-day block samples, next to DefiLlama's reported revenue accumulated from the first sample.</figcaption>
{line_chart([x['day'] for x in wv], [("On chain", "--s1", [x['wallets_near'] for x in wv]), ("Reported", "--s2", [x['defillama_cumulative_near'] for x in wv])], near)}</figure>
<figure><h3>Share of new supply offset, per 30-day step</h3><figcaption>Growth of the wallets divided by growth of total supply, both from block data. Lumpy, which is why a single 30-day reading misleads.</figcaption>
{bar_chart([month_label(x['to']) for x in steps], [x['cover_pct'] for x in steps], lambda v: f"{v:.0f}%", w=460, h=262)}</figure>
</div></section>

<section><p class="kicker">3 &middot; Usage</p>
<h2>Usage left the base layer and went to Intents</h2>
<p>Two charts, two scales: transactions and dollars are not comparable on one axis. Intents volume and fees come from one upstream source (datasets NEAR publishes on Dune, read through DefiLlama), so agreement between teams on these is not independent confirmation.</p>
<div class="grid2">
<figure><h3>Base-layer transactions per day</h3><figcaption>30-day mean, weekly samples. Now {count(m['tx_per_day_30d'])}, {m['tx_yoy_30d']:.0f}% in a year.</figcaption>
{line_chart([x['day'] for x in wk], [("Transactions per day", "--s1", [x['tx_per_day'] for x in wk])], count)}</figure>
<figure><h3>NEAR Intents volume per day</h3><figcaption>30-day mean, weekly samples. Now {money(m['intents_volume_avg_30d'])}, +{m['intents_volume_yoy_30d']:.0f}% in a year.</figcaption>
{line_chart([x['day'] for x in wk], [("Intents volume per day", "--s1", [x['intents_volume_usd_per_day'] for x in wk])], money)}</figure>
</div></section>

<section><p class="kicker">4 &middot; Falsification</p>
<h2>What would change our mind</h2>
<p>K rows are kill conditions: if one fails on a new snapshot, the thesis is dropped and <code>python3 -m replicated.checks</code> exits with an error. P rows are predictions written on 2026-11-11.</p>
{table(["Id", "Condition", "Due", "Today", "Status"], check_rows, num_cols=(3,))}</section>

<section><p class="kicker">5 &middot; Data</p>
<h2>Every claim we checked</h2>
<p class="note">"Ours" is the closest standard definition on the best day within {rep['lookback_days']} days before the snapshot. A match means a standard definition gives the published number, not that the team computed it that way.</p>
<details><summary>All {s['claims']} claims from {s['sources']} repositories</summary>
{table(["Metric", "Project", "Published", "Ours", "Gap", "Result", "Source"], claim_rows, num_cols=(2, 3, 4))}</details>
<details><summary>Data behind the charts</summary>
{table(["Sample", "Wallets, NEAR", "Reported cumulative, NEAR"], [[x['day'], f"{x['wallets_near']:,.0f}", f"{x['defillama_cumulative_near']:,.0f}"] for x in wv], num_cols=(1, 2))}
{table(["Step ending", "Wallet growth, NEAR", "Net issuance, NEAR", "Offset"], [[x['to'], f"{x['wallet_growth_near']:,.0f}", f"{x['net_issuance_near']:,.0f}", f"{x['cover_pct']:.1f}%"] for x in steps], num_cols=(1, 2, 3))}
</details></section>

<footer>
<div><b>Reproduce</b><p>Python 3.9+, standard library only. Clone {repo}, then <code>python3 -m replicated.build</code>. Runs offline from the committed snapshot.</p></div>
<div><b>Sources</b><p>DefiLlama (Intents volume, fees, revenue), NearBlocks (daily charts), a public archival RPC node (supply, wallet balances, validators). No API key.</p></div>
<div><b>Credit</b><p>The numbers under test belong to the teams quoted in the claims table, each linked to its source. Not investment advice. MIT license.</p></div>
</footer>
</main><div id="tip"></div><script>{JS}</script></body></html>
"""


def main() -> int:
    snap = build.thesis_snapshot()
    out = ROOT / "docs"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(render(snap))
    print(f"docs/index.html written from snapshot {snap}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
