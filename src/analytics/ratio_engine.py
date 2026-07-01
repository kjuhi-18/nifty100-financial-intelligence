import sys
import sqlite3
import logging

from pathlib import Path

import pandas as pd
import numpy as np


# ==========================================================
# Project Root
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))


# ==========================================================
# Imports
# ==========================================================

from src.analytics.ratios import (
    calculate_profitability_ratios,
    calculate_leverage_ratios
)

from src.analytics.cagr import (
    calculate_growth_metrics
)

from src.analytics.cashflow_kpis import (
    calculate_cashflow_metrics,
    generate_capital_allocation_csv
)

from src.etl.normaliser import normalize_year



# ==========================================================
# Paths
# ==========================================================

DB_PATH = ROOT / "db" / "nifty100.db"

OUTPUT_DIR = ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================================================
# Logger
# ==========================================================

edge_logger = logging.getLogger("ratio_edge_cases")

edge_logger.setLevel(logging.INFO)

edge_logger.handlers.clear()

file_handler = logging.FileHandler(
    OUTPUT_DIR / "ratio_edge_cases.log",
    mode="w",
    encoding="utf-8"
)

formatter = logging.Formatter("%(message)s")

file_handler.setFormatter(formatter)

edge_logger.addHandler(file_handler)


# ==========================================================
# Ratio Engine
# ==========================================================

class RatioEngine:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.cursor = self.conn.cursor()

        self.companies = None

        self.pnl = None

        self.bs = None

        self.cf = None

        self.sectors = None

        self.financial_ratios = None

        self.data = None

        self.kpi_df = None


# ==========================================================
# Load SQLite Tables
# ==========================================================

    def load_tables(self):

        print("\nLoading source tables...\n")

        self.companies = pd.read_sql(
            "SELECT * FROM companies",
            self.conn
        )

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


# ==========================================================
# Prepare Master Dataset
# ==========================================================

    def prepare_dataset(self):

        print("\nPreparing master dataset...\n")

        data = self.pnl.merge(

            self.bs,

            on=[
                "company_id",
                "year"
            ],

            how="left",

            suffixes=(
                "",
                "_bs"
            )

        )

        data = data.merge(

            self.cf,

            on=[
                "company_id",
                "year"
            ],

            how="left",

            suffixes=(
                "",
                "_cf"
            )

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
                "id_x",
                "id_y",
                "id_bs",
                "id_cf"
            ],

            inplace=True,

            errors="ignore"

        )

        self.data = data

        print(
            f"Master Dataset Rows : {len(self.data)}"
        )

        print(
            f"Master Dataset Columns : {len(self.data.columns)}"
        )

        print()

        print(
            self.data.head()
        )
# ==========================================================
# Company History
# ==========================================================

    def get_company_history(self, company_id):

        history = self.data[self.data["company_id"] == company_id].copy()

        # Sort chronologically by normalized year, putting TTM/None at the end (using a high year string)
        history["norm_year"] = history["year"].apply(lambda y: normalize_year(y) or "9999-12")
        history = history.sort_values("norm_year").reset_index(drop=True)

        return history


# ==========================================================
# Compute All KPIs
# ==========================================================

    def compute_kpis(self):

        print("\nComputing KPIs...\n")

        records = []

        for _, row in self.data.iterrows():

            company = row["company_id"]
            current_year = row["year"]
            norm_curr = normalize_year(current_year)

            history = self.get_company_history(company)

            # Filter history up to (and including) current_year
            if norm_curr is not None:
                history_up_to = history[history["norm_year"] <= norm_curr]
            else:
                # If current_year is TTM or similar, we keep all historical rows
                history_up_to = history

            # Build history lists
            revenue_history = history_up_to["sales"].fillna(0).tolist()
            pat_history = history_up_to["net_profit"].fillna(0).tolist()
            eps_history = history_up_to["eps"].fillna(0).tolist()
            cfo_history = history_up_to["operating_activity"].fillna(0).tolist()

            # Pass cfo_history and pat_history to row before calling
            row_dict = row.to_dict()
            row_dict["cfo_history"] = cfo_history
            row_dict["pat_history"] = pat_history

            # Detect and fix balance sheet scaling mismatch (e.g. for BEL, HAL, LT, INDIGO)
            # If total_assets is less than net_profit, the balance sheet values are scaled down by 100
            net_prof = row_dict.get("net_profit")
            tot_assets = row_dict.get("total_assets")
            if pd.notna(net_prof) and pd.notna(tot_assets) and tot_assets > 0 and tot_assets < net_prof:
                for col in ["equity_capital", "reserves", "borrowings", "total_assets", "investments"]:
                    if col in row_dict and pd.notna(row_dict[col]):
                        row_dict[col] = row_dict[col] * 100.0

            # ----------------------------------------
            # Ratio Modules
            # ----------------------------------------

            profitability = calculate_profitability_ratios(row_dict)

            leverage = calculate_leverage_ratios(row_dict)

            cashflow = calculate_cashflow_metrics(row_dict)

            cagr = calculate_growth_metrics(
                revenue_history=revenue_history,
                pat_history=pat_history,
                eps_history=eps_history
            )

            # ----------------------------------------
            # Composite Quality Score
            # ----------------------------------------

            score = 0

            roe = profitability.get(
                "return_on_equity_pct"
            )

            de = leverage.get(
                "debt_to_equity"
            )

            npm = profitability.get(
                "net_profit_margin_pct"
            )

            cfo_quality = cashflow.get(
                "cfo_quality_label"
            )

            sector = row.get(
                "broad_sector"
            )

            # ROE

            if roe is not None and roe > 15:

                score += 1

            # Debt / Equity
            # Skip Financial companies

            financial_sector = [

                "Financials",
                "Banks",
                "Banking",
                "NBFC",
                "Insurance"

            ]

            if sector not in financial_sector:

                if de is not None and de < 1:

                    score += 1

            # Net Profit Margin

            if npm is not None and npm > 10:

                score += 1

            # CFO Quality

            if cfo_quality == "High Quality":

                score += 1

            # ----------------------------------------
            # Begin Record
            # ----------------------------------------

            record = {

                "company_id": company,

                "year": row["year"],

                # Profitability

                "net_profit_margin_pct":

                    profitability.get(
                        "net_profit_margin_pct"
                    ),

                "operating_profit_margin_pct":

                    profitability.get(
                        "operating_profit_margin_pct"
                    ),

                "return_on_equity_pct":

                    profitability.get(
                        "return_on_equity_pct"
                    ),

                "return_on_capital_employed_pct":

                    profitability.get(
                        "return_on_capital_employed_pct"
                    ),

                "return_on_assets_pct":

                    profitability.get(
                        "return_on_assets_pct"
                    ),

                # Leverage

                "debt_to_equity":

                    leverage.get(
                        "debt_to_equity"
                    ),

                "interest_coverage":

                    leverage.get(
                        "interest_coverage"
                    ),

                "asset_turnover":

                    leverage.get(
                        "asset_turnover"
                    ),

                "high_leverage_flag":

                    leverage.get(
                        "high_leverage_flag"
                    ),                \
                # ==================================================
                # Cash Flow KPIs
                # ==================================================

                "free_cash_flow_cr":

                    cashflow.get(
                        "free_cash_flow_cr"
                    ),

                "capex_cr":

                    cashflow.get(
                        "capex_intensity_pct"
                    ),

                "cash_from_operations_cr":

                    row.get(
                        "operating_activity"
                    ),

                "cfo_quality_score":

                    cashflow.get(
                        "cfo_quality_score"
                    ),

                "capex_intensity":

                    cashflow.get(
                        "capex_intensity"
                    ),

                "fcf_conversion_rate":

                    cashflow.get(
                        "fcf_conversion_rate"
                    ),

                "capital_allocation_pattern":

                    cashflow.get(
                        "capital_allocation_pattern"
                    ),

                # ==================================================
                # Company Metrics
                # ==================================================

                "earnings_per_share":

                    row.get(
                        "eps"
                    ),

                "book_value_per_share":

                    row.get(
                        "book_value"
                    ),

                "dividend_payout_ratio_pct":

                    row.get(
                        "dividend_payout"
                    ),

                "total_debt_cr":

                    row_dict.get(
                        "borrowings"
                    ),

                # ==================================================
                # CAGR Values
                # ==================================================

                "revenue_cagr_3yr":

                    cagr.get(
                        "revenue_cagr_3yr"
                    ),

                "revenue_cagr_5yr":

                    cagr.get(
                        "revenue_cagr_5yr"
                    ),

                "revenue_cagr_10yr":

                    cagr.get(
                        "revenue_cagr_10yr"
                    ),

                "pat_cagr_3yr":

                    cagr.get(
                        "pat_cagr_3yr"
                    ),

                "pat_cagr_5yr":

                    cagr.get(
                        "pat_cagr_5yr"
                    ),

                "pat_cagr_10yr":

                    cagr.get(
                        "pat_cagr_10yr"
                    ),

                "eps_cagr_3yr":

                    cagr.get(
                        "eps_cagr_3yr"
                    ),

                "eps_cagr_5yr":

                    cagr.get(
                        "eps_cagr_5yr"
                    ),

                "eps_cagr_10yr":

                    cagr.get(
                        "eps_cagr_10yr"
                    ),

                # ==================================================
                # CAGR Flags
                # ==================================================

                "revenue_cagr_3yr_flag":

                    cagr.get(
                        "revenue_cagr_3yr_flag"
                    ),

                "revenue_cagr_5yr_flag":

                    cagr.get(
                        "revenue_cagr_5yr_flag"
                    ),

                "revenue_cagr_10yr_flag":

                    cagr.get(
                        "revenue_cagr_10yr_flag"
                    ),

                "pat_cagr_3yr_flag":

                    cagr.get(
                        "pat_cagr_3yr_flag"
                    ),

                "pat_cagr_5yr_flag":

                    cagr.get(
                        "pat_cagr_5yr_flag"
                    ),

                "pat_cagr_10yr_flag":

                    cagr.get(
                        "pat_cagr_10yr_flag"
                    ),

                "eps_cagr_3yr_flag":

                    cagr.get(
                        "eps_cagr_3yr_flag"
                    ),

                "eps_cagr_5yr_flag":

                    cagr.get(
                        "eps_cagr_5yr_flag"
                    ),

                "eps_cagr_10yr_flag":

                    cagr.get(
                        "eps_cagr_10yr_flag"
                    ),

                # ==================================================
                # Composite Score
                # ==================================================

                "composite_quality_score":

                    score

            }

            records.append(record)

        self.kpi_df = pd.DataFrame(records)

        generate_capital_allocation_csv(self.data)

        print(
            f"Computed KPI Rows : {len(self.kpi_df)}"
        )

        print()

        print(
            self.kpi_df.head()
        )
# ==========================================================
# Populate financial_ratios Table
# ==========================================================

    def populate_financial_ratios(self):

        print("\nUpdating financial_ratios table...\n")

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

        required_columns = [

            c

            for c in required_columns

            if c in self.kpi_df.columns

        ]

        self.cursor.execute(

            "DELETE FROM financial_ratios"

        )

        self.conn.commit()

        self.kpi_df[required_columns].to_sql(

            "financial_ratios",

            self.conn,

            if_exists="append",

            index=False

        )

        self.conn.commit()

        print("financial_ratios updated successfully.")


# ==========================================================
# Verify Database
# ==========================================================

    def verify_database(self):

        print("\n" + "=" * 60)

        print("DATABASE VERIFICATION")

        print("=" * 60)

        ratios = pd.read_sql(

            "SELECT * FROM financial_ratios",

            self.conn

        )

        print(

            f"\nRows Loaded : {len(ratios)}"

        )

        if len(ratios) >= 1100:

            print(

                "PASS : Row count meets sprint target"

            )

        else:

            print(

                "WARNING : Row count below sprint target"

            )

        print("\nChecking KPI Population...\n")

        kpi_columns = [

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

        for column in kpi_columns:

            if column in ratios.columns:

                populated = ratios[column].notna().sum()

                print(

                    f"{column:<35} {populated}"

                )

        print("\nForeign Key Check\n")

        self.cursor.execute(

            "PRAGMA foreign_key_check"

        )

        fk = self.cursor.fetchall()

        if len(fk) == 0:

            print(

                "PASS : No FK violations"

            )

        else:

            print(

                f"FAIL : {len(fk)} FK violations"

            )

        print()

        print("=" * 60)

        print("DATABASE VERIFICATION COMPLETE")

        print("=" * 60)
# ==========================================================
# Day 13
# Review ROE / ROCE Edge Cases
# ==========================================================

    def review_edge_cases(self):

        print("\nReviewing ROE / ROCE edge cases...\n")

        edge_logger.info("=" * 80)
        edge_logger.info("DAY 13 - RATIO EDGE CASE REVIEW")
        edge_logger.info("=" * 80)

        merged = self.kpi_df.merge(

            self.data[
                [
                    "company_id",
                    "year",
                    "roe_percentage",
                    "roce_percentage",
                    "broad_sector"
                ]
            ],

            on=[
                "company_id",
                "year"
            ],

            how="left"

        )

        roe_count = 0

        roce_count = 0

        financial_sector = [

            "Financials",
            "Banks",
            "Banking",
            "NBFC",
            "Insurance"

        ]

        for _, row in merged.iterrows():

            company = row["company_id"]

            year = row["year"]

            sector = row["broad_sector"]

            # ------------------------------------------
            # Skip TTM rows
            # ------------------------------------------

            if "TTM" in str(year).upper():

                continue

            computed_roe = row.get(
                "return_on_equity_pct"
            )

            computed_roce = row.get(
                "return_on_capital_employed_pct"
            )

            source_roe = row.get(
                "roe_percentage"
            )

            source_roce = row.get(
                "roce_percentage"
            )

            # ==========================================
            # ROE CHECK
            # ==========================================

            if (

                pd.notna(computed_roe)

                and

                pd.notna(source_roe)

            ):

                diff = abs(

                    computed_roe - source_roe

                )

                if diff > 5:

                    if abs(source_roe) < 2:

                        category = "Data Source Issue"

                    elif diff > 20:

                        category = "Formula Discrepancy"

                    else:

                        category = "Version Difference"

                    edge_logger.info(

                        f"{company} | "
                        f"{year} | "
                        f"ROE | "
                        f"Computed={computed_roe:.2f} | "
                        f"Source={source_roe:.2f} | "
                        f"Difference={diff:.2f} | "
                        f"Category={category}"

                    )

                    roe_count += 1

            # ==========================================
            # ROCE CHECK
            # ==========================================

            if (

                pd.notna(computed_roce)

                and

                pd.notna(source_roce)

            ):

                diff = abs(

                    computed_roce - source_roce

                )

                if diff > 5:

                    if abs(source_roce) < 2:

                        category = "Data Source Issue"

                    elif diff > 20:

                        category = "Formula Discrepancy"

                    else:

                        category = "Version Difference"

                    edge_logger.info(

                        f"{company} | "
                        f"{year} | "
                        f"ROCE | "
                        f"Computed={computed_roce:.2f} | "
                        f"Source={source_roce:.2f} | "
                        f"Difference={diff:.2f} | "
                        f"Category={category}"

                    )

                    roce_count += 1

        edge_logger.info("")
        edge_logger.info("=" * 80)
        edge_logger.info("SUMMARY")
        edge_logger.info("=" * 80)
        edge_logger.info(f"ROE mismatches  : {roe_count}")
        edge_logger.info(f"ROCE mismatches : {roce_count}")

        print("ratio_edge_cases.log generated.")

        print(f"ROE mismatches  : {roe_count}")

        print(f"ROCE mismatches : {roce_count}")
# ==========================================================
# Manual Spot Check
# ==========================================================

    def manual_spot_check(self):

        print("\n" + "=" * 60)
        print("MANUAL SPOT CHECK")
        print("=" * 60)

        companies = [

            "ABB",
            "TCS",
            "HDFCBANK"

        ]

        columns = [

            "company_id",
            "year",
            "return_on_equity_pct",
            "revenue_cagr_5yr",
            "composite_quality_score"

        ]

        for company in companies:

            print("\n" + "-" * 40)
            print(company)
            print("-" * 40)

            df = self.kpi_df[
                self.kpi_df["company_id"] == company
            ][columns]

            print(df.to_string(index=False))


# ==========================================================
# Close Database Connection
# ==========================================================

    def close(self):

        if self.conn:

            self.conn.close()

        file_handler.close()


# ==========================================================
# Main
# ==========================================================

def main():

    engine = RatioEngine()

    try:

        engine.load_tables()

        engine.prepare_dataset()

        engine.compute_kpis()

        engine.populate_financial_ratios()

        engine.verify_database()

        engine.manual_spot_check()

        engine.review_edge_cases()

        print("\n" + "=" * 70)
        print("SPRINT 2 - DAY 12 & DAY 13 COMPLETED")
        print("=" * 70)

        print("\nDeliverables")

        print("------------------------------------------")

        print("OK: financial_ratios table populated")

        print("OK: ratio_edge_cases.log generated")

        print("OK: Database verification completed")

        print("OK: Manual spot check completed")

        print("OK: ROE / ROCE review completed")

        print("\nReady for Day 14")

    except Exception as e:

        print("\nERROR")
        print("-" * 40)
        print(e)

        raise

    finally:

        engine.close()


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    main()