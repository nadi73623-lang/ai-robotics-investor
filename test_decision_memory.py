import json, tempfile, unittest
from pathlib import Path
from decision_memory import initial_memory, load_memory, record_scan, append_recommendation, append_gate_audit, append_scan_snapshot

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
        self.assertEqual(len(m["events"]),8)
        self.assertEqual(sum(x["basis"]=="intraday_range" for x in m["events"]),3)
    def test_close_touch_creates_event_and_deduplicates(self):
        seed=initial_memory()
        seed["events"]=[]
        seed["historical_imports"]=[]
        self.path.write_text(json.dumps(seed))
        companies=[{"ticker":"MU","price":{"close_usd":725.11,"low_usd":699.63,"high_usd":735.0,"date":"2026-11-10","source":"test"}}]
        m,h=record_scan(companies,"2026-11-12T00:00:00Z",self.path)
        self.assertEqual(len(h),2)
        m,h=record_scan(companies,"2026-11-12T06:00:00Z",self.path)
        self.assertEqual(len(h),0)
        self.assertEqual(len(m["events"]),2)
    def test_no_price_does_not_create_zero(self):
        m,h=record_scan([{"ticker":"MU","price":None}],"scan",self.path)
        self.assertEqual(m["price_observations"],[])
        self.assertEqual(h,[])
    def test_recommendation_is_append_only(self):
        a=append_recommendation("MU","WATCH",725.11,"USD","2026-11-10",{"good":[850,900]},"test",self.path)
        b=append_recommendation("MU","BUY",700,"USD","2026-11-11",{"good":[700,800]},"new test",self.path)
        self.assertNotEqual(a["id"],b["id"])
        self.assertEqual(len(json.loads(self.path.read_text())["recommendations"]),2)

    def test_scan_snapshot_is_immutable_and_hash_stable(self):
        companies=[{"ticker":"MU","price":{"close_usd":725.11,"date":"2026-11-10","currency":"USD"},"valuation":{"status":"partial","market_cap_usd":900}}]
        first=append_scan_snapshot("scan-1",companies,self.path)
        second=append_scan_snapshot("scan-1",[{"ticker":"MU"}],self.path)
        self.assertEqual(first["sha256"],second["sha256"])
        self.assertTrue(first["immutable"])
        self.assertEqual(first["company_count"],1)
        self.assertEqual(len(json.loads(self.path.read_text())["scan_snapshots"]),1)

    def test_snapshot_rejects_nonfinite_calculations(self):
        with self.assertRaises(ValueError):
            append_scan_snapshot("scan-nan",[{"ticker":"MU","valuation":{"pe":float("nan")}}],self.path)


    def test_historical_report_snapshots_and_levels_are_imported(self):
        m=initial_memory()
        self.assertGreaterEqual(len(m["historical_reports"]),5)
        self.assertGreaterEqual(len(m["price_observations"]),60)
        tickers={x["ticker"] for x in m["price_observations"]}
        self.assertTrue({"AVGO","MU","OUST","MP","FANUC","MinebeaMitsumi"}.issubset(tickers))
        levels={(x["ticker"],x.get("kind",x["zone"])) for x in m["entry_levels"]}
        self.assertIn(("FANUC","technical_observation"),levels)
        self.assertIn(("MinebeaMitsumi","historical_accumulation_zone"),levels)

    def test_empty_memory_file_bootstraps_without_json_error(self):
        self.path.write_text("",encoding="utf-8")
        m=load_memory(self.path)
        self.assertGreaterEqual(len(m["price_observations"]),60)
        self.assertTrue(json.loads(self.path.read_text(encoding="utf-8"))["historical_reports"])

    def test_native_currency_zone_touch_is_detected(self):
        m=initial_memory()
        self.path.write_text(json.dumps(m),encoding="utf-8")
        companies=[{"ticker":"FANUC","price":{"close_native":5200,"currency":"JPY",
            "low_native":5180,"high_native":5250,"date":"2026-11-20","source":"test"}}]
        updated,hits=record_scan(companies,"2026-11-20T08:00:00Z",self.path)
        self.assertTrue(any(x["ticker"]=="FANUC" and x["basis"]=="intraday_range" for x in hits))

    def test_gate_audit_requires_explicit_states(self):
        with self.assertRaises(ValueError):
            append_gate_audit("MU","scan",{"R/R":{"status":"MAYBE"}},[],self.path)
        r=append_gate_audit("MU","scan",{"R/R":{"status":"FAIL","value":1.2}},["R/R < 1.7"],self.path)
        self.assertEqual(r["gates"]["R/R"]["status"],"FAIL")

if __name__=="__main__": unittest.main()
