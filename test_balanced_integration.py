import unittest
from balanced_strategy import THRESHOLDS, evaluate_company


class BalancedStrategyIntegrationTests(unittest.TestCase):
    def test_production_thresholds_match_approved_spec(self):
        self.assertEqual(THRESHOLDS["buy_fundamental"], 80)
        self.assertEqual(THRESHOLDS["buy_entry"], 70)
        self.assertEqual(THRESHOLDS["buy_upside_pct"], 20)
        self.assertEqual(THRESHOLDS["buy_reward_risk"], 1.7)
        self.assertEqual(THRESHOLDS["rsi_veto"], 75)

    def test_missing_consensus_blocks_buy(self):
        company = {
            "price_quality": "refreshed",
            "fundamentals_quality": "refreshed",
            "price": {"date": "2026-11-13"},
            "fundamentals": {"filed": "2026-11-10", "as_of": "2026-11-13T00:00:00+00:00"},
            "analyst_targets": {"status": "unavailable"},
        }
        result = evaluate_company(company)
        self.assertFalse(result["buy_eligible"])
        self.assertEqual(result["decision_stage"], "analyst_consensus")
        self.assertIn("documented_analyst_consensus_missing", result["reasons"])

    def test_cached_quote_cannot_become_buy(self):
        company = {
            "price_quality": "cached",
            "fundamentals_quality": "refreshed",
            "price": {"date": "2026-11-13"},
            "fundamentals": {"filed": "2026-11-10", "as_of": "2026-11-13T00:00:00+00:00"},
            "analyst_targets": {"status": "documented", "upside_median_pct": 30, "downside_low_pct": -10},
        }
        result = evaluate_company(company)
        self.assertFalse(result["buy_eligible"])
        self.assertEqual(result["decision_stage"], "data_gate")
        self.assertIn("quote_not_refreshed_this_run", result["reasons"])


if __name__ == "__main__":
    unittest.main()
