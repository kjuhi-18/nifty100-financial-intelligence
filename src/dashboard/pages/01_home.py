import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import *

st.title("🏠 Home Dashboard")

# ==========================================================
# Sidebar
# ==========================================================

years = get_available_years()

selected_year = st.sidebar.selectbox(

    "Financial Year",

    years,

    index=len(years)-1

)

st.sidebar.success(
    f"Selected : {selected_year}"
)

# ==========================================================
# Load Data
# ==========================================================

companies = get_companies()

ratios = pd.read_sql(

    """

    SELECT *

    FROM financial_ratios

    WHERE year=?

    """,

    get_connection(),

    params=(selected_year,)

)

# ==========================================================
# KPI Calculations
# ==========================================================

avg_roe = round(

    ratios["return_on_equity_pct"].mean(),

    2

)

median_de = round(

    ratios["debt_to_equity"].median(),

    2

)

median_rev = round(

    ratios["revenue_cagr_5yr"].median(),

    2

)

debt_free = (

    ratios["debt_to_equity"]

    .fillna(999)

    .eq(0)

    .sum()

)

median_pe = None

if "price_to_earnings" in ratios.columns:

    median_pe = round(

        ratios["price_to_earnings"].median(),

        2

    )

elif "pe_ratio" in ratios.columns:

    median_pe = round(

        ratios["pe_ratio"].median(),

        2

    )

else:

    median_pe = "N/A"

# ==========================================================
# KPI Tiles
# ==========================================================

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(

        "Average ROE",

        avg_roe

    )

with c2:

    st.metric(

        "Median P/E",

        median_pe

    )

with c3:

    st.metric(

        "Median D/E",

        median_de

    )

c4, c5, c6 = st.columns(3)

with c4:

    st.metric(

        "Companies",

        len(companies)

    )

with c5:

    st.metric(

        "Median Revenue CAGR",

        median_rev

    )

with c6:

    st.metric(

        "Debt-Free Companies",

        debt_free

    )

st.markdown("---")
# ==========================================================
# Sector Breakdown
# ==========================================================

st.subheader("📊 Sector Breakdown")

conn = get_connection()

sector_df = pd.read_sql(

    """
    SELECT broad_sector,
           COUNT(*) AS company_count
    FROM sectors
    GROUP BY broad_sector
    ORDER BY company_count DESC
    """,

    conn

)

conn.close()

fig = px.pie(

    sector_df,

    values="company_count",

    names="broad_sector",

    hole=0.45,

    title="Companies by Sector"

)

fig.update_traces(

    textposition="inside",

    textinfo="percent+label"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.markdown("---")

# ==========================================================
# Top Companies
# ==========================================================

st.subheader("🏆 Top 5 Companies by Composite Quality Score")

conn = get_connection()

top5 = pd.read_sql(

    """

    SELECT
        fr.company_id,
        c.company_name,
        fr.return_on_equity_pct,
        fr.return_on_capital_employed_pct,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.composite_quality_score

    FROM financial_ratios fr

    LEFT JOIN companies c

        ON fr.company_id = c.id

    WHERE fr.year=?

    ORDER BY
        fr.composite_quality_score DESC,
        fr.return_on_equity_pct DESC

    LIMIT 5

    """,

    conn,

    params=(selected_year,)

)

conn.close()

st.dataframe(

    top5,

    use_container_width=True,

    hide_index=True

)
st.markdown("---")

st.subheader("✅ Home Screen Validation")

checks = [

    len(companies) > 0,

    len(ratios) > 0

]

if all(checks):

    st.success("Home Screen Validation PASSED")

else:

    st.error("Home Screen Validation FAILED")