# WORK_CHANGELOG — AI Investor Ecosystem
## 2026-11-16 — repair/scanner-clean-main-2026-11-16

### Zapisane zmiany
- Added `market_symbols.py`: explicit exchange-symbol routing and currency-to-benchmark reference map. Unknown/invalid symbols fail closed.
- Added `test_market_symbols.py`: tests for US symbols, Japanese/Taiwan suffixes, invalid symbols and benchmark lookup.
- Updated `scanner.py`:
  - Yahoo chart symbols can include explicit exchange suffixes.
  - Yahoo quote currency is retained from provider metadata.
  - Non-USD quotes retain native close/currency and are not represented as USD.
  - Valuation refuses non-USD prices until verified FX conversion exists.
  - Technical OHLCV bars remain available in native currency.
- Existing consensus, scenario, corporate-event and walk-forward validation modules remain wired as documented in the scanner.

### Verification
- GitHub Actions run `43894286174` completed successfully at commit `e0c8bd66bce073eb6d79fde6100d9fa05bee1003`; tests, guarded scan and report persistence passed.
- Latest run `43894391226` at commit `ef8ae557e701ddf482b6d70e6ce4b2d5f6f842d1`: test step completed successfully; guarded scan was still running at the last check. Do not treat the full run as passed until it completes.
- No backend or Android source tree was present at the inspected repository paths; no end-to-end mobile integration has been performed.

### Explicit blockers — do not publish BUY
- No verified historical analyst-consensus provider/data.
- No live corporate-event feed; missing/stale feed remains a veto.
- No audited point-in-time global universe including delisted securities.
- No actual strategy walk-forward backtest with generated historical signals, corporate actions, transaction costs and survivorship correction. Current module validates data and fold mechanics only.
- No verified FX conversion for non-USD valuations.
- Global market coverage is not complete; the current scanner universe remains a limited seed list and SEC facts cover US-reporting issuers.
- No backend/Android implementation or end-to-end test in this repository.

### Safety
- `main` was not modified.
- No paid data services were enabled.
- No APK was built or published.
- Investment BUY publication remains disabled.

## 2026-11-17 — global market symbol validation repair

### Zapisane zmiany
- Fixed the exchange-suffix regular expression in `market_symbols.py`; valid symbols such as `7203.T` and `2330.TW` are accepted without treating the dot as a wildcard or requiring a literal backslash.
- Expanded negative tests for malformed suffixes and invalid separators.

### Verification
- Changes pushed only to `repair/scanner-clean-main-2026-11-16`; `main` remains unchanged.
- GitHub Actions must complete the post-push test and scan workflow before this repair is considered verified.
- No paid data services enabled; no BUY authorization changed.

## 2026-11-17 — symbol validation and RSI integrity

### Zapisane zmiany
- Corrected the exchange-symbol suffix regex in `market_symbols.py`; dot separators are now literal. Added malformed-symbol rejection cases.
- Replaced the non-standard last-14-change RSI calculation in `scanner.py` with Wilder's recursive smoothing for RSI(14).
- Added `test_technical_indicators.py` covering monotonic rises/falls and insufficient OHLCV history; test dates use real calendar arithmetic.

### Verification status
- Commits: `a8d49f4` (symbol regex), `d02c9ea` (symbol tests), `adffc8f` (Wilder RSI), `7f0e1dd` (technical tests).
- Commits were made only on `repair/scanner-clean-main-2026-11-16`; `main` was not changed.
- GitHub Actions status must be checked after workflow completion; no green CI result is claimed here.
- No live analyst-consensus or corporate-event data was fabricated; BUY remains fail-closed.
- No paid services, backend deployment, APK build, or production publication performed.

## 2026-11-17 — corporate event risk regression tests

- Expanded `test_event_risk.py` for missing feed, fresh confirmed critical event, stale feed, unverifiable source and unconfirmed event handling.
- Tests validate the fail-closed event gate; they do not supply a live corporate-event provider.
- Validation remains pending GitHub Actions pull-request run.

## 2026-11-17 — technical entry trigger engine

- Added `entry_trigger.py`: deterministic EOD trend/pullback confirmation using validated close, SMA20/SMA50, Wilder RSI14, 20D volume ratio and 20D relative strength.
- Wired the trigger into `scanner.py`; it replaces the unconditional `entry_trigger=None`.
- Trigger fails closed when any input is missing, non-finite or invalid. It does not fabricate ATR, stop-loss, target price or expected return.
- Added regression tests for activation, overbought RSI, negative relative strength, missing inputs and NaN.
- This does not relax Balanced BUY gates; analyst consensus, full valuation and event feed remain independent blockers.
- Tests have been committed but no green CI result is claimed until GitHub Actions completes.

## 2026-11-17 — EARLY ENTRY watch monitor

- Added `early_entry.py`, a separate watch-only proximity monitor around SMA20.
- Conditions: price within -3% to +1% of SMA20, SMA20>SMA50, RSI14 40–60, volume/20D >=0.8 and positive 20D relative strength.
- Wired `early_entry` and boolean `early_buy_watch` into each company's report record.
- This is explicitly not a BUY signal. Missing or non-finite inputs fail closed.
- ATR, stop-loss and profit targets remain unavailable because current OHLCV payload stores close and volume only; daily high/low are not present. No ATR or price levels are fabricated.
- Added regression tests for proximity, oversold distance, overheated RSI, weak relative strength and missing data.
- No CI success claimed; GitHub Actions has not returned workflow runs for recent commits.

## 2026-11-17 — OHLC ATR, support/resistance and risk geometry

- Extended Stooq and Yahoo daily bars to retain genuine High/Low where supplied.
- Added Wilder ATR(14) and 20-session support/resistance only when real High/Low data are present; otherwise ATR remains unavailable.
- Added `risk_plan.py`: reference close, 1.5×ATR stop and 2R/3R scenario targets; explicit `scenario_only` status, not a forecast or BUY signal.
- Wired `risk_plan` into each company report record.
- Added tests for ATR availability, support/resistance, 2R/3R calculations and missing/invalid ATR.
- Note: Stooq may not return High/Low for all tickers; no ATR is fabricated when missing.
- No CI success claimed; tests require GitHub Actions execution.

- Follow-up: ATR test fixtures use valid calendar dates via `timedelta`; the test data no longer constructs invalid January day numbers.

## 2026-11-17 — signal authorization and report summary fix

- Fixed a pipeline defect: `buy_eligible` was unconditionally overwritten to `False` immediately after `evaluate_company`. It now preserves the strategy decision's boolean authorization.
- Added `summarize_signals()` and report-level counts for authorized BUY, EARLY ENTRY watch, active technical triggers, WATCH and blocked decisions.
- Added `test_signal_summary.py` to ensure a textual BUY without `buy_eligible=True` is not counted as an authorized BUY.
- Global investment ranking remains blocked until complete valuation, live event/consensus coverage and validated walk-forward backtest exist.

## 2026-11-17 — event-feed empty-state fail-closed and test correction

- Fixed a safety gap: an empty corporate-events CSV previously passed validation as an apparently healthy feed. Empty rows now return `unavailable` with `event_feed_empty`, preserving BUY veto.
- Added a regression test for the empty-feed case.
- Corrected the expected WATCH count in `test_signal_summary.py` (only records whose signal is WATCH are counted).

## 2026-11-17 — analyst consensus listing/currency and current-price rebasing

- Tightened consensus CSV contract: every record must specify exact exchange listing and 3-letter quote currency; this prevents ADR/local-line and currency mixing.
- Analyst upside/downside and probability-weighted scenario EV are recalculated against the latest quote for the same listing and currency, not the historical `price_at_consensus` snapshot.
- If ticker/listing/currency do not match, consensus becomes invalid and cannot support BUY.
- Added regression tests for current-price rebasing, adverse price movement turning upside/EV negative, listing/currency mismatch and missing listing metadata.
- Existing CSV rows without listing/currency are intentionally rejected until corrected; no automatic FX conversion is introduced.

## 2026-11-17 — native-currency technical risk levels and quote freshness

- Fixed risk-plan generation for non-USD listings: ATR and entry are both in the listing's native currency, so the module now uses `native_close` when USD-normalized price is deliberately unavailable and labels every level with its currency.
- Added a strict quote-date freshness check (maximum 7 calendar days; future dates rejected) before emitting levels.
- Added tests for JPY-native price/ATR consistency, currency labeling, stale-quote rejection and normal USD geometry.
- These levels remain `scenario_only`; they do not grant BUY eligibility.

## 2026-11-17 — relative-strength benchmark currency integrity

- Corrected the benchmark map: currency-specific USD-listed ETFs (EWJ/EWY/EWT/FXI/EWC/VGK/EWU) were not valid local-currency benchmarks for unconverted local share prices. Replaced them with local index symbols: ^N225, ^KS11, ^TWII, ^HSI, ^GSPTSE, ^STOXX50E and ^FTSE; USD remains SPY.
- Scanner now verifies the benchmark quote's provider-reported currency equals the listing quote currency before computing relative strength. A mismatch leaves RS unavailable and blocks the strategy technical gate.
- Added mapping tests for all supported local-currency indices and Yahoo symbol acceptance.
- This prevents a cross-currency return comparison from silently creating a false relative-strength signal. Actual index availability/currency remains provider-validated at runtime.

## 2026-11-17 — report coverage and decision blocker diagnostics

- Added a machine-readable `coverage_summary` to every scan report: quote/fundamental freshness, technical coverage, valuation availability, analyst-consensus status, decision-stage counts, corporate-event feed status and currency-matched benchmark availability.
- Added tests for complete count reconciliation and empty-universe behavior.
- This makes missing data visible per pipeline stage; it does not imply global market coverage or make incomplete securities BUY-eligible.

## 2026-11-17 — per-ticker corporate-event feed coverage gate

- Closed a false-clear path: a non-empty event CSV or a critical event for one company did not prove that the event calendar had been checked for every other ticker.
- Event feed now requires explicit, dated, source-linked `coverage_complete` marker rows (`status=coverage`) for each ticker whose calendar has been checked. Missing ticker coverage sets `event_feed_ticker_uncovered` and blocks BUY.
- Added tests for missing/empty feed, fresh coverage markers, absent markers, stale data, unverifiable source and unconfirmed events.
- CSV coverage marker contract: ticker, event_type=coverage_complete, event_date=as_of, source_url=https URL of that issuer's event calendar, as_of=current date, status=coverage. A marker must only be added after checking the issuer/exchange calendar.

## 2026-11-17 — corporate-event veto scoped to the issuer

- Fixed a critical overblocking bug: a confirmed event for one ticker was being placed in a global event-feed flag and therefore vetoed BUY for every company in the universe.
- Event feed validation now returns feed-integrity flags globally, while `event_flags_for_ticker` applies `critical_event_within_horizon` only to the matching ticker. Uncovered tickers remain blocked individually; invalid/missing feed still blocks all.
- Added regression tests proving XYZ's earnings do not veto ABC, while ABC remains blocked if its calendar lacks a coverage marker.
- Corrected the JPY benchmark strategy test from obsolete EWJ to the new local-index symbol ^N225.
