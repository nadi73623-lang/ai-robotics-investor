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


## Recovery automation — 2026-11-17
- Added workflow: `.github/workflows/recover-balanced-archive.yml` on branch `repair/balanced-1.3.4-scanner-port`.
- Trigger: push of a ZIP under `recovery-input/*.zip` (also supports manual dispatch).
- Runner checks the expected SHA-256, ZIP CRC, safe member paths/symlinks and expected project root; extracts the source, runs `compileall`, then commits the recovered tree to this repair branch.
- Workflow file was fetched back from GitHub and its content verified. This verifies the workflow definition exists, not that a run succeeded.
- The required archive is not present in the branch: GitHub returns 404 for `recovery-input/`. Therefore no recovery workflow run or source port has occurred yet.
- Remaining external step: upload the exact Library ZIP `AI_Robotics_Investor_Balanced_1.3.4_Global_Equity_Master_2026-11-08_2.zip` to `recovery-input/` on this branch. Expected SHA-256: `49d694dc8a3b3e3402654e2ed0c205b589fdaed0383baf0a8c5155ba3a9c8a81`.
- `main`, production workflow, Cloudflare Worker and BUY publication remain untouched/disabled.


## Follow-up verification — 2026-11-17 (independent rerun)
- Re-materialized the Library archive and verified the expected SHA-256: `49d694dc8a3b3e3402654e2ed0c205b589fdaed0383baf0a8c5155ba3a9c8a81`.
- Extracted the archive into a clean working directory. The six critical modules (`scanner.py`, `balanced_strategy.py`, `swing_engine.py`, `global_market_universe.py`, `release_gate.py`, `publish_guard.py`) passed `compileall`.
- Focused regression run with `PYTHONPATH=.`: `tests/test_balanced_strategy_integration.py`, `tests/test_balanced_audit_trace.py`, `tests/test_global_market_universe.py`, `tests/test_historical_data_pipeline.py`: **21 passed in 0.15s**.
- Initial test collection without `PYTHONPATH=.` failed to import root modules; rerunning with the repository root on the module path resolved collection. This is an invocation/environment issue, not a source fix.
- Important source audit finding: the archived scanner payload currently sets `investment_ranking_available: True`, while its `ranking_method` explicitly defines `attention_score` as a media-attention metric and its disclaimer says it is not a ranking/recommendation. This field is semantically misleading and must be reconciled before any report is exposed as an investment ranking. No change was made to the archive or published report in this pass.
- The repair branch's `scanner.py` still has the baseline SHA `9aa7ddda22d48b200a1c0f95c38b529d6eb7cc3e`; the archived scanner has not been ported. Recovery workflow still awaits the archive being committed under `recovery-input/`.
- No live scan, real-data backtest, production deployment, Cloudflare KV write, Android release, or BUY authorization was performed.

- Additional focused regression run with `PYTHONPATH=.`: analyst consensus/targets, release gate, extended publication integrity, SWING pipeline/watchlist, global market data and historical provider adapters: **38 passed in 0.18s**. Combined with the prior independent run, 59 focused tests passed (two separate runs; not a full-suite result).


## Corrective work — 2026-11-17 (local archive, not yet ported)
- Patched the recovered archive's `scanner.py`: `investment_ranking_available` changed from `True` to `False`; `ranking_method` now explicitly labels `attention_score` as media attention and not an investment ranking. This prevents a misleading capability flag from being emitted by that archive scanner.
- Added local regression test `tests/test_scanner_ranking_metadata.py`; result: **1 passed**.
- Re-ran focused suites for Balanced integration/audit, global universe/data, historical pipeline/providers, analyst import/targets, release gate, publication integrity and SWING pipeline: **53 passed**. Critical module `compileall` also passed.
- Patched local archive scanner SHA-256: `78d67b6ea77d252b8c3b55e2a82f518a6d3ea63c5ce046314edf803f8530feab`.
- This correction currently exists in the recovered working copy only. The GitHub repair branch still contains its older baseline scanner, and the archive recovery workflow has not run. No live scan or deployment was performed.


## CI guard added — 2026-11-17
- Converted the ranking-metadata guard to standard-library `unittest` so it can run without pytest.
- Updated `.github/workflows/balanced-validation.yml` to run the guard on pushes to this repair branch when scanner/test/workflow files change. Workflow commit: `5ab67d3e7421574d72ed61cfab8c2a398bb5ef97`.
- Test file commit: `908d98fe251d5ae246632fa1da035e60863eb3a7`.
- Verified both files by fetching them back from GitHub. A workflow run has not yet been confirmed; do not treat the CI result as passed.
- The workflow's existing legacy test command `python -m unittest -v test_balanced_strategy_repair.py` remains in place and is a separate pre-existing gate; its availability on this branch must be checked when reviewing the run.


## Corrected recovery package — 2026-11-17
- Re-extracted the Library source archive into a clean workspace and corrected the recovered `scanner.py` metadata: `investment_ranking_available=false` because `attention_score` is media attention, not an investment ranking.
- Added `tests/test_scanner_ranking_metadata.py` and updated stale `tests/test_android_import_safety_source.py` to assert the current asynchronous, bounded import validation implementation.
- Critical Python modules compile successfully. Focused regression suite: **54 passed**; Android import + ranking metadata tests: **3 passed**.
- Full pytest suite is NOT green/complete: an unrestricted run exposed multiple failures and timed out; `pytest -x` stopped after the first stale Android source assertion (now corrected locally) and a subsequent run stalled in the scan/network-heavy audit test. No full-suite pass is claimed.
- Corrected archive uploaded to the user's Library at `/AI INVESTOR ECOSYSTEM/AI_Robotics_Investor_Balanced_1.3.4_Corrected_2026-11-17.zip`. SHA-256: `d55e0aac82a10f9e1567395d70cf2d4a354ee3100301c02d01096c5db5781401`.
- Updated recovery workflow's expected checksum and recovery README for this corrected archive (workflow commit `3e8d66d9839ef09937d6ef2e93cc6f9503bac177`; README commit `114c9896bf714f5a074b59d26107a7e97128241d`). These files were fetched back and verified.
- Archive bytes have not yet been committed to `recovery-input/`; GitHub Actions recovery has not run, and recovered source has not been ported to the branch. This still requires the ZIP to be uploaded to that branch.
- No live scan, point-in-time backtest, production deployment, Cloudflare KV publication, Android release or physical-device test. BUY authorization remains false; `main` remains untouched.
