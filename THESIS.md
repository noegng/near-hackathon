# THESIS: NEAR is a growth bet on Intents revenue that covers about a sixth of issuance, and the money can be counted on chain

Snapshot 2026-11-11, daily data to 2026-11-10. Every number below is in the evidence table at the end with the id
of the metric that produced it; a test fails if the text and the computation disagree. Rebuild:
`python3 -m replicated.build && python3 -m replicated.compare && python3 -m replicated.checks`.

## The claim

1. NEAR's base layer no longer carries the investment case. Its activity fell by about 85% in a year and its fees
   offset under 2% of new supply.
2. NEAR Intents does carry it. Of the two sources of demand measured here, it is the one that grows and pays fees, and the share
   NEAR captures arrives as NEAR in three wallets anyone can read (DefiLlama's methodology describes it as an
   open-market buyback since 2026-02-23).
3. That captured revenue is real but small: over the last 90 days it equals 18.2% of the NEAR
   created in the same period. A holder is still diluted. The case for owning NEAR is therefore a bet that captured
   revenue grows about 5.5x before issuance is offset, not a claim that the token is cheap today.
4. The captured NEAR is held, not burned and not distributed. Until a rule says what happens to it, it is a
   treasury that could be spent, and the thesis depends on it not being spent.

## How this thesis was built

About thirty teams in this track measured NEAR independently. We recorded 119 of their published numbers from
20 public repositories, with the exact quote and commit, and recomputed each from raw data
([`out/replication.md`](out/replication.md)). 89 are within 5% of our number on our snapshot day and
109 when the day may move within two weeks (the theses were published on different days). The thesis uses only
quantities that replicate, and takes its uncertainty from the spread between teams instead of from one model.

Two things came out of the comparison that no single thesis shows.

**The agreement on Intents volume and fees is not independent evidence.** All 12 repositories that publish an
Intents number mention DefiLlama as a source. DefiLlama's adapter in turn reads datasets that NEAR itself uploads to
Dune (`dune.near.dataset_near_intents_metrics`, `..._fees`). Twelve matching numbers are one number read twelve
times. We did not rebuild volume from `intents.near` events; one team reports doing so
([near-thesis](https://github.com/soldanoandrea/near-thesis)) and we have not replicated their work.

**Captured revenue, in contrast, can be checked without trusting the party that reports it.** We read the balances of the three revenue
wallets from an archival RPC node at 15 block heights. Their growth equals 1.01x, 0.98x and 0.98x of
DefiLlama's reported revenue over 30, 90 and 360 days. So the revenue series is confirmed by a second, on-chain
route, and no net outflow shows: the total never fell between two samples. The list of wallets itself comes from
DefiLlama's adapter; revenue sent anywhere else would not appear in either route.

## Evidence for

- **Demand moved to Intents and is still growing.** $32.91B settled in 365 days; the 30-day mean is 57.8% above
  a year ago. Gross fees were $54.03M in 365 days, 46x the base layer's $1.16M. (Single upstream
  source, see above.)
- **NEAR's share of those fees is rising.** Captured revenue was $9.36M over 365 days, 17.3% of gross fees, and
  30.5% over the last 30.
- **The capture is verifiable and accumulating.** The revenue wallets hold 4.24M NEAR, 0.32% of supply.
- **The cover of issuance is rising.** On chain, wallet growth was 11.2% of net supply growth in the first half
  of the last 360 days and 14.5% in the second half.
- **Supply growth is measured, not assumed.** Net supply grew 31.32M NEAR in 360 days, 2.48% a year, read from block
  headers and matching NearBlocks to 0.001%.

## Evidence against

- **Base-layer usage collapsed.** Transactions -85.1%, active accounts -76.3%, new accounts -95.6% year on
  year (30-day means). Six teams publish the transaction figure and all six replicate. Fees offset 1.87% of
  net issuance over 365 days and 1.12% over the last 30.
- **Holders are still diluted.** Even counting all captured revenue, about five sixths of new supply is not offset.
- **The yield is thin.** Captured revenue annualized from the last 30 days is $22.11M, 0.47% of a
  $4.75B market cap: the market pays 215x that revenue.
- **Growth is not one-way.** Intents volume in the last 30 days was -20.7% against the 30 days before.
- **The time to break even is long and assumption-driven.** At the measured year-on-year volume growth it takes
  3.7 years; at half that rate 6.7 years; at 25% a year 7.6 years. These are projections, not
  measurements.
- **Captured NEAR is not returned to holders.** It sits in two Sputnik DAO accounts and one multisig account. It is not
  burned, staked for holders or paid out. Its effect on a holder today is only that it is off the market.
- **Stake is concentrated.** 9 of 351 validators hold more than a third of stake (44.4% of supply is staked).

## How much the answer depends on definitions

The spread between teams is mostly definition, not error, and it sets the error bar on this thesis.

| Quantity | Teams publish | Our variants | What moves it |
| --- | --- | --- | --- |
| Share of issuance offset by Intents revenue | 12.0% to 20.6% (7 numbers) | 12.9% (360 d), 15.3% (30 d), 18.2% (90 d) | Window length. Sweeps into the wallets are lumpy: single 30-day steps range from 6.5% to 19.8% since April. |
| Share offset by fee burn | 0.58% to 2.00% (7 numbers) | 1.12% (30 d) to 1.87% (365 d) | Window, and whether 70% or 100% of fees is counted as burnt. |
| Growth needed to offset issuance | 5.3x to 7.6x (5 numbers) | 5.5x (90 d, on chain) | Same as the first row. |
| NEAR price change over a year | +19%, +96% and +97% | +19% day to day, +98% between 30-day means | NEAR's price rose sharply in early November 2025, so the comparison day decides the result. |
| L1 fees in USD, change over a year | -27.6% to -55.3% (3 numbers) | -39% (30 d), -53% (90 d) | Window length: the same series gives either figure. |

We therefore state the cover as **13% to 18%**, not as one figure, and treat any 30-day reading as noise.

## What would change our mind

`python3 -m replicated.checks` evaluates these on every snapshot and exits with an error if a kill condition fails.

| Id | The thesis is dropped if this stops being true | Today |
| --- | --- | --- |
| K1 | Intents volume is higher than a year ago | 57.8% |
| K2 | Reported captured revenue matches wallet growth on chain within 10% (90 days) | 0.98x |
| K3 | The revenue wallets' total has not fallen between two samples | holds |
| K4 | Captured revenue offsets at least 10% of net issuance (90 days) | 18.2% |
| K5 | The cover over the last 180 days is higher than over the 180 days before | 14.5% vs 11.2% |

Dated predictions, written on 2026-11-11 and checked by the same command once a snapshot exists on or after the date:

| Id | Due | Prediction |
| --- | --- | --- |
| P1 | 2027-02-09 | 90-day on-chain cover is at least 18% |
| P2 | 2027-05-10 | 180-day on-chain cover reaches 18% |
| P3 | 2027-05-10 | The revenue wallets' total has not fallen |
| P4 | 2027-11-11 | Intents volume is at least 25% above November 2026 |

## Not measured

- Intents volume and gross fees from first principles (see above). If the Dune datasets overstate volume, the
  usage half of the thesis weakens; the revenue half does not, because it is read from wallets.
- Whether base-layer activity fell because bots left or because users left. Other teams address this
  ([NEAR Agent Census](https://github.com/daodudestiny56-netizen/near-thesis-), [near-thesis](https://github.com/soldanoandrea/near-thesis)); we did not replicate their classifiers.
- The proposed issuance cut HSP-029 that several teams cite. We did not read the vote on chain, so it is not used here.
- A burn would lower the wallet total and trip K3 and P3 although it would be good for holders. If a burn is
  announced, those two conditions need a new metric.
- Whether the three wallets are the complete set. They are the ones DefiLlama's adapter lists; we did not search
  for others.
- Wallet balances are sampled every 30 days. Money that entered and left between two samples is invisible; the
  match with reported revenue (0.98 to 1.01) bounds how much that could be.
- The claims registry is a sample of what each team published, read by hand from README and THESIS files.

## Evidence table

| Metric id | Value | Definition |
| --- | --- | --- |
| `tx_yoy_30d` | -85.1% | 30-day mean txns vs the 30 days ending 365 days earlier. |
| `active_accounts_yoy_30d` | -76.3% | 30-day mean active_accounts vs the 30 days ending 365 days earlier. |
| `new_accounts_yoy_30d` | -95.6% | 30-day mean new_accounts vs the 30 days ending 365 days earlier. |
| `l1_fees_usd_365d` | $1.16M | Sum of NearBlocks daily txn_fee_usd, 365 days. |
| `burn_cover_of_net_issuance_pct_365d` | 1.87% | L1 fees / net supply growth, 365 days. Treats all fees as burnt. |
| `burn_cover_of_net_issuance_pct_30d` | 1.12% | L1 fees / net supply growth, 30 days. Treats all fees as burnt. |
| `intents_volume_365d` | $32.91B | Sum of DefiLlama daily NEAR Intents volume, 365 days to asof. |
| `intents_volume_yoy_30d` | 57.8% | 30-day mean daily volume vs the 30 days ending 365 days earlier. |
| `intents_volume_30d_vs_prev_30d` | -20.7% | Last 30 days of volume vs the 30 days before. |
| `intents_fees_365d` | $54.03M | Sum of DefiLlama daily gross fees (protocol + affiliate), 365 days to asof. |
| `intents_fees_over_l1_fees_365d` | 46x | Gross Intents fees / L1 fees in USD, 365 days. |
| `intents_capture_share_365d` | 17.3% | Captured revenue / gross fees, 365 days. |
| `intents_capture_share_30d` | 30.5% | Captured revenue / gross fees, 30 days. |
| `intents_revenue_365d` | $9.36M | Sum of DefiLlama daily revenue captured by NEAR wallets, 365 days to asof. |
| `intents_revenue_annualized_30d` | $22.11M | 30-day captured revenue x 365/30. |
| `net_inflation_annual_pct_360d_rpc` | 2.48% | Net supply growth over 360 days, annualized linearly, from block headers. |
| `net_issuance_near_360d_rpc` | 31.32M NEAR | total_supply in block headers: first block of 2026-11-11 minus first block 360 days earlier (archival RPC). |
| `revenue_wallets_near` | 4.24M NEAR | NEAR + wNEAR held by the three Intents revenue wallets at the first block of 2026-11-11. |
| `revenue_wallets_share_of_supply_pct` | 0.32% | Revenue wallet holdings / total supply. |
| `wallet_growth_over_defillama_revenue_30d` | 1.01x | Growth of wallet holdings / DefiLlama captured revenue in NEAR over the same 30 days. 1.0 means all reported revenue is still held. |
| `wallet_growth_over_defillama_revenue_90d` | 0.98x | Growth of wallet holdings / DefiLlama captured revenue in NEAR over the same 90 days. 1.0 means all reported revenue is still held. |
| `wallet_growth_over_defillama_revenue_360d` | 0.98x | Growth of wallet holdings / DefiLlama captured revenue in NEAR over the same 360 days. 1.0 means all reported revenue is still held. |
| `wallet_growth_cover_of_net_issuance_pct_30d` | 15.3% | Growth of revenue wallet holdings / growth of total supply, both from archival RPC, 30 days. |
| `wallet_growth_cover_of_net_issuance_pct_90d` | 18.2% | Growth of revenue wallet holdings / growth of total supply, both from archival RPC, 90 days. |
| `wallet_growth_cover_of_net_issuance_pct_360d` | 12.9% | Growth of revenue wallet holdings / growth of total supply, both from archival RPC, 360 days. |
| `wallet_cover_pct_first_180d` | 11.2% | Wallet growth / supply growth, days 360 to 180 before the snapshot (RPC). |
| `wallet_cover_pct_last_180d` | 14.5% | Wallet growth / supply growth, last 180 days (RPC). |
| `growth_multiple_to_offset_issuance_90d` | 5.5x | 1 / (90-day wallet cover of net issuance): how many times captured revenue must grow, at constant issuance and price ratio. |
| `years_to_offset_issuance_at_measured_volume_growth` | 3.7 years | ln(multiple) / ln(1 + g) with g = 57.8% a year. A projection, not a measurement: assumes captured revenue grows at g and issuance in NEAR stays as is. |
| `years_to_offset_issuance_at_half_measured_volume_growth` | 6.7 years | ln(multiple) / ln(1 + g) with g = 28.9% a year. A projection, not a measurement: assumes captured revenue grows at g and issuance in NEAR stays as is. |
| `years_to_offset_issuance_at_25pct_growth` | 7.6 years | ln(multiple) / ln(1 + g) with g = 25.0% a year. A projection, not a measurement: assumes captured revenue grows at g and issuance in NEAR stays as is. |
| `market_cap_usd` | $4.75B | NearBlocks market cap on asof (circulating supply x price). |
| `revenue_yield_on_mcap_pct_30d` | 0.47% | 30-day captured revenue annualized / market cap. |
| `mcap_over_intents_revenue_annualized_30d` | 215x | Market cap / (30-day captured revenue annualized). |
| `price_yoy` | 19% | Price on asof vs 365 days earlier. |
| `price_yoy_30d_avg` | 98% | 30-day mean price vs a year earlier. |
| `staked_share_pct` | 44.4% | Sum of current validator stake / total_supply from the latest sampled block header. |
| `validators_current` | 351 | Length of current_validators in the RPC `validators` response. |
| `validators_to_one_third` | 9 | Smallest number of validators whose stake exceeds one third of current stake. |
