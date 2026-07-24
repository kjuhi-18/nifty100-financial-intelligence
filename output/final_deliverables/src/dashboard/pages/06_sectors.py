import pandas as pd
import plotly.express as px
import streamlit as st
from utils.db import *

st.title("🏭 Sector Analysis")

# ==========================================================
# Load Data
# ==========================================================

conn = get_connection()

query = """
SELECT
    fr.company_id,
    c.company_name,
    s.broad_sector,
    s.sector,
    fr.return_on_equity_pct,
    fr.revenue_cagr_5yr,
    fr.free_cash_flow_cr,
    fr.total_debt_cr,
    fr.composite_quality_score
FROM financial_ratios fr
LEFT JOIN companies c
    ON fr.company_id = c.id
LEFT JOIN sectors s
    ON fr.company_id = s.company_id
"""

df = pd.read_sql(query, conn)

conn.close()

# ==========================================================
# Sector Selection
# ==========================================================

sector_list = sorted(df["broad_sector"].dropna().unique())

selected_sector = st.selectbox("Select Sector", sector_list)

sector_df = df[df["broad_sector"] == selected_sector].copy()

# ==========================================================
# Market Cap Proxy
# (Replace with actual market_cap column on Day 26)
# ==========================================================

sector_df["market_cap"] = (
    sector_df["free_cash_flow_cr"].fillna(0).abs()
    + sector_df["total_debt_cr"].fillna(0).abs()
)

# ==========================================================
# Revenue Proxy
# (Replace with actual revenue column if available)
# ==========================================================

sector_df["revenue"] = sector_df["free_cash_flow_cr"]

# ==========================================================
# Bubble Chart
# ==========================================================

st.subheader("📊 Sector Bubble Chart")

fig = px.scatter(
    sector_df,
    x="revenue",
    y="return_on_equity_pct",
    size="market_cap",
    color="sector",
    hover_name="company_name",
    text="company_id",
    size_max=60,
)

fig.update_traces(textposition="top center")

fig.update_layout(height=650, xaxis_title="Revenue", yaxis_title="ROE (%)")

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Sector Summary
# ==========================================================

st.markdown("---")

st.subheader("Sector Summary")

c1, c2, c3 = st.columns(3)

with c1:

    st.metric("Companies", len(sector_df))

with c2:

    st.metric("Average ROE", round(sector_df["return_on_equity_pct"].mean(), 2))

with c3:

    st.metric("Average Revenue CAGR", round(sector_df["revenue_cagr_5yr"].mean(), 2))

# ==========================================================
# Company Table
# ==========================================================

st.subheader("Companies")

st.dataframe(
    sector_df[
        [
            "company_id",
            "company_name",
            "sector",
            "return_on_equity_pct",
            "revenue_cagr_5yr",
            "composite_quality_score",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)
# ==========================================================
# Sector Median KPI Chart
# ==========================================================

st.markdown("---")

st.subheader("📊 Sector Median KPI Comparison")

median_df = (
    sector_df[
        [
            "return_on_equity_pct",
            "revenue_cagr_5yr",
            "free_cash_flow_cr",
            "composite_quality_score",
        ]
    ]
    .median()
    .reset_index()
)

median_df.columns = ["Metric", "Median"]

fig = px.bar(median_df, x="Metric", y="Median", text="Median", color="Metric")

fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")

fig.update_layout(
    height=500, showlegend=False, xaxis_title="", yaxis_title="Median Value"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Sector Statistics
# ==========================================================

st.markdown("---")

st.subheader("📈 Sector Statistics")

stats = pd.DataFrame(
    {
        "Metric": [
            "Median ROE",
            "Median Revenue CAGR",
            "Median Free Cash Flow",
            "Median Composite Score",
        ],
        "Value": [
            round(sector_df["return_on_equity_pct"].median(), 2),
            round(sector_df["revenue_cagr_5yr"].median(), 2),
            round(sector_df["free_cash_flow_cr"].median(), 2),
            round(sector_df["composite_quality_score"].median(), 2),
        ],
    }
)

st.dataframe(stats, use_container_width=True, hide_index=True)

# ==========================================================
# Validation
# ==========================================================

st.markdown("---")

st.success(f"Sector : {selected_sector}")

st.success(f"Companies : {len(sector_df)}")

st.success("Sector Analysis Loaded Successfully")
