import sqlite3
import pandas as pd

from cashflow_kpis import capital_allocation_pattern

DB_PATH = "db/nifty100.db"

conn = sqlite3.connect(DB_PATH)

cashflow = pd.read_sql(
    "SELECT * FROM cashflow",
    conn
)

cashflow_intelligence = pd.read_excel(
    "output/cashflow_intelligence.xlsx"
)

capital_allocation = pd.read_csv(
    "output/capital_allocation.csv"
)
expected = cashflow[["company_id", "year"]].drop_duplicates()

actual = capital_allocation[["company_id", "year"]].drop_duplicates()

missing = expected.merge(
    actual,
    on=["company_id", "year"],
    how="left",
    indicator=True
)

missing = missing[
    missing["_merge"] == "left_only"
]
def extract_year(y):
    y = str(y).strip()

    if y.startswith("Mar-"):
        yy = int(y[-2:])
        return 2000 + yy

    if y.startswith("Mar "):
        return int(y.split()[-1])

    try:
        return int(y)
    except:
        return None


capital_allocation["year_num"] = capital_allocation["year"].apply(extract_year)

latest_year = capital_allocation["year_num"].max()

latest = capital_allocation[
    capital_allocation["year_num"] == latest_year
]

summary = (
    latest
    .groupby("pattern_label")
    .size()
    .reset_index(name="count")
)

print(summary)
print("=" * 60)
print("Verification")
print("=" * 60)

print("Expected :", len(expected))
print("Found    :", len(actual))
print("Missing  :", len(missing))
latest_year = capital_allocation["year"].max()



summary.to_csv(
    "output/capital_allocation_summary.csv",
    index=False
)
latest_pattern = (

    capital_allocation

    .sort_values("year")

    .groupby("company_id")

    .tail(1)

    [["company_id", "pattern_label"]]

)

cashflow_intelligence = cashflow_intelligence.merge(

    latest_pattern,

    on="company_id",

    how="left"

)

cashflow_intelligence.rename(

    columns={

        "pattern_label":

        "capital_allocation"

    },

    inplace=True

)

cashflow_intelligence.to_excel(

    "output/cashflow_intelligence.xlsx",

    index=False

)
changes = []

for company, group in capital_allocation.groupby("company_id"):

    group = group.sort_values("year")

    if len(group) < 2:
        continue

    previous = group.iloc[-2]

    current = group.iloc[-1]

    if previous["pattern_label"] != current["pattern_label"]:

        changes.append({

            "company_id": company,

            "previous_year": previous["year"],

            "previous_pattern": previous["pattern_label"],

            "current_year": current["year"],

            "current_pattern": current["pattern_label"]

        })

changes_df = pd.DataFrame(changes)

changes_df.to_csv(

    "output/pattern_changes.csv",

    index=False

)

print()

print("Pattern Changes :", len(changes_df))
