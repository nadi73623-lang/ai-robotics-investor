import unittest
from early_entry import build_early_entry

class EarlyEntryTests(unittest.TestCase):
    def company(self):
        return {"price":{"close_usd":99,"date":"2026-11-17"},
                "technical":{"sma20":100,"sma50":95,"rsi_14":52,
                             "volume_ratio20":1.0,"relative_strength_20d_pct":1.5}}
    def test_near_entry_is_watch_only(self):
        out=build_early_entry(self.company())
        self.assertTrue(out["near_entry"])
        self.assertEqual(out["status"],"near_entry")
    def test_too_far_below_sma20_is_not_near(self):
        c=self.company(); c["price"]["close_usd"]=95
        self.assertFalse(build_early_entry(c)["near_entry"])
    def test_overheated_rsi_is_not_near(self):
        c=self.company(); c["technical"]["rsi_14"]=65
        self.assertFalse(build_early_entry(c)["near_entry"])
    def test_weak_relative_strength_is_not_near(self):
        c=self.company(); c["technical"]["relative_strength_20d_pct"]=-0.2
        self.assertFalse(build_early_entry(c)["near_entry"])
    def test_missing_data_fails_closed(self):
        self.assertEqual(build_early_entry({"price":{}})["status"],"incomplete")

if __name__=="__main__": unittest.main()
