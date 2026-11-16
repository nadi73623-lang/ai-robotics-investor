import unittest
from datetime import date
from analyst_consensus import validate_consensus

class ConsensusTests(unittest.TestCase):
    def row(self):
        return {"ticker":"XYZ","as_of":"2026-11-16","provider":"Test source","source_url":"https://issuer.example/consensus",
                "target_low":"80","target_median":"110","target_high":"130","price_at_consensus":"100",
                "downside_case_pct":"-20","upside_case_pct":"30","prob_bear":"0.2","prob_base":"0.6","prob_bull":"0.2",
                "bear_fair_value":"70","base_fair_value":"115","bull_fair_value":"150"}
    def test_valid_consensus_has_weighted_ev(self):
        out=validate_consensus(self.row(),today=date(2026,11,16))
        self.assertEqual(out["status"],"documented")
        self.assertAlmostEqual(out["expected_fair_value"],114)
        self.assertGreater(out["probability_weighted_ev_pct"],0)
        self.assertEqual(out["scenario_analysis"]["status"],"calculated")
    def test_stale_consensus_rejected(self):
        row=self.row(); row["as_of"]="2026-09-01"
        self.assertEqual(validate_consensus(row,today=date(2026,11,16))["status"],"stale")
    def test_probability_sum_rejected(self):
        row=self.row(); row["prob_bear"]="0.5"
        self.assertEqual(validate_consensus(row,today=date(2026,11,16))["status"],"invalid")
    def test_non_https_source_rejected(self):
        row=self.row(); row["source_url"]="http://bad.example"
        self.assertEqual(validate_consensus(row,today=date(2026,11,16))["status"],"invalid")

if __name__=="__main__": unittest.main()
