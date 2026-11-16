"""Leakage- and survivorship-aware walk-forward backtest primitives.

A valid dataset must include point-in-time membership intervals for delisted
and acquired securities. Missing history is never inferred. This module
refuses to treat arithmetic fixtures as evidence of strategy performance.
"""
from __future__ import annotations
from datetime import date, timedelta
import math

REQUIRED={"ticker","decision_date","data_as_of","universe_start","universe_end","entry_price","exit_date","exit_price","signal"}

def validate_point_in_time_rows(rows):
    if not rows:
        return {"status":"blocked","reasons":["historical_dataset_empty"],"valid_rows":0}
    for i,row in enumerate(rows):
        missing=REQUIRED-set(row)
        if missing:
            return {"status":"blocked","reasons":[f"row_{i}_missing:{','.join(sorted(missing))}"],"valid_rows":0}
        try:
            decision=date.fromisoformat(str(row["decision_date"]))
            asof=date.fromisoformat(str(row["data_as_of"]))
            start=date.fromisoformat(str(row["universe_start"]))
            end=date.fromisoformat(str(row["universe_end"])) if row["universe_end"] else None
            exit_day=date.fromisoformat(str(row["exit_date"]))
            entry=float(row["entry_price"]); exit_price=float(row["exit_price"])
        except (TypeError,ValueError,OverflowError):
            return {"status":"blocked","reasons":[f"row_{i}_invalid_types_or_dates"],"valid_rows":0}
        if asof>decision:
            return {"status":"blocked","reasons":[f"row_{i}_lookahead_data"],"valid_rows":0}
        if start>decision or (end and decision>end):
            return {"status":"blocked","reasons":[f"row_{i}_outside_historical_universe_membership"],"valid_rows":0}
        if exit_day<=decision or not (math.isfinite(entry) and math.isfinite(exit_price) and entry>0 and exit_price>0):
            return {"status":"blocked","reasons":[f"row_{i}_invalid_trade_prices_or_exit_date"],"valid_rows":0}
    return {"status":"validated","reasons":[],"valid_rows":len(rows)}

def walk_forward_returns(rows, train_months=24, test_months=6):
    """Fold precomputed out-of-sample returns; not a strategy backtest."""
    if not rows:
        return {"status":"blocked","reason":"no_historical_trades","folds":[]}
    try:
        ordered=sorted(rows,key=lambda x:date.fromisoformat(x["decision_date"]))
        for row in ordered:
            value=float(row["return_pct"])
            if not math.isfinite(value): raise ValueError()
    except (KeyError,TypeError,ValueError):
        return {"status":"blocked","reason":"invalid_trade_history","folds":[]}
    first=date.fromisoformat(ordered[0]["decision_date"])
    last=date.fromisoformat(ordered[-1]["decision_date"])
    folds=[]; cursor=first
    while True:
        train_end=cursor+timedelta(days=30*train_months)
        test_end=train_end+timedelta(days=30*test_months)
        if test_end>last: break
        test=[r for r in ordered if train_end<date.fromisoformat(r["decision_date"])<=test_end]
        if test:
            vals=[float(r["return_pct"]) for r in test]
            folds.append({"train_end":train_end.isoformat(),"test_end":test_end.isoformat(),"trades":len(vals),
                          "mean_return_pct":round(sum(vals)/len(vals),4),
                          "win_rate_pct":round(100*sum(v>0 for v in vals)/len(vals),2)})
        cursor=test_end
    return {"status":"mechanics_only_not_performance_evidence",
            "reason":"requires audited point-in-time data, costs, delisted securities and generated strategy signals","folds":folds}
