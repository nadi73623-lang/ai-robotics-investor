# Backtest readiness — release gate

## Current status: BLOCKED

The current `walk_forward.py` contains validation of point-in-time row structure and chronological fold arithmetic. It does **not** generate historical strategy signals and is not evidence of strategy performance.

## Required source dataset
Every historical security observation must contain:
- permanent security identifier (not ticker alone), ticker and exchange mapping valid on decision date;
- point-in-time universe membership start/end, including delisted, bankrupt, acquired and renamed issuers;
- daily OHLCV adjusted for splits and dividends, plus raw prices for execution modelling;
- publication timestamps for fundamentals, analyst estimates and corporate events;
- FX rates and benchmark series known at the decision timestamp;
- delisting/merger cash or stock consideration and terminal returns;
- liquidity, spread/commission/slippage assumptions.

## Required methodology
- chronological train/validation/test periods; no random split;
- rolling or expanding walk-forward folds;
- no future revisions, restated financials or revised consensus before their publication timestamps;
- delisted securities retained; ticker reuse handled by permanent identifier;
- corporate actions and total-return treatment;
- fees, slippage, FX and realistic execution delay;
- benchmark comparison, drawdown, CAGR, volatility, Sharpe/Sortino, hit rate, payoff, turnover and exposure;
- parameter selection only inside training folds; final untouched holdout;
- report coverage and exclusions by exchange, year and market cap.

## Acceptance
No strategy-performance claim or BUY release until the data lineage audit passes, all folds are reproducible, and the untouched out-of-sample period has sufficient trades and stable results. Synthetic fixtures may test code only and must never be labelled a backtest.
