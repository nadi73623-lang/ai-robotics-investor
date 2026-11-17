import unittest
from datetime import date
from event_risk import validate_event_rows

class EventRiskTests(unittest.TestCase):
    def row(self, **updates):
        row={"ticker":"XYZ","event_type":"earnings","event_date":"2026-11-20",
             "source_url":"https://issuer.example/events","as_of":"2026-11-17","status":"confirmed"}
        row.update(updates)
        return row
    def test_missing_feed_blocks(self):
        out=validate_event_rows(None,today=date(2026,11,17))
        self.assertEqual(out["status"],"unavailable")
    def test_empty_feed_blocks(self):
        out=validate_event_rows([],today=date(2026,11,17))
        self.assertEqual(out["status"],"unavailable")
        self.assertIn("event_feed_empty",out["flags"])
    def test_critical_event_is_flagged(self):
        out=validate_event_rows([self.row()],today=date(2026,11,17))
        self.assertIn("critical_event_within_horizon",out["flags"])
    def test_fresh_coverage_marker_is_recorded(self):
        marker=self.row(event_type="coverage_complete",event_date="2026-11-17",status="coverage")
        out=validate_event_rows([marker],today=date(2026,11,17))
        self.assertEqual(out["status"],"ok")
        self.assertEqual(out["covered_tickers"],["XYZ"])
    def test_no_coverage_markers_is_unavailable(self):
        out=validate_event_rows([self.row()],today=date(2026,11,17))
        self.assertEqual(out["status"],"unavailable")
        self.assertIn("event_feed_has_no_coverage_markers",out["flags"])
    def test_stale_feed_blocks(self):
        marker=self.row(event_type="coverage_complete",event_date="2026-11-17",status="coverage",as_of="2026-11-10")
        out=validate_event_rows([marker],today=date(2026,11,17))
        self.assertEqual(out["status"],"stale")
    def test_unverifiable_source_blocks(self):
        marker=self.row(event_type="coverage_complete",event_date="2026-11-17",status="coverage",source_url="http://bad")
        out=validate_event_rows([marker],today=date(2026,11,17))
        self.assertEqual(out["status"],"invalid")
    def test_unconfirmed_event_not_promoted(self):
        marker=self.row(event_type="coverage_complete",event_date="2026-11-17",status="coverage")
        tentative=self.row(status="rumor")
        out=validate_event_rows([marker,tentative],today=date(2026,11,17))
        self.assertEqual(out["status"],"ok")
        self.assertEqual(out["events"],[])

if __name__=="__main__": unittest.main()
