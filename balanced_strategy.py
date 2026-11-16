"""Balanced 1.3 decision layer with auditable BUY gates.

Missing or stale evidence is a blocker, never a synthetic value. The evaluator
returns a research signal only; production publication remains separately gated.
"""
from __future__ import annotations
import math
from datetime import date

VERSION = "balanced-1.3-audit"
THRESHOLDS = {
    "strong_fundamental": 88, "strong_entry": 80, "strong_upside_pct": 20,
    "strong_reward_risk": 2.2, "buy_fundamental": 75, "buy_entry": 60,
    "buy_upside_pct": 15, "buy_reward_risk": 1.5,
    "early_fundamental": 68, "early_entry": 55,
    "early_upside_pct": 12, "early_reward_risk": 1.35, "rsi_veto": 75,
}

def _num(x):
    return type(x) in (int, float) and math.isfinite(x)

def _clamp(x):
    return max(0.0, min(100.0, float(x)))

def _score_company(company):
    f=company.get("fundamentals") or {}; v=company.get("valuation") or {}; q=company.get("price") or {}
    growth=f.get("revenue_growth_pct"); margin=f.get("net_margin_pct")
    ps=v.get("ps"); fcfy=v.get("fcf_yield_pct")
    missing=["missing_"+n for n,x in (("revenue_growth_pct",growth),("net_margin_pct",margin),("ps",ps),("fcf_yield_pct",fcfy)) if not _num(x)]
    if missing: return None,None,missing
    gs=_clamp(50+growth); ps_= _clamp(50+margin*2+(15 if fcfy>0 else -10))
    vs=_clamp(90-ps*5+max(-10,min(10,fcfy*2)))
    qs=_clamp(50+min(25,max(-25,margin))+(10 if fcfy>0 else -5))
    fundamental=round(.25*(gs+ps_+vs+qs),2)
    rsi=q.get("rsi_14")
    if not _num(rsi) or q.get("rsi_as_of")!=q.get("date"):
        return fundamental,None,["missing_or_stale_rsi_14"]
    fields=(("sma20","sma20_as_of"),("sma50","sma50_as_of"),("volume_ratio20","volume_as_of"),("relative_strength_20d_pct","relative_strength_as_of"))
    missing=[]
    for field,stamp in fields:
        if not _num(q.get(field)): missing.append("missing_current_"+field)
        elif q.get(stamp)!=q.get("date"): missing.append("stale_current_"+field)
    if missing: return fundamental,None,missing
    if q.get("relative_strength_benchmark")!="SPY": return fundamental,None,["missing_relative_strength_benchmark"]
    trend=100 if q.get("above_sma20") and q.get("above_sma50") else 65 if q.get("above_sma20") or q.get("above_sma50") else 25
    volume=_clamp(50+(q["volume_ratio20"]-1)*35)
    relative=_clamp(50+q["relative_strength_20d_pct"]*3)
    heat=100 if rsi<=55 else _clamp(100-(rsi-55)*3)
    return fundamental,round(.30*trend+.20*volume+.30*relative+.20*heat,2),[]

def _date_check(company):
    q=company.get("price") or {}; f=company.get("fundamentals") or {}
    try: qd=date.fromisoformat(q.get("date"))
    except (TypeError,ValueError): return ["invalid_quote_date"]
    problems=[]
    if not f.get("filed"): problems.append("missing_sec_filing_date")
    try:
        if f.get("as_of") and date.fromisoformat(str(f["as_of"])[:10])>date.today(): problems.append("sec_snapshot_after_today")
    except ValueError: problems.append("invalid_sec_snapshot_date")
    for field,stamp in (("rsi_14","rsi_as_of"),("sma20","sma20_as_of"),("sma50","sma50_as_of"),("volume_ratio20","volume_as_of"),("relative_strength_20d_pct","relative_strength_as_of")):
        if q.get(field) is not None and q.get(stamp)!=q.get("date"): problems.append(field+"_date_mismatch")
    for field in ("shares_as_of","revenue_period_end","net_income_period_end","cash_as_of","debt_as_of","cash_flow_period_end","capex_period_end","filed","shares_filed","revenue_filed","net_income_filed","cash_filed","debt_filed"):
        value=f.get(field)
        if value:
            try:
                if date.fromisoformat(str(value)[:10])>qd: problems.append(field+"_after_quote_date")
            except ValueError: problems.append(field+"_invalid_date")
    return problems

def _finish(result,stage,checks,reasons,**updates):
    result.update(updates); result["decision_stage"]=stage; result["decision_trace"]=checks; result["reasons"]=reasons
    return result

def evaluate_company(company):
    result={"strategy_version":VERSION,"signal":"WATCH","buy_eligible":False,"fundamental_score":None,"entry_score":None,
            "base_upside_pct":None,"base_downside_pct":None,"reward_risk":None,"decision_stage":"data_gate","decision_trace":[],"reasons":[]}
    trace=[]
    def check(stage,name,actual,operator,required,passed,reason):
        trace.append({"stage":stage,"check":name,"actual":actual,"operator":operator,"required":required,"passed":bool(passed),"reason":None if passed else reason})
    q=company.get("price") or {}; a=company.get("analyst_targets") or {}
    price_ok=company.get("price_quality")=="refreshed"; check("data_gate","price_quality",company.get("price_quality"),"==","refreshed",price_ok,"quote_not_refreshed_this_run")
    fund_ok=company.get("fundamentals_quality")=="refreshed"; check("data_gate","fundamentals_quality",company.get("fundamentals_quality"),"==","refreshed",fund_ok,"sec_not_refreshed_this_run")
    if not price_ok or not fund_ok: return _finish(result,"data_gate",trace,[x["reason"] for x in trace if not x["passed"]])
    errors=_date_check(company); check("date_integrity","quote_and_fundamental_dates",errors,"==",[],not errors,"evidence_date_mismatch_or_future_period")
    if errors: return _finish(result,"date_integrity",trace,errors)
    documented=a.get("status")=="documented"; check("analyst_consensus","consensus_status",a.get("status"),"==","documented",documented,"documented_analyst_consensus_missing")
    if not documented: return _finish(result,"analyst_consensus",trace,["documented_analyst_consensus_missing"])
    up=a.get("upside_median_pct"); low=a.get("downside_low_pct")
    valid=_num(up) and _num(low) and up>0 and low<0
    check("analyst_consensus","median_upside_and_low_target",{"upside_median_pct":up,"downside_low_pct":low},"upside>0 and downside<0","positive upside and defined downside",valid,"invalid_analyst_upside_or_downside")
    if not valid: return _finish(result,"analyst_consensus",trace,["invalid_analyst_upside_or_downside"])
    down=abs(low); rr=up/down
    fs,es,missing=_score_company(company)
    if missing:
        for reason in missing: check("score_inputs",reason,None,"present","valid same-session value",False,reason)
        return _finish(result,"score_inputs",trace,missing,base_upside_pct=up,base_downside_pct=down,reward_risk=round(rr,2))
    es=round(.65*es+.15*_clamp(rr*40)+.20*_clamp(up*2),2)
    result.update(fundamental_score=fs,entry_score=es,base_upside_pct=up,base_downside_pct=down,reward_risk=round(rr,2))
    flags=(company.get("investment_risk_flags") or {}).get("flags") or []
    check("risk_veto","investment_risk_flags",flags,"==",[],not bool(flags),"risk_flags_present")
    if flags: return _finish(result,"risk_veto",trace,["risk_flags_present"])
    rsi=q.get("rsi_14"); check("technical_veto","rsi_14",rsi,"<",THRESHOLDS["rsi_veto"],_num(rsi) and rsi<THRESHOLDS["rsi_veto"],"overbought_no_chase")
    if not _num(rsi) or rsi>=THRESHOLDS["rsi_veto"]: return _finish(result,"technical_veto",trace,["overbought_no_chase"])
    strong=[("strong_fundamental",fs,THRESHOLDS["strong_fundamental"]),("strong_entry",es,THRESHOLDS["strong_entry"]),("strong_upside_pct",up,THRESHOLDS["strong_upside_pct"]),("strong_reward_risk",rr,THRESHOLDS["strong_reward_risk"])]
    for n,x,t in strong: check("signal_thresholds",n,x,">=",t,x>=t,n+"_not_met")
    if all(x>=t for _,x,t in strong): return _finish(result,"approved",trace,["strong_thresholds_met"],signal="STRONG BUY",buy_eligible=True)
    buy=[("buy_fundamental",fs,THRESHOLDS["buy_fundamental"]),("buy_entry",es,THRESHOLDS["buy_entry"]),("buy_upside_pct",up,THRESHOLDS["buy_upside_pct"]),("buy_reward_risk",rr,THRESHOLDS["buy_reward_risk"])]
    for n,x,t in buy: check("signal_thresholds",n,x,">=",t,x>=t,n+"_not_met")
    if all(x>=t for _,x,t in buy): return _finish(result,"approved",trace,["balanced_thresholds_met"],signal="BUY",buy_eligible=True)
    early=[("early_fundamental",fs,THRESHOLDS["early_fundamental"]),("early_entry",es,THRESHOLDS["early_entry"]),("early_upside_pct",up,THRESHOLDS["early_upside_pct"]),("early_reward_risk",rr,THRESHOLDS["early_reward_risk"])]
    for n,x,t in early: check("signal_thresholds",n,x,">=",t,x>=t,n+"_not_met")
    if all(x>=t for _,x,t in early): return _finish(result,"early_setup",trace,["early_setup_requires_manual_confirmation"],signal="EARLY BUY",buy_eligible=True)
    if fs<55: return _finish(result,"fundamental_floor",trace,["fundamental_score_below_floor"],signal="LOW PRIORITY")
    failed=[x["reason"] for x in trace if x["stage"]=="signal_thresholds" and not x["passed"]]
    return _finish(result,"signal_thresholds",trace,failed or ["balanced_thresholds_not_met"])
