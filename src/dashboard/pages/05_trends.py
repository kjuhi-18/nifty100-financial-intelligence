import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.db import *

st.title("📈 Trend Analysis")

# ==========================================================
# Load Companies
# ==========================================================

companies = get_companies()

company = st.selectbox(

    "Select Company",

    companies["id"]

)

# ==========================================================
# Load Ratios
# ==========================================================

ratios = get_ratios(company)

if ratios.empty:

    st.warning("No historical data available.")

    st.stop()

# ==========================================================
# Metric Selection
# ==========================================================

available_metrics = [

    "return_on_equity_pct",

    "return_on_capital_employed_pct",

    "net_profit_margin_pct",

    "operating_profit_margin_pct",

    "debt_to_equity",

    "interest_coverage",

    "asset_turnover",

    "revenue_cagr_5yr",

    "pat_cagr_5yr",

    "free_cash_flow_cr"

]

selected_metrics = st.multiselect(

    "Select up to 3 Metrics",

    available_metrics,

    default=["return_on_equity_pct"],

    max_selections=3

)

# ==========================================================
# Trend Chart
# ==========================================================

fig = go.Figure()

for metric in selected_metrics:

    fig.add_trace(

        go.Scatter(

            x=ratios["year"],

            y=ratios[metric],

            mode="lines+markers+text",

            text=ratios[metric].round(1),

            textposition="top center",

            name=metric.replace("_", " ").title()

        )

    )

fig.update_layout(

    title="Financial Metric Trends",

    xaxis_title="Year",

    yaxis_title="Value",

    hovermode="x unified",

    height=600

)

st.plotly_chart(

    fig,

    use_container_width=True

)

# ==========================================================
# Data Table
# ==========================================================

st.subheader("Trend Data")

columns = ["year"] + selected_metrics

st.dataframe(

    ratios[columns],

    use_container_width=True,

    hide_index=True

)

# ==========================================================
# Validation
# ==========================================================

st.markdown("---")

st.success(f"Loaded {len(ratios)} years of data")

st.success(f"Displaying {len(selected_metrics)} metric(s)")