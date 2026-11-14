"""Compare each published claim with our recomputation.

For a claim, `candidates` lists the metric definitions that could plausibly have
produced it (different windows, net vs gross issuance, ...). We report:
  * at_publication: the closest candidate as of the day the number was published: the end
                    day the quote states if it states one, otherwise the last complete UTC
                    day before the commit that wrote the quote (`published`, recorded by
                    replicated.date_claims). One day per claim, no search over days. A day
                    after the snapshot's last day is read from the first later snapshot that
                    holds it, or the newest snapshot, capped at its last day, until one does.
  * at_snapshot:    the closest candidate as of our snapshot's last complete day, for
                    reference: it shows how far a number drifts once the data moves on.
Metrics that only describe the moment a snapshot was fetched (validators, stake, RPC samples)
have no past days: at publication they are read from the first snapshot fetched on or after the
day the quote was committed (the earliest snapshot for older quotes, the newest one until a later
snapshot exists), and at_snapshot from our snapshot. `dated` is false for them.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

from . import build, metrics

ROOT = Path(__file__).resolve().parent.parent
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


def published_day(claim: dict) -> int:
    """Unix day the claim is compared on, before capping at the snapshot's last complete day."""
    if "stated_asof" in claim:
        return metrics.day_of(claim["stated_asof"] + "T00:00:00Z")
    return metrics.day_of(claim["published"]["date"][:10] + "T00:00:00Z") - metrics.DAY


def run(snapshot: str) -> dict:
    raw = build.load_raw(snapshot)
    reg = json.loads((ROOT / "claims" / "claims.json").read_text())
    base = metrics.compute(raw)
    last = metrics.day_of(base["asof"] + "T00:00:00Z")
    # A claim published after the snapshot's last day is read from the first later snapshot that holds
    # its day (the newest one if none does yet), so it is not compared with data older than it was.
    later = []
    for s in build.all_snapshots():
        if s > snapshot:
            r = build.load_raw(s)
            later.append((metrics.day_of(metrics.compute(r)["asof"] + "T00:00:00Z"), r))
    by_day = {(0, last): base}
    # Snapshot-only metrics (validators, stake) are read from the snapshot fetched closest after publication.
    fetched = {s: (base if s == snapshot else None) for s in build.all_snapshots()}

    def at_fetch(commit_date: str) -> tuple[str, dict]:
        s = next((s for s in fetched if s >= commit_date[:10]), list(fetched)[-1])
        if fetched[s] is None:
            fetched[s] = metrics.compute(build.load_raw(s))
        return s, fetched[s]

    rows = []
    for c in reg["claims"]:
        want = published_day(c)
        src, day = 0, min(want, last)
        if want > last and later:
            src = next((i for i, (end, _) in enumerate(later, 1) if end >= want), len(later))
            day = min(want, later[src - 1][0])
        if (src, day) not in by_day:
            by_day[(src, day)] = metrics.compute(later[src - 1][1] if src else raw, day)
        at = by_day[(src, day)]
        g0, id0, v0 = closest(base["metrics"], c["candidates"], c["value"])
        gp, idp, vp = closest(at["metrics"], c["candidates"], c["value"])
        dated = not metrics.snapshot_only(idp)
        if not dated:
            snap_u, at = at_fetch(c["published"]["date"])
            gp, idp, vp = closest(at["metrics"], c["candidates"], c["value"])
        src = reg["sources"][c["source"]]
        rows.append({
            "id": c["id"], "family": c["family"], "project": src["project"], "claimed": c["value"], "unit": c["unit"],
            "quote": c["quote"], "published": c["published"]["date"], "published_commit": c["published"]["commit"],
            "url": f"https://{'gitlab.com' if src.get('host') == 'gitlab' else 'github.com'}/{src['repo']}/{'-/' if src.get('host') == 'gitlab' else ''}blob/{src['commit']}/{c['file']}",
            "at_publication": {"metric": idp, "ours": vp, "gap": gp, "status": status(gp), "dated": dated,
                               "asof": at["asof"] if dated else f"snapshot {snap_u}"},
            "at_snapshot": {"metric": id0, "ours": v0, "gap": g0, "status": status(g0)},
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
            "reproduced_at_publication": sum(r["at_publication"]["status"] == "reproduced" for r in rs),
            "reproduced_at_snapshot": sum(r["at_snapshot"]["status"] == "reproduced" for r in rs),
        }
    tally = lambda key: {s: sum(r[key]["status"] == s for r in rows) for s in ("reproduced", "close", "not reproduced")}
    return {"snapshot": snapshot, "asof": base["asof"],
            "thresholds": {"reproduced": REPRODUCED, "close": CLOSE},
            "summary": {"claims": len(rows), "sources": len(reg["sources"]), "undated": sum(not r["at_publication"]["dated"] for r in rows),
                        "at_publication": tally("at_publication"), "at_snapshot": tally("at_snapshot")},
            "families": families, "claims": rows}


def fmt(v: float, unit: str) -> str:
    if unit.startswith("USD"):
        return f"${v / 1e9:.2f}B" if abs(v) >= 1e9 else f"${v / 1e6:.2f}M" if abs(v) >= 1e6 else f"${v:,.0f}"
    if unit == "count":
        return f"{v:.0f}"
    return f"{v:,.2f}"


def markdown(res: dict) -> str:
    s = res["summary"]
    pub, snap = s["at_publication"], s["at_snapshot"]
    L = [f"# Replication table (snapshot {res['snapshot']}, data to {res['asof']})", "",
         f"{s['claims']} published numbers from {s['sources']} thesis repositories, each recomputed from raw data.",
         f"Thresholds: reproduced = within {res['thresholds']['reproduced']:.0%} of the published value, close = within {res['thresholds']['close']:.0%}.",
         "Each claim is compared on one day: the end day its quote states, otherwise the last complete UTC day before the",
         f"commit that wrote it. {s['undated']} claims use a metric that only describes the moment of a snapshot (validators, stake) and are compared on the first snapshot fetched on or after the day they were committed, or the earliest snapshot for older quotes.", "",
         "| Compared on | Reproduced | Close | Not reproduced |", "| --- | --- | --- | --- |",
         f"| The day each number was published | {pub['reproduced']} | {pub['close']} | {pub['not reproduced']} |",
         f"| Our snapshot day, for reference | {snap['reproduced']} | {snap['close']} | {snap['not reproduced']} |", "",
         "## Spread between teams, per metric family", "",
         "| Family | Teams' numbers | Min | Median | Max | Spread / median | Reproduced (publication day) |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for f, x in sorted(res["families"].items(), key=lambda kv: -(kv[1]["spread_pct_of_median"] or 0)):
        u = x["unit"]
        sp = f"{x['spread_pct_of_median']:.0f}%" if x["spread_pct_of_median"] is not None else "n/a"
        L.append(f"| {f} | {x['n']} | {fmt(x['min'], u)} | {fmt(x['median'], u)} | {fmt(x['max'], u)} | {sp} | {x['reproduced_at_publication']}/{x['n']} |")
    L += ["", "## Every claim", "", "| Family | Project | Published | Commit date | Ours, publication day | Gap | Ours, snapshot day | Gap | Source |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in sorted(res["claims"], key=lambda r: (r["family"], r["claimed"])):
        p, a, u = r["at_publication"], r["at_snapshot"], r["unit"]
        L.append(f"| {r['family']} | {r['project']} | {fmt(r['claimed'], u)} | {r['published'][:10]} | {fmt(p['ours'], u)} `{p['metric']}` @ {p['asof']} | {p['gap']:.1%} "
                 f"| {fmt(a['ours'], u)} `{a['metric']}` | {a['gap']:.1%} | [quote]({r['url']}) |")
    return "\n".join(L) + "\n"


def main() -> int:
    res = run(build.thesis_snapshot())
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    (out / "replication.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    (out / "replication.md").write_text(markdown(res))
    print(json.dumps(res["summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
