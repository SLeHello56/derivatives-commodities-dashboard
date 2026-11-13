import math
import pandas as pd
import pytest
from derivatives_dashboard.analytics import black_scholes, asian_arithmetic_call_mc, curve_structure


def test_put_call_parity():
    c = black_scholes(100, 106, 0.8, 0.03, 0.2, "call", 0.01)
    p = black_scholes(100, 106, 0.8, 0.03, 0.2, "put", 0.01)
    theoretical = 100 * math.exp(-0.01 * 0.8) - 106 * math.exp(-0.03 * 0.8)
    assert c.price - p.price == pytest.approx(theoretical, abs=1e-9)


def test_vega_positive_and_put_delta_negative():
    assert black_scholes(100, 100, 1, 0.02, 0.2).vega > 0
    assert black_scholes(100, 100, 1, 0.02, 0.2, "put").delta < 0


def test_one_observation_asian_matches_european_within_mc_error():
    exact = black_scholes(100, 105, 1, 0.02, 0.25).price
    mc, ci = asian_arithmetic_call_mc(100, 105, 1, 0.02, 0.25, observations=1, paths=50000, seed=2)
    assert abs(mc - exact) < 3 * ci


def test_curve_structure():
    raw = pd.DataFrame({"tenor_months": [3, 1, 2], "forward_eur_mwh": [21., 20., 19.]})
    out = curve_structure(raw)
    assert out.market_structure.tolist() == ["Flat/First", "Backwardation", "Contango"]


def test_bad_input():
    with pytest.raises(ValueError):
        black_scholes(-1, 100, 1, .02, .2)
