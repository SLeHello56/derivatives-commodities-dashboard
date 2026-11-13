# Derivatives & Commodities Dashboard

Python derivatives and commodities trading analytics: option pricing, numerical Greeks, Monte Carlo, synthetic commodity forward curves, contango/backwardation and scenario analysis. The dashboard is a desk-style educational prototype, not a live trading system.

## Run

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python examples/run_demo.py
streamlit run app.py
```

Synthetic market inputs are supplied for reproducibility. Optional external public historical series are for illustration, not an assertion of executable market quotes. See `src/` and `docs/CV_BULLETS.md`.
