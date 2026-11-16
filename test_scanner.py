import unittest
from unittest.mock import patch
import scanner
from scanner import latest_common_end


class ScannerTests(unittest.TestCase):
    def test_alias(self):
        self.assertTrue(scanner.matches("Broadcom expands AI networking", "AVGO", "Broadcom"))
        self.assertFalse(scanner.matches("AI changes everything", "AI", "C3.ai"))

    def test_unique_universe(self):
        tickers = [row[0] for row in scanner.UNIVERSE]
        self.assertEqual(len(tickers), len(set(tickers)))

    def test_latest_common_period(self):
        metrics = {
            "revenue": [
                {"start":"2025-01-01","end":"2025-12-31","value":100},
                {"start":"2024-01-01","end":"2024-12-31","value":80},
            ],
            "net_income": [{"start":"2024-01-01","end":"2024-12-31","value":8}],
        }
        period, values = latest_common_end(metrics, "revenue", "net_income")
        self.assertEqual(period, {"start":"2024-01-01","end":"2024-12-31"})
        self.assertEqual(values, {"revenue":80,"net_income":8})

    def test_no_common_period(self):
        period, values = latest_common_end({
            "a":[{"start":"2025-01-01","end":"2025-12-31","value":1}],
            "b":[{"start":"2024-01-01","end":"2024-12-31","value":2}],
        }, "a", "b")
        self.assertIsNone(period)
        self.assertIsNone(values)

    def test_technical_requires_50_valid_bars(self):
        self.assertEqual(scanner.technical_indicators({"bars":[]})["status"], "incomplete")
        bars=[]
        for i in range(50):
            bars.append({"date":f"2026-01-{(i%28)+1:02d}","close":100+i,"volume":1000})
        self.assertEqual(scanner.technical_indicators({"bars":bars})["status"], "ok")

    def test_technical_indicators_are_deterministic(self):
        bars=[{"date":f"2026-01-{(i%28)+1:02d}","close":100+i,"volume":1000+i} for i in range(50)]
        result=scanner.technical_indicators({"bars":bars})
        self.assertEqual(result["sma20"], sum(130+i for i in range(20))/20)
        self.assertEqual(result["sma50"], sum(100+i for i in range(50))/50)

if __name__ == "__main__":
    unittest.main()
