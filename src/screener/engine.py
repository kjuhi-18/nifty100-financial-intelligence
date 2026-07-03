import sys
import sqlite3
import yaml

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

CONFIG_PATH = ROOT / "config" / "screener_config.yaml"

OUTPUT_DIR = ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


# ==========================================================
# Screener Engine
# ==========================================================

class ScreenerEngine:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.cursor = self.conn.cursor()

        self.config = None

        self.data = None

        self.financial_ratios = None

        self.market_cap = None

        self.sectors = None

        self.companies = None

        self.profit_loss = None


# ==========================================================
# Load YAML Configuration
# ==========================================================

    def load_config(self):

        print("\nLoading screener configuration...\n")

        with open(

            CONFIG_PATH,

            "r",

            encoding="utf-8"

        ) as file:

            self.config = yaml.safe_load(file)
            

        print("Configuration loaded.")


# ==========================================================
# Load Database Tables
# ==========================================================

    def load_tables(self):

        print("\nLoading database tables...\n")

        self.financial_ratios = pd.read_sql(

            "SELECT * FROM financial_ratios",

            self.conn

        )

        self.profit_loss = pd.read_sql(

            "SELECT * FROM profitandloss",

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

        try:

            self.market_cap = pd.read_sql(

                "SELECT * FROM market_cap",

                self.conn

            )

        except Exception:

            self.market_cap = pd.DataFrame()

        print(f"Financial Ratios : {len(self.financial_ratios)}")
        print(f"Profit & Loss    : {len(self.profit_loss)}")
        print(f"Companies        : {len(self.companies)}")
        print(f"Sectors          : {len(self.sectors)}")
        print(f"Market Cap       : {len(self.market_cap)}")
# ==========================================================
# Prepare Master Dataset
# ==========================================================

    def prepare_dataset(self):

        print("\nPreparing screener dataset...\n")

        self.data = self.financial_ratios.merge(

            self.profit_loss[

                [

                    "company_id",

                    "year",

                    "sales",

                    "net_profit",

                    "operating_profit"

                ]

            ],

            on=[

                "company_id",

                "year"

            ],

            how="left"

        )

        self.data = self.data.merge(

            self.sectors[

                [

                    "company_id",

                    "broad_sector"

                ]

            ],

            on="company_id",

            how="left"

        )

        if not self.market_cap.empty:

            columns = self.market_cap.columns.tolist()

            if "market_cap" in columns:

                self.data = self.data.merge(

                    self.market_cap[

                        [

                            "company_id",

                            "market_cap"

                        ]

                    ],

                    on="company_id",

                    how="left"

                )

        print(

            f"Rows    : {len(self.data)}"

        )

        print(

            f"Columns : {len(self.data.columns)}"

        )

        print()

        print(

            self.data.head()

        )


# ==========================================================
# Generic Threshold Filter
# ==========================================================

    def apply_filter(

        self,

        dataframe,

        column,

        value,

        operator

    ):

        if column not in dataframe.columns:

            return dataframe

        if operator == ">=":

            dataframe = dataframe[

                dataframe[column] >= value

            ]

        elif operator == "<=":

            dataframe = dataframe[

                dataframe[column] <= value

            ]

        elif operator == ">":

            dataframe = dataframe[

                dataframe[column] > value

            ]

        elif operator == "<":

            dataframe = dataframe[

                dataframe[column] < value

            ]

        elif operator == "==":

            dataframe = dataframe[

                dataframe[column] == value

            ]

        return dataframe


# ==========================================================
# Apply Config Filters
# ==========================================================

    def apply_config_filters(self):

        print("\nApplying configured filters...\n")

        df = self.data.copy()

        filters = self.config["filters"]

        if filters["roe_min"]["enabled"]:

            df = self.apply_filter(

                df,

                "return_on_equity_pct",

                filters["roe_min"]["value"],

                ">="

            )

        if filters["free_cash_flow_min"]["enabled"]:

            df = self.apply_filter(

                df,

                "free_cash_flow_cr",

                filters["free_cash_flow_min"]["value"],

                ">="

            )

        if filters["revenue_cagr_5yr_min"]["enabled"]:

            df = self.apply_filter(

                df,

                "revenue_cagr_5yr",

                filters["revenue_cagr_5yr_min"]["value"],

                ">="

            )

        if filters["pat_cagr_5yr_min"]["enabled"]:

            df = self.apply_filter(

                df,

                "pat_cagr_5yr",

                filters["pat_cagr_5yr_min"]["value"],

                ">="

            )

        if filters["operating_profit_margin_min"]["enabled"]:

            df = self.apply_filter(

                df,

                "operating_profit_margin_pct",

                filters["operating_profit_margin_min"]["value"],

                ">="

            )

        if filters["interest_coverage_min"]["enabled"]:

            df = self.apply_filter(

                df,

                "interest_coverage",

                filters["interest_coverage_min"]["value"],

                ">="

            )

        if filters["asset_turnover_min"]["enabled"]:

            df = self.apply_filter(

                df,

                "asset_turnover",

                filters["asset_turnover_min"]["value"],

                ">="

            )

        if filters["sales_min"]["enabled"]:

            df = self.apply_filter(

                df,

                "sales",

                filters["sales_min"]["value"],

                ">="

            )

        if filters["net_profit_min"]["enabled"]:

            df = self.apply_filter(

                df,

                "net_profit",

                filters["net_profit_min"]["value"],

                ">="

            )

        if filters["eps_cagr_5yr_min"]["enabled"]:

            df = self.apply_filter(

                df,

                "eps_cagr_5yr",

                filters["eps_cagr_5yr_min"]["value"],

                ">="

            )

        self.filtered_data = df

        print(

            f"Filtered Rows : {len(df)}"

        )
# ==========================================================
# Financial Sector D/E Exception
# ==========================================================

    def apply_debt_to_equity_filter(self):

        filters = self.config["filters"]

        if not filters["debt_to_equity_max"]["enabled"]:

            return

        print("\nApplying Debt-to-Equity filter...\n")

        limit = filters["debt_to_equity_max"]["value"]

        financials = self.filtered_data[

            self.filtered_data["broad_sector"] == "Financials"

        ]

        non_financials = self.filtered_data[

            self.filtered_data["broad_sector"] != "Financials"

        ]

        non_financials = non_financials[

            non_financials["debt_to_equity"] <= limit

        ]

        self.filtered_data = pd.concat(

            [

                financials,

                non_financials

            ],

            ignore_index=True

        )

        print(

            f"Rows after D/E filter : {len(self.filtered_data)}"

        )


# ==========================================================
# Interest Coverage Filter
# Debt Free = Infinity
# ==========================================================

    def apply_interest_coverage_logic(self):

        filters = self.config["filters"]

        if not filters["interest_coverage_min"]["enabled"]:

            return

        print("\nApplying Interest Coverage filter...\n")

        minimum = filters["interest_coverage_min"]["value"]

        df = self.filtered_data.copy()

        df["interest_coverage"] = (

            df["interest_coverage"]

            .replace(

                "Debt Free",

                float("inf")

            )

        )

        df["interest_coverage"] = pd.to_numeric(

            df["interest_coverage"],

            errors="coerce"

        )

        df = df[

            df["interest_coverage"] >= minimum

        ]

        self.filtered_data = df

        print(

            f"Rows after ICR filter : {len(df)}"

        )


# ==========================================================
# Optional Filters
# ==========================================================

    def apply_optional_filters(self):

        filters = self.config["filters"]

        df = self.filtered_data.copy()

        optional_filters = [

            ("market_cap", "market_cap_min", ">="),

            ("pe_ratio", "pe_max", "<="),

            ("pb_ratio", "pb_max", "<="),

            ("dividend_yield", "dividend_yield_min", ">=")

        ]

        for column, config_key, operator in optional_filters:

            if column not in df.columns:

                continue

            if not filters[config_key]["enabled"]:

                continue

            df = self.apply_filter(

                df,

                column,

                filters[config_key]["value"],

                operator

            )

        self.filtered_data = df

        print(

            f"Rows after optional filters : {len(df)}"

        )


# ==========================================================
# Final Sorting
# ==========================================================

    def sort_results(self):

        print("\nSorting results...\n")

        if "composite_quality_score" in self.filtered_data.columns:

            self.filtered_data = self.filtered_data.sort_values(

                "composite_quality_score",

                ascending=False

            )

        elif "return_on_equity_pct" in self.filtered_data.columns:

            self.filtered_data = self.filtered_data.sort_values(

                "return_on_equity_pct",

                ascending=False

            )

        self.filtered_data = self.filtered_data.reset_index(

            drop=True

        )

        print(

            self.filtered_data.head(10)

        )
# ==========================================================
# Screener Summary
# ==========================================================

    def screener_summary(self):

        print("\n" + "=" * 60)
        print("SCREENER SUMMARY")
        print("=" * 60)

        print(f"Companies Selected : {len(self.filtered_data)}")

        if len(self.filtered_data) == 0:

            print("\nNo companies matched the filters.")
            return

        latest = self.filtered_data.copy()

        if "year" in latest.columns:

            latest = latest.sort_values(
                ["company_id", "year"]
            )

        print("\nTop 10 Companies\n")

        preview_columns = [

            "company_id",
            "year",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "composite_quality_score"

        ]

        preview_columns = [

            c for c in preview_columns
            if c in latest.columns

        ]

        print(

            latest[preview_columns]

            .head(10)

            .to_string(index=False)

        )


# ==========================================================
# Export Results
# ==========================================================

    def export_results(self):

        print("\nExporting screener results...\n")

        output_file = OUTPUT_DIR / "screener_results.csv"

        self.filtered_data.to_csv(

            output_file,

            index=False

        )

        print(

            f"Saved : {output_file}"

        )


# ==========================================================
# Verification
# ==========================================================

    def verify_results(self):

        print("\n" + "=" * 60)
        print("VERIFICATION")
        print("=" * 60)

        print(

            f"Rows Returned : {len(self.filtered_data)}"

        )

        print(

            f"Columns : {len(self.filtered_data.columns)}"

        )

        required = [

            "company_id",
            "year",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "composite_quality_score"

        ]

        print("\nChecking required columns...\n")

        for column in required:

            if column in self.filtered_data.columns:

                print(f"{column:<35} PASS")

            else:

                print(f"{column:<35} MISSING")

        print("\nChecking duplicate rows...\n")

        duplicates = self.filtered_data.duplicated(

            subset=[

                "company_id",

                "year"

            ]

        ).sum()

        print(

            f"Duplicate Company-Year Rows : {duplicates}"

        )

        print("\nChecking NULL counts...\n")

        nulls = self.filtered_data[required].isna().sum()

        print(nulls)

        print("\nVerification Complete.")
# ==========================================================
# Close Connection
# ==========================================================

    def close(self):

        if self.conn:

            self.conn.close()


# ==========================================================
# Main
# ==========================================================

def main():

    engine = ScreenerEngine()

    try:

        engine.load_config()

        engine.load_tables()

        engine.prepare_dataset()

        engine.apply_config_filters()

        engine.apply_debt_to_equity_filter()

        engine.apply_interest_coverage_logic()

        engine.apply_optional_filters()

        engine.sort_results()

        engine.screener_summary()

        engine.export_results()

        engine.verify_results()

        print("\n" + "=" * 70)
        print("SPRINT 3 - DAY 15 COMPLETED")
        print("=" * 70)

        print("\nDeliverables")
        print("-" * 40)

        print("✓ Configuration loaded")

        print("✓ Database tables loaded")

        print("✓ Screener dataset prepared")

        print("✓ Threshold filters applied")

        print("✓ Financial sector D/E exception handled")

        print("✓ Debt Free ICR handled")

        print("✓ Results sorted")

        print("✓ screener_results.csv generated")

        print("✓ Verification completed")

        print("\nReady for Day 16")

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