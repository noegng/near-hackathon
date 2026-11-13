# Proof of Numbers

Published NEAR numbers, recomputed from raw data.

Built at NEAR HACKATHON, track **Investment Thesis** (`thesis`). The thesis: [`THESIS.md`](THESIS.md).
The results on one page, generated from the build: <https://noegng.github.io/near-hackathon/>.

Many teams in this track measured the same chain independently and published their numbers. This project
treats those numbers as evidence: it records each one with its source, recomputes it from raw public data,
and shows where the teams agree, where they differ, and which definition explains the difference. The
thesis is then built only on numbers that replicate, and its conditions run as code.

## What it found

119 numbers published by 20 teams were recomputed from raw data, each for the day it was published: 101 are
within 5% of ours, 15 within 15%, 3 further apart. Recomputed on our snapshot day instead, only 89 are within 5%:
a correct 30-day number drifts as the window moves on. Team by team: <https://noegng.github.io/near-hackathon/>.

1. **The teams agree because they read one source.** 15 of the 20 repositories publish NEAR Intents volume,
   fees or revenue, and all 15 cite DefiLlama, whose adapter reads datasets NEAR uploads to Dune. Their
   agreement is one measurement read fifteen times. We added a second one: the three revenue wallets, read from an
   archival node at past block heights, grew by 0.98 to 1.01 times the reported revenue.
2. **Where published numbers differ, the definition differs, not the data.** NEAR's price over a year is +19%
   in one thesis and +96% or +97% in two others; L1 fees in USD fell 28%, 40% or 55%. Each of these six numbers
   is reproduced within 5% once the window and the end day are matched.
3. **One figure does not replicate, and we do not know why.** Two teams print 30-day Intents fees of
   $5,458,382 to the dollar and a third rounds it to $5.5M, all three committed on 11 Nov. Our 30-day total for
   10 Nov, the day before, is $5.96M (9% higher), and no 30-day window ending between 27 Oct and 10 Nov comes
   within 5% (closest: $5.78M, ending 8 Nov). Two other teams' fee totals match ours to 0.2% or better on their own
   publication days.

## Try it

Needs Python 3.9+ and nothing else (standard library only).

| Do | See |
| --- | --- |
| `python3 -m unittest discover -s tests` | 44 tests pass, offline, in about a second |
| `python3 -m replicated.build` | `out/metrics.json`: about 130 metrics, each with its definition, from the committed raw snapshot |
| `python3 -m replicated.compare` | `out/replication.md`: every published claim next to our number, and the spread per metric |
| `python3 -m replicated.checks` | the thesis's five kill conditions evaluated (all hold today) and four dated predictions (pending) |
| `python3 -m replicated.history` | `out/history.md`: every committed snapshot side by side, the kill conditions evaluated on each, and the past days a source changed between two snapshots |
| `python3 -m replicated.verify_claims` | (network) every quoted claim is found verbatim in its source file at the pinned commit |
| `python3 -m replicated.date_claims` | (network, git) re-derives the commit that wrote each quote and its date; `git diff claims/` stays empty |
| `python3 -m replicated.fetch` | (network, about 4 minutes) a new raw snapshot under `data/raw/<today>/` |

## Reproducibility

[![tests and rebuild](https://github.com/noegng/near-hackathon/actions/workflows/ci.yml/badge.svg)](https://github.com/noegng/near-hackathon/actions/workflows/ci.yml)

On every push, GitHub Actions runs the tests on Python 3.9 and 3.13, rebuilds `out/` and `docs/` from the
committed raw data, and fails if one byte differs from what is committed. Float sums use `math.fsum`, so
the outputs are identical on every Python version. `THESIS.md`, `out/` and the page are written from the
snapshot named in `data/THESIS_SNAPSHOT`. A scheduled job adds a raw snapshot every day at 15:00 UTC, evaluates
the kill conditions on it, and updates `out/history.md` and the "Re-checked every day" line and column on the page.

## How it works

- `data/raw/<date>/`: responses saved exactly as served, with URL and SHA-256 in `manifest.json`. Sources:
  DefiLlama (NEAR Intents volume, fees, captured revenue), NearBlocks daily charts (transactions, accounts,
  fees, price), and a public archival RPC: block headers (total supply), balances of the three Intents
  revenue wallets, `validators` and the protocol config. No API key is needed for any of them.
- `replicated/metrics.py`: pure functions. Where teams could reasonably choose different definitions
  (30, 90 or 365 days; net or gross issuance; gross fees or captured revenue), every variant is computed
  under its own id.
- `claims/claims.json`: published numbers, each with a verbatim quote, the file and the commit it was read at,
  and `published`: the commit that wrote the quote and its author date (`replicated/date_claims.py`).
- `replicated/checks.py`: the conditions under which the thesis is dropped, and dated predictions.
- `tests/test_thesis.py`: fails if a figure in `THESIS.md` differs from the computed metric.
- `replicated/compare.py`: matches each claim to the closest definition on the day it was published: the end
  day its quote states, otherwise the last complete UTC day before the commit that wrote it. One day per claim,
  no search over days. The same comparison on our snapshot day is kept for reference.

## Results (snapshot 2026-11-11)

- 119 numbers from 20 repositories: 101 are within 5% of our recomputation for the day each was published, 89 on
  our snapshot day. Full table, with each commit date: [`out/replication.md`](out/replication.md).
- Our own variants show the same spread as the teams: NEAR's price change over one year is +19% from day to day
  and +98% between 30-day averages.
- The wallet growth is 0.98 to 1.01 times DefiLlama's reported revenue over 30, 90 and 360 days.
- That revenue equals 13% to 18% of net issuance depending on the window, and all of it is still in the wallets.

## Limits

- Claims were extracted by reading each README and THESIS file, so the registry is a sample, not a census
  of everything each team published. Theses without a public repository linked from their demo post are absent,
  and so are two repositories we read that publish no number in these metric families (`l3ockydev/near-thesis-dashboard`:
  TVL against price; `3Nerion7/near-feelens`: a gas and storage cost model).
- Each claim is compared on one day only. A team that downloaded its data some days before committing shows a
  gap here even if its method matches ours. Where a family has several standard definitions (30, 90 or 365 days;
  net or gross issuance), the closest one is used and named, so a match shows that a standard definition gives
  the published number, not that the team computed it that way. Validators and stake (12 claims) can only be
  compared on our snapshot day, the only day the snapshot holds.
- The newest day of a DefiLlama series may still be filling when it is downloaded: at 07:38 UTC on 2026-11-12,
  Intents fees for 2026-11-11 read $23,742, against $195k to $298k on each of the three days before. The daily
  job therefore runs at 15:00 UTC, the time of day of the thesis snapshot, whose newest day the next snapshot
  confirmed unchanged.
- The 30-day fee total of $5,458,382 (finding 3) is closest to our series at 6% away. The source changing past
  days is one possible cause and is not supported so far: the snapshots of 2026-11-11 and 2026-11-12, taken a day
  apart, agree on every past day of the three DefiLlama Intents series (0 of 701, 550 and 550 days changed).
  `python3 -m replicated.restated <older> <newer>` compares two snapshots, and [`out/history.md`](out/history.md)
  lists the changed days for every pair of consecutive snapshots. A scheduled job (`.github/workflows/snapshot.yml`)
  commits one snapshot per day; the thesis stays pinned to 2026-11-11, the day its claims were matched.
- NearBlocks API v1 (`/v1/charts`) is announced to switch off on 2026-11-22; the committed snapshot keeps
  the build reproducible after that.

## Credits

The numbers under test belong to the teams listed in `claims/claims.json`, quoted with links. No code was
copied from their repositories. Built with Claude Code. License: MIT.
