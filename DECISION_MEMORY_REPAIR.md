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


## Latest verified execution — 2026-11-12 09:19 UTC
- GitHub Actions push run `43190290668` completed with conclusion `success`; job steps included the test suite, public-news scan, artifact save and push.
- All 24 unit tests passed (0.012s). Tests include fiscal-period start/end alignment and suppression of P/E/FCF yield when periods are missing or mismatched.
- Scan artifact commit: `3d6e4da519c7ba5dda6824cce8097dfc5b152846`.
- Latest report: 68 companies, 115 news articles; 62 SEC financial records; 65/68 price records; 21/24 attempted quotes refreshed in this run; valuation coverage 54/68 is partial descriptive coverage, not full valuation.
- Three current quote failures: ABB (Stooq returned HTML, Yahoo 404), IRBT (Stooq returned HTML, Yahoo currency not USD), KUKAF (Stooq returned HTML, Yahoo 404).
- AVGO quote succeeded via Yahoo for 2026-11-11 in this run; the earlier AVGO failure was transient/provider-specific.
- Decision memory now has 15 historical entry levels, 0 frozen recommendations, 476 cumulative gate audits, 12 events, 4 scan snapshots; latest snapshot SHA-256 `7b47c1f9e6aae67b8c5e57b33ea8546cc859f20fd52cf365880e92aaa89e2dce`.
- Latest scan has 68 per-company gate audits with eight explicit N/D gates each. No BUY signal is computed because the investment-ranking engine and validated technical/valuation inputs are not yet implemented.
- Five historical zone-hit imports are preserved. The monitor also recorded a new MU intraday range touch on 2026-11-11. Touches require a fresh review and are not BUY signals.
- The report explicitly identifies global coverage as incomplete, USD-quote-only and SEC-centric discovery. It is not a complete global scanner.
- PR #1 remains open and main is unchanged. The PR check run returned `action_required`; do not merge until repository approval/check requirements are satisfied.

## Next implementation priorities
1. Replace USD-only quote assumptions with exchange-aware ticker mapping, native currencies, FX conversion and validated daily OHLCV; reject HTML/error pages cleanly.
2. Expand discovery beyond SEC registrants to the committed global watchlist and verified primary listings, without ticker/ADR unit ambiguity.
3. Implement the Balanced 1.3 investment ranking and explicit blocker values only after required data is present; do not downgrade N/D into a pass.
4. Add historical consensus/targets and full valuation model; then build walk-forward tests on real, timestamped data.
5. Reconcile all historical three-tier price plans from prior project artifacts. Only the five issuers listed in this ledger currently have exact recovered levels; do not invent missing levels.
