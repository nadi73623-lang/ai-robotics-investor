import unittest
from scanner import technical_indicators

class AtrTests(unittest.TestCase):
    def quote(self, include_range=True):
        bars=[]
        for i in range(60):
            close=100+i*0.2
            bar={"date":f"2026-01-{i+1:02d}","close":close,"volume":1000}
            if include_range:
                bar.update(high=close+1,low=close-1)
            bars.append(bar)
        return {"bars":bars}
    def test_real_high_low_produce_atr_and_levels(self):
        out=technical_indicators(self.quote())
        self.assertEqual(out["status"],"ok")
        self.assertGreater(out["atr_14"],0)
        self.assertIsNotNone(out["support_20d"])
        self.assertIsNotNone(out["resistance_20d"])
    def test_close_only_data_does_not_fabricate_atr(self):
        out=technical_indicators(self.quote(False))
        self.assertIsNone(out["atr_14"])
        self.assertEqual(out["atr_status"],"unavailable_high_low_missing")

if __name__=="__main__": unittest.main()
