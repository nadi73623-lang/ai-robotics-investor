from pathlib import Path
import unittest


class ScannerRankingMetadataTests(unittest.TestCase):
    def test_attention_score_is_not_an_investment_ranking(self):
        source = (Path(__file__).resolve().parents[1] / "scanner.py").read_text(encoding="utf-8")
        self.assertIn("'investment_ranking_available':False", source)
        self.assertNotIn("'investment_ranking_available':True", source)
        self.assertIn("'ranking_method':'attention_score = 100*(1-exp(-mentions/4)); wskaźnik uwagi, NIE ocena inwestycyjna'", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
