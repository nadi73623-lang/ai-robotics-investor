import unittest
from datetime import date
from event_risk import validate_event_rows

class EventRiskTests(unittest.TestCase):
    def test_missing_feed_blocks(self):
        self.assertEqual(validate_event_rows(None,today=date(2026,11,16))["flags"],["event_feed_missing"])
    def test_near_earnings_flags(self):
        row={"ticker":"XYZ","event_type":"earnings","event_date":"2026-11-20","source_url":"https://issuer.example/ir","as_of":"2026-11-16","status":"confirmed"}
        out=validate_event_rows([row],today=date(2026,11,16))
        self.assertIn("critical_event_within_horizon",out["flags"])
    def test_stale_feed_blocks(self):
        row={"ticker":"XYZ","event_type":"earnings","event_date":"2026-11-20","source_url":"https://issuer.example/ir","as_of":"2026-11-01","status":"confirmed"}
        self.assertEqual(validate_event_rows([row],today=date(2026,11,16])["status"],"stale")

if __name__=="__main__": unittest.main()
