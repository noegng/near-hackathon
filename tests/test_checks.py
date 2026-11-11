import unittest

from replicated import build, checks, metrics, restated


class Checks(unittest.TestCase):
    def test_operators(self):
        m = {"a": {"value": 2.0}}
        self.assertTrue(checks.holds(3, ">", "a", m))
        self.assertFalse(checks.holds(2, ">", 2, m))
        self.assertTrue(checks.holds(2, ">=", 2, m))
        self.assertTrue(checks.holds(1.0, "between", (0.9, 1.1), m))
        self.assertFalse(checks.holds(1.2, "between", (0.9, 1.1), m))

    def test_every_condition_points_at_an_existing_metric(self):
        res = metrics.compute(build.load_raw(build.thesis_snapshot()))
        for row in checks.KILL:
            self.assertIn(row[1], res["metrics"])
        for row in checks.PREDICTIONS:
            self.assertIn(row[2], res["metrics"])

    def test_predictions_stay_pending_before_their_date_and_resolve_after(self):
        res = metrics.compute(build.load_raw(build.thesis_snapshot()))
        self.assertTrue(all(r["status"] == "PENDING" for r in checks.evaluate(res) if r["kind"] == "prediction"))
        later = dict(res, asof_rpc_supply="2028-01-01")
        self.assertTrue(all(r["status"] in ("HIT", "MISS") for r in checks.evaluate(later) if r["kind"] == "prediction"))

    def test_a_failing_kill_condition_is_reported(self):
        res = metrics.compute(build.load_raw(build.thesis_snapshot()))
        res["metrics"]["intents_volume_yoy_30d"] = {"value": -5.0}
        k1 = next(r for r in checks.evaluate(res) if r["id"] == "K1")
        self.assertEqual(k1["status"], "FAILS")

    def test_wallet_growth_matches_reported_revenue_in_committed_snapshot(self):
        m = metrics.compute(build.load_raw(build.thesis_snapshot()))["metrics"]
        for n in (30, 90, 360):
            self.assertAlmostEqual(m[f"wallet_growth_over_defillama_revenue_{n}d"]["value"], 1.0, delta=0.05)

    def test_restated_diff(self):
        r = restated.diff({1: 10.0, 2: 20.0, 3: 5.0}, {2: 25.0, 3: 5.0, 4: 1.0})
        self.assertEqual((r["days_compared"], r["days_changed"], r["changed"]), (2, 1, [(2, 20.0, 25.0)]))


if __name__ == "__main__":
    unittest.main()
