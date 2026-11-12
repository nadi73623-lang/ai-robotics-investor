# Decision memory repair — 2026-11-12

## Purpose
Prevent the scanner from losing its own historical recommendations, entry zones, price observations, and BUY-gate explanations between runs.

## Added
- `decision_memory.py`: append-only JSON memory with schema versioning.
- `data/decision_memory.json`: created on first scan; committed by scheduled workflow.
- Immutable historical entry-zone definitions recovered from the 2026-09-11 analysis for MU, ADBE, OUST, XPEV and MP (three tiers each).
- Five historical zone-hit imports from the 2026-11-12 audit, preserving the difference between intraday low and closing price.
- EOD close observation ledger with source, date, currency and timestamp.
- Zone-touch events; duplicate close events are suppressed.
- Append-only interfaces for frozen recommendations and per-gate PASS/FAIL/ND/VETO audits.
- Scan payload exposes memory counts, new hits and imported historical events.
- Workflow executes unit tests before running the scanner and commits both scan report and decision memory.

## Critical safeguards
- Entry-zone touch is not automatically BUY.
- No quote means N/D, never zero.
- Currency mismatch prevents zone comparison.
- Missing gate audit cannot be represented as a passed gate.
- Historical levels are immutable; changed levels must be appended as new versions/events.

## Known limitations — not yet fixed
- Current quote provider code still only supports USD tickers and does not provide reliable global OHLCV/FX coverage.
- This patch tracks EOD close touches only for new scans; it does not reconstruct missing daily lows from a verified historical OHLCV source.
- The five historical hits are imports from the prior audit, not independently re-downloaded exchange records in this commit.
- No complete Balanced 1.3 ranking, DCF valuation engine, analyst-consensus history, full rejection registry, Android integration or APK build is included.
- No live BUY signal is created by this patch.
- GitHub Actions test execution has not yet been observed; tests are wired into the workflow for the next run.

## Validation status
- Branch created from current `main`; main was not modified.
- Unit tests added for historical levels, zone-hit deduplication, missing prices, append-only recommendations and explicit gate states.
- Runtime CI result: pending.


## Follow-up changes — 2026-11-12
- Added daily low/high extraction from Stooq and Yahoo chart bars where the provider returns those fields.
- Entry-zone monitor now stores separate `intraday_range` and `close` events.
- Scanner writes an explicit per-ticker N/D gate audit for investment ranking, fundamental score, entry score, base upside, risk/reward, data quality, analyst consensus and veto review. This is an honest block, not a simulated pass/fail.
- Pull request workflow is test-only; scan publication is skipped for pull_request events.
- Scan job serializes runs and rebases generated artifact commits before pushing, to mitigate concurrent workflow updates.
- Unit tests passed in GitHub Actions on commit `50025b07fb819eff5bd80afc247fb616ad0233b4` (PR validation run).
- A scheduled/push scan execution is still pending final confirmation of artifact commit and ledger contents.


## Latest verified scan — 2026-11-12 08:56 UTC
- Scheduled/push scan completed successfully, including unit tests and artifact commit.
- 68 issuers scanned, 114 news articles collected.
- Price coverage: 65/68; only 21 refreshed in the current rotating batch; three quote failures.
- Valuation coverage: 54/68 partial/available, not full intrinsic valuations.
- Decision ledger: 15 entry levels, 68 explicit N/D gate audits, 6 events at that run (5 historical imports plus one MU close event).
- Investment ranking remains explicitly unavailable. No BUY was calculated.
- AVGO quote providers failed in this run (Stooq bad CSV, Yahoo blocked); therefore AVGO's current quote must remain N/D.
- Follow-up patch now attaches each issuer's gate audit and entry-zone history directly to the report and normalizes the imported intraday/close event basis.
- The workflow test suite passed on earlier commits; the latest per-company report and ledger migration changes are awaiting CI verification.
