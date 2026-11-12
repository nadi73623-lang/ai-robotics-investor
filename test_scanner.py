import unittest
import scanner
from scanner import latest_common_end
class Tests(unittest.TestCase):
 def test_alias(self):
  self.assertTrue(scanner.matches('Broadcom expands AI networking', 'AVGO','Broadcom'))
  self.assertFalse(scanner.matches('AI changes everything', 'AI','C3.ai'))
 def test_latest_common_end_requires_same_period(self):
  metrics={
   'revenue':[{'start':'2025-02-01','end':'2026-01-31','value':100},{'start':'2024-02-01','end':'2025-01-31','value':80}],
   'net_income':[{'start':'2024-02-01','end':'2025-01-31','value':8}],
   'cashflow':[{'start':'2025-02-01','end':'2026-01-31','value':20}],
  }
  end,values=latest_common_end(metrics,'revenue','net_income')
  self.assertEqual(end,{'start':'2024-02-01','end':'2025-01-31'})
  self.assertEqual(values,{'revenue':80,'net_income':8})
  end,values=latest_common_end(metrics,'revenue','cashflow')
  self.assertEqual(end,{'start':'2025-02-01','end':'2026-01-31'})
  self.assertEqual(values,{'revenue':100,'cashflow':20})
 def test_latest_common_end_no_match(self):
  end,values=latest_common_end({'a':[{'end':'2026-01-01','value':1}],'b':[{'end':'2025-01-01','value':2}]},'a','b')
  self.assertIsNone(end)
  self.assertIsNone(values)
 def test_universe(self):
  self.assertEqual(len(set(x[0] for x in scanner.UNIVERSE)),len(scanner.UNIVERSE))
if __name__=='__main__': unittest.main()

 def test_global_exchange_symbols_are_explicit(self):
  self.assertEqual(scanner.YAHOO_SYMBOLS['6479.T'],'6479.T')
  self.assertEqual(scanner.YAHOO_SYMBOLS['2498.HK'],'2498.HK')
  self.assertEqual(scanner.YAHOO_SYMBOLS['373220.KS'],'373220.KS')
 def test_fx_mappings_are_explicit(self):
  self.assertEqual(scanner.FX_SYMBOLS['JPY'],('JPY=X','inverse'))
  self.assertEqual(scanner.FX_SYMBOLS['EUR'],('EURUSD=X','direct'))
