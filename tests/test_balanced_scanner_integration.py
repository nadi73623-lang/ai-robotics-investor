import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scanner
from balanced_strategy import VERSION


class BalancedScannerIntegrationTests(unittest.TestCase):
    def test_technical_indicators_are_dated_and_use_spy_excess_return(self):
        dates=[f"2026-09-{i:02d}" for i in range(1,51)]
        closes=[100.0+i for i in range(50)]
        volumes=[1000.0]*50
        benchmark=[100.0+i*0.5 for i in range(50)]
        result=scanner.technical_indicators(closes,volumes,dates,benchmark,dates)
        self.assertEqual(result["sma20_as_of"],dates[-1])
        self.assertEqual(result["sma50_as_of"],dates[-1])
        self.assertEqual(result["volume_as_of"],dates[-1])
        self.assertEqual(result["relative_strength_as_of"],dates[-1])
        self.assertEqual(result["relative_strength_benchmark"],"SPY")
        self.assertGreater(result["relative_strength_20d_pct"],0)
        self.assertIsNotNone(scanner.rsi_wilder(closes))

    def test_missing_benchmark_does_not_fabricate_relative_strength(self):
        dates=[f"2026-09-{i:02d}" for i in range(1,51)]
        closes=[100.0+i for i in range(50)]
        result=scanner.technical_indicators(closes,[1000.0]*50,dates)
        self.assertNotIn("relative_strength_20d_pct",result)

    def test_scan_integration_persists_per_company_fail_closed_decisions(self):
        day="2026-11-17"
        company={
            "ticker":"TEST","name":"Test Co","price_quality":"refreshed",
            "fundamentals_quality":"refreshed",
            "price":{"close_usd":100,"date":day,"rsi_14":50,"rsi_as_of":day,
                     "sma20":98,"sma50":95,"sma20_as_of":day,"sma50_as_of":day,
                     "above_sma20":True,"above_sma50":True,"volume_ratio20":1.2,
                     "volume_as_of":day,"relative_strength_20d_pct":3,
                     "relative_strength_as_of":day,"relative_strength_benchmark":"SPY"},
            "fundamentals":{"revenue_growth_pct":30,"net_margin_pct":10,
                            "filed":"2026-10-01","as_of":"2026-10-01"},
            "valuation":{"ps":3,"fcf_yield_pct":4},
            "investment_risk_flags":{"flags":[]}
        }
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(scanner,"ROOT",Path(tmp)):
                counts=scanner.evaluate_balanced_signals([company])
                ledger=Path(tmp)/"data"/"signal_rejections.json"
                self.assertTrue(ledger.is_file())
                import json
                saved=json.loads(ledger.read_text())
        self.assertEqual(company["investment_signal"]["strategy_version"],VERSION)
        self.assertFalse(company["investment_signal"]["buy_eligible"])
        self.assertEqual(company["investment_signal"]["decision_stage"],"analyst_consensus")
        self.assertFalse(saved["buy_signals_authorized"])
        self.assertEqual(saved["total"],1)
        self.assertEqual(counts["WATCH"],1)


if __name__ == "__main__":
    unittest.main()
