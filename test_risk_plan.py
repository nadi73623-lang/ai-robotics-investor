import unittest
from datetime import date
from risk_plan import build_risk_plan

class RiskPlanTests(unittest.TestCase):
    def test_builds_atr_risk_geometry(self):
        c={"price":{"close_usd":100,"currency":"USD","date":"2026-11-17"},"technical":{"atr_14":2.0,"resistance_20d":108}}
        out=build_risk_plan(c,today=date(2026,11,17))
        self.assertEqual(out["status"],"scenario_only")
        self.assertEqual(out["stop_loss"],97.0)
        self.assertEqual(out["target_1_2r"],106.0)
        self.assertEqual(out["target_2_3r"],109.0)
        self.assertEqual(out["reward_risk_1"],2.0)
        self.assertFalse(out["target_1_below_resistance"])
    def test_non_usd_uses_native_price_and_labels_currency(self):
        c={"price":{"close_usd":None,"native_close":2500,"native_currency":"JPY","currency":"JPY","date":"2026-11-17"},"technical":{"atr_14":50}}
        out=build_risk_plan(c,today=date(2026,11,17))
        self.assertEqual(out["status"],"scenario_only")
        self.assertEqual(out["entry_reference"],2500)
        self.assertEqual(out["currency"],"JPY")
        self.assertEqual(out["stop_loss"],2425)
    def test_stale_quote_fails_closed(self):
        c={"price":{"close_usd":100,"date":"2026-11-01"},"technical":{"atr_14":2}}
        self.assertEqual(build_risk_plan(c,today=date(2026,11,17))["status"],"unavailable")
    def test_missing_atr_fails_closed(self):
        out=build_risk_plan({"price":{"close_usd":100,"date":"2026-11-17"},"technical":{}},today=date(2026,11,17))
        self.assertEqual(out["status"],"unavailable")
    def test_invalid_atr_fails_closed(self):
        out=build_risk_plan({"price":{"close_usd":100,"date":"2026-11-17"},"technical":{"atr_14":0}},today=date(2026,11,17))
        self.assertEqual(out["status"],"unavailable")

if __name__=="__main__": unittest.main()
