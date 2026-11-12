import json, tempfile, unittest
from pathlib import Path
from decision_memory import initial_memory, record_scan, append_recommendation, append_gate_audit

class DecisionMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"memory.json"
    def tearDown(self): self.tmp.cleanup()
    def test_legacy_levels_preserved(self):
        m=initial_memory()
        self.assertEqual(len(m["entry_levels"]),15)
        self.assertEqual({x["ticker"] for x in m["entry_levels"]},{"MU","ADBE","OUST","XPEV","MP"})
        self.assertTrue(all(x["immutable"] for x in m["entry_levels"]))
    def test_close_touch_creates_event_and_deduplicates(self):
        companies=[{"ticker":"MU","price":{"close_usd":725.11,"date":"2026-11-10","source":"test"}}]
        m,h=record_scan(companies,"2026-11-12T00:00:00Z",self.path)
        self.assertEqual(len(h),1)
        m,h=record_scan(companies,"2026-11-12T06:00:00Z",self.path)
        self.assertEqual(len(h),0)
        self.assertEqual(len(m["events"]),1)
    def test_no_price_does_not_create_zero(self):
        m,h=record_scan([{"ticker":"MU","price":None}],"scan",self.path)
        self.assertEqual(m["price_observations"],[])
        self.assertEqual(h,[])
    def test_recommendation_is_append_only(self):
        a=append_recommendation("MU","WATCH",725.11,"USD","2026-11-10",{"good":[850,900]},"test",self.path)
        b=append_recommendation("MU","BUY",700,"USD","2026-11-11",{"good":[700,800]},"new test",self.path)
        self.assertNotEqual(a["id"],b["id"])
        self.assertEqual(len(json.loads(self.path.read_text())["recommendations"]),2)
    def test_gate_audit_requires_explicit_states(self):
        with self.assertRaises(ValueError):
            append_gate_audit("MU","scan",{"R/R":{"status":"MAYBE"}},[],self.path)
        r=append_gate_audit("MU","scan",{"R/R":{"status":"FAIL","value":1.2}},["R/R < 1.7"],self.path)
        self.assertEqual(r["gates"]["R/R"]["status"],"FAIL")

if __name__=="__main__": unittest.main()
