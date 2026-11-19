#!/usr/bin/env python3
"""Persistent, append-only decision memory for historical entry levels and BUY gates.

This module never invents missing prices or turns an entry-zone touch into a BUY.
Historical recommendations are immutable records; changes are appended as events.
"""
import json, hashlib
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

# Canonical issuer keys connect historical report names to primary listing symbols.
TICKER_ALIASES = {
    "6954.T": "FANUC", "FANUY": "FANUC",
    "6479.T": "MinebeaMitsumi",
}

def canonical_ticker(ticker):
    return TICKER_ALIASES.get(ticker, ticker)

def _now():
    return datetime.now(timezone.utc).isoformat()

# Prices recovered from earlier reports in this conversation. These are report
# records, not independently re-downloaded exchange data. Ambiguous currency/date
# attributions are intentionally excluded rather than guessed.
HISTORICAL_PRICE_REPORTS = [
    {"report_date":"2026-10-23","quote_date":"2026-10-21","prices":[
        ("AVGO",337.80,"USD"),("NVDA",221.97,"USD"),("MU",911.22,"USD"),
        ("ANET",184.33,"USD"),("ONDS",6.27,"USD")]},
    {"report_date":"2026-10-23","quote_date":"2026-10-22","prices":[
        ("BESI",157.25,"EUR"),("PWR",557.12,"USD"),("OUST",27.97,"USD"),("PDYN",3.64,"USD")]},
    {"report_date":"2026-10-24","quote_date":"2026-10-23","prices":[
        ("AVGO",321.68,"USD"),("NVDA",210.96,"USD"),("TSM",418.51,"USD"),
        ("MU",877.55,"USD"),("ANET",172.37,"USD"),("BESI",145.10,"EUR"),
        ("NOKIA",7.370,"EUR"),("VRT",194.32,"USD"),("ADBE",263.82,"USD"),
        ("OUST",29.69,"USD"),("PDYN",3.70,"USD"),("MP",38.30,"USD"),("XPEV",9.21,"USD")]},
    {"report_date":"2026-11-07","quote_date":"2026-11-06","prices":[
        ("AVGO",293.69,"USD"),("NVDA",186.64,"USD"),("MU",690.00,"USD"),
        ("ANET",170.80,"USD"),("OUST",34.75,"USD"),("MP",35.41,"USD"),
        ("PDYN",3.02,"USD"),("SNPS",450.46,"USD"),("RoboSense",15.00,"HKD")]},
    {"report_date":"2026-11-18","quote_date":"2026-11-17","prices":[
        ("AVGO",341.60,"USD"),("NVDA",155.46,"USD"),("AMD",503.41,"USD"),
        ("TSM",359.69,"USD"),("ASML",1236.80,"EUR"),("MRVL",148.74,"USD"),
        ("ANET",186.42,"USD"),("MU",712.42,"USD"),("SNPS",435.51,"USD"),
        ("OUST",30.48,"USD"),("MP",34.86,"USD"),("PDYN",2.87,"USD"),
        ("ONDS",4.39,"USD"),("ADBE",235.55,"USD"),("FANUC",5232.0,"JPY"),
        ("HSAI",12.59,"USD")]},
    {"report_date":"2026-11-19","quote_date":"2026-11-18","prices":[
        ("AVGO",354.05,"USD"),("NVDA",150.96,"USD"),("AMD",530.14,"USD"),
        ("TSM",362.62,"USD"),("ARM",182.76,"USD"),("MRVL",145.54,"USD"),
        ("ANET",193.94,"USD"),("MU",705.27,"USD"),("SNPS",434.01,"USD"),
        ("CDNS",305.82,"USD"),("Nabtesco",3356.0,"JPY"),("MinebeaMitsumi",2852.0,"JPY"),
        ("PDYN",2.86,"USD"),("ONDS",4.42,"USD"),("OUST",29.30,"USD"),
        ("XPEV",9.74,"USD"),("ADBE",226.20,"USD"),("UMAC",9.61,"USD"),
        ("Delta Electronics",1000.0,"TWD"),("nVent",110.35,"USD"),("VRT",194.48,"USD")]}
]

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
    # Keep accumulation zones, model-entry prices and technical observation
    # areas distinct. None of these historical records is a current BUY signal.
    extra_levels = [
        ("PWR","historical_reanalysis",500,520,"USD","2026-10-23","historical_reanalysis_zone"),
        ("AVGO","historical_watch",260,270,"USD","2026-10-24","historical_watch_zone"),
        ("NVDA","historical_watch",180,190,"USD","2026-10-24","historical_watch_zone"),
        ("BESI","historical_watch",125,135,"EUR","2026-10-24","historical_watch_zone"),
        ("AVGO","model_entry_20261108",246.60,246.60,"USD","2026-11-08","model_entry"),
        ("MU","model_entry_20261108",568,568,"USD","2026-11-08","model_entry"),
        ("ANET","model_entry_20261108",140.40,140.40,"USD","2026-11-08","model_entry"),
        ("COHR","model_entry_20261108",187.50,187.50,"USD","2026-11-08","model_entry"),
        ("VRT","model_entry_20261108",144.30,144.30,"USD","2026-11-08","model_entry"),
        ("OUST","model_entry_20261108",28.30,28.30,"USD","2026-11-08","model_entry"),
        ("PDYN","model_entry_20261108",2.46,2.46,"USD","2026-11-08","model_entry"),
        ("MinebeaMitsumi","historical_entry_20261112",2850,2900,"JPY","2026-11-12","historical_accumulation_zone"),
        ("AVGO","technical_observation_20261118",327.80,330.13,"USD","2026-11-18","technical_observation"),
        ("NVDA","technical_observation_20261118",148.80,150.33,"USD","2026-11-18","technical_observation"),
        ("VRT","technical_observation_20261118",183.94,188.67,"USD","2026-11-18","technical_observation"),
        ("FANUC","technical_observation_20261118",5185,5343,"JPY","2026-11-18","technical_observation"),
    ]
    for ticker, zone, lower, upper, currency, created, kind in extra_levels:
        levels.append({"id":f"history-{created}-{ticker}-{zone}","ticker":ticker,"zone":zone,
            "lower":lower,"upper":upper,"currency":currency,"unit":"per_share",
            "created_at":created,"status":"historical_plan","kind":kind,"immutable":True,
            "provenance":"Recovered from prior report in this conversation; not independently re-downloaded and not a current recommendation."})
    observations = []
    report_index = []
    for report in HISTORICAL_PRICE_REPORTS:
        report_index.append({"report_date":report["report_date"],"quote_date":report["quote_date"],
            "price_count":len(report["prices"]),"source":"prior ChatGPT report in this conversation",
            "verification":"historical report recovery; not independently exchange-verified"})
        for ticker, close, currency in report["prices"]:
            observations.append({"ticker":ticker,"date":report["quote_date"],"close":close,
                "close_native":close,"currency":currency,"source":"prior ChatGPT report in this conversation",
                "source_url":None,"observed_at":report["report_date"]+"T00:00:00Z",
                "price_type":"reported_price_snapshot","immutable":True,
                "verification":"historical report recovery; not independently exchange-verified"})
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
        "scan_snapshots": [],
        "historical_reports": report_index,
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
        "price_observations": observations,
        "historical_imports": HISTORICAL_HITS,
        "last_scan": None
    }

def load_memory(path=MEMORY_PATH):
    if not path.exists():
        return initial_memory()
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        data = initial_memory()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data
    data = json.loads(raw)
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported decision memory schema")
    # Backward-compatible schema-v1 migration: preserve all existing records.
    data.setdefault("entry_levels", [])
    data.setdefault("recommendations", [])
    data.setdefault("scan_snapshots", [])
    data.setdefault("historical_reports", [])
    data.setdefault("gate_audits", [])
    data.setdefault("events", [])
    data.setdefault("price_observations", [])
    data.setdefault("historical_imports", [])
    # Independently and idempotently backfill each history collection. A ledger
    # may already contain report metadata but still be missing quote rows or levels.
    bootstrap = initial_memory()
    existing_levels = {x.get("id") for x in data["entry_levels"]}
    data["entry_levels"].extend(x for x in bootstrap["entry_levels"] if x.get("id") not in existing_levels)
    existing_obs = {(x.get("ticker"),x.get("date"),x.get("close"),x.get("currency")) for x in data["price_observations"]}
    data["price_observations"].extend(x for x in bootstrap["price_observations"]
        if (x.get("ticker"),x.get("date"),x.get("close"),x.get("currency")) not in existing_obs)
    existing_reports = {(x.get("report_date"),x.get("quote_date")) for x in data["historical_reports"]}
    data["historical_reports"].extend(x for x in bootstrap["historical_reports"]
        if (x.get("report_date"),x.get("quote_date")) not in existing_reports)
    for key in ("entry_levels", "recommendations", "scan_snapshots", "historical_reports", "gate_audits", "events", "price_observations", "historical_imports"):
        if not isinstance(data.get(key), list):
            raise ValueError(f"Invalid decision memory field: {key}")
    # Idempotent migration for ledgers created by earlier repair commits:
    # expand combined intraday+close imports into two separately auditable events.
    existing = {(e.get("level_id"), e.get("date"), e.get("basis")) for e in data["events"]}
    if data["historical_imports"]:
        for h in HISTORICAL_HITS:
            bases = ["intraday_range", "close"] if h["basis"] == "intraday_low_and_close" else [h["basis"]]
            for basis in bases:
                key = ("legacy-20260911-"+h["ticker"]+"-"+h["zone"], h["date"], basis)
                if key in existing:
                    continue
                data["events"].append({
                    "type":"HISTORICAL_ENTRY_ZONE_HIT", "level_id":key[0],
                    "ticker":h["ticker"], "zone":h["zone"], "date":h["date"],
                    "intraday_low":h["low"], "close":h["close"], "basis":basis,
                    "currency":"USD", "source":h["source"],
                    "status":"HISTORICAL_HIT_REQUIRES_REVIEW_NOT_AUTOMATIC_BUY"
                })
                existing.add(key)
    return data


def append_scan_snapshot(scan_id, companies, path=MEMORY_PATH):
    """Persist exact scan inputs/results as an immutable, hash-checked record."""
    if not scan_id or not isinstance(companies, list):
        raise ValueError("Scan snapshot requires scan_id and company list")
    memory = load_memory(path)
    existing = next((x for x in memory["scan_snapshots"] if x.get("scan_id") == scan_id), None)
    if existing:
        return existing
    fields = ("ticker", "name", "sector", "price", "fundamentals", "valuation",
              "valuation_status", "attention_score", "investment_score",
              "buy_gate_diagnostics", "entry_zone_history", "price_history", "status")
    rows = [{k: company.get(k) for k in fields if k in company} for company in companies]
    payload = {"scan_id": scan_id, "companies": rows}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    record = {**payload, "sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
              "company_count": len(rows), "immutable": True, "recorded_at": _now()}
    memory["scan_snapshots"].append(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(memory, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    return record

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
        ticker = canonical_ticker(company.get("ticker"))
        quote = company.get("price") or {}
        # Entry levels are denominated in native listing currency. Never
        # compare a USD-converted fallback with a non-USD native level.
        currency = quote.get("currency")
        if not currency:
            if quote.get("close_native") is not None:
                continue
            currency = "USD"  # legacy USD-only provider payload
        close = quote.get("close_native")
        if close is None and currency == "USD":
            close = quote.get("close_usd")
        date = quote.get("date")
        if not ticker or close is None or not date:
            continue
        close = float(close)
        if not (0 < close < 10_000_000):
            raise ValueError(f"Invalid price for {ticker}")
        obs_key = (ticker, date, close)
        if obs_key not in observations:
            memory["price_observations"].append({
                "ticker": ticker, "date": date, "close": close, "close_native": close,
                "close_usd": quote.get("close_usd"),
                "low": quote.get("low_native") if currency != "USD" else (quote.get("low_native") if quote.get("low_native") is not None else quote.get("low_usd")),
                "high": quote.get("high_native") if currency != "USD" else (quote.get("high_native") if quote.get("high_native") is not None else quote.get("high_usd")),
                "currency": currency, "source": quote.get("source"),
                "source_url": quote.get("source_url"),
                "observed_at": generated_at, "price_type": "EOD_close"
            })
            observations.add(obs_key)
        for level in memory["entry_levels"]:
            if canonical_ticker(level["ticker"]) != ticker or level.get("status") == "cancelled":
                continue
            if level.get("currency") != currency:
                continue
            lower, upper = float(level["lower"]), float(level["upper"])
            low = quote.get("low_native")
            high = quote.get("high_native")
            if currency == "USD":
                if low is None: low = quote.get("low_usd")
                if high is None: high = quote.get("high_usd")
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
                           "quotes_seen": sum(1 for c in companies if (c.get("price") or {}).get("close_native", (c.get("price") or {}).get("close_usd")) is not None),
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
