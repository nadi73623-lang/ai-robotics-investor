import unittest
from emerging_markets import MARKETS, COMPANIES, build_emerging_markets_radar

class EmergingMarketsTests(unittest.TestCase):
    def test_eight_markets_present(self):
        self.assertEqual(len(MARKETS), 8)
        self.assertEqual(len({m["id"] for m in MARKETS}), 8)

    def test_unique_seed_identifiers(self):
        tickers = [row[0] for row in COMPANIES]
        self.assertEqual(len(tickers), len(set(tickers)))

    def test_radar_never_emits_buy(self):
        radar = build_emerging_markets_radar([{"title": "IonQ announces a contract", "url": "https://example.invalid"}])
        self.assertFalse(radar["buy_signals_enabled"])
        all_rows = [c for m in radar["markets"] for c in m["companies"]]
        self.assertTrue(all(c["investment_signal"] == "WATCHLIST_ONLY" for c in all_rows))
        ionq = next(c for c in all_rows if c["ticker"] == "IONQ")
        self.assertEqual(ionq["news_mentions"], 1)
        self.assertIsNone(ionq["fundamental_score"])

    def test_absent_news_does_not_mean_no_market(self):
        radar = build_emerging_markets_radar([])
        self.assertTrue(all(m["market_stage"] == "unassessed" for m in radar["markets"]))
        self.assertTrue(all(m["candidate_count"] > 0 for m in radar["markets"]))

if __name__ == "__main__":
    unittest.main()
