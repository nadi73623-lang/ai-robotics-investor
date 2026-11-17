import unittest
from risk_plan import build_risk_plan

class RiskPlanTests(unittest.TestCase):
    def test_builds_atr_risk_geometry(self):
        c={"price":{"close_usd":100},"technical":{"atr_14":2.0,"resistance_20d":108}}
        out=build_risk_plan(c)
        self.assertEqual(out["status"],"scenario_only")
        self.assertEqual(out["stop_loss"],97.0)
        self.assertEqual(out["target_1_2r"],106.0)
        self.assertEqual(out["target_2_3r"],109.0)
        self.assertEqual(out["reward_risk_1"],2.0)
        self.assertFalse(out["target_1_below_resistance"])
    def test_missing_atr_fails_closed(self):
        out=build_risk_plan({"price":{"close_usd":100},"technical":{}})
        self.assertEqual(out["status"],"unavailable")
    def test_invalid_atr_fails_closed(self):
        out=build_risk_plan({"price":{"close_usd":100},"technical":{"atr_14":0}})
        self.assertEqual(out["status"],"unavailable")

if __name__=="__main__": unittest.main()
