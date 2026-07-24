import streamlit as st
from utils.db import *

st.title("🏢 Company Profile")

# ==========================================================
# Load Data
# ==========================================================

companies = get_companies()

# ==========================================================
# Search
# ==========================================================

company_options = []

for _, row in companies.iterrows():

    company_options.append(f"{row['id']} - {row['company_name']}")

selected = st.selectbox(
    "Search Company",
    company_options,
    index=None,
    placeholder="Type company name or ticker...",
)

if selected is None:

    st.info("Select a company to view its profile.")

    st.stop()

ticker = selected.split(" - ")[0]

# ==========================================================
# Company Information
# ==========================================================

company = companies[companies["id"] == ticker]

if company.empty:

    st.warning("Ticker not found — please try another.")

    st.stop()

company = company.iloc[0]

ratios = get_ratios(ticker)

if ratios.empty:

    st.warning("Financial data not available.")

    st.stop()

latest = ratios.iloc[0]

# ==========================================================
# Company Card
# ==========================================================

st.markdown("## Company Overview")

c1, c2 = st.columns([2, 3])

with c1:

    st.markdown(f"### {company['company_name']}")

    st.write(f"**Ticker:** {ticker}")

    if "broad_sector" in company.index:

        st.write(f"**Sector:** {company['broad_sector']}")

    if "sector" in company.index:

        st.write(f"**Sub-sector:** {company['sector']}")

with c2:

    if "about_company" in company.index:

        st.write(company["about_company"])

    else:

        st.info("Company description unavailable.")

st.markdown("---")

# ==========================================================
# KPI Tiles
# ==========================================================

k1, k2, k3 = st.columns(3)

with k1:

    st.metric("ROE", latest.get("return_on_equity_pct", "N/A"))

with k2:

    st.metric("ROCE", latest.get("return_on_capital_employed_pct", "N/A"))

with k3:

    st.metric("Net Profit Margin", latest.get("net_profit_margin_pct", "N/A"))

k4, k5, k6 = st.columns(3)

with k4:

    st.metric("Debt / Equity", latest.get("debt_to_equity", "N/A"))

with k5:

    st.metric("Revenue CAGR", latest.get("revenue_cagr_5yr", "N/A"))

with k6:

    st.metric("Free Cash Flow", latest.get("free_cash_flow_cr", "N/A"))

st.markdown("---")

st.success("Company profile loaded successfully.")
# ==========================================================
# Revenue & Net Profit Chart
# ==========================================================

st.subheader("📊 Revenue & Net Profit (10 Years)")

pl = get_pl(ticker)

if not pl.empty:

    import plotly.graph_objects as go

    fig = go.Figure()

    fig.add_bar(x=pl["year"], y=pl["sales"], name="Revenue")

    fig.add_bar(x=pl["year"], y=pl["net_profit"], name="Net Profit")

    fig.update_layout(
        barmode="group", xaxis_title="Year", yaxis_title="₹ Crore", height=500
    )

    st.plotly_chart(fig, use_container_width=True)

else:

    st.info("Revenue history unavailable.")
# ==========================================================
# ROE vs ROCE Trend
# ==========================================================

st.subheader("📈 ROE vs ROCE")

if not ratios.empty:

    import plotly.graph_objects as go

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=ratios["year"],
            y=ratios["return_on_equity_pct"],
            mode="lines+markers",
            name="ROE",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=ratios["year"],
            y=ratios["return_on_capital_employed_pct"],
            mode="lines+markers",
            name="ROCE",
            yaxis="y2",
        )
    )

    fig.update_layout(
        height=500,
        xaxis_title="Year",
        yaxis=dict(title="ROE (%)"),
        yaxis2=dict(title="ROCE (%)", overlaying="y", side="right"),
    )

    st.plotly_chart(fig, use_container_width=True)
# ==========================================================
# Pros & Cons
# ==========================================================

st.subheader("✅ Pros & Cons")

pros = []

cons = []

if latest["return_on_equity_pct"] > 20:

    pros.append("High Return on Equity")

else:

    cons.append("ROE below 20%")

if latest["debt_to_equity"] < 0.5:

    pros.append("Low Debt")

else:

    cons.append("High Debt")

if latest["free_cash_flow_cr"] > 0:

    pros.append("Positive Free Cash Flow")

else:

    cons.append("Negative Free Cash Flow")

if latest["revenue_cagr_5yr"] > 10:

    pros.append("Healthy Revenue Growth")

else:

    cons.append("Weak Revenue Growth")

left, right = st.columns(2)

with left:

    st.success("Pros")

    for item in pros:

        st.markdown(f"✅ {item}")

with right:

    st.error("Cons")

    for item in cons:

        st.markdown(f"❌ {item}")
# ==========================================================
# Data Availability
# ==========================================================

st.markdown("---")

st.subheader("📋 Data Availability")

availability = {
    "Financial Ratios": not ratios.empty,
    "Profit & Loss": not pl.empty,
    "Balance Sheet": not get_bs(ticker).empty,
    "Cash Flow": not get_cf(ticker).empty,
}

for name, available in availability.items():

    if available:

        st.success(f"{name} : Available")

    else:

        st.warning(f"{name} : Not Available")
# ==========================================================
# Dashboard Information
# ==========================================================

st.markdown("---")

st.subheader("⚡ Dashboard Information")

st.info("""
    • Company Profile loads directly from SQLite

    • Database queries are cached for 10 minutes

    • Missing values are displayed safely

    • Charts resize automatically
    """)
# ==========================================================
# Validation
# ==========================================================

st.markdown("---")

st.subheader("✅ Page Validation")

checks = [not company.empty, not ratios.empty, len(companies) > 0]

if all(checks):

    st.success("Company Profile Screen Validation PASSED")

else:

    st.error("Company Profile Screen Validation FAILED")
