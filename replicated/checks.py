"""The thesis as executable conditions. `python3 -m replicated.checks` evaluates every
condition in THESIS.md against the latest snapshot and exits 1 if a kill condition fires.

Kill conditions (K) say what result would make us drop the thesis. Dated predictions (P)
are written before their date and stay PENDING until a snapshot taken on or after it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from . import build, metrics

ROOT = Path(__file__).resolve().parent.parent

# id, metric, operator, threshold, statement
KILL = [
    ("K1", "intents_volume_yoy_30d", ">", 0.0, "Intents volume is higher than a year ago (30-day mean)."),
    ("K2", "wallet_growth_over_defillama_revenue_90d", "between", (0.9, 1.1), "Reported captured revenue matches what the revenue wallets received on chain (90 days)."),
    ("K3", "revenue_wallets_min_balance_ratio", ">=", 1.0, "Captured NEAR has not left the revenue wallets between any two samples."),
    ("K4", "wallet_growth_cover_of_net_issuance_pct_90d", ">=", 10.0, "Captured revenue offsets at least 10% of net issuance (90 days, on chain)."),
    ("K5", "wallet_cover_pct_last_180d", ">", "wallet_cover_pct_first_180d", "The cover over the last 180 days is higher than over the 180 days before."),
]
# id, due date, metric, operator, threshold, statement. Written on 2026-11-11.
PREDICTIONS = [
    ("P1", "2027-02-09", "wallet_growth_cover_of_net_issuance_pct_90d", ">=", 18.0, "90-day on-chain cover of net issuance is at least 18% (it is 18.2% today)."),
    ("P2", "2027-05-10", "wallet_cover_pct_last_180d", ">=", 18.0, "180-day on-chain cover reaches 18% (14.5% today)."),
    ("P3", "2027-05-10", "revenue_wallets_min_balance_ratio", ">=", 1.0, "Captured NEAR is still held or has been burned, not spent: wallet total has not fallen."),
    ("P4", "2027-11-11", "intents_volume_yoy_30d", ">=", 25.0, "Intents volume is at least 25% above its level of November 2026."),
]


def holds(value, op, thr, m) -> bool:
    if isinstance(thr, str):
        thr = m[thr]["value"]
    if op == ">":
        return value > thr
    if op == ">=":
        return value >= thr
    if op == "between":
        return thr[0] <= value <= thr[1]
    raise ValueError(op)


def evaluate(result: dict) -> list[dict]:
    m, snap_day = result["metrics"], result["asof_rpc_supply"]
    out = []
    for cid, metric, op, thr, text in KILL:
        ok = holds(m[metric]["value"], op, thr, m)
        out.append({"id": cid, "kind": "kill", "statement": text, "metric": metric, "value": m[metric]["value"],
                    "op": op, "threshold": thr, "status": "HOLDS" if ok else "FAILS"})
    for pid, due, metric, op, thr, text in PREDICTIONS:
        if snap_day < due:
            st = "PENDING"
        else:
            st = "HIT" if holds(m[metric]["value"], op, thr, m) else "MISS"
        out.append({"id": pid, "kind": "prediction", "due": due, "statement": text, "metric": metric,
                    "value": m[metric]["value"], "op": op, "threshold": thr, "status": st})
    return out


def main() -> int:
    snap = build.latest_snapshot()
    result = metrics.compute(build.load_raw(snap))
    rows = evaluate(result)
    (ROOT / "out").mkdir(exist_ok=True)
    (ROOT / "out" / "checks.json").write_text(json.dumps({"snapshot": snap, "checks": rows}, indent=1) + "\n")
    for r in rows:
        due = f" (due {r['due']})" if "due" in r else ""
        print(f"{r['status']:8} {r['id']}{due}: {r['statement']}  [{r['metric']} = {r['value']:.4g}, needs {r['op']} {r['threshold']}]")
    return 1 if any(r["status"] == "FAILS" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
