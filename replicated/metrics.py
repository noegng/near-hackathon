"""Metric definitions. Pure functions: parsed raw series in, numbers out.

Every metric is computed for explicit windows that end on `asof`, the last complete
UTC day in the snapshot. Where teams plausibly chose different definitions (window
length, gross fees vs captured revenue, net vs gross issuance) each variant is
computed under its own id, so a published number can be matched to the definition
that reproduces it.

Series are dicts {unix_day_start: float}. Money is USD unless the id ends in _near.
Token amounts are converted from yoctoNEAR with integer arithmetic before division.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

DAY = 86400
YOCTO = 10**24


def day_of(iso: str) -> int:
    return int(datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc).timestamp()) // DAY * DAY


def llama_series(doc: dict) -> dict[int, float]:
    return {int(t) // DAY * DAY: float(v) for t, v in doc["totalDataChart"]}


def nearblocks_series(doc: dict) -> dict[str, dict[int, float]]:
    """Daily chain statistics. txn_fee and total_supply arrive in yoctoNEAR."""
    out: dict[str, dict[int, float]] = {k: {} for k in (
        "txns", "active_accounts", "new_accounts", "price", "market_cap", "fee_near", "fee_usd", "supply_near")}
    for row in doc["charts"]:
        d = day_of(row["date"])
        out["txns"][d] = float(row["txns"])
        out["active_accounts"][d] = float(row["active_accounts"])
        out["new_accounts"][d] = float(row["new_accounts"])
        out["price"][d] = float(row["near_price"])
        out["market_cap"][d] = float(row["market_cap"])
        out["fee_near"][d] = int(row["txn_fee"].split(".")[0]) / YOCTO
        out["fee_usd"][d] = float(row["txn_fee_usd"])
        out["supply_near"][d] = int(row["total_supply"]) / YOCTO
    return out


def window(series: dict[int, float], end: int, days: int) -> list[float]:
    """Values for the `days` UTC days ending on `end` inclusive. Raises if a day is missing."""
    vals = []
    for k in range(days):
        d = end - k * DAY
        if d not in series:
            raise KeyError(f"missing day {datetime.fromtimestamp(d, timezone.utc).date()}")
        vals.append(series[d])
    return vals


def wsum(series, end, days) -> float:
    return sum(window(series, end, days))


def wavg(series, end, days) -> float:
    return wsum(series, end, days) / days


def pct_change(new: float, old: float) -> float:
    return (new / old - 1) * 100


def peak_avg(series: dict[int, float], end: int, days: int) -> tuple[float, int]:
    """Highest `days`-day average ending on or before `end`, and the day it ends on."""
    ds = sorted(d for d in series if d <= end)
    best, best_d, run = float("-inf"), ds[0], 0.0
    vals = [series[d] for d in ds]
    for i, v in enumerate(vals):
        run += v
        if i >= days:
            run -= vals[i - days]
        if i >= days - 1 and ds[i] - ds[i - days + 1] == (days - 1) * DAY and run / days > best:
            best, best_d = run / days, ds[i]
    return best, best_d


def supply_at(points: list[dict], day: int) -> float:
    """total_supply in NEAR at the first block of `day`, from RPC block headers."""
    for p in points:
        if p["day"] == day:
            return int(p["total_supply"]) / YOCTO
    raise KeyError(f"no RPC supply sample for {day}")


def last_complete_day(*series: dict[int, float]) -> int:
    return min(max(s) for s in series)


def compute(raw: dict, asof: int | None = None) -> dict:
    """raw: parsed JSON documents keyed by snapshot file name. Returns {metric_id: {...}}.

    asof (unix day start) defaults to the last complete day in the snapshot. An earlier
    asof recomputes the daily-series metrics as of that day from the same snapshot;
    staking and the *_rpc supply metrics always describe the snapshot itself.
    """
    vol = llama_series(raw["llama_intents_volume"])
    fees = llama_series(raw["llama_intents_fees"])
    rev = llama_series(raw["llama_intents_revenue"])
    nb = nearblocks_series(raw["nearblocks_charts"])
    dex = llama_series(raw["llama_near_dexs"])
    supply = raw["rpc_supply"]
    last = last_complete_day(vol, fees, rev, nb["txns"])
    asof = last if asof is None else asof
    if asof > last:
        raise ValueError("asof is after the last complete day in the snapshot")
    m: dict[str, dict] = {}
    series: dict[str, list] = {}

    def put(mid, value, unit, definition):
        m[mid] = {"value": value, "unit": unit, "definition": definition}

    def iso(d):
        return datetime.fromtimestamp(d, timezone.utc).strftime("%Y-%m-%d")

    # --- NEAR Intents: volume, gross fees, captured revenue (DefiLlama) ---
    for n in (30, 90, 365):
        put(f"intents_volume_{n}d", wsum(vol, asof, n), "USD", f"Sum of DefiLlama daily NEAR Intents volume, {n} days to asof.")
        put(f"intents_fees_{n}d", wsum(fees, asof, n), "USD", f"Sum of DefiLlama daily gross fees (protocol + affiliate), {n} days to asof.")
        put(f"intents_revenue_{n}d", wsum(rev, asof, n), "USD", f"Sum of DefiLlama daily revenue captured by NEAR wallets, {n} days to asof.")
        put(f"intents_take_rate_bps_{n}d", wsum(fees, asof, n) / wsum(vol, asof, n) * 1e4, "bps", f"Gross fees / volume, {n} days.")
        put(f"intents_capture_share_{n}d", wsum(rev, asof, n) / wsum(fees, asof, n) * 100, "%", f"Captured revenue / gross fees, {n} days.")
    put("intents_volume_alltime", sum(v for d, v in vol.items() if d <= asof), "USD", "Sum of the whole DefiLlama daily volume series to asof.")
    put("intents_volume_avg_30d", wavg(vol, asof, 30), "USD/day", "Mean daily volume, 30 days to asof.")
    put("intents_volume_yoy_30d", pct_change(wavg(vol, asof, 30), wavg(vol, asof - 365 * DAY, 30)), "%",
        "30-day mean daily volume vs the 30 days ending 365 days earlier.")
    put("intents_volume_30d_vs_prev_30d", pct_change(wsum(vol, asof, 30), wsum(vol, asof - 30 * DAY, 30)), "%",
        "Last 30 days of volume vs the 30 days before.")
    put("intents_fees_annualized_30d", wsum(fees, asof, 30) * 365 / 30, "USD/yr", "30-day gross fees x 365/30.")
    put("intents_revenue_annualized_30d", wsum(rev, asof, 30) * 365 / 30, "USD/yr", "30-day captured revenue x 365/30.")
    put("intents_revenue_annualized_90d", wsum(rev, asof, 90) * 365 / 90, "USD/yr", "90-day captured revenue x 365/90.")
    put("intents_share_of_near_dex_volume_30d", wsum(vol, asof, 30) / wsum(dex, asof, 30) * 100, "%",
        "Intents volume / all DEX volume DefiLlama attributes to Near, 30 days.")

    # --- Base layer activity (NearBlocks daily charts) ---
    for key, name in (("txns", "tx"), ("active_accounts", "active_accounts"), ("new_accounts", "new_accounts")):
        s = nb[key]
        now30 = wavg(s, asof, 30)
        put(f"{name}_per_day_30d", now30, "per day", f"Mean daily {key}, 30 days to asof.")
        put(f"{name}_yoy_30d", pct_change(now30, wavg(s, asof - 365 * DAY, 30)), "%", f"30-day mean {key} vs the 30 days ending 365 days earlier.")
        pk, pk_day = peak_avg(s, asof, 30)
        put(f"{name}_vs_peak_30d", pct_change(now30, pk), "%", f"30-day mean {key} vs the highest 30-day mean on record (ending {iso(pk_day)}).")
        pk1, pk1_day = max((v, d) for d, v in s.items() if d <= asof)
        put(f"{name}_vs_peak_day", pct_change(s[asof], pk1), "%", f"{key} on asof vs the single highest day ({iso(pk1_day)}).")

    # --- Supply and issuance ---
    days_rpc = sorted(p["day"] for p in supply)
    end_rpc = days_rpc[-1]
    for n in (30, 90, 360):
        if end_rpc - n * DAY in days_rpc:
            grown = supply_at(supply, end_rpc) - supply_at(supply, end_rpc - n * DAY)
            put(f"net_issuance_near_{n}d_rpc", grown, "NEAR", f"total_supply in block headers: first block of {iso(end_rpc)} minus first block {n} days earlier (archival RPC).")
            put(f"net_inflation_annual_pct_{n}d_rpc", grown / supply_at(supply, end_rpc - n * DAY) * 365 / n * 100, "%/yr",
                f"Net supply growth over {n} days, annualized linearly, from block headers.")
    for n in (30, 90, 365):
        fee_near = wsum(nb["fee_near"], asof, n)
        net = nb["supply_near"][asof] - nb["supply_near"][asof - n * DAY]
        rev_near = sum(rev[asof - k * DAY] / nb["price"][asof - k * DAY] for k in range(n))
        price = nb["price"][asof]
        put(f"l1_fees_near_{n}d", fee_near, "NEAR", f"Sum of NearBlocks daily txn_fee, {n} days.")
        put(f"l1_fees_usd_{n}d", wsum(nb["fee_usd"], asof, n), "USD", f"Sum of NearBlocks daily txn_fee_usd, {n} days.")
        put(f"net_issuance_near_{n}d", net, "NEAR", f"NearBlocks daily total_supply on asof minus {n} days earlier.")
        put(f"net_inflation_annual_pct_{n}d", net / nb["supply_near"][asof - n * DAY] * 365 / n * 100, "%/yr", f"Net supply growth over {n} days, annualized linearly.")
        # Upper bound on burn: all transaction fees. Teams that apply a 70% burn share get 0.7x this.
        put(f"burn_cover_of_net_issuance_pct_{n}d", fee_near / net * 100, "%", f"L1 fees / net supply growth, {n} days. Treats all fees as burnt.")
        put(f"burn_cover_of_gross_issuance_pct_{n}d", fee_near / (net + fee_near) * 100, "%", f"L1 fees / (net supply growth + fees), {n} days. Treats all fees as burnt.")
        put(f"burn70_cover_of_gross_issuance_pct_{n}d", 0.7 * fee_near / (net + 0.7 * fee_near) * 100, "%", f"As above with 70% of fees burnt, the rule before protocol version 87.")
        put(f"intents_revenue_near_{n}d", rev_near, "NEAR", f"Daily captured revenue / that day's NEAR price, summed over {n} days.")
        put(f"revenue_cover_of_gross_issuance_pct_{n}d", rev_near / (net + fee_near) * 100, "%", f"Captured Intents revenue in NEAR at daily prices / gross issuance, {n} days.")
        put(f"revenue_cover_of_net_issuance_pct_{n}d", rev_near / net * 100, "%", f"Captured Intents revenue in NEAR at daily prices / net supply growth, {n} days.")
        put(f"usage_cover_of_gross_issuance_pct_{n}d", (rev_near + fee_near) / (net + fee_near) * 100, "%", f"(Captured revenue + L1 fees) / gross issuance, {n} days.")
        put(f"usage_cover_of_net_issuance_pct_{n}d", (rev_near + fee_near) / net * 100, "%", f"(Captured revenue + L1 fees) / net supply growth, {n} days.")
        put(f"fees_cover_of_gross_issuance_usd_pct_{n}d", wsum(fees, asof, n) / ((net + fee_near) * price) * 100, "%", f"Gross Intents fees / gross issuance valued at the asof price, {n} days.")
        put(f"breakeven_multiple_{n}d", (net + fee_near) / (rev_near + fee_near), "x", f"Gross issuance / (captured revenue + L1 fees), {n} days: how many times usage must grow to offset issuance.")
        put(f"intents_fees_over_l1_fees_{n}d", wsum(fees, asof, n) / wsum(nb["fee_usd"], asof, n), "x", f"Gross Intents fees / L1 fees in USD, {n} days.")
        put(f"intents_revenue_over_l1_fees_{n}d", wsum(rev, asof, n) / wsum(nb["fee_usd"], asof, n), "x", f"Captured Intents revenue / L1 fees in USD, {n} days.")
    put("l1_fees_usd_yoy_30d", pct_change(wsum(nb["fee_usd"], asof, 30), wsum(nb["fee_usd"], asof - 365 * DAY, 30)), "%", "30-day L1 fees in USD vs a year earlier.")
    put("l1_fees_near_yoy_30d", pct_change(wsum(nb["fee_near"], asof, 30), wsum(nb["fee_near"], asof - 365 * DAY, 30)), "%", "30-day L1 fees in NEAR vs a year earlier.")

    # --- Revenue wallets read on chain (independent of DefiLlama and Dune) ---
    if "rpc_revenue_wallets" in raw:
        wb = {r["day"]: sum(int(v["near"] or 0) + int(v["wnear"]) for v in r["wallets"].values()) / YOCTO
              for r in raw["rpc_revenue_wallets"]}
        put("revenue_wallets_near", wb[end_rpc], "NEAR", f"NEAR + wNEAR held by the three Intents revenue wallets at the first block of {iso(end_rpc)}.")
        put("revenue_wallets_share_of_supply_pct", wb[end_rpc] / supply_at(supply, end_rpc) * 100, "%", "Revenue wallet holdings / total supply.")
        first = min(d for d, v in sorted(wb.items()) if v > 100)
        put("revenue_wallets_min_balance_ratio", min(wb[b] / wb[a] for a, b in zip(sorted(wb), sorted(wb)[1:]) if a >= first), "x",
            "Smallest ratio between consecutive samples of total holdings; >= 1 means the total never fell between samples.")
        for n in (30, 90, 360):
            d0 = end_rpc - n * DAY
            if d0 in wb and end_rpc - DAY <= asof + DAY:
                grown = wb[end_rpc] - wb[d0]
                net = supply_at(supply, end_rpc) - supply_at(supply, d0)
                # RPC samples are taken at the first block of a day, so the window is the n days before end_rpc.
                llama_near = sum(rev[end_rpc - k * DAY] / nb["price"][end_rpc - k * DAY] for k in range(1, n + 1))
                put(f"revenue_wallets_growth_near_{n}d", grown, "NEAR", f"Change in revenue wallet holdings over the {n} days before {iso(end_rpc)}.")
                put(f"wallet_growth_cover_of_net_issuance_pct_{n}d", grown / net * 100, "%",
                    f"Growth of revenue wallet holdings / growth of total supply, both from archival RPC, {n} days.")
                put(f"wallet_growth_over_defillama_revenue_{n}d", grown / llama_near, "x",
                    f"Growth of wallet holdings / DefiLlama captured revenue in NEAR over the same {n} days. 1.0 means all reported revenue is still held.")

        # 30-day steps along the sampled blocks: is the cover rising?
        ds = sorted(wb)
        steps = [{"from": iso(x), "to": iso(y), "wallet_growth_near": wb[y] - wb[x],
                  "net_issuance_near": supply_at(supply, y) - supply_at(supply, x),
                  "cover_pct": (wb[y] - wb[x]) / (supply_at(supply, y) - supply_at(supply, x)) * 100}
                 for x, y in zip(ds, ds[1:]) if x >= first - 30 * DAY]
        series["wallet_cover_steps"] = steps
        # Holdings at each sample next to DefiLlama's revenue accumulated since the first sample (both in NEAR).
        cum, track = 0.0, []
        for x in ds:
            if x > ds[0]:
                cum += sum(rev.get(x - k * DAY, 0.0) / nb["price"][x - k * DAY] for k in range(1, (x - prev) // DAY + 1) if nb["price"].get(x - k * DAY))
            track.append({"day": iso(x), "wallets_near": wb[x], "defillama_cumulative_near": cum + wb[ds[0]]})
            prev = x
        series["wallets_vs_reported"] = track
        if end_rpc - 360 * DAY in wb and end_rpc - 180 * DAY in wb:
            h1 = (wb[end_rpc - 180 * DAY] - wb[end_rpc - 360 * DAY]) / (supply_at(supply, end_rpc - 180 * DAY) - supply_at(supply, end_rpc - 360 * DAY)) * 100
            h2 = (wb[end_rpc] - wb[end_rpc - 180 * DAY]) / (supply_at(supply, end_rpc) - supply_at(supply, end_rpc - 180 * DAY)) * 100
            put("wallet_cover_pct_first_180d", h1, "%", "Wallet growth / supply growth, days 360 to 180 before the snapshot (RPC).")
            put("wallet_cover_pct_last_180d", h2, "%", "Wallet growth / supply growth, last 180 days (RPC).")
        if "wallet_growth_cover_of_net_issuance_pct_90d" in m:
            cover = m["wallet_growth_cover_of_net_issuance_pct_90d"]["value"] / 100
            g = m["intents_volume_yoy_30d"]["value"] / 100
            put("growth_multiple_to_offset_issuance_90d", 1 / cover, "x", "1 / (90-day wallet cover of net issuance): how many times captured revenue must grow, at constant issuance and price ratio.")
            for label, rate in (("at_measured_volume_growth", g), ("at_half_measured_volume_growth", g / 2), ("at_25pct_growth", 0.25)):
                if rate > 0:
                    put(f"years_to_offset_issuance_{label}", math.log(1 / cover) / math.log(1 + rate), "years",
                        f"ln(multiple) / ln(1 + g) with g = {rate:.1%} a year. A projection, not a measurement: assumes captured revenue grows at g and issuance in NEAR stays as is.")

    # Weekly samples of 30-day means, for charts.
    start = min(vol) + 29 * DAY
    series["weekly_30d_means"] = [
        {"day": iso(d), "tx_per_day": wavg(nb["txns"], d, 30), "intents_volume_usd_per_day": wavg(vol, d, 30)}
        for d in range(asof - ((asof - start) // (7 * DAY)) * 7 * DAY, asof + 1, 7 * DAY)]

    # --- Valuation and price ---
    mc = nb["market_cap"][asof]
    put("price_usd", nb["price"][asof], "USD", "NearBlocks daily price on asof.")
    put("price_yoy", pct_change(nb["price"][asof], nb["price"][asof - 365 * DAY]), "%", "Price on asof vs 365 days earlier.")
    put("price_yoy_30d_avg", pct_change(wavg(nb["price"], asof, 30), wavg(nb["price"], asof - 365 * DAY, 30)), "%", "30-day mean price vs a year earlier.")
    put("market_cap_usd", mc, "USD", "NearBlocks market cap on asof (circulating supply x price).")
    put("mcap_over_intents_fees_annualized_30d", mc / (wsum(fees, asof, 30) * 365 / 30), "x", "Market cap / (30-day gross fees annualized).")
    put("mcap_over_intents_revenue_annualized_30d", mc / (wsum(rev, asof, 30) * 365 / 30), "x", "Market cap / (30-day captured revenue annualized).")
    put("revenue_yield_on_mcap_pct_30d", wsum(rev, asof, 30) * 365 / 30 / mc * 100, "%/yr", "30-day captured revenue annualized / market cap.")
    put("intents_volume_365d_over_mcap", wsum(vol, asof, 365) / mc, "x", "365-day Intents volume / market cap.")

    # --- Staking (RPC, current epoch) ---
    v = raw["rpc_validators"]["result"]["current_validators"]
    staked = sum(int(x["stake"]) for x in v) / YOCTO
    put("validators_current", len(v), "count", "Length of current_validators in the RPC `validators` response.")
    put("staked_share_pct", staked / supply_at(supply, end_rpc) * 100, "%", "Sum of current validator stake / total_supply from the latest sampled block header.")
    stakes = sorted((int(x["stake"]) for x in v), reverse=True)
    acc, k = 0, 0
    while acc * 3 <= sum(stakes):
        acc += stakes[k]
        k += 1
    put("validators_to_one_third", k, "count", "Smallest number of validators whose stake exceeds one third of current stake.")
    cfg = raw["rpc_protocol_config"]["result"]
    num, den = cfg["max_inflation_rate"]
    put("max_inflation_rate_pct", num / den * 100, "%/yr", "max_inflation_rate in the live protocol config.")
    put("protocol_version", cfg["protocol_version"], "version", "protocol_version in the live protocol config.")

    return {"asof": iso(asof), "asof_rpc_supply": iso(end_rpc), "metrics": m, "series": series}
