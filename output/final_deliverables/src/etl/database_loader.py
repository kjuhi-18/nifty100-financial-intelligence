import sqlite3
import sys
from pathlib import Path

import pandas as pd

# =====================================================
# PROJECT PATHS
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT))

from src.etl.loader import ExcelLoader

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_PATH = PROJECT_ROOT / "output"


# =====================================================
# DATABASE LOADER
# =====================================================


class DatabaseLoader:

    def __init__(self):

        self.loader = ExcelLoader()

        self.conn = sqlite3.connect(DB_PATH)

        self.conn.execute("PRAGMA foreign_keys = ON;")

        self.audit = []

    # =================================================
    # LOAD TABLE
    # =================================================

    def load_table(self, file_name, table_name, header=1):

        print(f"\nLoading {table_name}...")

        df = self.loader.load_excel(file_name, header=header)

        removed = 0
        fk_removed = 0

        if table_name != "companies" and "company_id" in df.columns:

            valid_ids = pd.read_sql("SELECT id FROM companies", self.conn)["id"]

            before_fk = len(df)

            df = df[df["company_id"].isin(valid_ids)]

            fk_removed = before_fk - len(df)

            if fk_removed > 0:

                print(f"Removed {fk_removed} FK-invalid rows")

        # ---------------------------------------------
        # Remove duplicates for financial tables
        # ---------------------------------------------

        if table_name in ["profitandloss", "balancesheet", "cashflow"]:

            before = len(df)

            df = df.drop_duplicates(subset=["company_id", "year"])

            removed = before - len(df)

            if removed > 0:

                print(f"Removed {removed} duplicate rows")

        rows_loaded = len(df)
        if table_name == "financial_ratios":

            before = len(df)

            df = df.drop_duplicates(subset=["company_id", "year"], keep="first")

            removed = before - len(df)

            if removed:
                print(f"Removed {removed} duplicate rows")
        # ---------------------------------------------
        # Insert into SQLite
        # ---------------------------------------------
        print("\nColumns being inserted:")
        print(df.columns.tolist())

        print("\nFirst row:")
        print(df.head(1))
        df.to_sql(table_name, self.conn, if_exists="append", index=False)

        # ---------------------------------------------
        # Audit
        # ---------------------------------------------

        self.audit.append(
            {
                "table_name": table_name,
                "rows_loaded": rows_loaded,
                "rejected_rows": removed + fk_removed,
            }
        )

        print(f"Loaded {rows_loaded} rows")

    # =================================================
    # GENERATE AUDIT
    # =================================================

    def generate_audit(self):

        OUTPUT_PATH.mkdir(exist_ok=True)

        audit_df = pd.DataFrame(self.audit)

        audit_df.to_csv(OUTPUT_PATH / "load_audit.csv", index=False)

        print("\nCreated output/load_audit.csv")

    # =================================================
    # VERIFY COUNTS
    # =================================================

    def verify_counts(self):

        print("\n" + "=" * 50)
        print("TABLE COUNTS")
        print("=" * 50)

        cursor = self.conn.cursor()

        tables = ["companies", "profitandloss", "balancesheet", "cashflow"]

        for table in tables:

            count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

            print(f"{table:<20} {count}")

    # =================================================
    # FK CHECK
    # =================================================

    def foreign_key_check(self):

        result = self.conn.execute("PRAGMA foreign_key_check;").fetchall()

        print("\n" + "=" * 50)
        print("FOREIGN KEY CHECK")
        print("=" * 50)

        if len(result) == 0:

            print("PASS : No FK violations")

        else:

            print(f"FAIL : {len(result)} FK violations")

    # =================================================
    # CLOSE
    # =================================================

    def close(self):

        self.conn.commit()

        self.conn.close()


# =====================================================
# MAIN
# =====================================================


def main():

    db = DatabaseLoader()

    # ---------------------------------------------
    # Core Tables
    # ---------------------------------------------

    db.load_table("companies.xlsx", "companies")

    db.load_table("profitandloss.xlsx", "profitandloss")

    db.load_table("balancesheet.xlsx", "balancesheet")

    db.load_table("cashflow.xlsx", "cashflow")
    db.load_table("analysis.xlsx", "analysis")

    db.load_table("documents.xlsx", "documents")

    db.load_table("prosandcons.xlsx", "prosandcons")

    db.load_table("sectors.xlsx", "sectors", header=0)

    db.load_table("stock_prices.xlsx", "stock_prices", header=0)

    db.load_table("financial_ratios.xlsx", "financial_ratios", header=0)

    db.load_table("market_cap.xlsx", "market_cap", header=0)

    db.load_table("peer_groups.xlsx", "peer_groups", header=0)

    # ---------------------------------------------
    # Reports
    # ---------------------------------------------

    db.generate_audit()

    db.verify_counts()

    db.foreign_key_check()

    db.close()

    print("\nPhase 1 Load Complete")


if __name__ == "__main__":
    main()
