from dataclasses import dataclass


@dataclass
class ValidationFailure:
    rule: str
    severity: str
    table: str
    company_id: str
    year: str
    message: str
def dq01_pk_uniqueness(df, table_name, pk_col):
    failures = []

    duplicates = df[df.duplicated(subset=[pk_col], keep=False)]

    for _, row in duplicates.iterrows():
        failures.append(
            ValidationFailure(
                rule="DQ-01",
                severity="CRITICAL",
                table=table_name,
                company_id=str(row.get(pk_col)),
                year="",
                message=f"Duplicate primary key {row.get(pk_col)}"
            )
        )

    return failures
def dq02_company_year_unique(df, table_name):
    failures = []

    duplicates = df[
        df.duplicated(
            subset=["company_id", "year"],
            keep=False
        )
    ]

    for _, row in duplicates.iterrows():
        failures.append(
            ValidationFailure(
                rule="DQ-02",
                severity="CRITICAL",
                table=table_name,
                company_id=row["company_id"],
                year=row["year"],
                message="Duplicate company-year record"
            )
        )

    return failures
def dq03_fk_integrity(df, companies):
    failures = []

    valid_ids = set(companies["id"])

    for _, row in df.iterrows():

        if row["company_id"] not in valid_ids:

            failures.append(
                ValidationFailure(
                    rule="DQ-03",
                    severity="CRITICAL",
                    table="foreign_table",
                    company_id=row["company_id"],
                    year=row.get("year", ""),
                    message="Missing company_id in companies"
                )
            )

    return failures
def dq04_balance_sheet(bs_df):

    failures = []

    for _, row in bs_df.iterrows():

        assets = row["total_assets"]
        liabilities = row["total_liabilities"]

        if assets == 0:
            continue

        diff_pct = abs(
            assets - liabilities
        ) / assets * 100

        if diff_pct > 5:

            failures.append(
                ValidationFailure(
                    rule="DQ-04",
                    severity="WARNING",
                    table="balancesheet",
                    company_id=row["company_id"],
                    year=row["year"],
                    message=f"BS mismatch {diff_pct:.2f}%"
                )
            )

    return failures
def dq05_opm_validation(pl_df):

    failures = []

    for _, row in pl_df.iterrows():

        expected = row["sales"] - row["expenses"]

        if expected == 0:
            continue

        diff_pct = (
            abs(expected-row["operating_profit"])
            / expected
            * 100
        )

        if diff_pct > 1:

            failures.append(
                ValidationFailure(
                    rule="DQ-05",
                    severity="WARNING",
                    table="profitandloss",
                    company_id=row["company_id"],
                    year=row["year"],
                    message=f"OPM mismatch {diff_pct:.2f}%"
                )
            )

    return failures
def dq06_positive_sales(pl_df):

    failures = []

    invalid_rows = pl_df[pl_df["sales"] < 0]

    for _, row in invalid_rows.iterrows():

        failures.append(
            ValidationFailure(
                rule="DQ-06",
                severity="CRITICAL",
                table="profitandloss",
                company_id=row["company_id"],
                year=row["year"],
                message=f"Invalid sales value: {row['sales']}"
            )
        )

    return failures
def dq07_tax_rate(pl_df):

    failures = []

    invalid_rows = pl_df[
        (pl_df["tax_percentage"] < 0)
        | (pl_df["tax_percentage"] > 100)
    ]

    for _, row in invalid_rows.iterrows():

        failures.append(
            ValidationFailure(
                rule="DQ-07",
                severity="WARNING",
                table="profitandloss",
                company_id=row["company_id"],
                year=row["year"],
                message=f"Invalid tax rate: {row['tax_percentage']}"
            )
            
        )

    return failures

def dq08_eps_sign(pl_df):

    failures = []

    invalid_rows = pl_df[
        (pl_df["net_profit"] > 0)
        & (pl_df["eps"] <= 0)
    ]

    for _, row in invalid_rows.iterrows():

        failures.append(
            ValidationFailure(
                rule="DQ-08",
                severity="WARNING",
                table="profitandloss",
                company_id=row["company_id"],
                year=row["year"],
                message="Positive PAT but EPS <= 0"
            )
        )

    return failures
def dq09_dividend_cap(pl_df):

    failures = []

    invalid_rows = pl_df[
        pl_df["dividend_payout"] > 500
    ]

    for _, row in invalid_rows.iterrows():

        failures.append(
            ValidationFailure(
                rule="DQ-09",
                severity="WARNING",
                table="profitandloss",
                company_id=row["company_id"],
                year=row["year"],
                message=f"Dividend payout unusually high: {row['dividend_payout']}"
            )
        )

    return failures
import re


def dq10_url_validation(doc_df):

    failures = []

    pattern = r"^https?://"

    for _, row in doc_df.iterrows():

        url = str(row["Annual_Report"])

        if not re.match(pattern, url):

            failures.append(
                ValidationFailure(
                    rule="DQ-10",
                    severity="WARNING",
                    table="documents",
                    company_id=row["company_id"],
                    year=row["Year"],
                    message=f"Invalid URL: {url}"
                )
            )

    return failures
def dq11_cashflow_equation(cf_df):

    failures = []

    for _, row in cf_df.iterrows():

        calculated = (
            row["operating_activity"]
            + row["investing_activity"]
            + row["financing_activity"]
        )

        difference = abs(
            calculated - row["net_cash_flow"]
        )

        if difference > 10:

            failures.append(
                ValidationFailure(
                    rule="DQ-11",
                    severity="WARNING",
                    table="cashflow",
                    company_id=row["company_id"],
                    year=row["year"],
                    message=f"Cashflow mismatch: {difference:.2f}"
                )
            )

    return failures
def dq12_year_format(df):

    failures = []

    pattern = r"^\d{4}-\d{2}$"

    for _, row in df.iterrows():

        year = str(row["year"])

        if not re.match(pattern, year):

            failures.append(
                ValidationFailure(
                    rule="DQ-12",
                    severity="CRITICAL",
                    table="unknown",
                    company_id=row.get("company_id", ""),
                    year=year,
                    message="Invalid year format"
                )
            )

    return failures
def dq13_ticker_format(df):

    failures = []

    pattern = r"^[A-Z0-9&\-]+$"

    for _, row in df.iterrows():

        ticker = str(row["company_id"])

        if not re.match(pattern, ticker):

            failures.append(
                ValidationFailure(
                    rule="DQ-13",
                    severity="CRITICAL",
                    table="unknown",
                    company_id=ticker,
                    year=row.get("year", ""),
                    message="Invalid ticker format"
                )
            )

    return failures
def dq14_coverage_check(df):

    failures = []

    coverage = (
        df.groupby("company_id")["year"]
        .nunique()
        .reset_index()
    )

    low_coverage = coverage[
        coverage["year"] < 5
    ]

    for _, row in low_coverage.iterrows():

        failures.append(
            ValidationFailure(
                rule="DQ-14",
                severity="WARNING",
                table="coverage",
                company_id=row["company_id"],
                year="",
                message=f"Only {row['year']} years of data"
            )
        )

    return failures
def dq15_null_critical_fields(
    df,
    table_name,
    required_cols
):

    failures = []

    for col in required_cols:

        null_rows = df[df[col].isna()]

        for _, row in null_rows.iterrows():

            failures.append(
                ValidationFailure(
                    rule="DQ-15",
                    severity="CRITICAL",
                    table=table_name,
                    company_id=row.get("company_id", ""),
                    year=row.get("year", ""),
                    message=f"Null value in {col}"
                )
            )

    return failures
def dq16_duplicate_documents(doc_df):

    failures = []

    duplicates = doc_df[
        doc_df.duplicated(
            subset=["company_id", "Year"],
            keep=False
        )
    ]

    for _, row in duplicates.iterrows():

        failures.append(
            ValidationFailure(
                rule="DQ-16",
                severity="WARNING",
                table="documents",
                company_id=row["company_id"],
                year=row["Year"],
                message="Duplicate annual report record"
            )
        )

    return failures