#!/usr/bin/env python3
"""Persistent, append-only decision memory for historical entry levels and BUY gates.

This module never invents missing prices or turns an entry-zone touch into a BUY.
Historical recommendations are immutable records; changes are appended as events.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MEMORY_PATH = ROOT / "data" / "decision_memory.json"

# Historical levels recovered from the 2026-09-11 project analysis.
# Values are USD/share. They are historical plans, NOT current recommendations.
INITIAL_LEVELS = {
    "MU": {"good": [850, 900], "very_good": [700, 800], "exceptional": [0, 650]},
    "ADBE": {"good": [230, 240], "very_good": [205, 220], "exceptional": [0, 190]},
    "OUST": {"good": [27, 30], "very_good": [22, 25], "exceptional": [0, 20]},
    "XPEV": {"good": [8.50, 9.50], "very_good": [7, 8], "exceptional": [0, 6]},
    "MP": {"good": [40, 44], "very_good": [33, 37], "exceptional": [0, 30]},
}
# Independently recorded historical daily observations from the 2026-11-12 audit.
# "low" is an intraday low; "close" is a session close. These are explicitly
# provenance-tagged imports, not reconstructed OHLCV or live quote data.
HISTORICAL_HITS = [
    {"ticker":"MU","date":"2026-11-10","low":699.63,"close":725.11,"zone":"very_good","basis":"intraday_low_and_close","source":"historical quote audit 2026-11-12"},
    {"ticker":"ADBE","date":"2026-11-11","low":None,"close":237.60,"zone":"good","basis":"close","source":"historical quote audit 2026-11-12"},
    {"ticker":"OUST","date":"2026-11-05","low":28.16,"close":30.52,"zone":"good","basis":"intraday_low","source":"historical quote audit 2026-11-12"},
    {"ticker":"XPEV","date":"2026-10-30","low":8.94,"close":9.04,"zone":"good","basis":"intraday_low_and_close","source":"historical quote audit 2026-11-12"},
    {"ticker":"MP","date":"2026-11-05","low":31.90,"close":33.74,"zone":"very_good","basis":"intraday_low_and_close","source":"historical quote audit 2026-11-12"},
]

def _now():
    return datetime.now(timezone.utc).isoformat()

def initial_memory():
    levels = []
    for ticker, zones in INITIAL_LEVELS.items():
        for zone, bounds in zones.items():
            levels.append({
                "id": f"legacy-20260911-{ticker}-{zone}",
                "ticker": ticker, "zone": zone,
                "lower": bounds[0], "upper": bounds[1],
                "currency": "USD", "unit": "per_share",
                "created_at": "2026-09-11",
                "status": "historical_plan",
                "immutable": True,
                "provenance": "Recovered from prior project analysis dated 2026-09-11; not a current recommendation."
            })
    return {
        "schema_version": 1,
        "created_at": _now(),
        "policy": {
            "append_only": True,
            "never_overwrite_prior_levels": True,
            "entry_touch_is_not_BUY": True,
            "missing_data_is_ND_not_zero": True,
            "all_prices_require_currency_and_timestamp": True,
            "all_BUY_decisions_require_gate_audit": True
        },
        "entry_levels": levels,
        "recommendations": [],
        "gate_audits": [],
        "events": [
            {"type":"HISTORICAL_ENTRY_ZONE_HIT", "level_id":"legacy-20260911-"+h["ticker"]+"-"+h["zone"],
             "ticker":h["ticker"], "zone":h["zone"], "date":h["date"],
             "intraday_low":h["low"], "close":h["close"], "basis":basis,
             "currency":"USD", "source":h["source"],
             "status":"HISTORICAL_HIT_REQUIRES_REVIEW_NOT_AUTOMATIC_BUY"}
            for h in HISTORICAL_HITS
            for basis in (["intraday_range","close"] if h["basis"]=="intraday_low_and_close" else [h["basis"]])
        ],
        "price_observations": [],
        "historical_imports": HISTORICAL_HITS,
        "last_scan": None
    }

def load_memory(path=MEMORY_PATH):
    if not path.exists():
        return initial_memory()
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported decision memory schema")
    for key in ("entry_levels", "recommendations", "gate_audits", "events", "price_observations", "historical_imports"):
        if not isinstance(data.get(key), list):
            raise ValueError(f"Invalid decision memory field: {key}")
    return data

def _in_zone(price, lower, upper):
    return lower <= price <= upper

def record_scan(companies, generated_at=None, path=MEMORY_PATH):
    """Persist current quotes, detect entry-zone touches, and produce a gate audit stub."""
    memory = load_memory(path)
    generated_at = generated_at or _now()
    observations = {(x.get("ticker"), x.get("date"), x.get("close")) for x in memory["price_observations"]}
    events = {(x.get("level_id"), x.get("date"), x.get("basis")) for x in memory["events"]}
    gate_by_ticker = {x.get("ticker"): x for x in memory["gate_audits"] if x.get("scan_id") == generated_at}
    hits = []
    for company in companies:
        ticker = company.get("ticker")
        quote = company.get("price") or {}
        close = quote.get("close_usd")
        date = quote.get("date")
        currency = quote.get("currency") or "USD"
        if not ticker or close is None or not date:
            continue
        close = float(close)
        if not (0 < close < 10_000_000):
            raise ValueError(f"Invalid price for {ticker}")
        obs_key = (ticker, date, close)
        if obs_key not in observations:
            memory["price_observations"].append({
                "ticker": ticker, "date": date, "close": close,
                "low": quote.get("low_usd"), "high": quote.get("high_usd"),
                "currency": currency, "source": quote.get("source"),
                "source_url": quote.get("source_url"),
                "observed_at": generated_at, "price_type": "EOD_close"
            })
            observations.add(obs_key)
        for level in memory["entry_levels"]:
            if level["ticker"] != ticker or level.get("status") == "cancelled":
                continue
            if level.get("currency") != currency:
                continue
            lower, upper = float(level["lower"]), float(level["upper"])
            low, high = quote.get("low_usd"), quote.get("high_usd")
            touched_intraday = low is not None and high is not None and float(low) <= upper and float(high) >= lower
            touched_close = _in_zone(close, lower, upper)
            for basis, touched, observed_price in (
                ("intraday_range", touched_intraday, float(low) if low is not None else None),
                ("close", touched_close, close)
            ):
                if touched:
                    key = (level["id"], date, basis)
                    if key not in events:
                        event = {
                            "type": "ENTRY_ZONE_TOUCHED", "level_id": level["id"],
                            "ticker": ticker, "zone": level["zone"], "date": date,
                            "price": observed_price, "intraday_low": low, "intraday_high": high,
                            "close": close, "basis": basis, "currency": currency,
                            "detected_at": generated_at,
                            "status": "REQUIRES_FRESH_FUNDAMENTAL_AND_TECHNICAL_REVIEW"
                        }
                        memory["events"].append(event); hits.append(event); events.add(key)
        # Never infer a BUY from price alone. A separate complete gate audit is required.
    memory["last_scan"] = {"generated_at": generated_at, "companies_seen": len(companies),
                           "quotes_seen": sum(1 for c in companies if (c.get("price") or {}).get("close_usd") is not None),
                           "zone_hits": len(hits)}
    memory["updated_at"] = generated_at
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")
    return memory, hits

def append_recommendation(ticker, recommendation, price, currency, as_of, zones, rationale, path=MEMORY_PATH):
    """Append a frozen recommendation; corrections must be new events, never edits."""
    if recommendation not in {"BUY", "STRONG_BUY", "SPEC_BUY", "WATCH", "ACCUMULATION_CANDIDATE", "AVOID"}:
        raise ValueError("Unknown recommendation")
    if not ticker or not currency or not as_of or price is None:
        raise ValueError("Recommendation requires ticker, price, currency and timestamp")
    memory = load_memory(path)
    record = {"id": f"{ticker}-{as_of}-{len(memory['recommendations'])+1}",
              "ticker": ticker, "recommendation": recommendation, "price": float(price),
              "currency": currency, "as_of": as_of, "entry_zones": zones,
              "rationale": rationale, "immutable": True}
    memory["recommendations"].append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")
    return record

def append_gate_audit(ticker, scan_id, gates, blockers, path=MEMORY_PATH):
    """Persist every BUY gate, including pass/fail/ND, and explicit blocker values."""
    if not ticker or not scan_id or not isinstance(gates, dict):
        raise ValueError("Gate audit requires ticker, scan_id and gate map")
    for name, result in gates.items():
        if not isinstance(result, dict) or result.get("status") not in {"PASS", "FAIL", "ND", "VETO"}:
            raise ValueError(f"Invalid gate result: {name}")
    memory = load_memory(path)
    record = {"ticker": ticker, "scan_id": scan_id, "gates": gates,
              "blockers": blockers or [], "recorded_at": _now(), "immutable": True}
    memory["gate_audits"].append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")
    return record
