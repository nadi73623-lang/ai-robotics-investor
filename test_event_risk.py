import unittest
from datetime import date
from event_risk import validate_event_rows

class EventRiskTests(unittest.TestCase):
    def row(self, **overrides):
        row={"ticker":"XYZ","event_type":"earnings","event_date":"2026-11-20",
             "source_url":"https://issuer.example/events","as_of":"2026-11-17","status":"confirmed"}
        row.update(overrides)
        return row

    def test_missing_feed_blocks(self):
        out=validate_event_rows(None,today=date(2026,11,17))
        self.assertEqual(out["status"],"unavailable")
        self.assertIn("event_feed_missing",out["flags"])

    def test_fresh_critical_event_is_flagged(self):
        out=validate_event_rows([self.row()],today=date(2026,11,17))
        self.assertEqual(out["status"],"ok")
        self.assertIn("critical_event_within_horizon",out["flags"])
        self.assertEqual(out["events"][0]["days_to_event"],3)

    def test_stale_feed_rejected(self):
        out=validate_event_rows([self.row(as_of="2026-11-10")],today=date(2026,11,17))
        self.assertEqual(out["status"],"stale")
        self.assertIn("event_feed_stale",out["flags"])

    def test_unverifiable_source_rejected(self):
        out=validate_event_rows([self.row(source_url="http://issuer.example/events")],today=date(2026,11,17))
        self.assertEqual(out["status"],"invalid")

    def test_unconfirmed_event_not_used_as_veto(self):
        out=validate_event_rows([self.row(status="rumour")],today=date(2026,11,17))
        self.assertEqual(out["status"],"ok")
        self.assertEqual(out["events"],[])

if __name__=="__main__":
    unittest.main()
