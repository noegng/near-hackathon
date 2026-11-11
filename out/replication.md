# Replication table (snapshot 2026-11-11, data to 2026-11-10)

98 published numbers from 15 thesis repositories, each recomputed from raw data.
Thresholds: reproduced = within 5% of the published value, close = within 15%.

| Comparison | Reproduced | Close | Not reproduced |
| --- | --- | --- | --- |
| Same definition family, our snapshot day | 75 | 17 | 6 |
| Best day within 14 days before | 88 | 8 | 2 |

## Spread between teams, per metric family

| Family | Teams' numbers | Min | Median | Max | Spread / median | Reproduced (best day) |
| --- | --- | --- | --- | --- | --- | --- |
| price_yoy | 2 | 19.00 | 57.70 | 96.40 | 134% | 2/2 |
| burn_cover | 7 | 0.58 | 1.15 | 2.00 | 123% | 6/7 |
| intents_volume_yoy | 3 | 59.00 | 60.00 | 128.00 | 115% | 3/3 |
| issuance_cover | 7 | 12.00 | 18.00 | 20.60 | 48% | 6/7 |
| revenue_over_l1_fees | 2 | 13.00 | 17.00 | 21.00 | 47% | 1/2 |
| breakeven_multiple | 4 | 5.30 | 6.25 | 7.60 | 37% | 3/4 |
| l1_fees_usd_yoy | 2 | -40.00 | -33.80 | -27.60 | 37% | 2/2 |
| fees_over_l1_fees | 2 | 34.90 | 41.45 | 48.00 | 32% | 2/2 |
| intents_volume_avg_30d | 5 | $124.26M | $129.90M | $149.00M | 19% | 4/5 |
| intents_revenue_annualized | 3 | $21.60M | $22.60M | $25.60M | 18% | 3/3 |
| validators | 4 | 335 | 344 | 379 | 13% | 3/4 |
| intents_fees_30d | 5 | $5.46M | $5.50M | $6.13M | 12% | 2/5 |
| intents_share_of_near_dex_volume | 2 | 83.90 | 88.25 | 92.60 | 10% | 1/2 |
| intents_take_rate_bps | 2 | 14.53 | 15.04 | 15.56 | 7% | 2/2 |
| active_accounts_yoy | 4 | -78.00 | -76.50 | -73.50 | 6% | 4/4 |
| intents_capture_share | 2 | 32.10 | 33.01 | 33.92 | 6% | 2/2 |
| active_accounts_vs_peak | 2 | -97.00 | -94.55 | -92.10 | 5% | 2/2 |
| mcap_over_fees | 2 | 70.40 | 72.15 | 73.90 | 5% | 2/2 |
| revenue_yield_on_mcap | 2 | 0.45 | 0.46 | 0.47 | 4% | 2/2 |
| intents_volume_alltime | 3 | $35.70B | $37.00B | $37.17B | 4% | 3/3 |
| staked_share | 4 | 43.80 | 44.35 | 45.30 | 3% | 4/4 |
| net_inflation | 3 | 2.41 | 2.48 | 2.49 | 3% | 3/3 |
| mcap_over_revenue | 2 | 206.00 | 208.50 | 211.00 | 2% | 2/2 |
| tx_vs_peak | 3 | -93.00 | -91.80 | -91.00 | 2% | 3/3 |
| tx_yoy | 6 | -85.10 | -85.00 | -84.00 | 1% | 6/6 |
| intents_volume_30d | 2 | $3.73B | $3.74B | $3.76B | 1% | 2/2 |
| intents_volume_365d | 2 | $32.80B | $32.85B | $32.91B | 0% | 2/2 |
| new_accounts_yoy | 3 | -96.20 | -96.00 | -96.00 | 0% | 3/3 |
| intents_volume_30d_vs_prev | 1 | -20.70 | -20.70 | -20.70 | 0% | 1/1 |
| intents_fees_annualized | 1 | $74.50M | $74.50M | $74.50M | 0% | 1/1 |
| intents_fees_365d | 1 | $54.20M | $54.20M | $54.20M | 0% | 1/1 |
| intents_fees_90d | 1 | $17.40M | $17.40M | $17.40M | 0% | 1/1 |
| intents_revenue_365d | 1 | $9.35M | $9.35M | $9.35M | 0% | 1/1 |
| validators_to_one_third | 1 | 9 | 9 | 9 | 0% | 1/1 |
| l1_fees_usd_365d | 1 | $1.19M | $1.19M | $1.19M | 0% | 1/1 |
| l1_fees_usd_30d | 1 | $136,746 | $136,746 | $136,746 | 0% | 1/1 |

## Every claim

| Family | Project | Published | Ours (snapshot day) | Gap | Best dated match | Gap | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| active_accounts_vs_peak | NEAR Intents thesis: usage vs value capture | -97.00 | -96.91 `active_accounts_vs_peak_30d` | 0.1% | -97.02 `active_accounts_vs_peak_30d` @ 2026-11-05 | 0.0% | [quote](https://github.com/erfanmoheb/near-intents-thesis/blob/8bf528276c2f209394c0c9334ada3de2e6142168/THESIS.md) |
| active_accounts_vs_peak | NEAR as a Cross-Chain Settlement Business | -92.10 | -92.13 `active_accounts_vs_peak_day` | 0.0% | -92.13 `active_accounts_vs_peak_day` @ 2026-11-10 | 0.0% | [quote](https://github.com/Topeseun/near-intents-investment-thesis/blob/a02982df090e1a2e3c386f8c303fe4eae4f05094/README.md) |
| active_accounts_yoy | NEAR Demand Ledger | -78.00 | -76.28 `active_accounts_yoy_30d` | 2.2% | -77.86 `active_accounts_yoy_30d` @ 2026-11-09 | 0.2% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| active_accounts_yoy | near-thesis (rajeshmullippa) | -77.00 | -76.28 `active_accounts_yoy_30d` | 0.9% | -76.97 `active_accounts_yoy_30d` @ 2026-11-03 | 0.0% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| active_accounts_yoy | NEAR Thesis Scorecard | -76.00 | -76.28 `active_accounts_yoy_30d` | 0.4% | -75.75 `active_accounts_yoy_30d` @ 2026-11-02 | 0.3% | [quote](https://github.com/lvalentine16/near-thesis-indiciadesk/blob/d774e4528ec8f12a8c55ad2e6e1cf5c37a3e7eb6/THESIS.md) |
| active_accounts_yoy | NEAR Usage Thesis (lisaaai200) | -73.50 | -76.28 `active_accounts_yoy_30d` | 3.8% | -73.51 `active_accounts_yoy_30d` @ 2026-10-31 | 0.0% | [quote](https://github.com/lisaaai200/near-usage-thesis/blob/1e61facf7c79d23da8c0d8ec97871b9d24dd6951/THESIS.md) |
| breakeven_multiple | NEAR Books | 5.30 | 5.10 `breakeven_multiple_90d` | 3.8% | 5.31 `breakeven_multiple_90d` @ 2026-10-28 | 0.2% | [quote](https://github.com/IhorMuliar/nearbooks/blob/39f8c94a5d99fc4893a14e3b16283fb162e4455a/THESIS.md) |
| breakeven_multiple | NEAR Usage Thesis (Raindess69) | 5.30 | 5.10 `breakeven_multiple_90d` | 3.8% | 5.31 `breakeven_multiple_90d` @ 2026-10-28 | 0.2% | [quote](https://github.com/Raindess69/near-usage-thesis/blob/b3a9061544208bf5001e11deb7e8fcbb874df251/README.md) |
| breakeven_multiple | near-thesis: NEAR on the evidence | 7.20 | 6.81 `breakeven_multiple_365d` | 5.5% | 6.86 `breakeven_multiple_365d` @ 2026-11-07 | 4.7% | [quote](https://github.com/soldanoandrea/near-thesis/blob/13b580f37e97d04fa0403f5c1a785f962886bddd/README.md) |
| breakeven_multiple | NePu | 7.60 | 6.81 `breakeven_multiple_365d` | 10.4% | 6.86 `breakeven_multiple_365d` @ 2026-11-07 | 9.8% | [quote](https://github.com/Axlnd3r/NePu/blob/eb9fe8468b8fddfd2607b3db85a779b73b9788af/README.md) |
| burn_cover | NEAR Agent Census | 0.58 | 0.78 `burn70_cover_of_gross_issuance_pct_30d` | 34.4% | 0.78 `burn70_cover_of_gross_issuance_pct_30d` @ 2026-11-10 | 34.4% | [quote](https://github.com/daodudestiny56-netizen/near-thesis-/blob/fc071ba8aebce367fbe07fa87c0f2d635503b8f0/README.md) |
| burn_cover | NEAR Investment Thesis: the evidence | 0.80 | 0.78 `burn70_cover_of_gross_issuance_pct_30d` | 2.6% | 0.78 `burn70_cover_of_gross_issuance_pct_30d` @ 2026-11-10 | 2.6% | [quote](https://github.com/ridakalam52-design/near-investment-thesis/blob/39fede7aa774ae738215d4d4a7bfd8fc190b13ba/THESIS.md) |
| burn_cover | NEAR Intents thesis: usage vs value capture | 0.84 | 0.84 `burn70_cover_of_gross_issuance_pct_90d` | 0.3% | 0.84 `burn70_cover_of_gross_issuance_pct_90d` @ 2026-10-29 | 0.0% | [quote](https://github.com/erfanmoheb/near-intents-thesis/blob/8bf528276c2f209394c0c9334ada3de2e6142168/THESIS.md) |
| burn_cover | NEAR Usage Thesis (Raindess69) | 1.15 | 1.12 `burn_cover_of_net_issuance_pct_30d` | 2.4% | 1.12 `burn_cover_of_net_issuance_pct_30d` @ 2026-11-10 | 2.4% | [quote](https://github.com/Raindess69/near-usage-thesis/blob/b3a9061544208bf5001e11deb7e8fcbb874df251/README.md) |
| burn_cover | NEAR Demand Ledger | 1.88 | 1.87 `burn_cover_of_net_issuance_pct_365d` | 0.5% | 1.88 `burn_cover_of_net_issuance_pct_365d` @ 2026-11-09 | 0.1% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| burn_cover | near-thesis (rajeshmullippa) | 1.90 | 1.87 `burn_cover_of_net_issuance_pct_365d` | 1.5% | 1.90 `burn_cover_of_gross_issuance_pct_365d` @ 2026-11-02 | 0.1% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| burn_cover | NEAR Thesis Scorecard | 2.00 | 1.87 `burn_cover_of_net_issuance_pct_365d` | 6.4% | 1.97 `burn_cover_of_net_issuance_pct_365d` @ 2026-10-27 | 1.3% | [quote](https://github.com/lvalentine16/near-thesis-indiciadesk/blob/d774e4528ec8f12a8c55ad2e6e1cf5c37a3e7eb6/THESIS.md) |
| fees_over_l1_fees | Semilla1 NEAR Thesis | 34.90 | 43.35 `intents_fees_over_l1_fees_30d` | 24.2% | 34.88 `intents_fees_over_l1_fees_30d` @ 2026-11-08 | 0.1% | [quote](https://github.com/semilla1lab/semilla1-near-thesis/blob/94b8d27f2a7652db553b0ee6ac3ec4fa49237fa6/THESIS.md) |
| fees_over_l1_fees | NEAR Intents Thesis — Tested | 48.00 | 46.43 `intents_fees_over_l1_fees_365d` | 3.3% | 49.22 `intents_fees_over_l1_fees_90d` @ 2026-10-29 | 2.5% | [quote](https://github.com/luongs3/near-intents-thesis/blob/81f3ecce6fa0a619817a8f7f243b1aa336866b96/THESIS.md) |
| intents_capture_share | Semilla1 NEAR Thesis | 32.10 | 30.49 `intents_capture_share_30d` | 5.0% | 32.14 `intents_capture_share_30d` @ 2026-11-08 | 0.1% | [quote](https://github.com/semilla1lab/semilla1-near-thesis/blob/94b8d27f2a7652db553b0ee6ac3ec4fa49237fa6/THESIS.md) |
| intents_capture_share | NEAR as a Cross-Chain Settlement Business | 33.92 | 30.49 `intents_capture_share_30d` | 10.1% | 34.05 `intents_capture_share_30d` @ 2026-10-28 | 0.4% | [quote](https://github.com/Topeseun/near-intents-investment-thesis/blob/a02982df090e1a2e3c386f8c303fe4eae4f05094/README.md) |
| intents_fees_30d | NEAR Demand Ledger | $5.46M | $5.96M `intents_fees_30d` | 9.2% | $5.78M `intents_fees_30d` @ 2026-11-08 | 5.9% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| intents_fees_30d | NEAR as a Cross-Chain Settlement Business | $5.46M | $5.96M `intents_fees_30d` | 9.2% | $5.78M `intents_fees_30d` @ 2026-11-08 | 5.9% | [quote](https://github.com/Topeseun/near-intents-investment-thesis/blob/a02982df090e1a2e3c386f8c303fe4eae4f05094/README.md) |
| intents_fees_30d | NEAR Investment Thesis: the evidence | $5.50M | $5.96M `intents_fees_30d` | 8.4% | $5.78M `intents_fees_30d` @ 2026-11-08 | 5.1% | [quote](https://github.com/ridakalam52-design/near-investment-thesis/blob/39fede7aa774ae738215d4d4a7bfd8fc190b13ba/THESIS.md) |
| intents_fees_30d | Semilla1 NEAR Thesis | $5.78M | $5.96M `intents_fees_30d` | 3.1% | $5.78M `intents_fees_30d` @ 2026-11-08 | 0.0% | [quote](https://github.com/semilla1lab/semilla1-near-thesis/blob/94b8d27f2a7652db553b0ee6ac3ec4fa49237fa6/THESIS.md) |
| intents_fees_30d | NEAR Intents thesis: usage vs value capture | $6.13M | $5.96M `intents_fees_30d` | 2.8% | $6.13M `intents_fees_30d` @ 2026-11-05 | 0.1% | [quote](https://github.com/erfanmoheb/near-intents-thesis/blob/8bf528276c2f209394c0c9334ada3de2e6142168/THESIS.md) |
| intents_fees_365d | near-thesis (rajeshmullippa) | $54.20M | $54.03M `intents_fees_365d` | 0.3% | $54.19M `intents_fees_365d` @ 2026-11-02 | 0.0% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| intents_fees_90d | NEAR Intents Thesis — Tested | $17.40M | $18.76M `intents_fees_90d` | 7.8% | $17.43M `intents_fees_90d` @ 2026-10-31 | 0.2% | [quote](https://github.com/luongs3/near-intents-thesis/blob/81f3ecce6fa0a619817a8f7f243b1aa336866b96/THESIS.md) |
| intents_fees_annualized | NEAR Intents thesis: usage vs value capture | $74.50M | $72.52M `intents_fees_annualized_30d` | 2.7% | $74.49M `intents_fees_annualized_30d` @ 2026-11-04 | 0.0% | [quote](https://github.com/erfanmoheb/near-intents-thesis/blob/8bf528276c2f209394c0c9334ada3de2e6142168/THESIS.md) |
| intents_revenue_365d | near-thesis (rajeshmullippa) | $9.35M | $9.36M `intents_revenue_365d` | 0.1% | $9.35M `intents_revenue_365d` @ 2026-11-02 | 0.0% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| intents_revenue_annualized | NEAR's agent economy, measured | $21.60M | $22.11M `intents_revenue_annualized_30d` | 2.4% | $22.11M `intents_revenue_annualized_30d` @ 2026-11-10 | 2.4% | [quote](https://github.com/tenxagent/near-agent-economy/blob/c54570d5fa4993e5d625a6c36b5da70354b198be/README.md) |
| intents_revenue_annualized | Semilla1 NEAR Thesis | $22.60M | $22.11M `intents_revenue_annualized_30d` | 2.2% | $22.61M `intents_revenue_annualized_30d` @ 2026-11-08 | 0.0% | [quote](https://github.com/semilla1lab/semilla1-near-thesis/blob/94b8d27f2a7652db553b0ee6ac3ec4fa49237fa6/THESIS.md) |
| intents_revenue_annualized | near-thesis (rajeshmullippa) | $25.60M | $22.11M `intents_revenue_annualized_30d` | 13.6% | $25.55M `intents_revenue_annualized_30d` @ 2026-11-02 | 0.2% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| intents_share_of_near_dex_volume | NEAR Intents thesis: usage vs value capture | 83.90 | 92.78 `intents_share_of_near_dex_volume_30d` | 10.6% | 90.27 `intents_share_of_near_dex_volume_30d` @ 2026-10-27 | 7.6% | [quote](https://github.com/erfanmoheb/near-intents-thesis/blob/8bf528276c2f209394c0c9334ada3de2e6142168/THESIS.md) |
| intents_share_of_near_dex_volume | NEAR Demand Ledger | 92.60 | 92.78 `intents_share_of_near_dex_volume_30d` | 0.2% | 92.61 `intents_share_of_near_dex_volume_30d` @ 2026-11-07 | 0.0% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| intents_take_rate_bps | NEAR as a Cross-Chain Settlement Business | 14.53 | 15.50 `intents_take_rate_bps_90d` | 6.7% | 15.08 `intents_take_rate_bps_90d` @ 2026-10-29 | 3.8% | [quote](https://github.com/Topeseun/near-intents-investment-thesis/blob/a02982df090e1a2e3c386f8c303fe4eae4f05094/README.md) |
| intents_take_rate_bps | Semilla1 NEAR Thesis | 15.56 | 15.50 `intents_take_rate_bps_90d` | 0.4% | 15.56 `intents_take_rate_bps_30d` @ 2026-11-08 | 0.0% | [quote](https://github.com/semilla1lab/semilla1-near-thesis/blob/94b8d27f2a7652db553b0ee6ac3ec4fa49237fa6/THESIS.md) |
| intents_volume_30d | NEAR Demand Ledger | $3.73B | $3.76B `intents_volume_30d` | 0.8% | $3.73B `intents_volume_30d` @ 2026-11-09 | 0.0% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| intents_volume_30d | NEAR as a Cross-Chain Settlement Business | $3.76B | $3.76B `intents_volume_30d` | 0.0% | $3.76B `intents_volume_30d` @ 2026-11-10 | 0.0% | [quote](https://github.com/Topeseun/near-intents-investment-thesis/blob/a02982df090e1a2e3c386f8c303fe4eae4f05094/README.md) |
| intents_volume_30d_vs_prev | NEAR Investment Thesis: the evidence | -20.70 | -20.68 `intents_volume_30d_vs_prev_30d` | 0.1% | -20.68 `intents_volume_30d_vs_prev_30d` @ 2026-11-10 | 0.1% | [quote](https://github.com/ridakalam52-design/near-investment-thesis/blob/39fede7aa774ae738215d4d4a7bfd8fc190b13ba/THESIS.md) |
| intents_volume_365d | NEAR Thesis Scorecard | $32.80B | $32.91B `intents_volume_365d` | 0.3% | $32.79B `intents_volume_365d` @ 2026-10-29 | 0.0% | [quote](https://github.com/lvalentine16/near-thesis-indiciadesk/blob/d774e4528ec8f12a8c55ad2e6e1cf5c37a3e7eb6/THESIS.md) |
| intents_volume_365d | NEAR Investment Thesis: the evidence | $32.91B | $32.91B `intents_volume_365d` | 0.0% | $32.91B `intents_volume_365d` @ 2026-11-02 | 0.0% | [quote](https://github.com/ridakalam52-design/near-investment-thesis/blob/39fede7aa774ae738215d4d4a7bfd8fc190b13ba/THESIS.md) |
| intents_volume_alltime | NEAR Thesis Scorecard | $35.70B | $37.32B `intents_volume_alltime` | 4.6% | $35.75B `intents_volume_alltime` @ 2026-10-29 | 0.1% | [quote](https://github.com/lvalentine16/near-thesis-indiciadesk/blob/d774e4528ec8f12a8c55ad2e6e1cf5c37a3e7eb6/THESIS.md) |
| intents_volume_alltime | Semilla1 NEAR Thesis | $37.00B | $37.32B `intents_volume_alltime` | 0.9% | $37.01B `intents_volume_alltime` @ 2026-11-08 | 0.0% | [quote](https://github.com/semilla1lab/semilla1-near-thesis/blob/94b8d27f2a7652db553b0ee6ac3ec4fa49237fa6/THESIS.md) |
| intents_volume_alltime | NEAR Demand Ledger | $37.17B | $37.32B `intents_volume_alltime` | 0.4% | $37.17B `intents_volume_alltime` @ 2026-11-09 | 0.0% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| intents_volume_avg_30d | NEAR Demand Ledger | $124.26M | $125.26M `intents_volume_avg_30d` | 0.8% | $124.26M `intents_volume_avg_30d` @ 2026-11-09 | 0.0% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| intents_volume_avg_30d | NEAR Usage Thesis (Raindess69) | $127.59M | $125.26M `intents_volume_avg_30d` | 1.8% | $127.28M `intents_volume_avg_30d` @ 2026-11-01 | 0.2% | [quote](https://github.com/Raindess69/near-usage-thesis/blob/b3a9061544208bf5001e11deb7e8fcbb874df251/THESIS.md) |
| intents_volume_avg_30d | near-thesis (rajeshmullippa) | $129.90M | $125.26M `intents_volume_avg_30d` | 3.6% | $129.90M `intents_volume_avg_30d` @ 2026-11-02 | 0.0% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| intents_volume_avg_30d | NePu | $130.40M | $125.26M `intents_volume_avg_30d` | 3.9% | $130.41M `intents_volume_avg_30d` @ 2026-10-30 | 0.0% | [quote](https://github.com/Axlnd3r/NePu/blob/eb9fe8468b8fddfd2607b3db85a779b73b9788af/README.md) |
| intents_volume_avg_30d | NEAR Books | $149.00M | $125.26M `intents_volume_avg_30d` | 15.9% | $134.13M `intents_volume_avg_30d` @ 2026-11-06 | 10.0% | [quote](https://github.com/IhorMuliar/nearbooks/blob/39f8c94a5d99fc4893a14e3b16283fb162e4455a/THESIS.md) |
| intents_volume_yoy | NEAR Demand Ledger | 59.00 | 57.82 `intents_volume_yoy_30d` | 2.0% | 59.44 `intents_volume_yoy_30d` @ 2026-11-09 | 0.7% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| intents_volume_yoy | Semilla1 NEAR Thesis | 60.00 | 57.82 `intents_volume_yoy_30d` | 3.6% | 59.95 `intents_volume_yoy_30d` @ 2026-11-08 | 0.1% | [quote](https://github.com/semilla1lab/semilla1-near-thesis/blob/94b8d27f2a7652db553b0ee6ac3ec4fa49237fa6/README.md) |
| intents_volume_yoy | near-thesis (rajeshmullippa) | 128.00 | 57.82 `intents_volume_yoy_30d` | 54.8% | 128.47 `intents_volume_yoy_30d` @ 2026-11-02 | 0.4% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| issuance_cover | NePu | 12.00 | 12.85 `revenue_cover_of_gross_issuance_pct_365d` | 7.1% | 12.72 `revenue_cover_of_gross_issuance_pct_365d` @ 2026-11-07 | 6.0% | [quote](https://github.com/Axlnd3r/NePu/blob/eb9fe8468b8fddfd2607b3db85a779b73b9788af/THESIS.md) |
| issuance_cover | NEAR Agent Census | 15.10 | 15.04 `revenue_cover_of_gross_issuance_pct_30d` | 0.4% | 15.10 `revenue_cover_of_gross_issuance_pct_30d` @ 2026-11-08 | 0.0% | [quote](https://github.com/daodudestiny56-netizen/near-thesis-/blob/fc071ba8aebce367fbe07fa87c0f2d635503b8f0/README.md) |
| issuance_cover | NEAR Books | 17.30 | 16.33 `usage_cover_of_net_issuance_pct_30d` | 5.6% | 17.40 `usage_cover_of_gross_issuance_pct_30d` @ 2026-11-01 | 0.6% | [quote](https://github.com/IhorMuliar/nearbooks/blob/39f8c94a5d99fc4893a14e3b16283fb162e4455a/THESIS.md) |
| issuance_cover | NEAR Usage Thesis (Raindess69) | 18.00 | 18.42 `revenue_cover_of_gross_issuance_pct_90d` | 2.4% | 17.99 `usage_cover_of_net_issuance_pct_30d` @ 2026-10-30 | 0.1% | [quote](https://github.com/Raindess69/near-usage-thesis/blob/b3a9061544208bf5001e11deb7e8fcbb874df251/README.md) |
| issuance_cover | NEAR's agent economy, measured | 18.00 | 18.42 `revenue_cover_of_gross_issuance_pct_90d` | 2.4% | 17.99 `usage_cover_of_net_issuance_pct_30d` @ 2026-10-30 | 0.1% | [quote](https://github.com/tenxagent/near-agent-economy/blob/c54570d5fa4993e5d625a6c36b5da70354b198be/README.md) |
| issuance_cover | NEAR Usage Thesis (Raindess69) | 19.00 | 18.65 `revenue_cover_of_net_issuance_pct_90d` | 1.9% | 19.04 `usage_cover_of_net_issuance_pct_90d` @ 2026-10-27 | 0.2% | [quote](https://github.com/Raindess69/near-usage-thesis/blob/b3a9061544208bf5001e11deb7e8fcbb874df251/README.md) |
| issuance_cover | near-thesis (rajeshmullippa) | 20.60 | 19.86 `usage_cover_of_net_issuance_pct_90d` | 3.6% | 19.86 `usage_cover_of_net_issuance_pct_90d` @ 2026-11-10 | 3.6% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| l1_fees_usd_30d | NEAR Investment Thesis: the evidence | $136,746 | $137,506 `l1_fees_usd_30d` | 0.6% | $137,506 `l1_fees_usd_30d` @ 2026-11-10 | 0.6% | [quote](https://github.com/ridakalam52-design/near-investment-thesis/blob/39fede7aa774ae738215d4d4a7bfd8fc190b13ba/THESIS.md) |
| l1_fees_usd_365d | near-thesis (rajeshmullippa) | $1.19M | $1.16M `l1_fees_usd_365d` | 2.2% | $1.19M `l1_fees_usd_365d` @ 2026-11-05 | 0.0% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| l1_fees_usd_yoy | NEAR Investment Thesis: the evidence | -40.00 | -39.21 `l1_fees_usd_yoy_30d` | 2.0% | -39.21 `l1_fees_usd_yoy_30d` @ 2026-11-10 | 2.0% | [quote](https://github.com/ridakalam52-design/near-investment-thesis/blob/39fede7aa774ae738215d4d4a7bfd8fc190b13ba/THESIS.md) |
| l1_fees_usd_yoy | NEAR Usage Thesis (lisaaai200) | -27.60 | -39.21 `l1_fees_usd_yoy_30d` | 42.1% | -27.63 `l1_fees_usd_yoy_30d` @ 2026-10-31 | 0.1% | [quote](https://github.com/lisaaai200/near-usage-thesis/blob/1e61facf7c79d23da8c0d8ec97871b9d24dd6951/THESIS.md) |
| mcap_over_fees | NEAR Intents thesis: usage vs value capture | 70.40 | 65.52 `mcap_over_intents_fees_annualized_30d` | 6.9% | 70.44 `mcap_over_intents_fees_annualized_30d` @ 2026-11-05 | 0.1% | [quote](https://github.com/erfanmoheb/near-intents-thesis/blob/8bf528276c2f209394c0c9334ada3de2e6142168/THESIS.md) |
| mcap_over_fees | near-thesis: NEAR on the evidence | 73.90 | 65.52 `mcap_over_intents_fees_annualized_30d` | 11.3% | 74.70 `mcap_over_intents_fees_annualized_30d` @ 2026-10-31 | 1.1% | [quote](https://github.com/soldanoandrea/near-thesis/blob/13b580f37e97d04fa0403f5c1a785f962886bddd/README.md) |
| mcap_over_revenue | near-thesis (rajeshmullippa) | 206.00 | 214.89 `mcap_over_intents_revenue_annualized_30d` | 4.3% | 206.03 `mcap_over_intents_revenue_annualized_30d` @ 2026-11-07 | 0.0% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| mcap_over_revenue | Semilla1 NEAR Thesis | 211.00 | 214.89 `mcap_over_intents_revenue_annualized_30d` | 1.8% | 209.93 `mcap_over_intents_revenue_annualized_30d` @ 2026-11-09 | 0.5% | [quote](https://github.com/semilla1lab/semilla1-near-thesis/blob/94b8d27f2a7652db553b0ee6ac3ec4fa49237fa6/THESIS.md) |
| net_inflation | NEAR Agent Census | 2.41 | 2.48 `net_inflation_annual_pct_90d` | 2.7% | 2.45 `net_inflation_annual_pct_30d` @ 2026-10-28 | 1.6% | [quote](https://github.com/daodudestiny56-netizen/near-thesis-/blob/fc071ba8aebce367fbe07fa87c0f2d635503b8f0/THESIS.md) |
| net_inflation | NEAR Thesis Scorecard | 2.48 | 2.48 `net_inflation_annual_pct_365d` | 0.0% | 2.48 `net_inflation_annual_pct_365d` @ 2026-11-05 | 0.0% | [quote](https://github.com/lvalentine16/near-thesis-indiciadesk/blob/d774e4528ec8f12a8c55ad2e6e1cf5c37a3e7eb6/THESIS.md) |
| net_inflation | NEAR Usage Thesis (Raindess69) | 2.49 | 2.48 `net_inflation_annual_pct_365d` | 0.4% | 2.49 `net_inflation_annual_pct_365d` @ 2026-10-27 | 0.0% | [quote](https://github.com/Raindess69/near-usage-thesis/blob/b3a9061544208bf5001e11deb7e8fcbb874df251/THESIS.md) |
| new_accounts_yoy | NEAR Usage Thesis (lisaaai200) | -96.20 | -95.61 `new_accounts_yoy_30d` | 0.6% | -96.20 `new_accounts_yoy_30d` @ 2026-10-31 | 0.0% | [quote](https://github.com/lisaaai200/near-usage-thesis/blob/1e61facf7c79d23da8c0d8ec97871b9d24dd6951/THESIS.md) |
| new_accounts_yoy | NEAR Demand Ledger | -96.00 | -95.61 `new_accounts_yoy_30d` | 0.4% | -95.96 `new_accounts_yoy_30d` @ 2026-11-02 | 0.0% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| new_accounts_yoy | near-thesis (rajeshmullippa) | -96.00 | -95.61 `new_accounts_yoy_30d` | 0.4% | -95.96 `new_accounts_yoy_30d` @ 2026-11-02 | 0.0% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| price_yoy | NEAR Demand Ledger | 19.00 | 19.43 `price_yoy` | 2.3% | 19.43 `price_yoy` @ 2026-11-10 | 2.3% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| price_yoy | NEAR Usage Thesis (lisaaai200) | 96.40 | 97.80 `price_yoy_30d_avg` | 1.4% | 96.40 `price_yoy_30d_avg` @ 2026-10-30 | 0.0% | [quote](https://github.com/lisaaai200/near-usage-thesis/blob/1e61facf7c79d23da8c0d8ec97871b9d24dd6951/THESIS.md) |
| revenue_over_l1_fees | NEAR Usage Thesis (Raindess69) | 13.00 | 13.22 `intents_revenue_over_l1_fees_30d` | 1.7% | 13.22 `intents_revenue_over_l1_fees_30d` @ 2026-11-10 | 1.7% | [quote](https://github.com/Raindess69/near-usage-thesis/blob/b3a9061544208bf5001e11deb7e8fcbb874df251/THESIS.md) |
| revenue_over_l1_fees | near-thesis (rajeshmullippa) | 21.00 | 13.76 `intents_revenue_over_l1_fees_90d` | 34.5% | 13.76 `intents_revenue_over_l1_fees_90d` @ 2026-11-10 | 34.5% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| revenue_yield_on_mcap | NEAR's agent economy, measured | 0.45 | 0.47 `revenue_yield_on_mcap_pct_30d` | 3.4% | 0.45 `revenue_yield_on_mcap_pct_30d` @ 2026-10-27 | 1.0% | [quote](https://github.com/tenxagent/near-agent-economy/blob/c54570d5fa4993e5d625a6c36b5da70354b198be/README.md) |
| revenue_yield_on_mcap | Semilla1 NEAR Thesis | 0.47 | 0.47 `revenue_yield_on_mcap_pct_30d` | 1.0% | 0.47 `revenue_yield_on_mcap_pct_30d` @ 2026-11-10 | 1.0% | [quote](https://github.com/semilla1lab/semilla1-near-thesis/blob/94b8d27f2a7652db553b0ee6ac3ec4fa49237fa6/THESIS.md) |
| staked_share | near-thesis (rajeshmullippa) | 43.80 | 44.41 `staked_share_pct` | 1.4% | 44.41 `staked_share_pct` @ 2026-11-10 | 1.4% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| staked_share | NEAR Demand Ledger | 44.30 | 44.41 `staked_share_pct` | 0.2% | 44.41 `staked_share_pct` @ 2026-11-10 | 0.2% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| staked_share | NEAR Investment Thesis: the evidence | 44.40 | 44.41 `staked_share_pct` | 0.0% | 44.41 `staked_share_pct` @ 2026-11-10 | 0.0% | [quote](https://github.com/ridakalam52-design/near-investment-thesis/blob/39fede7aa774ae738215d4d4a7bfd8fc190b13ba/THESIS.md) |
| staked_share | NEAR Thesis Scorecard | 45.30 | 44.41 `staked_share_pct` | 2.0% | 44.41 `staked_share_pct` @ 2026-11-10 | 2.0% | [quote](https://github.com/lvalentine16/near-thesis-indiciadesk/blob/d774e4528ec8f12a8c55ad2e6e1cf5c37a3e7eb6/THESIS.md) |
| tx_vs_peak | NEAR as a Cross-Chain Settlement Business | -93.00 | -93.04 `tx_vs_peak_day` | 0.0% | -93.04 `tx_vs_peak_day` @ 2026-11-10 | 0.0% | [quote](https://github.com/Topeseun/near-intents-investment-thesis/blob/a02982df090e1a2e3c386f8c303fe4eae4f05094/README.md) |
| tx_vs_peak | NEAR Intents thesis: usage vs value capture | -91.80 | -92.07 `tx_vs_peak_30d` | 0.3% | -91.77 `tx_vs_peak_30d` @ 2026-11-05 | 0.0% | [quote](https://github.com/erfanmoheb/near-intents-thesis/blob/8bf528276c2f209394c0c9334ada3de2e6142168/THESIS.md) |
| tx_vs_peak | NEAR Usage Thesis (Raindess69) | -91.00 | -92.07 `tx_vs_peak_30d` | 1.2% | -91.02 `tx_vs_peak_30d` @ 2026-10-29 | 0.0% | [quote](https://github.com/Raindess69/near-usage-thesis/blob/b3a9061544208bf5001e11deb7e8fcbb874df251/THESIS.md) |
| tx_yoy | NEAR Investment Thesis: the evidence | -85.10 | -85.14 `tx_yoy_30d` | 0.0% | -85.09 `tx_yoy_30d` @ 2026-11-09 | 0.0% | [quote](https://github.com/ridakalam52-design/near-investment-thesis/blob/39fede7aa774ae738215d4d4a7bfd8fc190b13ba/THESIS.md) |
| tx_yoy | NEAR Demand Ledger | -85.00 | -85.14 `tx_yoy_30d` | 0.2% | -85.00 `tx_yoy_30d` @ 2026-11-06 | 0.0% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| tx_yoy | near-thesis (rajeshmullippa) | -85.00 | -85.14 `tx_yoy_30d` | 0.2% | -85.00 `tx_yoy_30d` @ 2026-11-06 | 0.0% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| tx_yoy | Semilla1 NEAR Thesis | -85.00 | -85.14 `tx_yoy_30d` | 0.2% | -85.00 `tx_yoy_30d` @ 2026-11-06 | 0.0% | [quote](https://github.com/semilla1lab/semilla1-near-thesis/blob/94b8d27f2a7652db553b0ee6ac3ec4fa49237fa6/README.md) |
| tx_yoy | NEAR Usage Thesis (lisaaai200) | -84.20 | -85.14 `tx_yoy_30d` | 1.1% | -84.25 `tx_yoy_30d` @ 2026-10-31 | 0.1% | [quote](https://github.com/lisaaai200/near-usage-thesis/blob/1e61facf7c79d23da8c0d8ec97871b9d24dd6951/THESIS.md) |
| tx_yoy | NEAR Thesis Scorecard | -84.00 | -85.14 `tx_yoy_30d` | 1.4% | -83.81 `tx_yoy_30d` @ 2026-10-30 | 0.2% | [quote](https://github.com/lvalentine16/near-thesis-indiciadesk/blob/d774e4528ec8f12a8c55ad2e6e1cf5c37a3e7eb6/THESIS.md) |
| validators | near-thesis (rajeshmullippa) | 335 | 351 `validators_current` | 4.8% | 351 `validators_current` @ 2026-11-10 | 4.8% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
| validators | NEAR Demand Ledger | 338 | 351 `validators_current` | 3.8% | 351 `validators_current` @ 2026-11-10 | 3.8% | [quote](https://github.com/hanafynst/near-demand-ledger/blob/1202e34a62258ba100256a42114b003091c3921f/THESIS.md) |
| validators | NEAR Investment Thesis: the evidence | 351 | 351 `validators_current` | 0.0% | 351 `validators_current` @ 2026-11-10 | 0.0% | [quote](https://github.com/ridakalam52-design/near-investment-thesis/blob/39fede7aa774ae738215d4d4a7bfd8fc190b13ba/THESIS.md) |
| validators | NEAR Thesis Scorecard | 379 | 351 `validators_current` | 7.4% | 351 `validators_current` @ 2026-11-10 | 7.4% | [quote](https://github.com/lvalentine16/near-thesis-indiciadesk/blob/d774e4528ec8f12a8c55ad2e6e1cf5c37a3e7eb6/THESIS.md) |
| validators_to_one_third | near-thesis (rajeshmullippa) | 9 | 9 `validators_to_one_third` | 0.0% | 9 `validators_to_one_third` @ 2026-11-10 | 0.0% | [quote](https://github.com/rajeshmullippa-collab/near-thesis/blob/2cd7ead764bf6e3b57e5ef1da22bdffbf5d43dbd/THESIS.md) |
