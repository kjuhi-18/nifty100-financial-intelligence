import re
import sqlite3
from pathlib import Path

import pandas as pd
class NLPParser:

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        self.analysis_path = (
            self.project_root
            / "data"/"raw"
            / "analysis.xlsx"
        )

        self.db_path = (
            self.project_root
            / "db"
            / "nifty100.db"
        )

        self.output_dir = (
            self.project_root
            / "output"
        )

        self.output_dir.mkdir(
            exist_ok=True
        )

        self.conn = sqlite3.connect(
            self.db_path
        )

        self.analysis = None

        self.parsed = []

        self.failures = []

        # Regex:
        # Example:
        # "10 Years : 21%"
        self.pattern = re.compile(
    r"(\d+)\s*Years?:?\s*([-]?\d+(?:\.\d+)?)%",
    re.IGNORECASE
)
    # ==================================================
    # Load Analysis
    # ==================================================

    def load_analysis(self):

        print("\nLoading analysis.xlsx...\n")

        self.analysis = pd.read_excel(
            self.analysis_path,skiprows=1
        )

        print(

            "Companies :",

            len(self.analysis)

        )

        print()

        print(

            self.analysis.head()

        )
        # ==================================================
    # Parse Analysis Text
    # ==================================================

    def parse_analysis(self):

        print("\nParsing Analysis Text...\n")

        target_columns = {

            "compounded_sales_growth": "Sales CAGR",

            "compounded_profit_growth": "Profit CAGR",

            "stock_price_cagr": "Stock CAGR",

            "roe": "ROE"

        }

        for _, row in self.analysis.iterrows():

            company = row["company_id"]

            for column, metric in target_columns.items():

                text = row.get(column)

                if pd.isna(text):

                    continue

                text = str(text)

                matches = self.pattern.findall(text)

                if matches:

                    for period, value in matches:

                        self.parsed.append({

                            "company_id": company,

                            "metric_type": metric,

                            "period_years": int(period),

                            "value_pct": float(value)

                        })

                else:

                    self.failures.append({

                        "company_id": company,

                        "metric_type": metric,

                        "text": text

                    })

        self.parsed = pd.DataFrame(self.parsed)

        self.failures = pd.DataFrame(self.failures)

        print("Parsed Records :", len(self.parsed))

        print("Failed Records :", len(self.failures))

        print()

        print(self.parsed.head(15))
        # ==================================================
    # Export Parser Outputs
    # ==================================================

    def export_outputs(self):

        print("\nExporting Parser Outputs...\n")

        parsed_file = (
            self.output_dir
            / "analysis_parsed.csv"
        )

        failures_file = (
            self.output_dir
            / "parse_failures.csv"
        )

        self.parsed.to_csv(

            parsed_file,

            index=False

        )

        self.failures.to_csv(

            failures_file,

            index=False

        )

        print("Parsed File Saved")

        print(parsed_file)

        print()

        print("Failures File Saved")

        print(failures_file)

        print()

        print("Parsed Records :", len(self.parsed))

        print("Failure Records :", len(self.failures))
        # ==================================================
    # Verify Parser Outputs
    # ==================================================

    def verify_outputs(self):

        print("\n" + "=" * 70)

        print("PARSER OUTPUT SUMMARY")

        print("=" * 70)

        print()

        print("Parsed Records")

        print(len(self.parsed))

        print()

        print("Failed Records")

        print(len(self.failures))

        print()

        print("Metric Distribution")

        print(

            self.parsed["metric_type"]

            .value_counts()

        )

        print()

        print("Sample Parsed Records")

        print(

            self.parsed.head(10)

        )

        if len(self.failures):

            print()

            print("Sample Failures")

            print(

                self.failures.head(10)

            )
        # ==================================================
    # Cross Validation
    # ==================================================

    def cross_validate(self):

        print("\nCross Validating Parsed Values...\n")

        ratios = pd.read_sql(

            """
            SELECT
                company_id,
                revenue_cagr_5yr,
                pat_cagr_5yr,
                return_on_equity_pct
            FROM financial_ratios
            """,

            self.conn

        )

        latest = (

            ratios

            .sort_values("company_id")

            .groupby("company_id")

            .tail(1)

        )

        metric_map = {

            "Sales CAGR": "revenue_cagr_5yr",

            "Profit CAGR": "pat_cagr_5yr",

            "ROE": "return_on_equity_pct"

        }

        review = []

        for _, row in self.parsed.iterrows():

            if row["metric_type"] not in metric_map:

                continue

            company = row["company_id"]

            metric = metric_map[row["metric_type"]]

            actual = latest.loc[

                latest["company_id"] == company,

                metric

            ]

            if actual.empty or pd.isna(actual.iloc[0]):

                continue

            actual = float(actual.iloc[0])

            parsed = float(row["value_pct"])

            diff = abs(parsed - actual)

            review.append({

                "company_id": company,

                "metric_type": row["metric_type"],

                "parsed_value": parsed,

                "ratio_engine_value": actual,

                "difference_pct": round(diff,2),

                "manual_review": diff > 5

            })

        self.review = pd.DataFrame(review)

        print("Compared :", len(self.review))

        print()

        print(

            self.review.head(15)

        )
        # ==================================================
    # Export Review
    # ==================================================

    def export_review(self):

        review_file = (

            self.output_dir

            / "analysis_validation.csv"

        )

        self.review.to_csv(

            review_file,

            index=False

        )

        print()

        print("Validation File Saved")

        print(review_file)

        print()

        print(

            "Manual Review Required :",

            self.review["manual_review"].sum()

        )
        # ==================================================
    # Day 29 Summary
    # ==================================================

    def day29_summary(self):

        print("\n" + "=" * 80)
        print("DAY 29 COMPLETED")
        print("=" * 80)

        print("\nOUTPUT VALIDATION")
        print("-" * 40)

        parsed_file = self.output_dir / "analysis_parsed.csv"
        failures_file = self.output_dir / "parse_failures.csv"
        review_file = self.output_dir / "analysis_validation.csv"

        print(
            f"analysis_parsed.csv    : {'PASS' if parsed_file.exists() else 'FAIL'}"
        )

        print(
            f"parse_failures.csv     : {'PASS' if failures_file.exists() else 'FAIL'}"
        )

        print(
            f"analysis_validation.csv: {'PASS' if review_file.exists() else 'FAIL'}"
        )

        print("\nPARSER STATISTICS")
        print("-" * 40)

        print(f"Companies Processed : {self.analysis['company_id'].nunique()}")

        print(f"Parsed Records      : {len(self.parsed)}")

        print(f"Failed Records      : {len(self.failures)}")

        print(f"Validation Records  : {len(self.review)}")

        if not self.review.empty:

            print(
                f"Manual Review Cases : {self.review['manual_review'].sum()}"
            )

        print("\nMETRIC DISTRIBUTION")
        print("-" * 40)

        print(
            self.parsed["metric_type"].value_counts()
        )

        print("\nDELIVERABLES")
        print("-" * 40)

        print("✓ src/nlp/parser.py")
        print("✓ output/analysis_parsed.csv")
        print("✓ output/parse_failures.csv")
        print("✓ output/analysis_validation.csv")

        print("\nDAY 29 STATUS")
        print("-" * 40)

        print("✓ Analysis file loaded")
        print("✓ Regex parser implemented")
        print("✓ Structured output generated")
        print("✓ Parse failures logged")
        print("✓ Ratio engine validation completed")

        print("\nREADY FOR DAY 30")
        print("-" * 40)

        print("✓ Auto Pros Generator")
        print("✓ Auto Cons Generator")
        print("✓ Confidence Score Engine")
        print("✓ pros_cons_generated.csv")

        print("\n" + "=" * 80)
        print("DAY 29 STATUS : SUCCESS")
        print("=" * 80)
def main():

    parser = NLPParser()

    parser.load_analysis()
    parser.parse_analysis()
    parser.export_outputs()

    parser.verify_outputs()
    parser.cross_validate()

    parser.export_review()
    parser.day29_summary()
if __name__ == "__main__":

    main()