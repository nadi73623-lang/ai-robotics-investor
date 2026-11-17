"""Validated analyst-consensus import contract. No invented or scraped estimates.

Input CSV columns: ticker,listing,currency,as_of,provider,source_url,target_low,target_median,target_high,
price_at_consensus,downside_case_pct,upside_case_pct,prob_bear,prob_base,prob_bull,
bear_fair_value,base_fair_value,bull_fair_value
"""
from __future__ import annotations
import csv, math
from datetime import date
from scenario_valuation import scenario_valuation

REQUIRED={"ticker","listing","currency","as_of","provider","source_url","target_low","target_median","target_high",
          "price_at_consensus","downside_case_pct","upside_case_pct","prob_bear","prob_base",
          "prob_bull","bear_fair_value","base_fair_value","bull_fair_value"}

def _num(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError): return None

def validate_consensus(row, today=None, max_age_days=45):
    today=today or date.today()
    missing=sorted(REQUIRED-set(row))
    if missing: return {"status":"unavailable","reasons":["missing_fields:"+",".join(missing)]}
    try: asof=date.fromisoformat(str(row["as_of"]))
    except (ValueError,TypeError): return {"status":"invalid","reasons":["invalid_as_of"]}
    if (today-asof).days<0 or (today-asof).days>max_age_days:
        return {"status":"stale","reasons":["consensus_outside_freshness_window"]}
    nums={k:_num(row[k]) for k in REQUIRED-{"ticker","listing","currency","as_of","provider","source_url"}}
    if any(v is None for v in nums.values()):
        return {"status":"invalid","reasons":["non_numeric_or_non_finite_consensus_field"]}
    if not row["ticker"] or not row["listing"] or not str(row["currency"]).isalpha() or len(str(row["currency"]))!=3 or not row["provider"] or not str(row["source_url"]).startswith("https://"):
        return {"status":"invalid","reasons":["missing_identity_or_verifiable_source"]}
    low,med,high=(nums[k] for k in ("target_low","target_median","target_high"))
    price=nums["price_at_consensus"]
    probs=[nums[k] for k in ("prob_bear","prob_base","prob_bull")]
    fvs=[nums[k] for k in ("bear_fair_value","base_fair_value","bull_fair_value")]
    if not (0<low<=med<=high and price>0 and all(x>=0 for x in probs) and abs(sum(probs)-1)<1e-6 and all(x>0 for x in fvs)):
        return {"status":"invalid","reasons":["inconsistent_targets_probabilities_or_fair_values"]}
    scenario=scenario_valuation(price,fvs[0],fvs[1],fvs[2],probs[0],probs[1],probs[2])
    if scenario.get('status')!='calculated': return {'status':'invalid','reasons':['scenario_valuation_failed']}
    expected=scenario['probability_weighted_fair_value']
    ev_pct=scenario['probability_weighted_ev_pct']
    upside=(med/price-1)*100
    downside=(low/price-1)*100
    return {"status":"documented","ticker":row["ticker"],"as_of":asof.isoformat(),
            "provider":row["provider"],"source_url":row["source_url"],"listing":row["listing"],"currency":row["currency"],"price_at_consensus":price,
            "target_low":low,"target_median":med,"target_high":high,
            "upside_median_pct":round(upside,2),"downside_low_pct":round(downside,2),
            "probability_weighted_ev_pct":round(ev_pct,2),"expected_fair_value":round(expected,4),
            "probabilities":{"bear":probs[0],"base":probs[1],"bull":probs[2]},
            "scenario_fair_values":{"bear":fvs[0],"base":fvs[1],"bull":fvs[2]},
            "scenario_analysis":scenario}

def rebase_consensus_to_current_price(consensus, ticker, current_price, current_currency, current_listing):
    """Recalculate targets and scenario EV against the current same-listing quote."""
    if not isinstance(consensus, dict) or consensus.get("status") != "documented":
        return {**(consensus or {"status":"unavailable"}), "rebase_status":"blocked_consensus_not_documented"}
    if (str(consensus.get("ticker","")).upper() != str(ticker).upper()
        or consensus.get("listing") != current_listing
        or str(consensus.get("currency","")).upper() != str(current_currency).upper()):
        return {**consensus, "status":"invalid", "rebase_status":"listing_or_currency_mismatch"}
    try:
        price=float(current_price)
        if not math.isfinite(price) or price<=0: raise ValueError()
        low=float(consensus["target_low"]); med=float(consensus["target_median"])
        probs=consensus["probabilities"]; fvs=consensus["scenario_fair_values"]
        scenario=scenario_valuation(price,float(fvs["bear"]),float(fvs["base"]),float(fvs["bull"]),
            float(probs["bear"]),float(probs["base"]),float(probs["bull"]))
        if scenario.get("status")!="calculated": raise ValueError()
    except (KeyError,TypeError,ValueError,OverflowError):
        return {**consensus, "status":"invalid", "rebase_status":"invalid_current_quote_or_scenario"}
    return {**consensus, "current_price":price,
        "upside_median_pct":round((med/price-1)*100,2),
        "downside_low_pct":round((low/price-1)*100,2),
        "probability_weighted_ev_pct":scenario["probability_weighted_ev_pct"],
        "expected_fair_value":scenario["probability_weighted_fair_value"],
        "scenario_analysis":scenario, "rebase_status":"current_same_listing_quote"}

def load_consensus_csv(path, today=None):
    try:
        with open(path,newline="",encoding="utf-8-sig") as f: rows=list(csv.DictReader(f))
    except FileNotFoundError: return {}
    result={}
    for row in rows:
        item=validate_consensus(row,today)
        ticker=row.get("ticker","").strip().upper()
        if ticker: result[ticker]=item
    return result
