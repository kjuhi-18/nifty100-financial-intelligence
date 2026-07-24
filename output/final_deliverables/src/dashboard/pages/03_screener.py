import pandas as pd
import streamlit as st
from utils.db import *

st.title("📊 Financial Screener")
# ==========================================================
# Screener Presets
# ==========================================================

PRESETS = {
    "Custom": {},
    "Quality": {
        "roe": 15.0,
        "de": 1.0,
        "fcf": 0.0,
        "rev": 10.0,
        "pat": 10.0,
        "opm": 10.0,
        "pe": 100.0,
        "pb": 20.0,
        "div": 0.0,
        "icr": 3.0,
    },
    "Value": {
        "roe": 0.0,
        "de": 2.0,
        "fcf": -999999.0,
        "rev": -50.0,
        "pat": -50.0,
        "opm": 0.0,
        "pe": 20.0,
        "pb": 3.0,
        "div": 1.0,
        "icr": 0.0,
    },
    "Growth": {
        "roe": 0.0,
        "de": 2.0,
        "fcf": -999999.0,
        "rev": 15.0,
        "pat": 20.0,
        "opm": 0.0,
        "pe": 100.0,
        "pb": 20.0,
        "div": 0.0,
        "icr": 0.0,
    },
    "Dividend": {
        "roe": 0.0,
        "de": 10.0,
        "fcf": 0.0,
        "rev": -50.0,
        "pat": -50.0,
        "opm": 0.0,
        "pe": 100.0,
        "pb": 20.0,
        "div": 2.0,
        "icr": 0.0,
    },
    "Debt-Free": {
        "roe": 12.0,
        "de": 0.0,
        "fcf": 0.0,
        "rev": 0.0,
        "pat": 0.0,
        "opm": 0.0,
        "pe": 100.0,
        "pb": 20.0,
        "div": 0.0,
        "icr": 0.0,
    },
    "Turnaround": {
        "roe": 0.0,
        "de": 2.0,
        "fcf": 0.0,
        "rev": 10.0,
        "pat": 0.0,
        "opm": 0.0,
        "pe": 100.0,
        "pb": 20.0,
        "div": 0.0,
        "icr": 0.0,
    },
}
# ==========================================================
# Load Data
# ==========================================================

conn = get_connection()

query = """
SELECT
    fr.*,
    c.company_name,
    s.broad_sector
FROM financial_ratios fr
LEFT JOIN companies c
    ON fr.company_id = c.id
LEFT JOIN sectors s
    ON fr.company_id = s.company_id
"""

df = pd.read_sql(query, conn)

conn.close()

# ==========================================================
# Sidebar Filters
# ==========================================================

st.sidebar.header("Screening Filters")

preset = st.sidebar.selectbox("Preset", list(PRESETS.keys()))

preset_values = PRESETS[preset]

roe_min = st.sidebar.slider(
    "ROE Minimum (%)", 0.0, 100.0, preset_values.get("roe", 15.0)
)

de_max = st.sidebar.slider(
    "Debt / Equity Maximum", 0.0, 10.0, preset_values.get("de", 2.0)
)

fcf_min = st.sidebar.number_input(
    "Minimum Free Cash Flow", value=preset_values.get("fcf", 0.0)
)

rev_min = st.sidebar.slider(
    "Revenue CAGR (%)", -50.0, 100.0, preset_values.get("rev", 0.0)
)

pat_min = st.sidebar.slider("PAT CAGR (%)", -50.0, 100.0, preset_values.get("pat", 0.0))

opm_min = st.sidebar.slider(
    "Operating Margin (%)", -20.0, 100.0, preset_values.get("opm", 0.0)
)

pe_max = st.sidebar.slider("P/E Maximum", 0.0, 100.0, preset_values.get("pe", 100.0))

pb_max = st.sidebar.slider("P/B Maximum", 0.0, 20.0, preset_values.get("pb", 20.0))

dividend_min = st.sidebar.slider(
    "Dividend Yield (%)", 0.0, 20.0, preset_values.get("div", 0.0)
)

icr_min = st.sidebar.slider(
    "Interest Coverage", 0.0, 100.0, preset_values.get("icr", 0.0)
)
# ==========================================================
# Apply Filters
# ==========================================================

filtered = df.copy()

filtered = filtered[(filtered["return_on_equity_pct"] >= roe_min)]

filtered = filtered[(filtered["debt_to_equity"] <= de_max)]

filtered = filtered[(filtered["free_cash_flow_cr"] >= fcf_min)]

filtered = filtered[(filtered["revenue_cagr_5yr"] >= rev_min)]

filtered = filtered[(filtered["pat_cagr_5yr"] >= pat_min)]

filtered = filtered[(filtered["operating_profit_margin_pct"] >= opm_min)]

# Only apply these if the columns exist
if "price_to_earnings" in filtered.columns:
    filtered = filtered[filtered["price_to_earnings"] <= pe_max]

if "price_to_book" in filtered.columns:
    filtered = filtered[filtered["price_to_book"] <= pb_max]

if "dividend_yield" in filtered.columns:
    filtered = filtered[filtered["dividend_yield"] >= dividend_min]

filtered = filtered[filtered["interest_coverage"] >= icr_min]

# ==========================================================
# Sort Results
# ==========================================================

filtered = filtered.sort_values(by="composite_quality_score", ascending=False)

# ==========================================================
# Result Count
# ==========================================================

st.markdown("---")

st.subheader("📋 Screening Results")

st.metric("Matching Companies", len(filtered))

# ==========================================================
# Display Columns
# ==========================================================

display_columns = [
    "company_id",
    "company_name",
    "broad_sector",
    "composite_quality_score",
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "debt_to_equity",
    "operating_profit_margin_pct",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "free_cash_flow_cr",
    "interest_coverage",
]

# Keep only columns that actually exist
display_columns = [col for col in display_columns if col in filtered.columns]

st.dataframe(filtered[display_columns], use_container_width=True, hide_index=True)
# ==========================================================
# CSV Download
# ==========================================================

st.markdown("---")

csv = filtered[display_columns].to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Screener Results (CSV)",
    data=csv,
    file_name="screener_results.csv",
    mime="text/csv",
)

st.caption(f"Exporting {len(filtered)} companies with {len(display_columns)} columns.")
