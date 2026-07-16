import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


class ValuationEngine:

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        self.db_path = self.project_root / "db" / "nifty100.db"

        self.market_cap_path = self.project_root / "data" / "raw"/ "market_cap.xlsx"

        self.output_dir = self.project_root / "output"

        self.conn = sqlite3.connect(self.db_path)

        self.market_df = None
        self.ratios = None
        self.companies = None
        self.sectors = None
        self.latest = None
        self.valuation = None
        # =====================================================
    # Load Source Data
    # =====================================================

    def load_data(self):

        print("\nLoading source tables...\n")

        self.market_df = pd.read_excel(
        self.market_cap_path
    )

        self.ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        self.conn
    )

        self.companies = pd.read_excel(
        self.project_root / "data" / "raw"/"companies.xlsx",
        skiprows=1
    )

        self.sectors = pd.read_excel(
        self.project_root / "data" / "raw"/"sectors.xlsx"
    )

        print(f"Market Cap : {len(self.market_df)}")
        print(f"Ratios     : {len(self.ratios)}")
        print(f"Companies  : {len(self.companies)}")
        print(f"Sectors    : {len(self.sectors)}")
# =====================================================
# Latest Snapshot
# =====================================================

    def prepare_latest_snapshot(self):

        print("\nPreparing latest company snapshot...\n")

        # Latest year from market cap file
        latest_year = self.market_df["year"].max()

        market = (
        self.market_df[
            self.market_df["year"] == latest_year
        ]
        .copy()
        .drop(columns=["id"], errors="ignore")
        )

        # Latest financial ratios
        ratios = (
        self.ratios
        .sort_values("year")
        .groupby("company_id")
        .tail(1)
        .drop(columns=["id"], errors="ignore")
        )

    # Companies
        companies = (
        self.companies
        .copy()
        .drop(columns=["roce_percentage", "roe_percentage"], errors="ignore")
        )

    # Sectors
        sectors = (
        self.sectors
        .copy()
        .drop(columns=["id"], errors="ignore")
    )

    # Merge everything
        self.latest = (

        market

        .merge(
            ratios,
            on="company_id",
            how="left"
        )

        .merge(
            companies,
            left_on="company_id",
            right_on="id",
            how="left"
        )

        .drop(columns=["id"], errors="ignore")

        .merge(
            sectors,
            on="company_id",
            how="left"
        )

    )

        print(f"Latest Companies : {len(self.latest)}")

        print()

        print(self.latest.head())

        print()

        print(self.latest.columns.tolist())
    # =====================================================
# Compute Valuation Metrics
# =====================================================

    def compute_valuation(self):

        print("\nComputing Valuation Metrics...\n")

        df = self.latest.copy()

    # -------------------------------------------------
    # FCF Yield %
    # -------------------------------------------------

        df["fcf_yield_pct"] = (
        df["free_cash_flow_cr"]
        / df["market_cap_crore"]
    ) * 100

    # -------------------------------------------------
    # Sector Median PE
    # -------------------------------------------------

        sector_pe = (
        df.groupby("broad_sector")["pe_ratio"]
        .median()
        .reset_index()
        .rename(columns={
            "pe_ratio": "sector_median_pe"
        })
    )

        df = df.merge(
        sector_pe,
        on="broad_sector",
        how="left"
    )

    # -------------------------------------------------
    # Company 5-Year Median PE
    # -------------------------------------------------

        median_pe = (
        self.market_df
        .groupby("company_id")["pe_ratio"]
        .median()
        .reset_index()
        .rename(columns={
            "pe_ratio": "median_pe_5yr"
        })
    )

        df = df.merge(
        median_pe,
        on="company_id",
        how="left"
    )

    # -------------------------------------------------
    # PE vs Sector Median
    # -------------------------------------------------

        df["pe_vs_sector_median_pct"] = (
        df["pe_ratio"]
        / df["sector_median_pe"]
    ) * 100

    # -------------------------------------------------
    # Valuation Flag
    # -------------------------------------------------

        df["flag"] = "Fair"

        df.loc[
        df["pe_ratio"] > df["sector_median_pe"] * 1.5,
        "flag"
    ] = "Caution"

        df.loc[
        df["pe_ratio"] < df["sector_median_pe"] * 0.7,
        "flag"
    ] = "Discount"

        self.valuation = df

        print("Valuation Completed Successfully.\n")
# =====================================================
# Preview
# =====================================================

    def preview_valuation(self):

        print("\n" + "=" * 70)
        print("VALUATION PREVIEW")
        print("=" * 70)

        print(
        self.valuation[
            [
                "company_id",
                "company_name",
                "broad_sector",
                "market_cap_crore",
                "pe_ratio",
                "pb_ratio",
                "ev_ebitda",
                "fcf_yield_pct",
                "sector_median_pe",
                "median_pe_5yr",
                "pe_vs_sector_median_pct",
                "flag"
            ]
        ].head(15)
    )

        print("\nFlag Distribution\n")

        print(
        self.valuation["flag"].value_counts()
    )

        print("\nCompanies :", len(self.valuation))
    # =====================================================
# Export Valuation Outputs
# =====================================================

    def export_outputs(self):

        print("\nExporting valuation reports...\n")

        output = self.valuation.copy()

        export_columns = [

        "company_id",

        "company_name",

        "broad_sector",

        "pe_ratio",

        "pb_ratio",

        "ev_ebitda",

        "fcf_yield_pct",

        "median_pe_5yr",

        "pe_vs_sector_median_pct",

        "flag"

    ]

        output = output[export_columns]

        output = output.rename(columns={

        "broad_sector": "sector",

        "pe_ratio": "P/E",

        "pb_ratio": "P/B",

        "ev_ebitda": "EV/EBITDA",

        "fcf_yield_pct": "FCF_yield_pct",

        "median_pe_5yr": "5yr_median_PE",

        "pe_vs_sector_median_pct": "PE_vs_sector_median_pct"

    })

        summary_file = self.output_dir / "valuation_summary.xlsx"

        output.to_excel(

        summary_file,

        index=False

    )

        flags = output[

        output["flag"] != "Fair"

    ].copy()

        flags_file = self.output_dir / "valuation_flags.csv"

        flags.to_csv(

        flags_file,

        index=False

    )

        print("Valuation Summary Saved")

        print(summary_file)

        print()

        print("Valuation Flags Saved")

        print(flags_file)

        self.summary_output = output

        self.flags_output = flags
    # =====================================================
# Export Verification
# =====================================================

    def verify_exports(self):

        print("\n" + "=" * 70)

        print("VALUATION EXPORT SUMMARY")

        print("=" * 70)

        print()

        print("Total Companies :", len(self.summary_output))

        print("Flags :", len(self.flags_output))

        print()

        print(self.summary_output.head(10))

        print()

        print("Flag Distribution")

        print(

        self.summary_output["flag"]

        .value_counts()

    )
# =====================================================
# Day 26 Validation
# =====================================================

    def validate_outputs(self):

        print("\n" + "=" * 70)
        print("DAY 26 OUTPUT VALIDATION")
        print("=" * 70)

    # -------------------------------------------------
    # Files
    # -------------------------------------------------

        summary_file = self.output_dir / "valuation_summary.xlsx"
        flags_file = self.output_dir / "valuation_flags.csv"

        print("\nOutput Files")
        print("-" * 40)

        print(
        f"valuation_summary.xlsx : {'PASS' if summary_file.exists() else 'FAIL'}"
    )

        print(
        f"valuation_flags.csv    : {'PASS' if flags_file.exists() else 'FAIL'}"
    )

    # -------------------------------------------------
    # Company Count
    # -------------------------------------------------

        print("\nCompany Validation")
        print("-" * 40)

        print(f"Companies : {len(self.summary_output)}")

        if len(self.summary_output) == 92:
            print("PASS : 92 companies exported")
        else:
            print("FAIL : Company count mismatch")

    # -------------------------------------------------
    # Required Columns
    # -------------------------------------------------

        print("\nColumn Validation")
        print("-" * 40)

        required = [

        "company_id",

        "company_name",

        "sector",

        "P/E",

        "P/B",

        "EV/EBITDA",

        "FCF_yield_pct",

        "5yr_median_PE",

        "PE_vs_sector_median_pct",

        "flag"

    ]

        for col in required:

            if col in self.summary_output.columns:
                print(f"✓ {col}")
            else:
                print(f"✗ {col}")

    # -------------------------------------------------
    # Flags
    # -------------------------------------------------

        print("\nValuation Flags")
        print("-" * 40)

        print(

        self.summary_output["flag"]

        .value_counts()

    )

    # -------------------------------------------------
    # Sector Medians
    # -------------------------------------------------

        print("\nSector Median PE")
        print("-" * 40)

        sector_summary = (

        self.valuation

        .groupby("broad_sector")["sector_median_pe"]

        .first()

        .reset_index()

    )

        print(sector_summary)

    # -------------------------------------------------
    # Preview
    # -------------------------------------------------

        print("\nSample Output")
        print("-" * 40)

        print(

        self.summary_output.head(10)

    )

        print("\nValidation Complete.")
# =====================================================
# Day 26 Summary
# =====================================================

    def day26_summary(self):

        print("\n" + "=" * 80)
        print("DAY 26 COMPLETED")
        print("=" * 80)

        print("\nVALUATION MODULE")
        print("-" * 40)

        print("✓ Latest company snapshot prepared")
        print("✓ Market Cap data loaded")
        print("✓ FCF Yield calculated")
        print("✓ Sector Median P/E calculated")
        print("✓ Company 5-Year Median P/E calculated")
        print("✓ PE vs Sector Median calculated")
        print("✓ Valuation Flags assigned")

        print("\nOUTPUT FILES")
        print("-" * 40)

        print("✓ output/valuation_summary.xlsx")
        print("✓ output/valuation_flags.csv")

        print("\nVALUATION STATISTICS")
        print("-" * 40)

        print(f"Companies Analysed : {len(self.summary_output)}")

        print(f"Fair Companies     : {(self.summary_output['flag'] == 'Fair').sum()}")

        print(f"Discount Companies : {(self.summary_output['flag'] == 'Discount').sum()}")

        print(f"Caution Companies  : {(self.summary_output['flag'] == 'Caution').sum()}")

        print("\nDELIVERABLES")
        print("-" * 40)

        print("✓ src/analytics/valuation.py")
        print("✓ valuation_summary.xlsx")
        print("✓ valuation_flags.csv")

        print("\nREADY FOR DAY 27")
        print("-" * 40)

        print("✓ Dashboard Integration QA")
        print("✓ Screen Testing")
        print("✓ Missing Data Validation")
        print("✓ Performance Testing")
        print("✓ Bug Fixes")

        print("\n" + "=" * 80)
        print("DAY 26 STATUS : SUCCESS")
        print("=" * 80)
def main():
    
    engine = ValuationEngine()

    engine.load_data()

    engine.prepare_latest_snapshot()

    engine.compute_valuation()

    engine.preview_valuation()

    engine.export_outputs()

    engine.verify_exports()

    engine.validate_outputs()
    engine.day26_summary()

if __name__ == "__main__":
    
    main()