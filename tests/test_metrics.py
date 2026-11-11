import unittest

from replicated import metrics as M

D = M.DAY


def flat(end, days, value):
    return {end - k * D: float(value) for k in range(days)}


class Windows(unittest.TestCase):
    def test_sum_and_avg_include_end_day(self):
        s = {0: 1.0, D: 2.0, 2 * D: 4.0}
        self.assertEqual(M.wsum(s, 2 * D, 2), 6.0)
        self.assertEqual(M.wavg(s, 2 * D, 3), 7 / 3)

    def test_missing_day_raises_instead_of_shrinking_the_window(self):
        s = {0: 1.0, 2 * D: 4.0}
        with self.assertRaises(KeyError):
            M.wsum(s, 2 * D, 3)

    def test_pct_change(self):
        self.assertAlmostEqual(M.pct_change(15, 100), -85.0)

    def test_peak_avg_finds_best_window_and_its_end(self):
        s = {k * D: v for k, v in enumerate([1, 1, 9, 9, 1, 1])}
        best, end = M.peak_avg(s, 5 * D, 2)
        self.assertEqual((best, end), (9.0, 3 * D))

    def test_peak_avg_ignores_windows_spanning_a_gap(self):
        s = {0: 100.0, 5 * D: 100.0, 6 * D: 2.0, 7 * D: 2.0}
        best, end = M.peak_avg(s, 7 * D, 2)
        self.assertEqual((best, end), (51.0, 6 * D))

    def test_day_of_parses_nearblocks_dates(self):
        self.assertEqual(M.day_of("2026-11-10T00:00:00.000Z"), 1794268800)

    def test_supply_uses_integer_yocto(self):
        pts = [{"day": 0, "total_supply": str(3 * M.YOCTO + 1)}]
        self.assertAlmostEqual(M.supply_at(pts, 0), 3.0)


def synthetic_raw():
    """A year-plus of constant data with round numbers, so every ratio is checkable by hand."""
    end, n = 1794268800, 800
    chart = lambda v: {"totalDataChart": [[end - k * D, v] for k in range(n)][::-1]}
    rows = []
    for k in range(n):
        d = end - k * D
        from datetime import datetime, timezone
        rows.append({
            "date": datetime.fromtimestamp(d, timezone.utc).strftime("%Y-%m-%dT00:00:00.000Z"),
            "txns": "1000" if k < 365 else "4000",
            "active_accounts": "50", "new_accounts": "5",
            "near_price": "2.00000000", "market_cap": "7300000.0",
            "txn_fee": f"{10 * M.YOCTO}.00000000", "txn_fee_usd": "20.0",
            "total_supply": str((1_000_000 - 100 * k) * M.YOCTO),
        })
    return {
        "llama_intents_volume": chart(1_000_000), "llama_intents_fees": chart(1000),
        "llama_intents_revenue": chart(200), "llama_near_dexs": chart(1_250_000),
        "nearblocks_charts": {"charts": rows[::-1]},
        "rpc_supply": [{"day": end - k * 30 * D, "total_supply": str((1_000_000 - 3000 * k) * M.YOCTO)} for k in range(13)][::-1],
        "rpc_validators": {"result": {"current_validators": [{"stake": str(s * M.YOCTO)} for s in (300_000, 100_000, 100_000)]}},
        "rpc_protocol_config": {"result": {"max_inflation_rate": [1, 40], "protocol_version": 88}},
    }


class Compute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = M.compute(synthetic_raw())
        cls.m = {k: v["value"] for k, v in cls.out["metrics"].items()}

    def test_asof_is_last_common_day(self):
        self.assertEqual(self.out["asof"], "2026-11-10")

    def test_intents_ratios(self):
        self.assertAlmostEqual(self.m["intents_volume_30d"], 30e6)
        self.assertAlmostEqual(self.m["intents_take_rate_bps_30d"], 10.0)
        self.assertAlmostEqual(self.m["intents_capture_share_90d"], 20.0)
        self.assertAlmostEqual(self.m["intents_share_of_near_dex_volume_30d"], 80.0)
        self.assertAlmostEqual(self.m["intents_volume_yoy_30d"], 0.0)
        self.assertAlmostEqual(self.m["intents_revenue_annualized_30d"], 200 * 365)

    def test_activity_year_on_year(self):
        self.assertAlmostEqual(self.m["tx_yoy_30d"], -75.0)
        self.assertAlmostEqual(self.m["tx_vs_peak_30d"], -75.0)

    def test_issuance_cover(self):
        # per day: 100 NEAR net supply growth, 10 NEAR fees, revenue 200 USD / 2 USD = 100 NEAR
        self.assertAlmostEqual(self.m["net_issuance_near_30d"], 3000.0)
        self.assertAlmostEqual(self.m["net_issuance_near_30d_rpc"], 3000.0)
        self.assertAlmostEqual(self.m["burn_cover_of_net_issuance_pct_30d"], 10.0)
        self.assertAlmostEqual(self.m["burn_cover_of_gross_issuance_pct_30d"], 10 / 110 * 100)
        self.assertAlmostEqual(self.m["burn70_cover_of_gross_issuance_pct_30d"], 7 / 107 * 100)
        self.assertAlmostEqual(self.m["revenue_cover_of_gross_issuance_pct_365d"], 100 / 110 * 100)
        self.assertAlmostEqual(self.m["breakeven_multiple_90d"], 1.0)
        self.assertAlmostEqual(self.m["intents_fees_over_l1_fees_30d"], 50.0)

    def test_valuation(self):
        self.assertAlmostEqual(self.m["mcap_over_intents_revenue_annualized_30d"], 100.0)
        self.assertAlmostEqual(self.m["revenue_yield_on_mcap_pct_30d"], 1.0)

    def test_staking(self):
        self.assertEqual(self.m["validators_current"], 3)
        self.assertAlmostEqual(self.m["staked_share_pct"], 50.0)
        self.assertEqual(self.m["validators_to_one_third"], 1)
        self.assertAlmostEqual(self.m["max_inflation_rate_pct"], 2.5)

    def test_every_metric_has_a_definition_and_unit(self):
        for k, v in self.out["metrics"].items():
            self.assertTrue(v["definition"] and v["unit"], k)


if __name__ == "__main__":
    unittest.main()
