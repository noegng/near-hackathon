# THESIS: NEAR is a growth bet on Intents revenue that covers about a sixth of issuance, and the money can be counted on chain

Snapshot 2026-11-13, daily data to 2026-11-12 (first written on snapshot 2026-11-11 and moved to the newest
snapshot on 2026-11-14 with no change to its conclusions or its kill conditions). Every number below is in the evidence table at the end with the id
of the metric that produced it; a test fails if the text and the computation disagree. Rebuild:
`python3 -m replicated.build && python3 -m replicated.compare && python3 -m replicated.checks`.

## The claim

1. NEAR's base layer no longer carries the investment case. Its activity fell by about 85% in a year and its fees
   offset under 2% of new supply.
2. NEAR Intents does carry it. Of the two sources of demand measured here, it is the one that grows and pays fees, and the share
   NEAR captures arrives as NEAR in three wallets anyone can read (DefiLlama's methodology describes it as an
   open-market buyback since 2026-02-23).
3. That captured revenue is real but small: over the last 90 days it equals 18.6% of the NEAR
   created in the same period. A holder is still diluted. The case for owning NEAR is therefore a bet that captured
   revenue grows about 5.4x before issuance is offset, not a claim that the token is cheap today.
4. The captured NEAR is held, not burned and not distributed. Until a rule says what happens to it, it is a
   treasury that could be spent, and the thesis depends on it not being spent.

## How this thesis was built

Dozens of teams in this track measured NEAR independently. We recorded 264 of their published numbers from
43 public repositories, with the exact quote and commit, and recomputed each from raw data
([`out/replication.md`](out/replication.md)). 231 are within 5% of our number for the day each was
published (the last complete day before the commit that wrote it), and 194 if all are recomputed on our snapshot day. The thesis uses only
quantities that replicate, and takes its uncertainty from the spread between teams instead of from one model.

Two things came out of the comparison that no single thesis shows.

**The agreement on Intents volume and fees is not independent evidence.** All 34 repositories that publish an
Intents number mention DefiLlama as a source. DefiLlama's adapter in turn reads datasets that NEAR itself uploads to
Dune (`dune.near.dataset_near_intents_metrics`, `..._fees`). Thirty-four matching repositories are one number read
34 times. We did not rebuild volume from `intents.near` events; one team reports doing so
([near-thesis](https://github.com/soldanoandrea/near-thesis)) and we have not replicated their work.

**Captured revenue, in contrast, can be checked without trusting the party that reports it.** We read the balances of the three revenue
wallets from an archival RPC node at 15 block heights. Their growth equals 1.01x, 0.98x and 0.98x of
DefiLlama's reported revenue over 30, 90 and 360 days. So the revenue series is confirmed by a second, on-chain
route, and no net outflow shows: the total never fell between two samples. The list of wallets itself comes from
DefiLlama's adapter; revenue sent anywhere else would not appear in either route.

## Evidence for

- **Demand moved to Intents and is still growing.** $32.93B settled in 365 days; the 30-day mean is 47.9% above
  a year ago. Gross fees were $54.12M in 365 days, 47x the base layer's $1.15M. (Single upstream
  source, see above.)
- **NEAR's share of those fees is rising.** Captured revenue was $9.50M over 365 days, 17.6% of gross fees, and
  30.5% over the last 30.
- **The capture is verifiable and accumulating.** The revenue wallets hold 4.28M NEAR, 0.33% of supply.
- **The cover of issuance is rising.** On chain, wallet growth was 11.3% of net supply growth in the first half
  of the last 360 days and 14.6% in the second half.
- **Supply growth is measured, not assumed.** Net supply grew 31.32M NEAR in 360 days, 2.48% a year, read from block
  headers and matching NearBlocks to 0.001%.

## Evidence against

- **Base-layer usage collapsed.** Transactions -84.8%, active accounts -75.6%, new accounts -95.6% year on
  year (30-day means). Twelve teams publish the transaction figure and all twelve replicate. Fees offset 1.86% of
  net issuance over 365 days and 1.11% over the last 30.
- **Holders are still diluted.** Even counting all captured revenue, about five sixths of new supply is not offset.
- **The yield is thin.** Captured revenue annualized from the last 30 days is $22.42M, 0.48% of a
  $4.70B market cap: the market pays 210x that revenue.
- **Growth is not one-way.** Intents volume in the last 30 days was -21.6% against the 30 days before.
- **The time to break even is long and assumption-driven.** At the measured year-on-year volume growth it takes
  4.3 years; at 25% a year 7.5 years; at half the measured rate 7.8 years. These are projections, not
  measurements.
- **Captured NEAR is not returned to holders.** It sits in two Sputnik DAO accounts and one multisig account. It is not
  burned, staked for holders or paid out. Its effect on a holder today is only that it is off the market.
- **Stake is concentrated.** 10 of 356 validators hold more than a third of stake (45.0% of supply is staked).

## How much the answer depends on definitions

The spread between teams is mostly definition, not error, and it sets the error bar on this thesis.

| Quantity | Teams publish | Our variants | What moves it |
| --- | --- | --- | --- |
| Share of issuance offset by Intents revenue | 8.7% to 21.0% (20 numbers) | 13.0% (360 d), 16.0% (30 d), 18.6% (90 d) | Window length. Sweeps into the wallets are lumpy: single 30-day steps range from 6.9% to 20.1% since April. |
| Share offset by fee burn | 0.58% to 2.00% (11 numbers) | 1.11% (30 d) to 1.86% (365 d) | Window, and whether 70% or 100% of fees is counted as burnt. |
| Growth needed to offset issuance | 5.1x to 7.6x (9 numbers) | 5.4x (90 d, on chain) | Same as the first row. |
| NEAR price change over a year | +19% to +97% (5 numbers) | +41% day to day, +91% between 30-day means | NEAR's price rose sharply in early November 2025, so the comparison day decides the result. |
| L1 fees in USD, change over a year | -27.6% to -55.3% (3 numbers) | -42% (30 d), -52% (90 d) | Window length: the same series gives either figure. |

We therefore state the cover as **13% to 19%**, not as one figure, and treat any 30-day reading as noise.

## What would change our mind

`python3 -m replicated.checks` evaluates these on every snapshot and exits with an error if a kill condition fails.

| Id | The thesis is dropped if this stops being true | Today |
| --- | --- | --- |
| K1 | Intents volume is higher than a year ago | 47.9% |
| K2 | Reported captured revenue matches wallet growth on chain within 10% (90 days) | 0.98x |
| K3 | The revenue wallets' total has not fallen between two samples | holds |
| K4 | Captured revenue offsets at least 10% of net issuance (90 days) | 18.6% |
| K5 | The cover over the last 180 days is higher than over the 180 days before | 14.6% vs 11.3% |

Dated predictions, written on 2026-11-11 (their thresholds were not moved with the snapshot) and checked by the same command once a snapshot exists on or after the date:

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
| `tx_yoy_30d` | -84.8% | 30-day mean txns vs the 30 days ending 365 days earlier. |
| `active_accounts_yoy_30d` | -75.6% | 30-day mean active_accounts vs the 30 days ending 365 days earlier. |
| `new_accounts_yoy_30d` | -95.6% | 30-day mean new_accounts vs the 30 days ending 365 days earlier. |
| `l1_fees_usd_365d` | $1.15M | Sum of NearBlocks daily txn_fee_usd, 365 days. |
| `burn_cover_of_net_issuance_pct_365d` | 1.86% | L1 fees / net supply growth, 365 days. Treats all fees as burnt. |
| `burn_cover_of_net_issuance_pct_30d` | 1.11% | L1 fees / net supply growth, 30 days. Treats all fees as burnt. |
| `intents_volume_365d` | $32.93B | Sum of DefiLlama daily NEAR Intents volume, 365 days to asof. |
| `intents_volume_yoy_30d` | 47.9% | 30-day mean daily volume vs the 30 days ending 365 days earlier. |
| `intents_volume_30d_vs_prev_30d` | -21.6% | Last 30 days of volume vs the 30 days before. |
| `intents_fees_365d` | $54.12M | Sum of DefiLlama daily gross fees (protocol + affiliate), 365 days to asof. |
| `intents_fees_over_l1_fees_365d` | 47x | Gross Intents fees / L1 fees in USD, 365 days. |
| `intents_capture_share_365d` | 17.6% | Captured revenue / gross fees, 365 days. |
| `intents_capture_share_30d` | 30.5% | Captured revenue / gross fees, 30 days. |
| `intents_revenue_365d` | $9.50M | Sum of DefiLlama daily revenue captured by NEAR wallets, 365 days to asof. |
| `intents_revenue_annualized_30d` | $22.42M | 30-day captured revenue x 365/30. |
| `net_inflation_annual_pct_360d_rpc` | 2.48% | Net supply growth over 360 days, annualized linearly, from block headers. |
| `net_issuance_near_360d_rpc` | 31.32M NEAR | total_supply in block headers: first block of 2026-11-13 minus first block 360 days earlier (archival RPC). |
| `revenue_wallets_near` | 4.28M NEAR | NEAR + wNEAR held by the three Intents revenue wallets at the first block of 2026-11-13. |
| `revenue_wallets_share_of_supply_pct` | 0.33% | Revenue wallet holdings / total supply. |
| `wallet_growth_over_defillama_revenue_30d` | 1.01x | Growth of wallet holdings / DefiLlama captured revenue in NEAR over the same 30 days. 1.0 means all reported revenue is still held. |
| `wallet_growth_over_defillama_revenue_90d` | 0.98x | Growth of wallet holdings / DefiLlama captured revenue in NEAR over the same 90 days. 1.0 means all reported revenue is still held. |
| `wallet_growth_over_defillama_revenue_360d` | 0.98x | Growth of wallet holdings / DefiLlama captured revenue in NEAR over the same 360 days. 1.0 means all reported revenue is still held. |
| `wallet_growth_cover_of_net_issuance_pct_30d` | 16.0% | Growth of revenue wallet holdings / growth of total supply, both from archival RPC, 30 days. |
| `wallet_growth_cover_of_net_issuance_pct_90d` | 18.6% | Growth of revenue wallet holdings / growth of total supply, both from archival RPC, 90 days. |
| `wallet_growth_cover_of_net_issuance_pct_360d` | 13.0% | Growth of revenue wallet holdings / growth of total supply, both from archival RPC, 360 days. |
| `wallet_cover_pct_first_180d` | 11.3% | Wallet growth / supply growth, days 360 to 180 before the snapshot (RPC). |
| `wallet_cover_pct_last_180d` | 14.6% | Wallet growth / supply growth, last 180 days (RPC). |
| `growth_multiple_to_offset_issuance_90d` | 5.4x | 1 / (90-day wallet cover of net issuance): how many times captured revenue must grow, at constant issuance and price ratio. |
| `years_to_offset_issuance_at_measured_volume_growth` | 4.3 years | ln(multiple) / ln(1 + g) with g = 47.9% a year. A projection, not a measurement: assumes captured revenue grows at g and issuance in NEAR stays as is. |
| `years_to_offset_issuance_at_half_measured_volume_growth` | 7.8 years | ln(multiple) / ln(1 + g) with g = 23.9% a year. A projection, not a measurement: assumes captured revenue grows at g and issuance in NEAR stays as is. |
| `years_to_offset_issuance_at_25pct_growth` | 7.5 years | ln(multiple) / ln(1 + g) with g = 25.0% a year. A projection, not a measurement: assumes captured revenue grows at g and issuance in NEAR stays as is. |
| `market_cap_usd` | $4.70B | NearBlocks market cap on asof (circulating supply x price). |
| `revenue_yield_on_mcap_pct_30d` | 0.48% | 30-day captured revenue annualized / market cap. |
| `mcap_over_intents_revenue_annualized_30d` | 210x | Market cap / (30-day captured revenue annualized). |
| `price_yoy` | 41% | Price on asof vs 365 days earlier. |
| `price_yoy_30d_avg` | 91% | 30-day mean price vs a year earlier. |
| `staked_share_pct` | 45.0% | Sum of current validator stake / total_supply from the latest sampled block header. |
| `validators_current` | 356 | Length of current_validators in the RPC `validators` response. |
| `validators_to_one_third` | 10 | Smallest number of validators whose stake exceeds one third of current stake. |
