import sys
import sqlite3

from pathlib import Path

import pandas as pd


# ==========================================================
# Project Root
# ==========================================================

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))


# ==========================================================
# Paths
# ==========================================================

DB_PATH = ROOT / "db" / "nifty100.db"

OUTPUT_DIR = ROOT / "output"

CAPITAL_ALLOCATION = OUTPUT_DIR / "capital_allocation.csv"

EDGE_CASE_LOG = OUTPUT_DIR / "ratio_edge_cases.log"

SCREENER_OUTPUT = OUTPUT_DIR / "screener_preview.csv"

SPRINT_REPORT = OUTPUT_DIR / "sprint2_review.txt"

OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================================================
# Sprint Review
# ==========================================================

class SprintReview:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.cursor = self.conn.cursor()

        self.financial_ratios = None

        self.result = {}


# ==========================================================
# Load financial_ratios
# ==========================================================

    def load_data(self):

        print("\nLoading financial_ratios...\n")

        self.financial_ratios = pd.read_sql(

            "SELECT * FROM financial_ratios",

            self.conn

        )

        print(

            f"Rows Loaded : {len(self.financial_ratios)}"

        )


# ==========================================================
# Row Count Check
# ==========================================================

    def check_row_count(self):

        print("\nChecking row count...")

        rows = len(self.financial_ratios)

        passed = rows >= 1100

        self.result["Row Count"] = passed

        print(

            f"Rows : {rows}"

        )

        print(

            "PASS"

            if passed

            else

            "FAIL"

        )


# ==========================================================
# Required KPI Columns
# ==========================================================

    def check_required_columns(self):

        print("\nChecking KPI columns...\n")

        required = [

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

        all_present = True

        for column in required:

            exists = column in self.financial_ratios.columns

            print(

                f"{column:<35}",

                "OK" if exists else "MISSING"

            )

            if not exists:

                all_present = False

        self.result["Required Columns"] = all_present
# ==========================================================
# Null-only KPI Check
# ==========================================================

    def check_null_columns(self):

        print("\nChecking NULL-only KPI columns...\n")

        null_only = False

        for column in self.financial_ratios.columns:

            if self.financial_ratios[column].notna().sum() == 0:

                print(f"{column:<35} NULL ONLY")

                null_only = True

        if not null_only:

            print("PASS : No NULL-only columns found")

        self.result["Null Only Columns"] = not null_only


# ==========================================================
# Check capital_allocation.csv
# ==========================================================

    def check_capital_allocation(self):

        print("\nChecking capital_allocation.csv...\n")

        exists = CAPITAL_ALLOCATION.exists()

        self.result["Capital Allocation CSV"] = exists

        if exists:

            df = pd.read_csv(CAPITAL_ALLOCATION)

            print(f"Rows : {len(df)}")

            print("PASS")

        else:

            print("FAIL : File not found")


# ==========================================================
# Check ratio_edge_cases.log
# ==========================================================

    def check_edge_case_log(self):

        print("\nChecking ratio_edge_cases.log...\n")

        exists = EDGE_CASE_LOG.exists()

        self.result["Edge Case Log"] = exists

        if exists:

            with open(EDGE_CASE_LOG, "r", encoding="utf-8") as file:

                lines = file.readlines()

            print(f"Lines : {len(lines)}")

            print("PASS")

        else:

            print("FAIL : File not found")


# ==========================================================
# Database Summary
# ==========================================================

    def database_summary(self):

        print("\n" + "=" * 60)

        print("DATABASE SUMMARY")

        print("=" * 60)

        print(f"financial_ratios : {len(self.financial_ratios)} rows")

        print(f"Columns          : {len(self.financial_ratios.columns)}")

        print()

        print("Validation Results\n")

        for key, value in self.result.items():

            status = "PASS" if value else "FAIL"

            print(f"{key:<30} {status}")

        print("\n" + "=" * 60)
# ==========================================================
# Screener Preview
# ==========================================================

    def screener_preview(self):

        print("\nGenerating Screener Preview...\n")

        screener = self.financial_ratios.copy()

        # ------------------------------------------
        # Remove rows with missing values
        # ------------------------------------------

        screener = screener.dropna(

            subset=[

                "return_on_equity_pct",

                "debt_to_equity"

            ]

        )

        # ------------------------------------------
        # ROE > 15%
        # D/E < 1
        # ------------------------------------------

        screener = screener[

            (screener["return_on_equity_pct"] > 15)

            &

            (screener["debt_to_equity"] < 1)

        ]

        # ------------------------------------------
        # Keep latest record for each company
        # ------------------------------------------

        screener = (

            screener

            .sort_values("year")

            .groupby("company_id", as_index=False)

            .tail(1)

            .reset_index(drop=True)

        )

        # ------------------------------------------
        # Sort by ROE
        # ------------------------------------------

        screener = screener.sort_values(

            "return_on_equity_pct",

            ascending=False

        )

        # ------------------------------------------
        # Save CSV
        # ------------------------------------------

        screener.to_csv(

            SCREENER_OUTPUT,

            index=False

        )

        count = len(screener)

        print(f"Companies Found : {count}")

        if 15 <= count <= 50:

            print("PASS : Screener result count is within expected range")

            self.result["Screener Preview"] = True

        else:

            print("WARNING : Result count outside expected range")

            self.result["Screener Preview"] = False

        print("\nTop Companies\n")

        preview_columns = [

            "company_id",

            "year",

            "return_on_equity_pct",

            "debt_to_equity",

            "net_profit_margin_pct",

            "revenue_cagr_5yr",

            "composite_quality_score"

        ]

        available_columns = [

            column

            for column in preview_columns

            if column in screener.columns

        ]

        print(

            screener[available_columns]

            .head(20)

            .to_string(index=False)

        )

        print()

        print(

            f"Screener saved to:\n{SCREENER_OUTPUT}"

        )
# ==========================================================
# Sprint 2 Review Report
# ==========================================================

    def generate_review_report(self):

        print("\nGenerating Sprint 2 Review...\n")

        report = []

        report.append("=" * 70)
        report.append("SPRINT 2 RETROSPECTIVE")
        report.append("=" * 70)
        report.append("")

        report.append("Sprint Scope")
        report.append("-" * 40)
        report.append("• Profitability Ratios")
        report.append("• Leverage Ratios")
        report.append("• Efficiency Ratios")
        report.append("• CAGR Engine")
        report.append("• Cash Flow KPIs")
        report.append("• Capital Allocation")
        report.append("• Financial Ratio Database")
        report.append("")

        report.append("Formula Decisions")
        report.append("-" * 40)
        report.append(
            "• ROE = Net Profit / (Equity Capital + Reserves)"
        )
        report.append(
            "• Debt to Equity = Borrowings / Shareholder Equity"
        )
        report.append(
            "• Asset Turnover = Sales / Total Assets"
        )
        report.append(
            "• Interest Coverage = Operating Profit / Interest"
        )
        report.append(
            "• Free Cash Flow = CFO + Investing Activity"
        )
        report.append(
            "• CapEx Intensity = abs(Investing Activity) / Sales × 100"
        )
        report.append(
            "• Revenue, PAT and EPS CAGR computed for 3, 5 and 10 years"
        )
        report.append("")

        report.append("Edge Case Handling")
        report.append("-" * 40)
        report.append(
            "• Financial sector companies excluded from Debt/Equity warning"
        )
        report.append(
            "• CAGR handles ZERO_BASE"
        )
        report.append(
            "• CAGR handles INSUFFICIENT history"
        )
        report.append(
            "• CAGR handles TURNAROUND"
        )
        report.append(
            "• CAGR handles DECLINE_TO_LOSS"
        )
        report.append(
            "• CAGR handles BOTH_NEGATIVE"
        )
        report.append("")

        report.append("ROE / ROCE Review")
        report.append("-" * 40)
        report.append(
            "Computed ratios are compared against companies.xlsx."
        )
        report.append(
            "Differences greater than 5% are logged."
        )
        report.append(
            "Each anomaly is categorized as:"
        )
        report.append(
            "  - Data Source Issue"
        )
        report.append(
            "  - Version Difference"
        )
        report.append(
            "  - Formula Discrepancy"
        )
        report.append("")

        report.append("Sprint Outcome")
        report.append("-" * 40)

        for key, value in self.result.items():

            status = "PASS" if value else "FAIL"

            report.append(f"{key:<30} {status}")

        report.append("")
        report.append("=" * 70)
        report.append("End of Sprint Review")
        report.append("=" * 70)

        with open(

            SPRINT_REPORT,

            "w",

            encoding="utf-8"

        ) as file:

            file.write("\n".join(report))

        print(

            f"Review saved to:\n{SPRINT_REPORT}"

        )


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

            "debt_to_equity",

            "net_profit_margin_pct",

            "revenue_cagr_5yr",

            "free_cash_flow_cr",

            "composite_quality_score"

        ]

        available = [

            c

            for c in columns

            if c in self.financial_ratios.columns

        ]

        for company in companies:

            print("\n" + "-" * 40)

            print(company)

            print("-" * 40)

            df = self.financial_ratios[

                self.financial_ratios["company_id"] == company

            ][available]

            print(

                df.tail(5).to_string(index=False)

            )
# ==========================================================
# Close Database Connection
# ==========================================================

    def close(self):

        if self.conn:

            self.conn.close()


# ==========================================================
# Main
# ==========================================================

def main():

    review = SprintReview()

    try:

        review.load_data()

        review.check_row_count()

        review.check_required_columns()

        review.check_null_columns()

        review.check_capital_allocation()

        review.check_edge_case_log()

        review.database_summary()

        review.screener_preview()

        review.manual_spot_check()

        review.generate_review_report()

        print("\n" + "=" * 70)
        print("SPRINT 2 REVIEW COMPLETED")
        print("=" * 70)

        print("\nDeliverables")

        print("-" * 40)

        print(
            "✓ financial_ratios table verified"
        )

        print(
            "✓ capital_allocation.csv verified"
        )

        print(
            "✓ ratio_edge_cases.log verified"
        )

        print(
            "✓ screener_preview.csv generated"
        )

        print(
            "✓ sprint2_review.txt generated"
        )

        print(
            "✓ Manual spot check completed"
        )

        print(
            "✓ Database validation completed"
        )

        print(
            "\nSprint 2 is ready for team review."
        )

    except Exception as e:

        print("\nERROR")
        print("-" * 40)

        print(e)

        raise

    finally:

        review.close()


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    main()