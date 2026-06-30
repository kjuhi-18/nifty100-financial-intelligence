import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import sqlite3
from pathlib import Path

import pandas as pd


# KPI Modules

from src.analytics.ratios import (
    calculate_profitability_ratios,
    calculate_leverage_ratios
)

from src.analytics.cashflow_kpis import (
    calculate_cashflow_metrics
)

from src.analytics.cagr import (
    calculate_growth_metrics
)


# --------------------------------------------------
# Database
# --------------------------------------------------

DB_PATH = Path("db") / "nifty100.db"


class RatioEngine:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

        self.data = None


# --------------------------------------------------
# Load Source Tables
# --------------------------------------------------

    def load_tables(self):

        print("\nLoading source tables...\n")

        self.pnl = pd.read_sql(
            "SELECT * FROM profitandloss",
            self.conn
        )

        self.bs = pd.read_sql(
            "SELECT * FROM balancesheet",
            self.conn
        )

        self.cf = pd.read_sql(
            "SELECT * FROM cashflow",
            self.conn
        )

        self.companies = pd.read_sql(
            "SELECT * FROM companies",
            self.conn
        )

        self.sectors = pd.read_sql(
            "SELECT * FROM sectors",
            self.conn
        )

        self.financial_ratios = pd.read_sql(
            "SELECT * FROM financial_ratios",
            self.conn
        )

        print(f"Companies         : {len(self.companies)}")
        print(f"Profit & Loss     : {len(self.pnl)}")
        print(f"Balance Sheet     : {len(self.bs)}")
        print(f"Cash Flow         : {len(self.cf)}")
        print(f"Sectors           : {len(self.sectors)}")
        print(f"Financial Ratios  : {len(self.financial_ratios)}")


# --------------------------------------------------
# Merge Data
# --------------------------------------------------

    def prepare_dataset(self):

        print("\nPreparing master dataset...\n")

        data = self.pnl.merge(

            self.bs,

            on=["company_id", "year"],

            how="left",

            suffixes=("_pnl", "_bs")

        )

        data = data.merge(

            self.cf,

            on=["company_id", "year"],

            how="left",

            suffixes=("", "_cf")

        )

        data = data.merge(

            self.sectors[
                [
                    "company_id",
                    "broad_sector"
                ]
            ],

            on="company_id",

            how="left"

        )

        data = data.merge(

            self.companies[
                [
                    "id",
                    "book_value",
                    "roe_percentage",
                    "roce_percentage"
                ]
            ],

            left_on="company_id",

            right_on="id",

            how="left"

        )

        data.drop(

            columns=[
                "id",
                "id_pnl",
                "id_bs",
                "id_cf"
            ],

            errors="ignore",

            inplace=True

        )

        self.data = data

        print(f"Master Dataset Rows : {len(self.data)}")
        print(f"Master Dataset Columns : {len(self.data.columns)}")


# --------------------------------------------------
# Preview
# --------------------------------------------------

    def preview(self):

        print("\nColumns\n")

        print(self.data.columns.tolist())

        print("\nSample Record\n")

        print(self.data.head())

    # --------------------------------------------------
# History Helper
# --------------------------------------------------

    def get_history(
        self,
        company_id,
        column
    ):
        """
        Returns historical values for a company,
        sorted by year.
        """

        history = (
            self.data[
                self.data["company_id"] == company_id
            ]
            .sort_values("year")
        )

        return history[column].fillna(0).tolist()


# --------------------------------------------------
# Compute All KPIs
# --------------------------------------------------

    def compute_kpis(self):

        print("\nComputing KPIs...\n")

        results = []

        companies = sorted(
            self.data["company_id"].unique()
        )

        for company in companies:

            company_df = (
                self.data[
                    self.data["company_id"] == company
                ]
                .sort_values("year")
            )

            revenue_history = self.get_history(
                company,
                "sales"
            )

            pat_history = self.get_history(
                company,
                "net_profit"
            )

            eps_history = self.get_history(
                company,
                "eps"
            )

            cfo_history = self.get_history(
                company,
                "operating_activity"
            )

            for _, row in company_df.iterrows():

                row = row.to_dict()

                row["cfo_history"] = cfo_history
                row["pat_history"] = pat_history

                # -----------------------------
                # Profitability
                # -----------------------------

                profitability = (
                    calculate_profitability_ratios(
                        row
                    )
                )

                # -----------------------------
                # Leverage
                # -----------------------------

                leverage = (
                    calculate_leverage_ratios(
                        row
                    )
                )

                # -----------------------------
                # Cash Flow
                # -----------------------------

                cashflow = (
                    calculate_cashflow_metrics(
                        row
                    )
                )

                # -----------------------------
                # CAGR
                # -----------------------------

                growth = (
                    calculate_growth_metrics(
                        revenue_history,
                        pat_history,
                        eps_history
                    )
                )

                # -----------------------------
                # Composite Quality Score
                # -----------------------------

                score = 0

                roe = profitability.get(
                    "return_on_equity_pct"
                )

                if roe is not None and roe > 15:
                    score += 1

                de = leverage.get(
                    "debt_to_equity"
                )

                if de is not None and de < 1:
                    score += 1

                cfo_score = cashflow.get(
                    "cfo_quality_score"
                )

                if cfo_score is not None and cfo_score > 1:
                    score += 1

                # -----------------------------
                # Final Record
                # -----------------------------

                record = {

                    "company_id": row["company_id"],

                    "year": row["year"],

                    "earnings_per_share": row.get("eps"),

                    "book_value_per_share": row.get("book_value"),

                    "dividend_payout_ratio_pct": row.get("dividend_payout"),

                    "total_debt_cr": row.get("borrowings"),

                    "cash_from_operations_cr": row.get("operating_activity"),

                    "composite_quality_score": score

                }

                record.update(profitability)
                record.update(leverage)
                record.update(cashflow)
                record.update(growth)

                results.append(record)

        self.kpi_df = pd.DataFrame(results)
        self.kpi_df.rename(
    columns={
        "capex_intensity_pct": "capex_cr"
    },
    inplace=True
)

        print(
            f"Computed KPI Rows : {len(self.kpi_df)}"
        )

        print()

        print(
            self.kpi_df.head()
        )
    # --------------------------------------------------
# Populate financial_ratios Table
# --------------------------------------------------

    def populate_financial_ratios(self):

        print("\nUpdating financial_ratios table...\n")

        self.cursor.execute(
            "DELETE FROM financial_ratios"
        )

        self.conn.commit()

        required_columns = [
        "company_id",
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
            "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_cr",
        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",
        "cash_from_operations_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score"
        ]

        self.kpi_df[required_columns].to_sql(
        "financial_ratios",
        self.conn,
        if_exists="append",
        index=False
        )

        self.conn.commit()

        print("financial_ratios updated successfully.")


# --------------------------------------------------
# Verify Database
# --------------------------------------------------

    def verify_database(self):

        print("\nVerification\n")

        count = self.cursor.execute(

            """
            SELECT COUNT(*)
            FROM financial_ratios
            """

        ).fetchone()[0]

        print(f"Rows : {count}")

        if count >= 1100:

            print("PASS : Row count requirement met")

        else:

            print("WARNING : Row count below sprint target")

        print()

        nulls = pd.read_sql(

            """
            SELECT

            SUM(
                CASE
                WHEN net_profit_margin_pct IS NULL
                THEN 1
                ELSE 0
                END
            ) AS npm_null,

            SUM(
                CASE
                WHEN return_on_equity_pct IS NULL
                THEN 1
                ELSE 0
                END
            ) AS roe_null,

            SUM(
                CASE
                WHEN debt_to_equity IS NULL
                THEN 1
                ELSE 0
                END
            ) AS de_null,

            SUM(
                CASE
                WHEN revenue_cagr_5yr IS NULL
                THEN 1
                ELSE 0
                END
            ) AS revenue_cagr_null

            FROM financial_ratios

            """,

            self.conn

        )

        print("NULL Summary\n")

        print(nulls)

        print()

        sample = pd.read_sql(

            """
            SELECT *

            FROM financial_ratios

            LIMIT 5
            """,

            self.conn

        )

        print(sample)
    # --------------------------------------------------
# Verify Database
# --------------------------------------------------

    def verify_database(self):

        print("\n" + "=" * 60)
        print("DATABASE VERIFICATION")
        print("=" * 60)

        row_count = pd.read_sql(
            """
            SELECT COUNT(*) AS total
            FROM financial_ratios
            """,
            self.conn
        )

        total = int(row_count.loc[0, "total"])

        print(f"Rows Loaded : {total}")

        if total >= 1100:
            print("PASS : Row count meets sprint target")
        else:
            print("WARNING : Row count below sprint target")

        print("\nChecking NULL-only KPI columns...\n")

        cols = [
            "net_profit_margin_pct",
            "operating_profit_margin_pct",
            "return_on_equity_pct",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover",
            "free_cash_flow_cr",
            "capex_cr",
            "earnings_per_share",
            "book_value_per_share",
            "dividend_payout_ratio_pct",
            "total_debt_cr",
            "cash_from_operations_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "eps_cagr_5yr",
            "composite_quality_score"
        ]

        for col in cols:

            q = f"""
            SELECT COUNT(*) AS cnt
            FROM financial_ratios
            WHERE {col} IS NOT NULL
            """

            cnt = pd.read_sql(q, self.conn).loc[0, "cnt"]

            print(f"{col:<35}{cnt}")

        print("\nForeign Key Check\n")

        fk = self.conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if len(fk) == 0:
            print("PASS : No FK violations")
        else:
            print(f"FAIL : {len(fk)} FK violations")
# --------------------------------------------------
# Manual Spot Check
# --------------------------------------------------

    def manual_spot_check(self):

        print("\n" + "=" * 60)
        print("MANUAL SPOT CHECK")
        print("=" * 60)

        companies = [

            "ABB",

            "TCS",

            "HDFCBANK"

        ]

        for company in companies:

            print("\n" + "-" * 40)

            print(company)

            print("-" * 40)

            df = pd.read_sql(
                f"""
                SELECT

                company_id,
                year,
                return_on_equity_pct,
                revenue_cagr_5yr,
                composite_quality_score

                FROM financial_ratios

                WHERE company_id='{company}'

                ORDER BY year
                """,
                self.conn
            )

            print(df.head())

# --------------------------------------------------
# Close Connection
# --------------------------------------------------

    def close(self):

        self.conn.close()
# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    engine = RatioEngine()

    engine.load_tables()

    engine.prepare_dataset()

    engine.compute_kpis()

    engine.populate_financial_ratios()

    engine.verify_database()

    engine.manual_spot_check()

    engine.close()