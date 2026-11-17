"""Risk geometry from real OHLC-derived ATR; levels are technical scenarios, not forecasts."""
from __future__ import annotations
import math

def build_risk_plan(company):
    quote=company.get("price") or {}
    tech=company.get("technical") or {}
    out={"status":"unavailable","entry_reference":None,"stop_loss":None,
         "target_1_2r":None,"target_2_3r":None,"risk_per_share":None,
         "reward_risk_1":None,"reward_risk_2":None,"method":"ATR14 risk geometry; targets are 2R/3R scenarios, not analyst targets."}
    try:
        entry=float(quote["close_usd"]); atr=float(tech["atr_14"])
        if not all(math.isfinite(x) for x in (entry,atr)) or entry<=0 or atr<=0:
            raise ValueError()
    except (KeyError,TypeError,ValueError,OverflowError):
        out["reason"]="fresh_price_or_real_ohlc_atr14_missing"
        return out
    stop=entry-1.5*atr
    risk=entry-stop
    if stop<=0 or risk<=0:
        out["reason"]="invalid_stop_geometry"
        return out
    out.update(status="scenario_only",entry_reference=round(entry,4),
               stop_loss=round(stop,4),target_1_2r=round(entry+2*risk,4),
               target_2_3r=round(entry+3*risk,4),risk_per_share=round(risk,4),
               reward_risk_1=2.0,reward_risk_2=3.0,
               atr14=round(atr,4),atr_pct=round(atr/entry*100,2))
    resistance=tech.get("resistance_20d")
    if isinstance(resistance,(int,float)) and math.isfinite(float(resistance)):
        out["resistance_20d"]=round(float(resistance),4)
        out["target_1_below_resistance"]=bool(float(resistance)>=entry+2*risk)
    return out
