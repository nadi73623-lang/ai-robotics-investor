from pathlib import Path


def test_attention_score_is_not_an_investment_ranking():
    source = (Path(__file__).resolve().parents[1] / "scanner.py").read_text(encoding="utf-8")
    assert "'investment_ranking_available':False" in source
    assert "'investment_ranking_available':True" not in source
    assert "'ranking_method':'attention_score = 100*(1-exp(-mentions/4)); wskaźnik uwagi, NIE ocena inwestycyjna'" in source
