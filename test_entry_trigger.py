import unittest
from entry_trigger import build_entry_trigger

class EntryTriggerTests(unittest.TestCase):
    def company(self):
        return {"price":{"close_usd":105,"date":"2026-11-17"},
                "technical":{"sma20":102,"sma50":98,"rsi_14":57,
                             "volume_ratio20":1.1,"relative_strength_20d_pct":2.5}}
    def test_trigger_activates_only_when_all_conditions_pass(self):
        out=build_entry_trigger(self.company())
        self.assertTrue(out["active"])
        self.assertEqual(out["status"],"active")
        self.assertEqual(out["price"],105)
    def test_overheated_rsi_blocks_trigger(self):
        c=self.company(); c["technical"]["rsi_14"]=72
        out=build_entry_trigger(c)
        self.assertFalse(out["active"])
        self.assertIn("rsi_entry_band",out["reasons"])
    def test_weak_relative_strength_blocks_trigger(self):
        c=self.company(); c["technical"]["relative_strength_20d_pct"]=-1
        self.assertFalse(build_entry_trigger(c)["active"])
    def test_missing_data_fails_closed(self):
        self.assertEqual(build_entry_trigger({"price":{}})["status"],"incomplete")
    def test_nan_fails_closed(self):
        c=self.company(); c["technical"]["rsi_14"]=float("nan")
        self.assertFalse(build_entry_trigger(c)["active"])

if __name__=="__main__": unittest.main()
