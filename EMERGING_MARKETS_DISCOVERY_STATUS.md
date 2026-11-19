# Emerging Markets Discovery — implementation status

## Scope
Added a separate discovery layer for eight structural markets: quantum technologies, silicon photonics/optical interconnect, advanced nuclear/SMR, next-generation batteries/storage, Physical AI/robotics, advanced materials/semiconductor manufacturing, space infrastructure, and neurotechnology/BCI.

## Files
- `emerging_markets.py`: market theses, commercial-evidence gates, risks, and a global seed list of listed-company candidates.
- `test_emerging_markets.py`: basic integrity and safety tests.
- `scanner.py`: integration point to expose the radar as a separate report section.

## Safety / interpretation
- This is discovery/watchlist functionality, not a trading strategy.
- Every candidate is marked `WATCHLIST_ONLY`; fundamental, valuation and entry scores remain null.
- Listing status, instrument type, issuer exposure, current price, liquidity, filings, dilution and valuation must be verified before promotion.
- News mentions are not evidence of commercial adoption.
- Private companies are not treated as investable listed equities.
- Existing Balanced 1.3 thresholds and publication gates are not changed.

## Remaining work
1. Integrate into `scanner.py` and report schema.
2. Run unit tests and workflow validation.
3. Add exchange-native discovery beyond SEC / US-only issuers (Japan, Korea, Taiwan, Europe, Canada).
4. Add independent sources for patents, grants, procurement, standards, clinical/regulatory milestones and company filings.
5. Add historical event snapshots and a deduplicated evidence ledger before claiming early-detection performance.
6. Connect the new report section to backend and Android only after end-to-end validation.

## Current status
Initial isolated module and tests prepared on `feature/emerging-markets-discovery`. Not merged to `main`; not a BUY engine; no paid data services used.
