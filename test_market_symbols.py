import unittest
from market_symbols import yahoo_symbol, benchmark_for_currency

class MarketSymbolTests(unittest.TestCase):
    def test_us_symbol(self):
        self.assertEqual(yahoo_symbol("NVDA"),"NVDA")
    def test_japan_suffix(self):
        self.assertEqual(yahoo_symbol("7203.T"),"7203.T")
    def test_taiwan_symbol(self):
        self.assertEqual(yahoo_symbol("2330.TW"),"2330.TW")
    def test_invalid_symbol_rejected(self):
        for symbol in ("bad symbol", "7203..T", "7203.TW.extra", "ABC/DEF"):
            with self.subTest(symbol=symbol):
                with self.assertRaises(ValueError): yahoo_symbol(symbol)
    def test_currency_benchmarks(self):
        self.assertEqual(benchmark_for_currency("JPY"),"EWJ")
        self.assertIsNone(benchmark_for_currency("XYZ"))

if __name__=="__main__": unittest.main()
