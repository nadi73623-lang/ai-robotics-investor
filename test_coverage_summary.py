import unittest
from scanner import coverage_summary

class CoverageSummaryTests(unittest.TestCase):
    def test_reports_quality_and_decision_coverage(self):
        companies=[
            {"price_quality":"refreshed","fundamentals_quality":"cached","technical":{"status":"ok"},"valuation":{"status":"partial"},"analyst_targets":{"status":"unavailable"},"investment_decision":{"decision_stage":"analyst_consensus"}},
            {"price_quality":"cached","fundamentals_quality":"unavailable","technical":{"status":"incomplete"},"valuation":{"status":"unavailable"},"analyst_targets":{"status":"documented"},"investment_decision":{"decision_stage":"technical_inputs"}},
            {"price_quality":"unavailable","fundamentals_quality":"refreshed","technical":{"status":"ok"},"valuation":{"status":"invalid"},"analyst_targets":{"status":"stale"},"investment_decision":{"decision_stage":"data_gate"}},
        ]
        out=coverage_summary(companies,{"status":"unavailable"},{"USD":{}})
        self.assertEqual(out["universe_total"],3)
        self.assertEqual(out["price_quality"],{"refreshed":1,"cached":1,"unavailable":1})
        self.assertEqual(out["fundamentals_quality"],{"refreshed":1,"cached":1,"unavailable":1})
        self.assertEqual(out["technical"],{"ok":2,"incomplete":1})
        self.assertEqual(out["analyst_consensus"],{"documented":1,"stale":1,"invalid":0,"unavailable":1})
        self.assertEqual(out["event_feed_status"],"unavailable")
        self.assertEqual(out["benchmark_currencies"],["USD"])
        self.assertEqual(out["decision_stages"],{"analyst_consensus":1,"data_gate":1,"technical_inputs":1})
    def test_empty_universe(self):
        out=coverage_summary([])
        self.assertEqual(out["universe_total"],0)
        self.assertEqual(out["benchmark_currencies"],[])

if __name__=="__main__": unittest.main()
