"""Streamlit entry point: streamlit run app.py"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from derivatives_dashboard.analytics import black_scholes, asian_arithmetic_call_mc, curve_structure
from derivatives_dashboard.data import synthetic_forward_curve

st.set_page_config(page_title="Derivatives & Commodities", page_icon="📈", layout="wide")
st.title("Derivatives & Commodities Dashboard")
st.caption("Independent portfolio demo · Synthetic data by default · Not associated with IMC Trading")
options, curves = st.tabs(["Option pricing & Monte Carlo", "Commodities forward curve"])
with options:
    c1, c2, c3, c4 = st.columns(4)
    spot = c1.number_input("Spot (€)", 1.0, value=100.0)
    strike = c2.number_input("Strike (€)", 1.0, value=105.0)
    tenor = c3.number_input("Maturity (years)", 0.01, value=0.75)
    sigma_pct = c4.slider("Implied volatility (%)", 1, 100, 24)
    c5, c6, c7 = st.columns(3)
    rate_pct = c5.number_input("Risk-free rate (%)", value=2.5)
    div_pct = c6.number_input("Dividend yield (%)", value=0.0)
    kind = c7.selectbox("Option", ["call", "put"])
    result = black_scholes(spot, strike, tenor, rate_pct / 100, sigma_pct / 100, kind, div_pct / 100)
    a, b, c, d, e = st.columns(5)
    a.metric("Premium (€)", f"{result.price:.3f}")
    b.metric("Delta", f"{result.delta:.3f}")
    c.metric("Gamma", f"{result.gamma:.4f}")
    d.metric("Vega / vol pt", f"{result.vega / 100:.3f}")
    e.metric("Theta / day", f"{result.theta / 365:.3f}")
    strikes = [spot * (0.7 + 0.02 * i) for i in range(31)]
    vols = [10, 15, 20, 25, 30, 35, 40, 45, 50, 60]
    z = [[black_scholes(spot, k, tenor, rate_pct / 100, vol / 100, kind, div_pct / 100).price
          for k in strikes] for vol in vols]
    fig = go.Figure(go.Heatmap(x=strikes, y=vols, z=z, colorscale="Viridis", colorbar_title="€"))
    fig.update_layout(title="Black–Scholes premium sensitivity", xaxis_title="Strike (€)", yaxis_title="Volatility (%)")
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Arithmetic Asian call · Monte Carlo pricing"):
        mc_paths = st.slider("Simulated paths", 2000, 50000, 12000, 2000)
        estimate, ci_half = asian_arithmetic_call_mc(spot, strike, tenor, rate_pct / 100, sigma_pct / 100, paths=mc_paths)
        st.write(f"Price: **€{estimate:.3f}** · Approx. 95% confidence interval: **€{estimate-ci_half:.3f} to €{estimate+ci_half:.3f}**")
        st.caption("Averaging: 12 monthly-equidistant observations; risk-neutral GBM, fixed seed.")
with curves:
    st.info("Default curve is generated locally and is NOT ICE/EEX/Bloomberg market data.")
    upload = st.file_uploader("Optional: upload your CSV with tenor_months,forward_eur_mwh", type="csv")
    df = pd.read_csv(upload) if upload is not None else synthetic_forward_curve()
    try:
        term = curve_structure(df)
        fig = go.Figure(go.Scatter(x=term.tenor_months, y=term.forward_eur_mwh, mode="lines+markers"))
        fig.update_layout(title="Synthetic gas forward curve", xaxis_title="Tenor (months)", yaxis_title="Forward (€/MWh)")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(term, use_container_width=True, hide_index=True)
        st.download_button("Export classified forward curve", term.to_csv(index=False), "curve_analytics.csv", "text/csv")
    except (ValueError, KeyError) as exc:
        st.error(f"Input validation error: {exc}")

with st.expander("Optional real historical SPOT reference — not futures curve"):
    st.caption("FRED historical WTI / US Henry Hub spot reference data are NOT TTF forward prices and must not be used as a commodity tenor curve.")
    series = st.selectbox("FRED spot reference", ["oil_wti_spot_usd_bbl", "us_henry_hub_spot_usd_mmbtu"])
    if st.button("Load reference history (internet required)"):
        try:
            from derivatives_dashboard.historical import fetch_spot_reference
            hist=fetch_spot_reference(series)
            st.line_chart(hist.set_index("date")["spot_reference"])
            st.download_button("Download reference observations",hist.to_csv(index=False),"fred_spot_reference.csv")
        except Exception as exc:
            st.warning(f"Reference history unavailable: {exc}")
