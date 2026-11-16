import unittest
from scenario_valuation import scenario_valuation

class ScenarioTests(unittest.TestCase):
    def test_weighted_fair_value(self):
        out=scenario_valuation(100,70,110,150,.2,.6,.2)
        self.assertEqual(out["status"],"calculated")
        self.assertAlmostEqual(out["probability_weighted_fair_value"],110)
        self.assertTrue(out["positive_ev"])
    def test_probabilities_must_sum_to_one(self):
        self.assertEqual(scenario_valuation(100,70,110,150,.2,.5,.2)["status"],"invalid")
    def test_zero_prices_rejected(self):
        self.assertEqual(scenario_valuation(0,70,110,150,.2,.6,.2)["status"],"invalid")
    def test_negative_ev_reported(self):
        out=scenario_valuation(100,50,80,110,.5,.4,.1)
        self.assertFalse(out["positive_ev"])

if __name__=="__main__": unittest.main()
