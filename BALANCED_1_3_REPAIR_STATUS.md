# Balanced 1.3 repair branch — status

## Branch safety
- Branch: `repair/balanced-1.3-integration`
- Base: `main` at `7307d7c33b2dc9db61741242932d14c8e8c6fb2d` (2026-11-09)
- The exact original `main/scanner.py` is preserved at `baseline/main-2026-11-09/scanner.py`.
- No production workflow, `main`, production report, or Android release was changed.

## Recovered reference source
- Archive: `AI_Robotics_Investor_Balanced_1.3.4_Global_Equity_Master_2026-11-08.zip`
- SHA-256: `49d694dc8a3b3e3402654e2ed0c205b589fdaed0383baf0a8c5155ba3a9c8a81`
- Contains scanner version `5.1.0-global-equity-master-balanced-1.3.4`, `balanced_strategy.py` version `balanced-1.3-audit`, technical-indicator generation, per-company decision traces and rejection ledger.
- The recovered scanner calls `evaluate_company` for each company and persists `data/signal_rejections.json`.
- Its operational health explicitly sets `buy_signals_authorized: false`.

## Strategy gates in recovered source
- BUY: Fundamental >= 75, Entry >= 60, median upside >= 15%, Reward/Risk >= 1.5.
- STRONG BUY: 88 / 80 / 20% / 2.2.
- EARLY BUY: 68 / 55 / 12% / 1.35; manual confirmation only.
- RSI >= 75 is a veto. Missing/stale quote, SEC filing, analyst consensus or technical input blocks eligibility.
- These thresholds are frozen for validation; no calibration has been performed on real historical data.

## Validation performed on recovered archive
- Focused regression suite: 45 passed.
- Covered Balanced evaluator, audit trace, event-study mechanics, historical data validation, provider adapters, global equity master, global OHLCV/FX parsing, analyst import and target validation.
- This is code-level validation only. It is not a strategy-performance result.

## Release blockers — do not enable BUY publication
The archive's `historical_dataset_manifest.json` remains:
`blocked_waiting_for_free_provider_key_and_point_in_time_target_access_test`.
- No real point-in-time historical dataset has been audited.
- No full historical universe including delisted securities has been imported.
- Eulerpool historical target-history entitlement/schema is unverified; no API key is available in runtime.
- No full-universe analyst-consensus coverage matrix exists.
- Historical backtest input data is not present in the archive's data directory.
- The backtest's strict-threshold sensitivity is not an exact legacy strategy reproduction. The preserved `main` scanner was attention/news-only and had no investment BUY engine.

## Next implementation gates
1. Port the recovered Balanced 1.3 scanner and required modules into this branch; keep the preserved baseline untouched.
2. Wire historical global OHLCV + FX, point-in-time SEC fundamentals and analyst target snapshots into the same as-of snapshot.
3. Add an integration test proving the production scan path calls Balanced 1.3 and writes one rejection/decision trace per security.
4. Run the real-data audit and walk-forward event study. Reject any dataset with future-dated inputs, incomplete corporate-action treatment, or survivorship bias.
5. Keep BUY authorization false until coverage and performance acceptance criteria pass. Only then consider a separate production PR.


## Recovery audit — 2026-11-12
- The exact archive was found in the user's Library (not missing): `AI_Robotics_Investor_Balanced_1.3.4_Global_Equity_Master_2026-11-08.zip`.
- SHA-256 verified: `49d694dc8a3b3e3402654e2ed0c205b589fdaed0383baf0a8c5155ba3a9c8a81`; ZIP integrity check passed.
- The archive's `scanner.py` is version `5.1.0-global-equity-master-balanced-1.3.4`; it invokes `evaluate_company` for each company and writes `data/signal_rejections.json`. This integration is in the archive, not yet in this repair branch.
- Focused local tests on the recovered archive: 95 passed across scanner, Balanced evaluator/audit trace, global market universe/data and analyst-target/import tests. Core Python modules passed `py_compile`.
- Full-scan integration test is stale: it asserts a 68-company universe while the recovered scanner now has 92 tracked entries. After updating the expected universe and expanding fixture batch sizes, the SEC-success fixture passed; the SEC-outage fixture still timed out due to unmocked external/network fallback and remains unresolved.
- The archive's cached `data/scan.json` and `data/coverage_report.json` are dated 2026-10-16 and are not current market evidence.
- Historical dataset manifest remains blocked: no audited point-in-time OHLCV/FX + delisted universe + historical analyst-target coverage. No real-data walk-forward backtest was performed.
- BUY publication remains unauthorized. No production workflow, main branch, Worker, or Android release was changed.


## Follow-up verification — 2026-11-12 (recovered archive executed locally)
- Materialized the exact Library archive into the working container and extracted it: 873 ZIP entries, 843 files; ZIP integrity test returned no corrupt member.
- `python -m compileall -q .` completed successfully for the recovered project tree.
- Targeted regression command (Python 3.13, `PYTHONPATH=.`) covering Balanced evaluator/audit trace/backtest, global universe/data, analyst target/import, scanner, release gate/publish integrity, historical pipeline/adapters: **119 passed in 15.34s**.
- A broad `pytest -q` attempt did not complete within the execution window; it was interrupted during the suite. This is not a full-suite pass.
- The earlier note of 95 tests is superseded by the reproducible 119-test targeted run above.
- Source archive scanner SHA-256: `b8c8d974efcfd1b40802c8a1b91081fb631f088a2f5d5af925c24d882678a216`; repair-branch scanner baseline SHA-256: `9aa7ddda22d48b200a1c0f95c38b529d6eb7cc3e`. They are different versions; the archive scanner has not yet been ported into this branch.
- Recovered archive `historical_dataset_manifest.json` still reports `blocked_waiting_for_free_provider_key_and_point_in_time_target_access_test`. It explicitly states that historical target access, delisted-universe history and full point-in-time dataset are not verified.
- The recovered archive's cached scan and coverage artifacts are historical snapshots, not current market data. No live market scan or walk-forward performance test was run.
- Current repair branch remains an evaluator repair branch; no production scan, Worker, Android app, `main`, or BUY authorization was changed.
