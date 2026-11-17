import unittest
from datetime import date
from balanced_strategy import evaluate_company

class BalancedStrategyFreshnessTests(unittest.TestCase):
    def candidate(self, currency="USD", benchmark="SPY"):
        return {
            "price":{"date":"2026-11-17","currency":currency,"rsi_14":60,
                     "sma20":110,"sma50":100,"volume_ratio20":1.2,
                     "relative_strength_20d_pct":10,"relative_strength_benchmark":benchmark},
            "fundamentals":{"source":"SEC EDGAR XBRL","filed":"2026-11-16",
                "revenue_growth_pct":40,"net_margin_pct":20},
            "valuation":{"ps":2,"fcf_yield_pct":6,"periods_aligned":True},
            "analyst_targets":{"status":"documented","upside_median_pct":25,
                "downside_low_pct":-10,"probability_weighted_ev_pct":12},
            "entry_trigger":{"active":True,"price":110},
            "investment_risk_flags":{"flags":[]}
        }
    def test_cached_but_current_eod_and_sec_filing_can_qualify(self):
        c=self.candidate()
        c["price_quality"]="cached"; c["fundamentals_quality"]="cached"
        out=evaluate_company(c,today=date(2026,11,17))
        self.assertEqual(out["signal"],"BUY")
        self.assertTrue(out["buy_eligible"])
    def test_stale_quote_is_blocked(self):
        c=self.candidate(); c["price"]["date"]="2026-11-10"
        out=evaluate_company(c,today=date(2026,11,17))
        self.assertIn("price_stale_or_future",out["reasons"])
        self.assertFalse(out["buy_eligible"])
    def test_stale_filing_is_blocked(self):
        c=self.candidate(); c["fundamentals"]["filed"]="2024-01-01"
        out=evaluate_company(c,today=date(2026,11,17))
        self.assertIn("fundamentals_missing_or_stale",out["reasons"])
        self.assertFalse(out["buy_eligible"])
    def test_jpy_listing_requires_jpy_benchmark(self):
        c=self.candidate("JPY","^N225")
        out=evaluate_company(c,today=date(2026,11,17))
        self.assertTrue(out["buy_eligible"])
    def test_wrong_currency_benchmark_is_blocked(self):
        c=self.candidate("JPY","SPY")
        out=evaluate_company(c,today=date(2026,11,17))
        self.assertIn("technical_inputs_or_benchmark_missing",out["reasons"])
        self.assertFalse(out["buy_eligible"])

if __name__=="__main__": unittest.main()
