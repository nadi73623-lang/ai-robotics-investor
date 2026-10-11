import unittest
from datetime import date
from scanner import calculate_valuation

class ValuationTests(unittest.TestCase):
    def setUp(self):
        self.c={'ticker':'AVGO','price':{'close_usd':100,'date':'2026-10-09'},'fundamentals':{'shares_outstanding':1000000,'shares_as_of':'2026-08-01','revenue_usd':20000000,'revenue_period_end':'2026-08-01','net_income_usd':5000000,'net_income_period_end':'2026-08-01','free_cash_flow_usd':3000000,'cash_flow_period_end':'2026-08-01','capex_period_end':'2026-08-01'}}
    def test_ratios(self):
        v=calculate_valuation(self.c,date(2026,10,11));self.assertEqual(v['market_cap_usd'],100000000);self.assertEqual(v['ps'],5);self.assertEqual(v['pe'],20);self.assertEqual(v['fcf_yield_pct'],3)
    def test_stale_quote(self):
        self.c['price']['date']='2026-09-01';self.assertEqual(calculate_valuation(self.c,date(2026,10,11))['status'],'unavailable')
    def test_missing_shares(self):
        del self.c['fundamentals']['shares_outstanding'];self.assertEqual(calculate_valuation(self.c,date(2026,10,11))['status'],'unavailable')
    def test_adr(self):
        self.c['ticker']='TSM';self.assertEqual(calculate_valuation(self.c,date(2026,10,11))['status'],'unavailable')
    def test_negative_income(self):
        self.c['fundamentals']['net_income_usd']=-1;self.assertIsNone(calculate_valuation(self.c,date(2026,10,11))['pe'])
    def test_mismatched_fcf_period(self):
        self.c['fundamentals']['capex_period_end']='2025-08-01';self.assertIsNone(calculate_valuation(self.c,date(2026,10,11))['fcf_yield_pct'])
if __name__=='__main__':unittest.main()
