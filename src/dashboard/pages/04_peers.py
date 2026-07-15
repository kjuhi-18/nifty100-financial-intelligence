import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.db import *

st.title("👥 Peer Comparison")

# ==========================================================
# Load Data
# ==========================================================

conn = get_connection()

peer_groups = pd.read_sql(
    "SELECT DISTINCT peer_group_name FROM peer_percentiles ORDER BY peer_group_name",
    conn
)

selected_group = st.selectbox(
    "Peer Group",
    peer_groups["peer_group_name"]
)

peer_df = pd.read_sql(
    """
    SELECT *
    FROM peer_percentiles
    WHERE peer_group_name=?
    """,
    conn,
    params=(selected_group,)
)

companies = sorted(peer_df["company_id"].unique())

selected_company = st.selectbox(
    "Company",
    companies
)

# ==========================================================
# Radar Chart
# ==========================================================

st.subheader("📊 Peer Radar Chart")

company_metrics = peer_df[
    peer_df["company_id"] == selected_company
]

peer_avg = (
    peer_df
    .groupby("metric")["value"]
    .mean()
)

metrics = company_metrics["metric"].tolist()

company_values = company_metrics["value"].fillna(0).tolist()

peer_values = [
    peer_avg.get(metric, 0)
    for metric in metrics
]

fig = go.Figure()

fig.add_trace(

    go.Scatterpolar(

        r=company_values,

        theta=metrics,

        fill="toself",

        name=selected_company

    )

)

fig.add_trace(

    go.Scatterpolar(

        r=peer_values,

        theta=metrics,

        line=dict(dash="dash"),

        name="Peer Average"

    )

)

fig.update_layout(

    polar=dict(
        radialaxis=dict(visible=True)
    ),

    showlegend=True,

    height=600

)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==========================================================
# KPI Table
# ==========================================================

st.subheader("📋 Peer KPI Table")

table = peer_df.pivot_table(

    index="company_id",

    columns="metric",

    values="percentile_rank"

).reset_index()

benchmark = pd.read_sql(
    """
    SELECT company_id
    FROM peer_groups
    WHERE peer_group_name=?
    AND is_benchmark=1
    """,
    conn,
    params=(selected_group,)
)

conn.close()

benchmark_company = None

if not benchmark.empty:
    benchmark_company = benchmark.iloc[0]["company_id"]


def highlight(row):

    if row["company_id"] == benchmark_company:

        return [
            "background-color:#FFD966"
        ] * len(row)

    return [
        ""
    ] * len(row)


st.dataframe(

    table.style.apply(

        highlight,

        axis=1

    ),

    use_container_width=True

)

# ==========================================================
# Validation
# ==========================================================

st.markdown("---")

st.success(f"Peer Group : {selected_group}")

st.success(f"Companies : {len(companies)}")

st.success("Peer Comparison Loaded Successfully")