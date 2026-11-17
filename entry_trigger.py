"""Deterministic technical entry trigger; no synthetic OHLC/ATR or price targets."""
from __future__ import annotations
import math

def build_entry_trigger(company):
    quote=company.get("price") or {}
    tech=company.get("technical") or {}
    result={"active":False,"status":"unavailable","type":"trend_pullback_confirmation",
            "price":None,"as_of":quote.get("date"),"checks":{},"reasons":[]}
    try:
        price=float(quote["close_usd"])
        sma20=float(tech["sma20"]); sma50=float(tech["sma50"])
        rsi=float(tech["rsi_14"]); volume=float(tech["volume_ratio20"])
        rs=float(tech["relative_strength_20d_pct"])
        values=(price,sma20,sma50,rsi,volume,rs)
        if not all(math.isfinite(x) for x in values) or min(price,sma20,sma50)<=0 or volume<0:
            raise ValueError()
    except (KeyError,TypeError,ValueError,OverflowError):
        result["status"]="incomplete"
        result["reasons"]=["price_or_required_technical_input_missing"]
        return result
    checks={
        "price_above_sma20":price>=sma20,
        "sma20_above_sma50":sma20>sma50,
        "rsi_entry_band":45<=rsi<=68,
        "volume_not_collapsing":volume>=0.8,
        "relative_strength_positive":rs>0,
    }
    result.update(price=round(price,6),checks=checks)
    failed=[name for name,passed in checks.items() if not passed]
    result["active"]=not failed
    result["status"]="active" if not failed else "inactive"
    result["reasons"]=failed
    result["definition"]="EOD confirmation: close >= SMA20 > SMA50, RSI14 45-68, volume/20D >= 0.8, 20D relative strength > 0."
    return result
