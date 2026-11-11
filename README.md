# NEAR, replicated

Built at NEAR HACKATHON, track **Investment Thesis** (`thesis`). The thesis: [`THESIS.md`](THESIS.md).
The results on one page, generated from the build: <https://noegng.github.io/near-hackathon/>.

Many teams in this track measured the same chain independently and published their numbers. This project
treats those numbers as evidence: it records each one with its source, recomputes it from raw public data,
and shows where the teams agree, where they differ, and which definition explains the difference. The
thesis is then built only on numbers that replicate, and its conditions run as code.

## Try it

Needs Python 3.9+ and nothing else (standard library only).

| Do | See |
| --- | --- |
| `python3 -m unittest discover -s tests` | 40 tests pass, offline, in about a second |
| `python3 -m replicated.build` | `out/metrics.json`: about 130 metrics, each with its definition, from the committed raw snapshot |
| `python3 -m replicated.compare` | `out/replication.md`: every published claim next to our number, and the spread per metric |
| `python3 -m replicated.checks` | the thesis's five kill conditions evaluated (all hold today) and four dated predictions (pending) |
| `python3 -m replicated.history` | `out/history.md`: every committed snapshot side by side, the kill conditions evaluated on each, and the past days a source changed between two snapshots |
| `python3 -m replicated.verify_claims` | (network) every quoted claim is found verbatim in its source file at the pinned commit |
| `python3 -m replicated.fetch` | (network, about 4 minutes) a new raw snapshot under `data/raw/<today>/` |

## Reproducibility

[![tests and rebuild](https://github.com/noegng/near-hackathon/actions/workflows/ci.yml/badge.svg)](https://github.com/noegng/near-hackathon/actions/workflows/ci.yml)

On every push, GitHub Actions runs the tests on Python 3.9 and 3.13, rebuilds `out/` and `docs/` from the
committed raw data, and fails if one byte differs from what is committed. Float sums use `math.fsum`, so
the outputs are identical on every Python version. `THESIS.md`, `out/` and the page are written from the
snapshot named in `data/THESIS_SNAPSHOT`; later snapshots only feed `out/history.md`.

## How it works

- `data/raw/<date>/`: responses saved exactly as served, with URL and SHA-256 in `manifest.json`. Sources:
  DefiLlama (NEAR Intents volume, fees, captured revenue), NearBlocks daily charts (transactions, accounts,
  fees, price), and a public archival RPC: block headers (total supply), balances of the three Intents
  revenue wallets, `validators` and the protocol config. No API key is needed for any of them.
- `replicated/metrics.py`: pure functions. Where teams could reasonably choose different definitions
  (30, 90 or 365 days; net or gross issuance; gross fees or captured revenue), every variant is computed
  under its own id.
- `claims/claims.json`: published numbers, each with a verbatim quote, the file and the commit it was read at.
- `replicated/checks.py`: the conditions under which the thesis is dropped, and dated predictions.
- `tests/test_thesis.py`: fails if a figure in `THESIS.md` differs from the computed metric.
- `replicated/compare.py`: matches each claim to the closest definition, on our snapshot day and on the
  best day within the 14 days before (the theses were published on different days).

## Results (snapshot 2026-11-11)

- 119 numbers from 20 repositories: 89 are within 5% of our recomputation on the snapshot day, 109 when the day may
  move within two weeks. Full table: [`out/replication.md`](out/replication.md).
- The numbers that differ most between teams differ by definition, not by error. NEAR's price change over one year
  is +19% from day to day and +98% between 30-day averages; both appear in published theses.
- Every repository that publishes an Intents volume or fee number mentions DefiLlama, whose adapter reads datasets
  NEAR uploads to Dune. That agreement is one source read many times.
- Captured revenue is confirmed by a second route: the growth of the three revenue wallets, read from an archival
  node, is 0.98 to 1.01 times DefiLlama's reported revenue over 30, 90 and 360 days.
- That revenue equals 13% to 18% of net issuance depending on the window, and all of it is still in the wallets.

## Limits

- Claims were extracted by reading each README and THESIS file, so the registry is a sample, not a census
  of everything each team published. Theses without a public repository linked from their demo post are absent,
  and so are two repositories we read that publish no number in these metric families (`l3ockydev/near-thesis-dashboard`:
  TVL against price; `3Nerion7/near-feelens`: a gas and storage cost model).
- The dated search tries several definitions and 15 days per claim. A match shows that a standard
  definition on a nearby day gives the published number, not that the team computed it that way.
- DefiLlama restates recent days: three teams quote a 30-day fee total of $5,458,382 that the current series does
  not give for any end day in the two weeks before our snapshot (closest: 6% away). `python3 -m replicated.restated <older> <newer>` compares two snapshots, and
  [`out/history.md`](out/history.md) lists the changed days for every pair of consecutive snapshots. A scheduled job
  (`.github/workflows/snapshot.yml`) commits one snapshot per day from 2026-11-12.
- NearBlocks API v1 (`/v1/charts`) is announced to switch off on 2026-11-22; the committed snapshot keeps
  the build reproducible after that.

## Credits

The numbers under test belong to the teams listed in `claims/claims.json`, quoted with links. No code was
copied from their repositories. Built with Claude Code. License: MIT.
