import sqlite3
import pandas as pd

from cashflow_kpis import *

DB_PATH = r"db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

print("Connected to database.")
cashflow_df = pd.read_sql(
    "SELECT * FROM cashflow",
    conn
)

ratios_df = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

pnl_df = pd.read_sql(
    "SELECT * FROM profitandloss",
    conn
)

sectors_df = pd.read_sql(
    """
    SELECT
        company_id,
        broad_sector,
        sub_sector,
        market_cap_category
    FROM sectors
    """,
    conn
)

print("Cashflow :", len(cashflow_df))
print("Ratios   :", len(ratios_df))
print("PnL      :", len(pnl_df))
latest = prepare_latest_snapshot(
    cashflow_df,
    ratios_df,
    pnl_df
)

latest = latest.merge(
    sectors_df,
    on="company_id",
    how="left"
)
records = []

for _, row in latest.iterrows():

    cid = row["company_id"]

    cfo_history = (
        cashflow_df[
            cashflow_df.company_id == cid
        ]
        .sort_values("year")
        ["operating_activity"]
        .tolist()
    )

    pat_history = (
        pnl_df[
            pnl_df.company_id == cid
        ]
        .sort_values("year")
        ["net_profit"]
        .tolist()
    )

    temp = row.to_dict()

    temp["cfo_history"] = cfo_history
    temp["pat_history"] = pat_history

    metrics = calculate_cashflow_metrics(temp)

    records.append(metrics)

metrics_df = pd.DataFrame(records)
latest = pd.concat(
    [
        latest.reset_index(drop=True),
        metrics_df.reset_index(drop=True)
    ],
    axis=1
)
fcf_df = calculate_fcf_cagr(
    ratios_df
)

deleveraging_df = calculate_deleveraging_flags(
    cashflow_df,
    ratios_df
)
intelligence_df = build_cashflow_intelligence(
    latest,
    fcf_df,
    deleveraging_df
)
export_cashflow_intelligence(
    intelligence_df
)

export_distress_alerts(
    intelligence_df
)

validate_outputs(
    intelligence_df
)
conn.close()

print("\nDay 31 completed successfully.")