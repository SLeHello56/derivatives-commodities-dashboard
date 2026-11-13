from derivatives_dashboard.analytics import black_scholes, asian_arithmetic_call_mc, curve_structure
from derivatives_dashboard.data import synthetic_forward_curve

if __name__ == "__main__":
    call = black_scholes(100, 105, 0.75, 0.025, 0.24, "call")
    mc_price, half_width = asian_arithmetic_call_mc(100, 105, 0.75, 0.025, 0.24, paths=5000)
    print(f"European call: {call.price:.4f}; delta={call.delta:.4f}; vega per vol pt={call.vega/100:.4f}")
    print(f"Asian call Monte Carlo: {mc_price:.4f} +/- {half_width:.4f} (95% CI approx.)")
    print(curve_structure(synthetic_forward_curve()).head(6).to_string(index=False))
