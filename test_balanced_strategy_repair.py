import hashlib
import unittest
from pathlib import Path
from balanced_strategy import VERSION, evaluate_company

class RepairBranchTests(unittest.TestCase):
    def company(self):
        d="2026-11-05"
        return {
            "price_quality":"refreshed","fundamentals_quality":"refreshed",
            "price":{"close_usd":100,"currency":"USD","date":d,"rsi_14":54,"rsi_as_of":d,
                "sma20":98,"sma50":95,"sma20_as_of":d,"sma50_as_of":d,
                "above_sma20":True,"above_sma50":True,"volume_ratio20":1.4,"volume_as_of":d,
                "relative_strength_20d_pct":5,"relative_strength_as_of":d,"relative_strength_benchmark":"SPY"},
            "analyst_targets":{"status":"documented","upside_median_pct":20,"downside_low_pct":-10},
            "fundamentals":{"revenue_growth_pct":35,"net_margin_pct":12,"filed":"2026-10-01","as_of":"2026-11-04"},
            "valuation":{"ps":3,"pe":18,"fcf_yield_pct":4},
            "investment_risk_flags":{"flags":[]}}

    def test_strategy_version_and_reachable_buy(self):
        self.assertEqual(VERSION,"balanced-1.3-audit")
        result=evaluate_company(self.company())
        self.assertEqual(result["signal"],"BUY")
        self.assertTrue(result["buy_eligible"])
        self.assertTrue(result["decision_trace"])

    def test_missing_consensus_fails_closed(self):
        c=self.company(); c["analyst_targets"]={"status":"unavailable"}
        result=evaluate_company(c)
        self.assertFalse(result["buy_eligible"])
        self.assertEqual(result["decision_stage"],"analyst_consensus")

    def test_stale_price_fails_closed(self):
        c=self.company(); c["price_quality"]="cached_recent"
        self.assertFalse(evaluate_company(c)["buy_eligible"])

    def test_preserved_main_scanner_baseline_hash(self):
        p=Path("baseline/main-2026-11-09/scanner.py")
        self.assertTrue(p.is_file())
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),
                         "9aa7ddda22d48b200a1c0f95c38b529d6eb7cc3e")

if __name__=="__main__":
    unittest.main()
