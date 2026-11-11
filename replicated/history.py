"""Every committed snapshot, side by side: the headline metrics, the kill conditions
re-evaluated on each one, and the past daily values a source changed between two snapshots.

`python3 -m replicated.history` writes out/history.md and out/history.json and exits 1 if a
kill condition fails on the newest snapshot. A scheduled job adds one snapshot per day.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import build, checks, metrics, restated

ROOT = Path(__file__).resolve().parent.parent
HEADLINE = ("intents_volume_30d", "intents_fees_30d", "intents_revenue_30d",
            "wallet_growth_cover_of_net_issuance_pct_90d", "wallet_growth_over_defillama_revenue_90d",
            "tx_per_day_30d", "price_usd")


def iso(day: int) -> str:
    return datetime.fromtimestamp(day, timezone.utc).strftime("%Y-%m-%d")


def run() -> dict:
    snaps = build.all_snapshots()
    raws = {s: build.load_raw(s) for s in snaps}
    rows = []
    for s in snaps:
        res = metrics.compute(raws[s])
        rows.append({"snapshot": s, "asof": res["asof"],
                     "metrics": {k: res["metrics"][k]["value"] for k in HEADLINE},
                     "checks": {c["id"]: c["status"] for c in checks.evaluate(res)}})
    restatements = []
    for a, b in zip(snaps, snaps[1:]):
        for key in restated.SERIES:
            d = restated.diff(metrics.llama_series(raws[a][key]), metrics.llama_series(raws[b][key]))
            restatements.append({"older": a, "newer": b, "series": key, "days_compared": d["days_compared"],
                                 "days_changed": d["days_changed"], "sum_old": d["sum_old"], "sum_new": d["sum_new"],
                                 "largest": [{"day": iso(day), "old": x, "new": y}
                                             for day, x, y in sorted(d["changed"], key=lambda t: -abs(t[2] - t[1]))[:5]]})
    return {"thesis_snapshot": build.thesis_snapshot(), "snapshots": rows, "restatements": restatements}


def money(v: float) -> str:
    return f"${v / 1e9:.3f}B" if abs(v) >= 1e9 else f"${v / 1e6:.3f}M" if abs(v) >= 1e6 else f"${v:,.0f}"


def markdown(res: dict) -> str:
    L = ["# Snapshot history", "",
         f"Raw snapshots committed: {len(res['snapshots'])}. THESIS.md is written from `{res['thesis_snapshot']}`;",
         "the conditions under which it is dropped are evaluated again on every later snapshot.", "",
         "| Snapshot | Data to | Intents volume 30 d | Fees 30 d | Captured 30 d | Cover of net issuance 90 d | Wallets / reported 90 d | Tx per day | Price | Kill conditions | Predictions |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in res["snapshots"]:
        m, c = r["metrics"], r["checks"]
        kills = [k for k in c if k.startswith("K")]
        failed = [k for k in kills if c[k] == "FAILS"]
        preds = ", ".join(f"{k} {v.lower()}" for k, v in c.items() if k.startswith("P"))
        L.append(f"| {r['snapshot']} | {r['asof']} | {money(m['intents_volume_30d'])} | {money(m['intents_fees_30d'])} | {money(m['intents_revenue_30d'])} "
                 f"| {m['wallet_growth_cover_of_net_issuance_pct_90d']:.1f}% | {m['wallet_growth_over_defillama_revenue_90d']:.2f}x | {m['tx_per_day_30d']:,.0f} | ${m['price_usd']:.2f} "
                 f"| {'all ' + str(len(kills)) + ' hold' if not failed else 'FAILS: ' + ', '.join(failed)} | {preds} |")
    L += ["", "## Past values changed by the source between snapshots", ""]
    if not res["restatements"]:
        L.append("Needs two snapshots; one is committed so far.")
    else:
        L += ["Days present in both snapshots whose value differs. A thesis that quotes a 30-day total inherits these changes.", "",
              "| Older | Newer | Series | Days compared | Days changed | Total before | Total after | Largest changes |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for x in res["restatements"]:
            big = "; ".join(f"{g['day']}: {g['old']:,.0f} to {g['new']:,.0f}" for g in x["largest"]) or "none"
            L.append(f"| {x['older']} | {x['newer']} | {x['series']} | {x['days_compared']} | {x['days_changed']} | {money(x['sum_old'])} | {money(x['sum_new'])} | {big} |")
    return "\n".join(L) + "\n"


def main() -> int:
    res = run()
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    (out / "history.json").write_text(json.dumps(res, indent=1) + "\n")
    (out / "history.md").write_text(markdown(res))
    last = res["snapshots"][-1]
    failed = [k for k, v in last["checks"].items() if v == "FAILS"]
    print(f"{len(res['snapshots'])} snapshots, newest {last['snapshot']}: " + ("kill conditions hold" if not failed else "FAILS " + ", ".join(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
