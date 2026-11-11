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

    def test_dated_match_is_never_worse_than_snapshot_match(self):
        res = compare.run(build.thesis_snapshot())
        for r in res["claims"]:
            self.assertLessEqual(r["best_dated"]["gap"], r["at_snapshot"]["gap"] + 1e-12, r["id"])
        self.assertEqual(sum(res["summary"]["at_snapshot"].values()), res["summary"]["claims"])


if __name__ == "__main__":
    unittest.main()
