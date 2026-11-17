"""Explicit exchange-symbol and benchmark routing.

Yahoo symbols are identifiers only; currency is read from the provider response.
No implicit FX conversion is performed here.
"""
from __future__ import annotations

# Canonical company ticker -> Yahoo Finance symbol. Add entries only after
# confirming the listing and share class; never guess a suffix.
YAHOO_SYMBOLS = {
    "TSM":"TSM", "ASML":"ASML", "ARM":"ARM",
    "FANUY":"FANUY", "KUKAF":"KUKAF", "SIEGY":"SIEGY",
    "7203.T":"7203.T", "6758.T":"6758.T", "6861.T":"6861.T",
    "6954.T":"6954.T", "6501.T":"6501.T", "6506.T":"6506.T",
    "005930.KS":"005930.KS", "000660.KS":"000660.KS",
    "2330.TW":"2330.TW", "2454.TW":"2454.TW",
    "0700.HK":"0700.HK", "9988.HK":"9988.HK",
    "300124.SZ":"300124.SZ", "002050.SZ":"002050.SZ",
    "ABB":"ABB", "SPY":"SPY", "EWJ":"EWJ", "EWY":"EWY",
    "EWT":"EWT", "FXI":"FXI", "EWC":"EWC", "VGK":"VGK", "EWU":"EWU",
}

BENCHMARKS = {
    "USD":"SPY", "JPY":"EWJ", "KRW":"EWY", "TWD":"EWT",
    "HKD":"FXI", "CAD":"EWC", "EUR":"VGK", "GBP":"EWU",
}

def yahoo_symbol(ticker: str) -> str:
    value=(ticker or "").strip().upper()
    if value in YAHOO_SYMBOLS:
        return YAHOO_SYMBOLS[value]
    # Explicit exchange suffixes are accepted only for syntactically valid symbols.
    import re
    if re.fullmatch(r"[A-Z0-9]{1,12}(?:\.[A-Z]{1,4})?", value):
        return value
    raise ValueError("unmapped_or_invalid_market_symbol")

def benchmark_for_currency(currency: str) -> str | None:
    return BENCHMARKS.get((currency or "").upper())
