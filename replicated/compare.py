"""Compare each published claim with our recomputation.

For a claim, `candidates` lists the metric definitions that could plausibly have
produced it (different windows, net vs gross issuance, ...). We report:
  * at_snapshot: the closest candidate as of our snapshot's last complete day;
  * best_dated:  the closest (candidate, day) over the LOOKBACK days before it, since
                 the theses were published on different days.
The second search has many degrees of freedom, so a match there says "a standard
definition on a nearby date gives this number", not "this is what the team computed".
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

from . import build, metrics

ROOT = Path(__file__).resolve().parent.parent
LOOKBACK = 14
REPRODUCED, CLOSE = 0.05, 0.15  # relative gap thresholds


def rel_gap(ours: float, theirs: float) -> float:
    if theirs == 0:
        return float("inf") if ours else 0.0
    return abs(ours - theirs) / abs(theirs)


def status(gap: float) -> str:
    return "reproduced" if gap <= REPRODUCED else "close" if gap <= CLOSE else "not reproduced"


def closest(mset: dict, cands: list[str], value: float):
    best = None
    for c in cands:
        if c in mset:
            g = rel_gap(mset[c]["value"], value)
            if best is None or g < best[0]:
                best = (g, c, mset[c]["value"])
    return best


def run(snapshot: str) -> dict:
    raw = build.load_raw(snapshot)
    reg = json.loads((ROOT / "claims" / "claims.json").read_text())
    base = metrics.compute(raw)
    end = metrics.day_of(base["asof"] + "T00:00:00Z")
    dated = {end - k * metrics.DAY: (base if k == 0 else metrics.compute(raw, end - k * metrics.DAY)) for k in range(LOOKBACK + 1)}
    rows = []
    for c in reg["claims"]:
        g0, id0, v0 = closest(base["metrics"], c["candidates"], c["value"])
        gb, idb, vb, dayb = min(((*closest(d["metrics"], c["candidates"], c["value"]), d["asof"]) for d in dated.values()), key=lambda t: t[0])
        src = reg["sources"][c["source"]]
        rows.append({
            "id": c["id"], "family": c["family"], "project": src["project"], "claimed": c["value"], "unit": c["unit"],
            "quote": c["quote"],
            "url": f"https://{'gitlab.com' if src.get('host') == 'gitlab' else 'github.com'}/{src['repo']}/{'-/' if src.get('host') == 'gitlab' else ''}blob/{src['commit']}/{c['file']}",
            "at_snapshot": {"metric": id0, "ours": v0, "gap": g0, "status": status(g0)},
            "best_dated": {"metric": idb, "ours": vb, "gap": gb, "status": status(gb), "asof": dayb},
        })
    fams = {}
    for r in rows:
        fams.setdefault(r["family"], []).append(r)
    families = {}
    for f, rs in fams.items():
        vals = [r["claimed"] for r in rs]
        families[f] = {
            "n": len(rs), "unit": rs[0]["unit"], "min": min(vals), "max": max(vals), "median": statistics.median(vals),
            "spread_pct_of_median": (max(vals) - min(vals)) / abs(statistics.median(vals)) * 100 if statistics.median(vals) else None,
            "reproduced_at_snapshot": sum(r["at_snapshot"]["status"] == "reproduced" for r in rs),
            "reproduced_best_dated": sum(r["best_dated"]["status"] == "reproduced" for r in rs),
        }
    tally = lambda key: {s: sum(r[key]["status"] == s for r in rows) for s in ("reproduced", "close", "not reproduced")}
    return {"snapshot": snapshot, "asof": base["asof"], "lookback_days": LOOKBACK,
            "thresholds": {"reproduced": REPRODUCED, "close": CLOSE},
            "summary": {"claims": len(rows), "sources": len(reg["sources"]), "at_snapshot": tally("at_snapshot"), "best_dated": tally("best_dated")},
            "families": families, "claims": rows}


def fmt(v: float, unit: str) -> str:
    if unit.startswith("USD"):
        return f"${v / 1e9:.2f}B" if abs(v) >= 1e9 else f"${v / 1e6:.2f}M" if abs(v) >= 1e6 else f"${v:,.0f}"
    if unit == "count":
        return f"{v:.0f}"
    return f"{v:,.2f}"


def markdown(res: dict) -> str:
    s = res["summary"]
    L = [f"# Replication table (snapshot {res['snapshot']}, data to {res['asof']})", "",
         f"{s['claims']} published numbers from {s['sources']} thesis repositories, each recomputed from raw data.",
         f"Thresholds: reproduced = within {res['thresholds']['reproduced']:.0%} of the published value, close = within {res['thresholds']['close']:.0%}.", "",
         "| Comparison | Reproduced | Close | Not reproduced |", "| --- | --- | --- | --- |",
         f"| Same definition family, our snapshot day | {s['at_snapshot']['reproduced']} | {s['at_snapshot']['close']} | {s['at_snapshot']['not reproduced']} |",
         f"| Best day within {res['lookback_days']} days before | {s['best_dated']['reproduced']} | {s['best_dated']['close']} | {s['best_dated']['not reproduced']} |", "",
         "## Spread between teams, per metric family", "",
         "| Family | Teams' numbers | Min | Median | Max | Spread / median | Reproduced (best day) |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for f, x in sorted(res["families"].items(), key=lambda kv: -(kv[1]["spread_pct_of_median"] or 0)):
        u = x["unit"]
        sp = f"{x['spread_pct_of_median']:.0f}%" if x["spread_pct_of_median"] is not None else "n/a"
        L.append(f"| {f} | {x['n']} | {fmt(x['min'], u)} | {fmt(x['median'], u)} | {fmt(x['max'], u)} | {sp} | {x['reproduced_best_dated']}/{x['n']} |")
    L += ["", "## Every claim", "", "| Family | Project | Published | Ours (snapshot day) | Gap | Best dated match | Gap | Source |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in sorted(res["claims"], key=lambda r: (r["family"], r["claimed"])):
        a, b, u = r["at_snapshot"], r["best_dated"], r["unit"]
        L.append(f"| {r['family']} | {r['project']} | {fmt(r['claimed'], u)} | {fmt(a['ours'], u)} `{a['metric']}` | {a['gap']:.1%} | {fmt(b['ours'], u)} `{b['metric']}` @ {b['asof']} | {b['gap']:.1%} | [quote]({r['url']}) |")
    return "\n".join(L) + "\n"


def main() -> int:
    res = run(build.latest_snapshot())
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    (out / "replication.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    (out / "replication.md").write_text(markdown(res))
    print(json.dumps(res["summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
