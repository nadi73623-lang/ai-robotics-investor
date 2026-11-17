"""Early-entry proximity monitor. Never emits a BUY recommendation."""
from __future__ import annotations
import math

def build_early_entry(company):
    quote=company.get("price") or {}
    tech=company.get("technical") or {}
    out={"status":"unavailable","near_entry":False,"distance_to_sma20_pct":None,
         "as_of":quote.get("date"),"checks":{},"reasons":[]}
    try:
        price=float(quote["close_usd"])
        sma20=float(tech["sma20"]); sma50=float(tech["sma50"])
        rsi=float(tech["rsi_14"]); volume=float(tech["volume_ratio20"])
        rs=float(tech["relative_strength_20d_pct"])
        vals=(price,sma20,sma50,rsi,volume,rs)
        if not all(math.isfinite(x) for x in vals) or min(price,sma20,sma50)<=0 or volume<0:
            raise ValueError()
    except (KeyError,TypeError,ValueError,OverflowError):
        out["status"]="incomplete"
        out["reasons"]=["price_or_required_technical_input_missing"]
        return out
    distance=(price/sma20-1)*100
    checks={
        "price_near_sma20":-3.0<=distance<=1.0,
        "positive_trend_structure":sma20>sma50,
        "rsi_not_overheated":40<=rsi<=60,
        "volume_not_collapsing":volume>=0.8,
        "relative_strength_positive":rs>0,
    }
    failed=[k for k,v in checks.items() if not v]
    near=not failed
    out.update(status="near_entry" if near else "not_near_entry",
               near_entry=near,distance_to_sma20_pct=round(distance,2),
               checks=checks,reasons=failed,
               definition="Watch-only: close within -3% to +1% of SMA20, SMA20>SMA50, RSI14 40-60, volume/20D >=0.8, 20D relative strength >0.")
    return out
