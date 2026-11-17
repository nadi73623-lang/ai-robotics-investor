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
