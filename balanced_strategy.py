"""Conservative Balanced decision gate.

This module cannot create a BUY from incomplete inputs. It is deliberately
separate from publication; the scan pipeline records every blocker.
"""
from __future__ import annotations
import math
from datetime import date
from market_symbols import benchmark_for_currency

VERSION = "balanced-1.3.4-integrity"
THRESHOLDS = {
    "buy_fundamental": 80, "buy_entry": 70, "buy_upside_pct": 20,
    "buy_reward_risk": 1.7, "stable_a_buy_upside_pct": 15,
    "strong_fundamental": 88, "strong_entry": 80,
    "strong_upside_pct": 25, "strong_reward_risk": 2.2,
    "rsi_veto": 75,
}

def _number(value):
    return type(value) in (int, float) and math.isfinite(value)

def evaluate_company(company, today=None):
    today=today or date.today()
    result = {"strategy_version": VERSION, "signal": "WATCH", "buy_eligible": False,
              "decision_stage": "data_gate", "decision_trace": [], "reasons": [],
              "fundamental_score": None, "entry_score": None}
    checks = result["decision_trace"]
    def check(stage, name, actual, required, passed, reason):
        checks.append({"stage": stage, "check": name, "actual": actual,
                       "required": required, "passed": bool(passed),
                       "reason": None if passed else reason})
    q = company.get("price") or {}
    f = company.get("fundamentals") or {}
    v = company.get("valuation") or {}
    a = company.get("analyst_targets") or {}
    try:
        quote_day = date.fromisoformat(q["date"])
        filed_day = date.fromisoformat(f["filed"])
        quote_age = (today - quote_day).days
        filing_age = (quote_day - filed_day).days
        price_current = 0 <= quote_age <= 4
        filing_current = 0 <= filing_age <= 540 and f.get("source") == "SEC EDGAR XBRL"
    except (KeyError, TypeError, ValueError):
        quote_day = filed_day = None
        quote_age = filing_age = None
        price_current = filing_current = False
    check("data", "quote_current", {"date": q.get("date"), "age_days": quote_age},
          "EOD quote no older than 4 calendar days", price_current, "price_stale_or_future")
    check("data", "filing_current", {"filed": f.get("filed"), "age_days_at_quote": filing_age},
          "SEC EDGAR filing no older than 540 days at quote date", filing_current, "fundamentals_missing_or_stale")
    if any(not x["passed"] for x in checks):
        result["reasons"] = [x["reason"] for x in checks if not x["passed"]]
        return result
    check("consensus", "analyst_targets", a.get("status"), "documented",
          a.get("status") == "documented", "analyst_consensus_missing")
    if a.get("status") != "documented":
        result["decision_stage"] = "analyst_consensus"
        result["reasons"] = ["analyst_consensus_missing"]
        return result
    up, down = a.get("upside_median_pct"), a.get("downside_low_pct")
    if not (_number(up) and _number(down) and up > 0 and down < 0):
        result["decision_stage"] = "analyst_consensus"
        result["reasons"] = ["invalid_analyst_targets"]
        return result
    ev = a.get("probability_weighted_ev_pct")
    check("valuation", "probability_weighted_ev", ev, "> 0", _number(ev) and ev > 0,
          "positive_probability_weighted_ev_missing")
    trigger = company.get("entry_trigger")
    check("entry", "active_entry_trigger", trigger, "active numeric trigger",
          isinstance(trigger, dict) and trigger.get("active") is True and _number(trigger.get("price")),
          "active_entry_trigger_missing")
    if any(not x["passed"] for x in checks):
        result["decision_stage"] = "valuation_or_entry"
        result["reasons"] = [x["reason"] for x in checks if not x["passed"]]
        return result
    growth, margin, ps, fcfy = f.get("revenue_growth_pct"), f.get("net_margin_pct"), v.get("ps"), v.get("fcf_yield_pct")
    if not all(_number(x) for x in (growth, margin, ps, fcfy)):
        result["decision_stage"] = "score_inputs"
        result["reasons"] = ["fundamental_or_valuation_inputs_missing"]
        return result
    if not v.get("periods_aligned"):
        result["decision_stage"] = "period_integrity"
        result["reasons"] = ["valuation_periods_not_aligned"]
        return result
    technical = (q.get("rsi_14"), q.get("sma20"), q.get("sma50"),
                 q.get("volume_ratio20"), q.get("relative_strength_20d_pct"))
    expected_benchmark=benchmark_for_currency(q.get("currency", "USD"))
    if not all(_number(x) for x in technical) or not expected_benchmark or q.get("relative_strength_benchmark") != expected_benchmark:
        result["decision_stage"] = "technical_inputs"
        result["reasons"] = ["technical_inputs_or_benchmark_missing"]
        return result
    if q["rsi_14"] >= THRESHOLDS["rsi_veto"]:
        result["decision_stage"] = "technical_veto"
        result["reasons"] = ["overbought_no_chase"]
        return result
    if company.get("investment_risk_flags", {}).get("flags"):
        result["decision_stage"] = "risk_veto"
        result["reasons"] = list(company["investment_risk_flags"]["flags"])
        return result
    rr = up / abs(down)
    fs = max(0, min(100, 50 + growth * .5 + margin * .5 + fcfy - ps))
    es = max(0, min(100, 50 + (q["sma20"] > q["sma50"]) * 10 +
                    (q["volume_ratio20"] > 1) * 10 + q["relative_strength_20d_pct"] * 2 -
                    max(0, q["rsi_14"] - 55)))
    result.update(fundamental_score=round(fs, 2), entry_score=round(es, 2),
                  base_upside_pct=up, base_downside_pct=abs(down), reward_risk=round(rr, 2))
    passed = fs >= THRESHOLDS["buy_fundamental"] and es >= THRESHOLDS["buy_entry"] and up >= THRESHOLDS["buy_upside_pct"] and rr >= THRESHOLDS["buy_reward_risk"]
    result["decision_stage"] = "thresholds"
    result["signal"] = "BUY" if passed else "WATCH"
    result["buy_eligible"] = bool(passed)
    result["reasons"] = [] if passed else ["balanced_buy_thresholds_not_met"]
    return result
