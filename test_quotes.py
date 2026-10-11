import unittest
from unittest.mock import patch
import scanner
class QuotesTest(unittest.TestCase):
 def test_reject_invalid_ticker(self):
  self.assertIsNone(scanner.stooq_quote('INVALID-TICKER'))
 def test_quote_missing(self):
  with patch.object(scanner,'stooq_quote',return_value=None):
   companies=[{'ticker':'AVGO'}]
   self.assertEqual(scanner.add_prices(companies,{}),0)
   self.assertIsNone(companies[0]['price'])
if __name__=='__main__':unittest.main()
