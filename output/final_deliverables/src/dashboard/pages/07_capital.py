import pandas as pd
import plotly.express as px
import streamlit as st
from utils.db import *

st.title("💰 Capital Allocation Map")

# ==========================================================
# Load Data
# ==========================================================

conn = get_connection()

query = """
SELECT
    fr.company_id,
    c.company_name,
    fr.return_on_equity_pct,
    fr.debt_to_equity,
    fr.free_cash_flow_cr,
    fr.revenue_cagr_5yr,
    fr.pat_cagr_5yr,
    fr.dividend_payout_ratio_pct,
    fr.capex_cr
FROM financial_ratios fr
LEFT JOIN companies c
ON fr.company_id = c.id
"""

df = pd.read_sql(query, conn)

conn.close()

# ==========================================================
# Capital Allocation Pattern
# ==========================================================


def classify(row):

    if row["debt_to_equity"] <= 0.30 and row["free_cash_flow_cr"] > 0:
        return "Debt Free Compounders"

    elif row["capex_cr"] > row["free_cash_flow_cr"]:
        return "Heavy Capex"

    elif row["dividend_payout_ratio_pct"] >= 40:
        return "Dividend Focus"

    elif row["revenue_cagr_5yr"] >= 15:
        return "Growth Focus"

    elif row["pat_cagr_5yr"] >= 15:
        return "Profit Growth"

    elif row["return_on_equity_pct"] >= 20:
        return "High ROE"

    elif row["free_cash_flow_cr"] > 0:
        return "Cash Generators"

    else:
        return "Balanced"


df["capital_pattern"] = df.apply(classify, axis=1)

# ==========================================================
# Treemap
# ==========================================================

st.subheader("Capital Allocation Treemap")

fig = px.treemap(
    df,
    path=["capital_pattern", "company_id"],
    values="free_cash_flow_cr",
    color="return_on_equity_pct",
    hover_data=["company_name", "debt_to_equity", "revenue_cagr_5yr"],
)

fig.update_layout(height=700)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Pattern Explorer
# ==========================================================

patterns = sorted(df["capital_pattern"].unique())

selected = st.selectbox("Select Capital Allocation Pattern", patterns)

companies = df[df["capital_pattern"] == selected].sort_values(
    "return_on_equity_pct", ascending=False
)

st.subheader(f"{selected} Companies")

st.dataframe(
    companies[
        [
            "company_id",
            "company_name",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

# ==========================================================
# Summary
# ==========================================================

summary = df.groupby("capital_pattern").size().reset_index(name="Companies")

st.markdown("---")

st.subheader("Pattern Distribution")

st.dataframe(summary, use_container_width=True, hide_index=True)

# ==========================================================
# Validation
# ==========================================================

st.markdown("---")

st.success(f"Patterns : {len(patterns)}")

st.success(f"Companies : {len(df)}")

st.success("Capital Allocation Dashboard Loaded Successfully")
