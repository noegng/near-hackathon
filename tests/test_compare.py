import json
import unittest
from pathlib import Path

from replicated import build, compare

ROOT = Path(__file__).resolve().parent.parent


class Compare(unittest.TestCase):
    def test_gap_and_status_thresholds(self):
        self.assertAlmostEqual(compare.rel_gap(105, 100), 0.05)
        self.assertAlmostEqual(compare.rel_gap(-84, -85), 1 / 85)
        self.assertEqual(compare.status(0.05), "reproduced")
        self.assertEqual(compare.status(0.051), "close")
        self.assertEqual(compare.status(0.2), "not reproduced")

    def test_closest_picks_smallest_gap_and_skips_unknown_ids(self):
        m = {"a": {"value": 10.0}, "b": {"value": 19.0}}
        gap, mid, val = compare.closest(m, ["a", "b", "nope"], 20.0)
        self.assertEqual((mid, val), ("b", 19.0))

    def test_registry_is_well_formed(self):
        reg = json.loads((ROOT / "claims" / "claims.json").read_text())
        known = set(build.metrics.compute(build.load_raw(build.thesis_snapshot()))["metrics"])
        ids = [c["id"] for c in reg["claims"]]
        self.assertEqual(len(ids), len(set(ids)))
        for c in reg["claims"]:
            self.assertIn(c["source"], reg["sources"])
            self.assertTrue(c["quote"].strip())
            self.assertTrue(c["candidates"])
            for cand in c["candidates"]:
                self.assertIn(cand, known, f"{c['id']}: unknown metric {cand}")
        for s in reg["sources"].values():
            self.assertRegex(s["commit"], r"^[0-9a-f]{40}$")

    def test_every_claim_records_the_commit_that_published_it(self):
        reg = json.loads((ROOT / "claims" / "claims.json").read_text())
        for c in reg["claims"]:
            p = c["published"]
            self.assertRegex(p["commit"], r"^[0-9a-f]{40}$", c["id"])
            self.assertRegex(p["date"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$", c["id"])
            self.assertLessEqual(p["date"][:10], reg["collected"], c["id"])

    def test_each_claim_is_compared_on_its_publication_day(self):
        res = compare.run(build.thesis_snapshot())
        reg = {c["id"]: c for c in json.loads((ROOT / "claims" / "claims.json").read_text())["claims"]}
        for r in res["claims"]:
            p, c = r["at_publication"], reg[r["id"]]
            if not p["dated"]:
                self.assertEqual(p["asof"], res["asof"], r["id"])
            elif "stated_asof" in c:
                self.assertEqual(p["asof"], c["stated_asof"], r["id"])
            else:  # the last complete UTC day before the commit, capped at the snapshot
                day_before = compare.metrics.day_of(c["published"]["date"][:10] + "T00:00:00Z") - compare.metrics.DAY
                want = min(day_before, compare.metrics.day_of(res["asof"] + "T00:00:00Z"))
                self.assertEqual(compare.metrics.day_of(p["asof"] + "T00:00:00Z"), want, r["id"])
        for key in ("at_publication", "at_snapshot"):
            self.assertEqual(sum(res["summary"][key].values()), res["summary"]["claims"])

    def test_snapshot_only_metrics_are_exactly_those_that_do_not_move_with_the_day(self):
        raw = build.load_raw(build.thesis_snapshot())
        now = compare.metrics.compute(raw)
        before = compare.metrics.compute(raw, compare.metrics.day_of(now["asof"] + "T00:00:00Z") - 10 * compare.metrics.DAY)
        for mid, v in now["metrics"].items():
            if mid in before["metrics"]:
                self.assertEqual(v["value"] == before["metrics"][mid]["value"], compare.metrics.snapshot_only(mid), mid)


if __name__ == "__main__":
    unittest.main()
