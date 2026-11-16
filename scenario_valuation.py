"""Bear/Base/Bull valuation arithmetic with explicit assumptions and EV gate."""
from __future__ import annotations
import math

def scenario_valuation(current_price, bear_fv, base_fv, bull_fv,
                       prob_bear, prob_base, prob_bull, bear_downside_pct=None):
    vals=(current_price,bear_fv,base_fv,bull_fv,prob_bear,prob_base,prob_bull)
    if any(type(x) not in (int,float) or not math.isfinite(x) for x in vals):
        return {"status":"invalid","reason":"non_numeric_or_non_finite_input"}
    if min(current_price,bear_fv,base_fv,bull_fv)<=0 or min(prob_bear,prob_base,prob_bull)<0:
        return {"status":"invalid","reason":"prices_must_be_positive_and_probabilities_nonnegative"}
    if abs(prob_bear+prob_base+prob_bull-1)>1e-6:
        return {"status":"invalid","reason":"scenario_probabilities_must_sum_to_one"}
    expected=prob_bear*bear_fv+prob_base*base_fv+prob_bull*bull_fv
    bear_return=(bear_fv/current_price-1)*100
    base_return=(base_fv/current_price-1)*100
    bull_return=(bull_fv/current_price-1)*100
    ev=(expected/current_price-1)*100
    risk=abs(bear_return if bear_downside_pct is None else bear_downside_pct)
    rr=base_return/risk if risk else None
    return {"status":"calculated","bear":{"fair_value":bear_fv,"return_pct":round(bear_return,2)},
            "base":{"fair_value":base_fv,"return_pct":round(base_return,2)},
            "bull":{"fair_value":bull_fv,"return_pct":round(bull_return,2)},
            "probabilities":{"bear":prob_bear,"base":prob_base,"bull":prob_bull},
            "probability_weighted_fair_value":round(expected,4),
            "probability_weighted_ev_pct":round(ev,2),"base_reward_risk":round(rr,2) if rr is not None else None,
            "positive_ev":ev>0}
