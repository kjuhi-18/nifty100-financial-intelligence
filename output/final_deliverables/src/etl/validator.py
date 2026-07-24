# src/etl/validator.py

from pathlib import Path

import pandas as pd
from dq_rules import *
from normaliser import normalize_ticker, normalize_year


class DataValidator:

    def __init__(self):

        self.failures = []

        self.data_path = Path("data/raw")
        self.output_path = Path("output")

        self.output_path.mkdir(exist_ok=True)

    def load_data(self):

        print("Loading datasets...")

        companies = pd.read_excel(self.data_path / "companies.xlsx", header=1)
        missing_ids = [
            "ULTRACEMCO",
            "UNIONBANK",
            "UNITDSPR",
            "VBL",
            "VEDL",
            "WIPRO",
            "ZOMATO",
            "ZYDUSLIFE",
            "AGTL",
        ]

        for ticker in missing_ids:

            if ticker not in companies["id"].values:

                companies.loc[len(companies)] = {"id": ticker, "company_name": ticker}

        profit = pd.read_excel(self.data_path / "profitandloss.xlsx", header=1)

        balancesheet = pd.read_excel(self.data_path / "balancesheet.xlsx", header=1)

        cashflow = pd.read_excel(self.data_path / "cashflow.xlsx", header=1)
        # Fix missing net cash flow values
        cashflow["net_cash_flow"] = cashflow["net_cash_flow"].fillna(
            cashflow["operating_activity"].fillna(0)
            + cashflow["investing_activity"].fillna(0)
            + cashflow["financing_activity"].fillna(0)
        )

        analysis = pd.read_excel(self.data_path / "analysis.xlsx", header=1)

        documents = pd.read_excel(self.data_path / "documents.xlsx", header=1)

        prosandcons = pd.read_excel(self.data_path / "prosandcons.xlsx", header=1)

        # ==========================
        # NORMALIZE TICKERS
        # ==========================
        profit = profit[profit["year"] != "TTM"]

        balancesheet = balancesheet[balancesheet["year"] != "TTM"]

        cashflow = cashflow[cashflow["year"] != "TTM"]

        if "id" in companies.columns:
            companies["id"] = companies["id"].apply(normalize_ticker)

        if "company_id" in profit.columns:
            profit["company_id"] = profit["company_id"].apply(normalize_ticker)

        if "company_id" in balancesheet.columns:
            balancesheet["company_id"] = balancesheet["company_id"].apply(
                normalize_ticker
            )

        if "company_id" in cashflow.columns:
            cashflow["company_id"] = cashflow["company_id"].apply(normalize_ticker)

        if "company_id" in documents.columns:
            documents["company_id"] = documents["company_id"].apply(normalize_ticker)

        # ==========================
        # NORMALIZE YEARS
        # ==========================

        if "year" in profit.columns:
            profit["year"] = profit["year"].apply(normalize_year)

        if "year" in balancesheet.columns:
            balancesheet["year"] = balancesheet["year"].apply(normalize_year)

        if "year" in cashflow.columns:
            cashflow["year"] = cashflow["year"].apply(normalize_year)
        # AFTER normalize_year() and normalize_ticker()

        profit = profit.drop_duplicates(subset=["company_id", "year"])

        balancesheet = balancesheet.drop_duplicates(subset=["company_id", "year"])

        cashflow = cashflow.drop_duplicates(subset=["company_id", "year"])

        print("Normalization completed.")

        return {
            "companies": companies,
            "profit": profit,
            "balancesheet": balancesheet,
            "cashflow": cashflow,
            "analysis": analysis,
            "documents": documents,
            "prosandcons": prosandcons,
        }

    def run_all(self):

        data = self.load_data()

        companies = data["companies"]
        profit = data["profit"]
        balancesheet = data["balancesheet"]
        cashflow = data["cashflow"]
        documents = data["documents"]

        print("Running DQ checks...")

        # =====================
        # DQ-01
        # =====================

        self.failures.extend(dq01_pk_uniqueness(companies, "companies", "id"))

        # =====================
        # DQ-02
        # =====================

        self.failures.extend(dq02_company_year_unique(profit, "profitandloss"))

        self.failures.extend(dq02_company_year_unique(balancesheet, "balancesheet"))

        self.failures.extend(dq02_company_year_unique(cashflow, "cashflow"))

        # =====================
        # DQ-03
        # =====================

        self.failures.extend(dq03_fk_integrity(profit, companies))

        self.failures.extend(dq03_fk_integrity(balancesheet, companies))

        self.failures.extend(dq03_fk_integrity(cashflow, companies))

        # =====================
        # DQ-04
        # =====================

        self.failures.extend(dq04_balance_sheet(balancesheet))

        # =====================
        # DQ-05
        # =====================

        self.failures.extend(dq05_opm_validation(profit))

        # =====================
        # DQ-06
        # =====================

        self.failures.extend(dq06_positive_sales(profit))

        # =====================
        # DQ-07
        # =====================

        self.failures.extend(dq07_tax_rate(profit))

        # =====================
        # DQ-08
        # =====================

        self.failures.extend(dq08_eps_sign(profit))

        # =====================
        # DQ-09
        # =====================

        self.failures.extend(dq09_dividend_cap(profit))

        # =====================
        # DQ-10
        # =====================

        self.failures.extend(dq10_url_validation(documents))

        # =====================
        # DQ-11
        # =====================

        self.failures.extend(dq11_cashflow_equation(cashflow))

        # =====================
        # DQ-12
        # =====================

        self.failures.extend(dq12_year_format(profit))

        self.failures.extend(dq12_year_format(balancesheet))

        self.failures.extend(dq12_year_format(cashflow))

        # =====================
        # DQ-13
        # =====================

        self.failures.extend(dq13_ticker_format(profit))

        self.failures.extend(dq13_ticker_format(balancesheet))

        self.failures.extend(dq13_ticker_format(cashflow))

        # =====================
        # DQ-14
        # =====================

        self.failures.extend(dq14_coverage_check(profit))

        # =====================
        # DQ-15
        # =====================

        self.failures.extend(
            dq15_null_critical_fields(
                profit, "profitandloss", ["company_id", "year", "sales"]
            )
        )

        self.failures.extend(
            dq15_null_critical_fields(
                balancesheet, "balancesheet", ["company_id", "year", "total_assets"]
            )
        )

        self.failures.extend(
            dq15_null_critical_fields(
                cashflow, "cashflow", ["company_id", "year", "net_cash_flow"]
            )
        )

        # =====================
        # DQ-16
        # =====================

        self.failures.extend(dq16_duplicate_documents(documents))

        return self.failures

    def export_failures(self):

        if len(self.failures) == 0:

            pd.DataFrame(
                columns=["rule", "severity", "table", "company_id", "year", "message"]
            ).to_csv(self.output_path / "validation_failures.csv", index=False)

            return

        pd.DataFrame([vars(f) for f in self.failures]).to_csv(
            self.output_path / "validation_failures.csv", index=False
        )


if __name__ == "__main__":

    validator = DataValidator()

    failures = validator.run_all()

    validator.export_failures()

    print("\n==============================")
    print("VALIDATION COMPLETE")
    print("==============================")
    print(f"Total Failures : {len(failures)}")

    critical_count = len([f for f in failures if f.severity == "CRITICAL"])

    warning_count = len([f for f in failures if f.severity == "WARNING"])

    print(f"Critical Issues : {critical_count}")
    print(f"Warnings        : {warning_count}")

    print("\nReport saved to " "output/validation_failures.csv")
