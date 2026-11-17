import unittest
from datetime import date, timedelta
from scanner import technical_indicators

class TechnicalIndicatorTests(unittest.TestCase):
    def quote(self, closes):
        start=date(2026,1,1)
        return {"bars":[{"date":(start+timedelta(days=i)).isoformat(),"close":v,"volume":1000} for i,v in enumerate(closes)]}

    def test_rsi_is_100_for_monotonic_rise(self):
        out=technical_indicators(self.quote([100+i for i in range(60)]))
        self.assertEqual(out["status"],"ok")
        self.assertEqual(out["rsi_14"],100.0)

    def test_rsi_is_zero_for_monotonic_fall(self):
        out=technical_indicators(self.quote([200-i for i in range(60)]))
        self.assertEqual(out["status"],"ok")
        self.assertEqual(out["rsi_14"],0.0)

    def test_insufficient_bars_do_not_synthesize_indicators(self):
        out=technical_indicators(self.quote([100+i for i in range(49)]))
        self.assertEqual(out["status"],"incomplete")
        self.assertIsNone(out.get("rsi_14"))

if __name__=="__main__":
    unittest.main()
