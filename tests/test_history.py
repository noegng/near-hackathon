"""The snapshot history covers every committed snapshot and the thesis snapshot exists."""
import unittest

from replicated import build, history, restated


class History(unittest.TestCase):
    def test_every_snapshot_is_evaluated(self):
        res = history.run()
        self.assertEqual([r["snapshot"] for r in res["snapshots"]], build.all_snapshots())
        self.assertIn(res["thesis_snapshot"], build.all_snapshots())
        self.assertEqual(len(res["restatements"]), (len(res["snapshots"]) - 1) * len(restated.SERIES))
        for r in res["snapshots"]:
            self.assertEqual(sorted(k for k in r["checks"] if k.startswith("K")), ["K1", "K2", "K3", "K4", "K5"])
        self.assertIn(res["snapshots"][-1]["snapshot"], history.markdown(res))

    def test_restated_diff_reports_changed_days_only(self):
        d = restated.diff({1: 10.0, 2: 20.0, 3: 30.0}, {2: 20.0, 3: 33.0, 4: 40.0})
        self.assertEqual((d["days_compared"], d["days_changed"], d["changed"]), (2, 1, [(3, 30.0, 33.0)]))


if __name__ == "__main__":
    unittest.main()
