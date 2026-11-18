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


## Latest local verification and archive v2 — 2026-11-17
- Re-ran the focused validation matrix after correcting the global equity master cache test fixture to use a timestamp relative to current UTC time (the old hard-coded 2026-11-08 timestamp became stale as the calendar advanced). No production cache policy was changed.
- Focused validation matrix: **88 passed in 0.34s** across Balanced strategy/audit, global universe/master, historical providers, analyst consensus/targets, release/publication gates, SWING pipeline/watchlist, Android import safety, and related regression tests.
- Critical Python modules compile successfully. ZIP CRC/integrity check passed.
- Refreshed archive v2 is stored in Library at `/AI INVESTOR ECOSYSTEM/AI_Robotics_Investor_Balanced_1.3.4_Corrected_2026-11-17_v2.zip`; SHA-256 `a128ecc73cc7ff62b96104c1ecb41d19f9c060601b59dea001c8be288fdd8f5f`.
- Recovery workflow and README now pin this v2 checksum (workflow commit `f5cc75fe4e38eea971e9bd4821e8f75c93970aa3`; README commit `b997f10582813f1adcc205c233314590f4e3245a`).
- Pull request #5 is open as DRAFT against `main`; mergeable flag true, merged=false. It has 8 changed files and does not yet include the recovered full scanner source. CI statuses were empty at the time of verification.
- Archive transfer to `recovery-input/` and the GitHub recovery workflow run remain outstanding. No live data scan, point-in-time backtest, deployment, KV publication, Android device test, or BUY authorization.


## CI verification follow-up — 2026-11-17
- Re-ran the latest PR-triggered isolated validation associated with commit `8a0aa9ea66d7ee1785a0d27f6f15514a690d61df`.
- GitHub Actions run **44082705529** completed with conclusion **success**. Both job steps "Verify baseline and Balanced 1.3 decision gates" and "Verify scanner ranking metadata semantics" passed.
- A separate retry of the older failing run (head SHA `6b086ca1cd71787f600d600d11cfd2ee6d317de9`) still failed because that run tested an earlier revision of the SHA assertion. It is not the validation result for commit `8a0aa9ea`.
- Current successful CI validates only the isolated guard tests; it does not validate the recovered full scanner archive or live data pipeline.
- PR #5 remains DRAFT and unmerged. The archive ZIP is still absent from `recovery-input/`; the recovery workflow has not run. Full source integration, real-data scan, point-in-time backtest, production deployment, KV publication, Android device test, and BUY authorization remain outstanding. `main` remains unchanged.


## Local archive revalidation — 2026-11-17 (continued)
- Re-materialized the corrected v2 archive from the project Library into the active runtime. SHA-256 verified as `a128ecc73cc7ff62b96104c1ecb41d19f9c060601b59dea001c8be288fdd8f5f`; ZIP CRC check passed; archive contains 1,069 members.
- Extracted source compiles for critical modules: `scanner.py`, `balanced_strategy.py`, `swing_engine.py`, `release_gate.py`, `publish_guard.py`, `global_market_universe.py`, and `historical_data_pipeline.py`.
- Targeted regression run: **34 tests passed** across Balanced integration/audit trace, release and publication gates, global market universe, historical pipeline, analyst consensus import, SWING pipeline, and scanner ranking metadata.
- A broader `unittest discover` run began successfully but exceeded the execution time limit after initial Android/release checks and 49 dots; it is not recorded as a pass. No complete-suite result is claimed.
- The archive is verified locally, but its binary is still not present in GitHub `recovery-input/`; recovery workflow cannot run until the archive is uploaded there. No live market scan, audited point-in-time backtest, production deployment, KV publication, physical Android test, or BUY authorization was performed. `main` remains unchanged.


## Revalidation from Library source — 2026-11-17 (continued)
- Re-listed the project Library and selected the exact corrected v2 archive `AI_Robotics_Investor_Balanced_1.3.4_Corrected_2026-11-17_v2.zip` (1,994,202 bytes), not the older 1.3.4 master archive.
- Materialized the v2 archive and independently verified SHA-256 `a128ecc73cc7ff62b96104c1ecb41d19f9c060601b59dea001c8be288fdd8f5f`; ZIP integrity test passed.
- Full archive `compileall` passed.
- Re-ran focused integration/guard regression tests with the archive root on PYTHONPATH: **29 passed** (Balanced strategy integration/audit trace, global universe, historical provider adapters, analyst consensus import, SWING bundle priority, and publication integrity).
- An expanded run including scanner/full-scan tests reached 75% before the execution time limit; no pass is claimed for that expanded run. The first invocation without PYTHONPATH failed test collection due to import-path setup, then the corrected focused invocation passed.
- Source inspection confirms scanner output explicitly sets `investment_ranking_available: False`, labels `attention_score` as media attention rather than investment rating, and retains `buy_signals_authorized: false`. These are safeguards, not a functioning BUY publication path.
- Recovery workflow was re-read: it requires exactly one ZIP in `recovery-input/` with the v2 SHA-256, validates ZIP paths/symlinks/CRC, extracts under `recovered/AI_Robotics_Investor`, compiles, and commits to the repair branch. GitHub repository still does not contain the ZIP, so the workflow remains untriggered.
- No live market scan, real-data backtest, complete suite pass, deployment, KV write, production publication, or Android device test was performed. `main` remains unchanged.


## Full-scan fixture maintenance — 2026-11-17 (Cycle 291)
- Found a stale integration-test assumption: `tests/test_full_scan_integration.py` asserted exactly 68 companies although the recovered scanner's current `UNIVERSE` contains 92.
- Replaced hard-coded expected counts with `len(scanner.UNIVERSE)`; strict equality checks remain for company count, quote coverage, SEC refresh and shares coverage.
- Both integration scenarios passed independently: SEC fixtures available **1/1 PASS**; simulated SEC outage **1/1 PASS**. The outage test retains its assertion that release readiness is false and the capitalization blocker is present.
- Combined invocation exceeded the runtime limit; no full-suite pass is claimed.
- Created corrected archive v3 in the project Library: `AI_Robotics_Investor_Balanced_1.3.4_Corrected_2026-11-17_v3.zip`, SHA-256 `25b70bf831667bbb90e8cb6562d96f080dc27fdeca563b707ee1e30a76f56610`, 1,038 files, ZIP CRC passed. This v3 checksum is not yet configured in the GitHub recovery workflow; the current workflow still expects v2. The v3 archive is not in GitHub `recovery-input/`.
- No live market scan, real-data backtest, deployment, KV publication, Android device test, or BUY authorization. `main` unchanged.


## v3 recovery preparation and integration-test investigation — 2026-11-17
- Updated `.github/workflows/recover-balanced-archive.yml` expected SHA-256 from v2 to v3: `25b70bf831667bbb90e8cb6562d96f080dc27fdeca563b707ee1e30a76f56610`. Commit: `db44b1acdb267b869beaa3a1f6d371e1e88af9a3`.
- Updated `recovery-input/README.md` to identify the exact v3 archive and checksum. Commit: `cd68b2b03edda67cb18cfcd518afaef60e6a21d1`.
- Locally reverified v3 ZIP: 1,038 entries, CRC clean, SHA-256 matches workflow. The archive does not include the recovery workflow itself; workflow remains maintained in the GitHub repair branch.
- Re-ran `tests.test_full_scan_integration`: SEC-outage case passes. SEC-success case does not finish within the execution limit, including with a reduced local test budget. Inspection shows `scanner.main()` also invokes global-universe loading and other stages not covered by the current mocks. This test is therefore NOT fully passing and requires deterministic isolation of external providers / bounded fixtures before it can be accepted.
- Recovery workflow still cannot execute: `recovery-input/` has README only; archive bytes are not committed to GitHub. No binary-upload action is available in the connected GitHub toolset. The workflow has not been dispatched because it would fail its exactly-one-archive precondition.
- No full production scanner integration, live-data scan, real-data backtest, deployment, KV publication, physical Android test, or BUY authorization. `main` remains unchanged.


## Deterministic full-scan fixture and v4 package — 2026-11-17
- Repaired `tests/test_full_scan_integration.py` in the local recovered v3 tree: mocked `load_global_market_universe` and `load_analyst_targets` in addition to RSS, SEC, quote and sleep dependencies. This removes nondeterministic global directory/network work from the SEC success/outage fixture while preserving coverage assertions.
- Full-scan SEC success and SEC outage integration tests: **2/2 PASS (0.42s)**.
- Focused combined regression suite: **35 passed (0.94s)** covering full scan, Balanced strategy integration, release gate, global market universe, historical pipeline, analyst consensus, SWING pipeline and Balanced audit trace.
- Created clean v4 archive excluding Python cache/bytecode: 606 files, ZIP CRC clean, size 808,908 bytes, SHA-256 `783e2029896a381e82ccf814c1fc8b4793e2c5f3588612a96ed84eeb4051eeca`. Stored in project Library as `AI_Robotics_Investor_Balanced_1.3.4_Corrected_2026-11-17_v4.zip`.
- Updated recovery workflow expected checksum and README to v4. Workflow commit `510adda3b8edbbf0ac7d3e3f4a59d0e67250d5a8`; README commit `b5a065d1e6d44b11688921a9d0718afd8f6f4087`.
- Important limitation: local recovered source changes are packaged in v4 but have NOT yet been committed to the GitHub repair branch because archive bytes are still absent from `recovery-input/`. GitHub recovery workflow has not run. The connected GitHub toolset has no repository binary-upload action.
- No complete repository test suite pass, live market scan, point-in-time backtest, deployment, KV publication, physical Android test, or BUY authorization. `main` unchanged.


## Independent v4 revalidation — 2026-11-17 (continued session)
- Re-listed the project Library and materialized the exact v4 archive `AI_Robotics_Investor_Balanced_1.3.4_Corrected_2026-11-17_v4.zip` (808,908 bytes) into a clean runtime.
- Independently verified SHA-256 `783e2029896a381e82ccf814c1fc8b4793e2c5f3588612a96ed84eeb4051eeca`; ZIP contains 606 entries, `testzip()` returned no corrupt member, and the only archive root is `AI_Robotics_Investor/`.
- Full archive Python bytecode compilation: `python -m compileall -q .` completed successfully.
- Targeted regression command with `PYTHONPATH=.` covering full-scan integration (SEC success and outage), Balanced strategy integration, Balanced backtest, historical pipeline, global market universe, analyst targets, and operational delivery gate: **35 passed in 0.35s**.
- Initial pytest invocation without `PYTHONPATH=.` failed collection because root modules were not on `sys.path`; corrected invocation passed. This is an environment invocation detail, not a code failure.
- Re-read recovery workflow from GitHub: it expects the exact v4 SHA above, validates one ZIP, CRC, safe paths and root, compiles the extracted tree, then commits it to `repair/balanced-1.3.4-scanner-port`. GitHub `recovery-input/` currently contains only `README.md`; workflow has not run.
- PR #5 remains open, Draft, unmerged; its description confirms the recovered scanner archive is not yet ported. `main` remains untouched.
- No full repository test-suite pass, live market scan, audited point-in-time backtest, Cloudflare deployment/KV publication, Android device test, or BUY authorization. Keep `investment_ranking_available=false` and `buy_signals_authorized=false` until the separate acceptance gates are met.


## Independent follow-up — 2026-11-18 (local v4 extraction)
- Revalidated the Library v4 archive in a clean extracted working copy; its SHA-256 remains `783e2029896a381e82ccf814c1fc8b4793e2c5f3588612a96ed84eeb4051eeca`.
- Full `python -m compileall -q .` completed successfully.
- Focused regression matrix across 19 modules: **88 passed, 4 subtests passed in 6.06s**.
- Two stale test fixtures were corrected locally in `tests/test_evidence_freshness.py` and `tests/test_research_priority_and_atomic.py`; validators and production strategy logic were not weakened or changed.
- Full `pytest -q` did not complete within the execution window; it timed out after partial progress. No full-suite pass is claimed.
- These two fixture corrections are in the local extracted working copy only; they are not in the v4 ZIP or GitHub branch. A refreshed archive v5 was not created.
- Current GitHub CI for head `1f804d67ac15d1991928280cbebe3cd5647b6137`: run `44097392838` completed successfully. Both isolated job steps passed: baseline/Balanced decision gates and scanner ranking metadata semantics. This does not test the recovered full scanner archive.
- PR #5 remains open as Draft and unmerged. The v4 ZIP is still absent from `recovery-input/`; the recovery workflow has not run. Full source port, real-data walk-forward backtest, live scan, Cloudflare deployment/KV publication, Android device test and BUY authorization remain outstanding. `main` remains unchanged.


## Recovery workflow hardening — 2026-11-18
- Updated `.github/workflows/recover-balanced-archive.yml` to set up Python 3.13 and run a focused 17-module pytest regression matrix after checksum/ZIP safety checks and bytecode compilation, before committing recovered source.
- Workflow commit: `a5b77cf9a7c635171fa4b10a2496e3898f8be192`; fetched the workflow back from GitHub and verified the regression step and all 17 test paths are present.
- PR-triggered isolated CI for this commit: run `44271656218`, job `isolated-tests`, conclusion `success`. This is not execution of the recovery workflow or the new archive regression matrix.
- The exact v4 archive remains absent from `recovery-input/`; the recovery workflow has not run and the full scanner is still not ported. The upload path is still the only immediate blocker to that operation.
- No live scan, point-in-time backtest, production deployment, KV publication, Android device test, or BUY authorization. `main` remains unchanged.


## Main-branch scan audit — 2026-11-18
- Re-fetched `scanner.py` on `main` (SHA `9aa7ddda22d48b200a1c0f95c38b529d6eb7cc3e`) and `.github/workflows/scan.yml` (SHA `a4b22131841baf455dd875e7ef2b6687a2ba3fab`). Scheduled workflow runs every 6 hours and writes only `data/scan.json`; it does not publish to Cloudflare KV.
- Latest `data/scan.json` generated at `2026-11-18T07:21:56.535227+00:00`: 68 companies, 111 collected news articles, 65/68 price coverage, 62/68 financial coverage, 54/68 valuation coverage.
- Data contract explicitly says `investment_ranking_available=false`; ranking method is media attention (`attention_score`), not investment quality. No company has `investment_score`. Statuses: 12 `Do analizy`, 56 `Obserwacja`. This is a news/coverage scan, not an actionable BUY scanner.
- Quote health is partial (21 updated out of 24 attempts); ABB, IRBT and KUKAF quote retrieval failed. Latest price observations in this scan are EOD dated 2026-11-17.
- Conclusion: do not publish this scan as an investment report or feed it to the Android report endpoint as a release-ready report. Preserve BUY disabled until recovered Balanced engine, validated OHLCV/point-in-time analyst history and end-to-end release gates pass.


## Web PWA implementation and CI — 2026-11-18
- Reused existing static PWA shell in `index.html` (no new mobile app framework or paid service). Refreshed branch `data/scan.json` from the latest main scan (source blob `2f0ad3a37aac2beda3730693cf182c0be7e4cbf2`, generated `2026-11-18T07:21:56.535227+00:00`, 68 companies). This data remains explicitly non-actionable: `investment_ranking_available=false`.
- Updated the web UI disclosure so the unavailable investment ranking and BUY signals are explicitly marked disabled; no inferred BUY signals were added.
- Added `.github/workflows/web-validation.yml`; run `44272569957` completed with conclusion `success`. It validated JSON, required safety flag, PWA entrypoint, manifest, service worker and icon.
- Existing `web-deploy.yml` validation job passed on run `44272503876`, but deploy job failed before a runner started (job has zero steps and runner_id 0). Deployment is therefore NOT confirmed. Repository Pages configuration/permissions need owner-side verification; do not claim a live web URL until a successful deploy run reports its page_url.
- The PWA is a read-only static view of the current news/coverage scan, not a full Balanced investment engine and not connected to private Cloudflare Worker. Browser localStorage stores only local watchlist/notes. It is not yet live-deployed or verified on the Motorola device.
- The v4 source archive still has not been integrated into the branch. Full recovered-code regression suite, historical OHLCV/analyst consensus validation, walk-forward backtest and Android/Worker integration remain blocked. `main` unchanged; no production report publication or BUY authorization.

## Kontynuacja — 2026-11-18 (Pages deployment diagnosis)
- Rechecked PR #5: open, Draft, unmerged; head `9d51f437873fb9968074741e24bd5dd9f3559011`; `main` unchanged.
- Inspected prior Pages run `44272503876`: validation and `upload-pages-artifact` succeeded; deploy job failed before reporting any steps. A subsequent attempt to retrieve job logs returned 404, so the exact failure reason is not confirmed.
- Updated `.github/workflows/web-deploy.yml` to run `actions/configure-pages@v5` before validation/build and Pages artifact upload. Commit: `a290a8b054243baf92948ad27f6117f016b56f13`.
- Updated service worker cache key from `robotics-v422-20261011` to `robotics-v422-20261118`. Commit: `9d51f437873fb9968074741e24bd5dd9f3559011`.
- Fetched current PR metadata after the writes and confirmed the branch head advanced to the service-worker commit. No workflow run is yet associated with that head; deployment remains unverified.
- The archive v4 remains absent from `recovery-input/` (prior GitHub 404); full Balanced source recovery and its remote regression matrix have not run.
- No audited point-in-time OHLCV/analyst-consensus dataset, real-data walk-forward result, backend integration, Pages live URL, or phone test is confirmed. BUY authorization remains false; no production report publication; `main` unchanged.

## Web app build continuation — 2026-11-18
- Extended the existing mobile PWA `index.html` with a Settings tab for configuring a read-only HTTPS report endpoint.
- Added browser GET-only backend retrieval and strict acceptance checks: `release_ready=true`, `strategy_version` or `strategy` exactly `balanced-1.3-audit`, `generated_at` present/not future/not older than 36h, and `companies` array. Rejected responses leave the existing local/static report in place.
- No write method, API key, or publication token is stored in browser localStorage. The endpoint must support browser CORS; authenticated private endpoints are not yet integrated.
- Added CI source guards for backend validation and read-only behavior in `.github/workflows/web-validation.yml`.
- Commits: `386d8fb4149b151185417bce0068ac5b7336494f` (PWA backend settings/integration), `ed60fca98c615b4a43a7a1901558bee965121e7c` (CI validation).
- Workflow runs for the latest commit were not yet visible at verification time. No runtime test against a real backend was performed.
- PR #5 remains Draft/unmerged. GitHub currently reports `mergeable=false`; do not merge or modify `main` until conflicts and base status are examined.
- Balanced 1.3.4 archive is still not in `recovery-input/`; full strategy recovery, full tests, historical OHLCV/analyst-consensus audit, walk-forward backtest and live backend deployment remain blocked.
- GitHub Pages live deployment and physical mobile-browser test are not confirmed. BUY remains disabled; no production report is published.
## PWA backend integration syntax correction — 2026-11-18
- Latest observed PR CI for commit `2d5357c2cbd61594fdb8487104135d1606f245e2`: Web PWA validation run `44275123460` SUCCESS; isolated Balanced guard run `44275123461` SUCCESS. The former did not yet parse inline JavaScript, so it did not detect a literal escaped-newline syntax defect introduced in the backend functions.
- Inspected the committed `index.html` and found three literal `\\n` separators between JavaScript function declarations. Corrected them to actual line breaks in commit `b5bc186e6b8bd86086dad7a12eabeacc35b04bbb`.
- Added a `node --check` step for the inline application JavaScript to `.github/workflows/web-validation.yml`, commit `ccb85cd77d8a428ad3352b049c38a4eb72716cef`. This is intended to prevent recurrence; its CI result is pending.
- PR #5 currently reports open, Draft, unmerged, mergeable=true; latest checked head before the JavaScript CI workflow update was `2d5357c2...`. Do not merge until latest workflow result and full integration gates are checked.
- Backend remains a user-configurable GET endpoint. No real endpoint URL or runtime response was supplied, so no backend connection test is claimed. The endpoint requires CORS and a public read-only release-ready response.
- Archive v4 still absent from `recovery-input/`; recovered source integration, full tests, point-in-time OHLCV/analyst consensus audit and real-data walk-forward remain unexecuted remotely. GitHub Pages deployment and phone test remain unconfirmed. `main` untouched; BUY and production publication disabled.
## Current continuation checkpoint — 2026-11-18
- Re-verified current PR #5: open, Draft, unmerged, mergeable=true; head `d54ff7162612e77bf3c6eb6f9635204ce307522a`; base `main` unchanged.
- Latest PR CI runs associated with that head: Web PWA validation `44275767327` SUCCESS (including embedded JavaScript syntax parse); Balanced isolated validation `44275767397` SUCCESS. These are guard tests, not full recovered-scanner tests.
- Confirmed `main:data/scan.json` is a monitoring/news dataset (111 RSS articles; `investment_ranking_available=false`; ranking_method explicitly defines `attention_score` as media attention, not investment merit). Not suitable for investment ranking or BUY decisions.
- Rechecked recovery README and archive path: v4 ZIP remains absent from `recovery-input/`; recovery workflow cannot run until the archive is committed.
- PWA includes scanner, company cards, price/fundamental/valuation provenance labels, discovery/news, local watchlist/notes, export, and read-only HTTPS backend configuration with release gate. Backend endpoint/CORS not supplied, so runtime backend integration is unverified.
- GitHub Pages deploy workflow contains configure-pages and artifact/deploy jobs, but a successful deploy run and live page could not be confirmed. No physical phone test.
- No verified point-in-time OHLCV + historical analyst consensus dataset was found in the current report. No honest walk-forward backtest can be produced from this news/current-snapshot dataset.
- No production report published; BUY remains disabled; no secrets or paid services added; `main` untouched.