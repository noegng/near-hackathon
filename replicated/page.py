"""Render docs/index.html: one static, self-contained page (inline SVG, no dependencies, no network).

Reads the latest snapshot and recomputes everything, so the page cannot drift from the build.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

from . import build, checks, compare, metrics

ROOT = Path(__file__).resolve().parent.parent
E = html.escape
REPO_URL = "https://github.com/noegng/near-hackathon"  # empty makes the page link relatively

CSS = """
:root{color-scheme:light;--surface:#fcfcfb;--panel:#f3f2ef;--text:#0b0b0b;--text2:#52514e;--muted:#8a8985;--grid:#e3e2de;
--s1:#2a78d6;--s2:#eb6834;--good:#0ca30c;--crit:#d03b3b;--warn:#fab219}
@media (prefers-color-scheme:dark){:root{color-scheme:dark;--surface:#1a1a19;--panel:#242422;--text:#f0efec;--text2:#c3c2b7;--muted:#8f8e88;--grid:#34342f;--s1:#3987e5;--s2:#d95926}}
*{box-sizing:border-box}body{margin:0;background:var(--surface);color:var(--text);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:980px;margin:0 auto;padding:40px 20px 80px}h1{font-size:2rem;line-height:1.2;margin:0 0 12px}h2{font-size:1.3rem;margin:56px 0 8px}
h3{font-size:1rem;margin:0 0 2px}p{margin:8px 0;max-width:70ch}.lede{font-size:1.15rem;color:var(--text2)}.note{color:var(--text2);font-size:.9rem}
a{color:var(--s1)}code{font:0.85em ui-monospace,Menlo,monospace;background:var(--panel);padding:1px 5px;border-radius:4px;white-space:nowrap}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:28px 0}
.tile{background:var(--panel);border-radius:10px;padding:16px}.tile b{display:block;font-size:1.9rem;line-height:1.1;font-variant-numeric:tabular-nums}
.tile span{color:var(--text2);font-size:.9rem}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:28px}
figure{margin:20px 0 0}figcaption{color:var(--text2);font-size:.9rem;margin-bottom:6px}
svg{display:block;width:100%;height:auto;overflow:visible}svg text{fill:var(--text2);font:12px system-ui,sans-serif;font-variant-numeric:tabular-nums}
svg .strong{fill:var(--text);font-weight:600}.gridl{stroke:var(--grid);stroke-width:1}.hit{fill:transparent;cursor:crosshair}
.dot{opacity:0;pointer-events:none}.hit:hover+.dot{opacity:1}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:.85rem;color:var(--text2);margin:4px 0}.legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}
.legend i.dia{border-radius:0;transform:rotate(45deg)}
table{border-collapse:collapse;width:100%;font-size:.88rem;font-variant-numeric:tabular-nums}th,td{text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--grid);vertical-align:top}
th{color:var(--text2);font-weight:600}td.n,th.n{text-align:right}details{margin:10px 0}summary{cursor:pointer;color:var(--text2);font-size:.9rem}
.st{font-weight:600;white-space:nowrap}.st.ok::before{content:"\\2713  ";color:var(--good)}.st.bad::before{content:"\\2717  ";color:var(--crit)}.st.wait::before{content:"\\25CB  ";color:var(--muted)}
.scroll{overflow-x:auto}#tip{position:fixed;pointer-events:none;background:var(--text);color:var(--surface);padding:6px 9px;border-radius:6px;font-size:.8rem;display:none;z-index:9;max-width:260px}
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
    shift = (sum(out) - sum(ys)) / len(ys)
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

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NEAR, replicated</title><style>{CSS}</style></head><body><main>
<h1>NEAR, replicated</h1>
<p class="lede">About thirty teams measured NEAR for the same hackathon track. We recomputed {s['claims']} of their published numbers from raw data, kept what replicates, and built one thesis on it: NEAR is a growth bet on Intents revenue that today offsets {lo:.0f}% to {hi:.0f}% of new supply, and that revenue can be counted on chain.</p>
<p class="note">Snapshot {E(snapshot)}, daily data to {E(res['asof'])}. Everything on this page is generated by <code>python3 -m replicated.page</code> from the committed raw data. Full argument: <a href="{REPO_URL + '/blob/main/THESIS.md' if REPO_URL else '../THESIS.md'}">THESIS.md</a>.</p>
<div class="tiles">
<div class="tile"><b>{s['best_dated']['reproduced']} / {s['claims']}</b><span>published numbers within 5% of our recomputation ({s['at_snapshot']['reproduced']} on the snapshot day itself)</span></div>
<div class="tile"><b>{lo:.0f}% to {hi:.0f}%</b><span>of net issuance offset by captured Intents revenue, depending on the window</span></div>
<div class="tile"><b>{m['revenue_wallets_near'] / 1e6:.2f}M NEAR</b><span>held by the three revenue wallets, read from an archival node; the total has never fallen</span></div>
<div class="tile"><b>{m['growth_multiple_to_offset_issuance_90d']:.1f}x</b><span>growth in captured revenue needed before issuance is offset</span></div>
</div>

<h2>Where the teams disagree, it is the definition</h2>
<p>Each row has its own scale starting at zero. Circles are numbers published by other teams; diamonds are our recomputation under different, equally defensible definitions. The spread of the circles is about as wide as the spread of the diamonds.</p>
<div class="legend"><span><i style="background:var(--s1)"></i>Published by a team</span><span><i class="dia" style="background:var(--s2)"></i>Our recomputation, per definition</span></div>
<figure>{strip(strips)}</figure>

<h2>The revenue is on chain, and it is all still there</h2>
<div class="grid2">
<figure><h3>Revenue wallets against reported revenue</h3><figcaption>NEAR held by the three wallets at 30-day block samples, next to DefiLlama's reported revenue accumulated from the first sample.</figcaption>
<div class="legend"><span><i style="background:var(--s1)"></i>Held on chain</span><span><i style="background:var(--s2)"></i>Reported, cumulative</span></div>
{line_chart([x['day'] for x in wv], [("On chain", "--s1", [x['wallets_near'] for x in wv]), ("Reported", "--s2", [x['defillama_cumulative_near'] for x in wv])], near)}</figure>
<figure><h3>Share of new supply offset, per 30-day step</h3><figcaption>Growth of the wallets divided by growth of total supply, both from block data. Lumpy, which is why a single 30-day reading misleads.</figcaption>
{bar_chart([month_label(x['to']) for x in steps], [x['cover_pct'] for x in steps], lambda v: f"{v:.0f}%", w=460, h=262)}</figure>
</div>

<h2>Usage left the base layer and went to Intents</h2>
<p>Two charts, two scales: transactions and dollars are not comparable on one axis. Intents volume and fees come from one upstream source (datasets NEAR publishes on Dune, read through DefiLlama), so agreement between teams on these is not independent confirmation.</p>
<div class="grid2">
<figure><h3>Base-layer transactions per day</h3><figcaption>30-day mean, weekly samples. Now {count(m['tx_per_day_30d'])}, {m['tx_yoy_30d']:.0f}% in a year.</figcaption>
{line_chart([x['day'] for x in wk], [("Transactions per day", "--s1", [x['tx_per_day'] for x in wk])], count)}</figure>
<figure><h3>NEAR Intents volume per day</h3><figcaption>30-day mean, weekly samples. Now {money(m['intents_volume_avg_30d'])}, +{m['intents_volume_yoy_30d']:.0f}% in a year.</figcaption>
{line_chart([x['day'] for x in wk], [("Intents volume per day", "--s1", [x['intents_volume_usd_per_day'] for x in wk])], money)}</figure>
</div>

<h2>What would change our mind</h2>
<p>K rows are kill conditions: if one fails on a new snapshot, the thesis is dropped and <code>python3 -m replicated.checks</code> exits with an error. P rows are predictions written on 2026-11-11.</p>
{table(["Id", "Condition", "Due", "Today", "Status"], check_rows, num_cols=(3,))}

<h2>Every claim we checked</h2>
<p class="note">"Ours" is the closest standard definition on the best day within {rep['lookback_days']} days before the snapshot. A match means a standard definition gives the published number, not that the team computed it that way.</p>
<details><summary>Show all {s['claims']} claims from {s['sources']} repositories</summary>
{table(["Metric", "Project", "Published", "Ours", "Gap", "Result", "Source"], claim_rows, num_cols=(2, 3, 4))}</details>
<details><summary>Data behind the charts</summary>
{table(["Sample", "Wallets, NEAR", "Reported cumulative, NEAR"], [[x['day'], f"{x['wallets_near']:,.0f}", f"{x['defillama_cumulative_near']:,.0f}"] for x in wv], num_cols=(1, 2))}
{table(["Step ending", "Wallet growth, NEAR", "Net issuance, NEAR", "Offset"], [[x['to'], f"{x['wallet_growth_near']:,.0f}", f"{x['net_issuance_near']:,.0f}", f"{x['cover_pct']:.1f}%"] for x in steps], num_cols=(1, 2, 3))}
</details>
</main><div id="tip"></div><script>{JS}</script></body></html>
"""


def main() -> int:
    snap = build.latest_snapshot()
    out = ROOT / "docs"
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(render(snap))
    print(f"docs/index.html written from snapshot {snap}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
