"""Transparent Black-Scholes, Monte Carlo and term-structure analytics.

Educational pricing assumptions: European options, constant risk-free and dividend
rates, constant lognormal volatility, no transaction costs.
"""
from dataclasses import dataclass
from math import erf, exp, log, pi, sqrt
import numpy as np
import pandas as pd


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def norm_pdf(x: float) -> float:
    return exp(-0.5 * x * x) / sqrt(2.0 * pi)


@dataclass(frozen=True)
class OptionAnalytics:
    price: float
    delta: float
    gamma: float
    vega: float   # price change per 1.00 absolute volatility change
    theta: float  # price change per one calendar year, other inputs unchanged


def black_scholes(spot: float, strike: float, tenor: float, rate: float,
                  volatility: float, kind: str = "call", dividend_yield: float = 0.0) -> OptionAnalytics:
    """Price a European call/put and return spot Greeks under Black–Scholes.

    `tenor` in years, `rate`/`dividend_yield`/`volatility` in decimals (0.20 = 20%).
    """
    if spot <= 0 or strike <= 0 or tenor <= 0 or volatility <= 0:
        raise ValueError("spot, strike, tenor and volatility must be strictly positive")
    if kind not in {"call", "put"}:
        raise ValueError("kind must be 'call' or 'put'")
    d1 = (log(spot / strike) + (rate - dividend_yield + 0.5 * volatility**2) * tenor) / (volatility * sqrt(tenor))
    d2 = d1 - volatility * sqrt(tenor)
    dq = exp(-dividend_yield * tenor)
    dr = exp(-rate * tenor)
    gamma = dq * norm_pdf(d1) / (spot * volatility * sqrt(tenor))
    vega = spot * dq * norm_pdf(d1) * sqrt(tenor)
    common_theta = -(spot * dq * norm_pdf(d1) * volatility) / (2 * sqrt(tenor))
    if kind == "call":
        price = spot * dq * norm_cdf(d1) - strike * dr * norm_cdf(d2)
        delta = dq * norm_cdf(d1)
        theta = common_theta - rate * strike * dr * norm_cdf(d2) + dividend_yield * spot * dq * norm_cdf(d1)
    else:
        price = strike * dr * norm_cdf(-d2) - spot * dq * norm_cdf(-d1)
        delta = -dq * norm_cdf(-d1)
        theta = common_theta + rate * strike * dr * norm_cdf(-d2) - dividend_yield * spot * dq * norm_cdf(-d1)
    return OptionAnalytics(price, delta, gamma, vega, theta)


def asian_arithmetic_call_mc(spot: float, strike: float, tenor: float,
                             rate: float, volatility: float, observations: int = 12,
                             paths: int = 20000, seed: int = 42) -> tuple[float, float]:
    """Risk-neutral arithmetic-average Asian call with 95% CI half-width.

    Excludes the initial spot from the averaging schedule. No control variate.
    """
    if min(spot, strike, tenor, volatility) <= 0 or observations < 1 or paths < 2:
        raise ValueError("Check strictly positive inputs, observations >= 1 and paths >= 2")
    rng = np.random.default_rng(seed)
    dt = tenor / observations
    shocks = rng.standard_normal((paths, observations))
    log_steps = (rate - 0.5 * volatility**2) * dt + volatility * sqrt(dt) * shocks
    values = spot * np.exp(np.cumsum(log_steps, axis=1))
    payoffs = np.maximum(values.mean(axis=1) - strike, 0.0) * exp(-rate * tenor)
    return float(payoffs.mean()), float(1.96 * payoffs.std(ddof=1) / sqrt(paths))


def curve_structure(curve: pd.DataFrame) -> pd.DataFrame:
    """Categorize adjacent forward price changes as contango/backwardation/flat.

    Required columns: tenor_months, forward_eur_mwh. Adjacent absolute changes
    are not roll yields or investable P&L.
    """
    needed = {"tenor_months", "forward_eur_mwh"}
    if not needed.issubset(curve):
        raise ValueError(f"Required columns: {sorted(needed)}")
    data = curve.loc[:, ["tenor_months", "forward_eur_mwh"]].copy().sort_values("tenor_months")
    if data.empty or data.isna().any().any() or (data["tenor_months"] <= 0).any() or (data["forward_eur_mwh"] <= 0).any():
        raise ValueError("Nonempty curve with positive tenor/price and no missing values required")
    if data["tenor_months"].duplicated().any():
        raise ValueError("Tenors must be unique")
    data["change_eur_mwh"] = data["forward_eur_mwh"].diff()
    data["market_structure"] = np.select([data["change_eur_mwh"] > 0,
                                          data["change_eur_mwh"] < 0],
                                          ["Contango", "Backwardation"], default="Flat/First")
    return data.reset_index(drop=True)
