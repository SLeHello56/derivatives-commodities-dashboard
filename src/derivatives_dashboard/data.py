"""Reproducible teaching-only data; not historical exchange quotations."""
import numpy as np
import pandas as pd


def synthetic_forward_curve(seed: int = 7, level: float = 43.0, slope: float = 0.42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    tenors = np.arange(1, 25)
    values = level + slope * tenors + 1.6 * np.sin(tenors / 2.5) + rng.normal(0, 0.25, len(tenors))
    return pd.DataFrame({"tenor_months": tenors, "forward_eur_mwh": np.round(values, 2)})
