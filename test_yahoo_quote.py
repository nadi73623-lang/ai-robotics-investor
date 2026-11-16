import unittest
from unittest.mock import patch
from scanner import yahoo_quote, QuoteError, technical_indicators

class YahooQuoteTests(unittest.TestCase):
    @patch("scanner.urllib.request.urlopen")
    def test_yahoo_uses_resolved_symbol_and_native_currency(self, open_url):
        class Response:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self,*args):
                return b'{"chart":{"result":[{"meta":{"currency":"JPY"},"timestamp":[1794787200],"indicators":{"quote":[{"close":[1234.5],"volume":[1000]}]}}],"error":null}}'
        open_url.return_value=Response()
        out=yahoo_quote("7203.T")
        self.assertEqual(out["market_symbol"],"7203.T")
        self.assertEqual(out["currency"],"JPY")
        self.assertEqual(out["bars"][0]["close"],1234.5)
        self.assertIn("7203.T",open_url.call_args.args[0].full_url)
    def test_invalid_ticker_rejected(self):
        with self.assertRaises(QuoteError): yahoo_quote("invalid ticker")
    def test_usd_relative_strength_needs_benchmark(self):
        quote={"bars":[{"date":f"2026-01-{i:02d}","close":100+i,"volume":100} for i in range(1,31)]}
        out=technical_indicators(quote,None)
        self.assertIsNone(out.get("relative_strength_20d_pct"))
    def test_non_us_benchmark_not_assumed(self):
        quote={"currency":"JPY","bars":[]}
        self.assertEqual(quote["currency"],"JPY")

if __name__=="__main__": unittest.main()
