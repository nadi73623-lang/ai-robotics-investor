"""Point-in-time corporate-event risk gate. Missing or stale feeds block BUY."""
from __future__ import annotations
import csv
from datetime import date

REQUIRED={"ticker","event_type","event_date","source_url","as_of","status"}
CRITICAL={"earnings","guidance","share_issuance","merger_vote","regulatory","trial_result","lockup_expiry"}

def validate_event_rows(rows, today=None, max_age_days=2, horizon_days=14):
    today=today or date.today()
    if rows is None:
        return {"status":"unavailable","flags":["event_feed_missing"],"events":[]}
    if not rows:
        return {"status":"unavailable","flags":["event_feed_empty"],"events":[]}
    events=[]
    for row in rows:
        if not REQUIRED.issubset(row):
            return {"status":"invalid","flags":["event_feed_schema_invalid"],"events":[]}
        try:
            asof=date.fromisoformat(str(row["as_of"]))
            event_day=date.fromisoformat(str(row["event_date"]))
        except (TypeError,ValueError):
            return {"status":"invalid","flags":["event_date_invalid"],"events":[]}
        if (today-asof).days<0 or (today-asof).days>max_age_days:
            return {"status":"stale","flags":["event_feed_stale"],"events":[]}
        if not str(row["source_url"]).startswith("https://") or not row["ticker"] or not row["event_type"]:
            return {"status":"invalid","flags":["event_source_unverifiable"],"events":[]}
        if row["status"].lower() not in {"confirmed","scheduled"}:
            continue
        days=(event_day-today).days
        if 0<=days<=horizon_days and row["event_type"].lower() in CRITICAL:
            events.append({**row,"days_to_event":days})
    return {"status":"ok","flags":(["critical_event_within_horizon"] if events else []),"events":events}

def load_event_risk_csv(path, today=None):
    try:
        with open(path,newline="",encoding="utf-8-sig") as f:
            rows=list(csv.DictReader(f))
    except FileNotFoundError:
        return {"status":"unavailable","flags":["event_feed_missing"],"events":[]}
    return validate_event_rows(rows,today=today)
