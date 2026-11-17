"""Risk geometry from genuine OHLC-derived ATR; levels are scenarios, not forecasts."""
from __future__ import annotations
import math
from datetime import date

def build_risk_plan(company, today=None, max_quote_age_days=7):
    quote=company.get("price") or {}
    tech=company.get("technical") or {}
    currency=str(quote.get("currency") or quote.get("native_currency") or "USD").upper()
    out={"status":"unavailable","entry_reference":None,"currency":currency,
         "stop_loss":None,"target_1_2r":None,"target_2_3r":None,
         "risk_per_share":None,"reward_risk_1":None,"reward_risk_2":None,
         "method":"ATR14 risk geometry; targets are 2R/3R scenarios, not analyst targets."}
    today=today or date.today()
    try:
        entry_value=quote.get("close_usd")
        if entry_value is None:
            entry_value=quote.get("native_close")
        entry=float(entry_value); atr=float(tech["atr_14"])
        quote_day=date.fromisoformat(str(quote["date"]))
        age=(today-quote_day).days
        if age<0 or age>max_quote_age_days:
            raise ValueError("stale_or_future_quote")
        if not all(math.isfinite(x) for x in (entry,atr)) or entry<=0 or atr<=0:
            raise ValueError("invalid_price_or_atr")
    except (KeyError,TypeError,ValueError,OverflowError) as exc:
        out["reason"]=str(exc) or "fresh_price_or_real_ohlc_atr14_missing"
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
               atr14=round(atr,4),atr_pct=round(atr/entry*100,2),
               quote_date=quote_day.isoformat(),quote_age_days=age)
    resistance=tech.get("resistance_20d")
    if isinstance(resistance,(int,float)) and math.isfinite(float(resistance)):
        out["resistance_20d"]=round(float(resistance),4)
        out["target_1_below_resistance"]=bool(float(resistance)>=entry+2*risk)
    return out
