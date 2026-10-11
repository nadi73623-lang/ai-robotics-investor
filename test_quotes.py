import unittest
from unittest.mock import patch
import scanner

class QuotesTest(unittest.TestCase):
 def test_bad_ticker(self):
  with self.assertRaises(scanner.QuoteError): scanner.stooq_quote('INVALID-TICKER')
 def test_missing_csv_header(self):
  class Resp:
   def __enter__(self): return self
   def __exit__(self,*args): pass
   def read(self,n): return b'No data'
  with patch.object(scanner.urllib.request,'urlopen',return_value=Resp()):
   with self.assertRaisesRegex(scanner.QuoteError,'missing Date/Close'): scanner.stooq_quote('AVGO')
 def test_fallback(self):
  companies=[{'ticker':'AVGO'}]
  q={'close_usd':100.0,'date':scanner.datetime.now(scanner.timezone.utc).date().isoformat(),'source':'Yahoo Finance chart EOD','source_url':'https://example.org','is_live':False}
  with patch.object(scanner,'stooq_quote',side_effect=scanner.QuoteError('missing Close')),patch.object(scanner,'yahoo_quote',return_value=q),patch.object(scanner.time,'sleep'):
   count,health=scanner.add_prices(companies,{})
  self.assertEqual(count,1)
  self.assertEqual(health['status'],'ok')
  self.assertEqual(companies[0]['price']['source'],'Yahoo Finance chart EOD')
 def test_both_fail(self):
  companies=[{'ticker':'AVGO'}]
  with patch.object(scanner,'stooq_quote',side_effect=scanner.QuoteError('bad CSV')),patch.object(scanner,'yahoo_quote',side_effect=scanner.QuoteError('blocked')),patch.object(scanner.time,'sleep'):
   count,health=scanner.add_prices(companies,{})
  self.assertEqual(count,0)
  self.assertEqual(health['status'],'unavailable')
  self.assertIsNone(companies[0]['price'])
if __name__=='__main__': unittest.main()
