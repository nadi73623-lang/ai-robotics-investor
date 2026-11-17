"""Point-in-time corporate-event risk gate. Missing, stale or uncovered tickers block BUY."""
from __future__ import annotations
import csv
from datetime import date

REQUIRED={"ticker","event_type","event_date","source_url","as_of","status"}
CRITICAL={"earnings","guidance","share_issuance","merger_vote","regulatory","trial_result","lockup_expiry"}

def validate_event_rows(rows, today=None, max_age_days=2, horizon_days=14):
    today=today or date.today()
    if rows is None:
        return {"status":"unavailable","flags":["event_feed_missing"],"events":[],"covered_tickers":[]}
    if not rows:
        return {"status":"unavailable","flags":["event_feed_empty"],"events":[],"covered_tickers":[]}
    events=[]; covered=set()
    for row in rows:
        if not REQUIRED.issubset(row):
            return {"status":"invalid","flags":["event_feed_schema_invalid"],"events":[],"covered_tickers":[]}
        try:
            asof=date.fromisoformat(str(row["as_of"]))
            event_day=date.fromisoformat(str(row["event_date"]))
        except (TypeError,ValueError):
            return {"status":"invalid","flags":["event_date_invalid"],"events":[],"covered_tickers":[]}
        if (today-asof).days<0 or (today-asof).days>max_age_days:
            return {"status":"stale","flags":["event_feed_stale"],"events":[],"covered_tickers":[]}
        if not str(row["source_url"]).startswith("https://") or not row["ticker"] or not row["event_type"]:
            return {"status":"invalid","flags":["event_source_unverifiable"],"events":[],"covered_tickers":[]}
        ticker=str(row["ticker"]).strip().upper()
        status=str(row["status"]).strip().lower()
        event_type=str(row["event_type"]).strip().lower()
        if status=="coverage":
            if event_type!="coverage_complete":
                return {"status":"invalid","flags":["event_coverage_marker_invalid"],"events":[],"covered_tickers":[]}
            covered.add(ticker)
            continue
        if status not in {"confirmed","scheduled"}:
            continue
        days=(event_day-today).days
        if 0<=days<=horizon_days and event_type in CRITICAL:
            events.append({**row,"ticker":ticker,"days_to_event":days})
    if not covered:
        return {"status":"unavailable","flags":["event_feed_has_no_coverage_markers"],"events":events,"covered_tickers":[]}
    return {"status":"ok","flags":(["critical_event_within_horizon"] if events else []),
            "events":events,"covered_tickers":sorted(covered)}

def load_event_risk_csv(path, today=None):
    try:
        with open(path,newline="",encoding="utf-8-sig") as f:
            rows=list(csv.DictReader(f))
    except FileNotFoundError:
        return {"status":"unavailable","flags":["event_feed_missing"],"events":[],"covered_tickers":[]}
    return validate_event_rows(rows,today=today)
