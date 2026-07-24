import pandas as pd

from src.etl.dq_rules import *

# --------------------------------------------------
# DQ01 Primary Key
# --------------------------------------------------


def test_dq01_duplicate_pk():

    df = pd.DataFrame({"id": ["A", "A"]})

    failures = dq01_pk_uniqueness(df, "companies", "id")

    assert len(failures) == 2


# --------------------------------------------------
# DQ02 Company Year
# --------------------------------------------------


def test_dq02_duplicate_company_year():

    df = pd.DataFrame({"company_id": ["ABC", "ABC"], "year": ["2024-03", "2024-03"]})

    failures = dq02_company_year_unique(df, "balancesheet")

    assert len(failures) == 2


# --------------------------------------------------
# DQ03 FK
# --------------------------------------------------


def test_dq03_fk():

    companies = pd.DataFrame({"id": ["ABC"]})

    df = pd.DataFrame({"company_id": ["XYZ"], "year": ["2024-03"]})

    failures = dq03_fk_integrity(df, companies)

    assert len(failures) == 1


# --------------------------------------------------
# DQ04 Balance Sheet
# --------------------------------------------------


def test_dq04_balance():

    df = pd.DataFrame(
        {
            "company_id": ["ABC"],
            "year": ["2024-03"],
            "total_assets": [1000],
            "total_liabilities": [800],
        }
    )

    failures = dq04_balance_sheet(df)

    assert len(failures) == 1


# --------------------------------------------------
# DQ05 OPM
# --------------------------------------------------


def test_dq05_opm():

    df = pd.DataFrame(
        {
            "company_id": ["ABC"],
            "year": ["2024-03"],
            "sales": [1000],
            "expenses": [700],
            "operating_profit": [200],
        }
    )

    failures = dq05_opm_validation(df)

    assert len(failures) == 1


# --------------------------------------------------
# DQ06 Sales
# --------------------------------------------------


def test_dq06_sales():

    df = pd.DataFrame({"company_id": ["ABC"], "year": ["2024-03"], "sales": [-100]})

    failures = dq06_positive_sales(df)

    assert len(failures) == 1


# --------------------------------------------------
# DQ07 Tax
# --------------------------------------------------


def test_dq07_tax():

    df = pd.DataFrame(
        {"company_id": ["ABC"], "year": ["2024-03"], "tax_percentage": [120]}
    )

    failures = dq07_tax_rate(df)

    assert len(failures) == 1


# --------------------------------------------------
# DQ08 EPS
# --------------------------------------------------


def test_dq08_eps():

    df = pd.DataFrame(
        {"company_id": ["ABC"], "year": ["2024-03"], "net_profit": [100], "eps": [0]}
    )

    failures = dq08_eps_sign(df)

    assert len(failures) == 1


# --------------------------------------------------
# DQ09 Dividend
# --------------------------------------------------


def test_dq09_dividend():

    df = pd.DataFrame(
        {"company_id": ["ABC"], "year": ["2024-03"], "dividend_payout": [600]}
    )

    failures = dq09_dividend_cap(df)

    assert len(failures) == 1


# --------------------------------------------------
# DQ10 URL
# --------------------------------------------------


def test_dq10_url():

    df = pd.DataFrame(
        {"company_id": ["ABC"], "Year": ["2024-03"], "Annual_Report": ["google.com"]}
    )

    failures = dq10_url_validation(df)

    assert len(failures) == 1


# --------------------------------------------------
# DQ11 Cashflow
# --------------------------------------------------


def test_dq11_cashflow():

    df = pd.DataFrame(
        {
            "company_id": ["ABC"],
            "year": ["2024-03"],
            "operating_activity": [100],
            "investing_activity": [-50],
            "financing_activity": [-10],
            "net_cash_flow": [100],
        }
    )

    failures = dq11_cashflow_equation(df)

    assert len(failures) == 1


# --------------------------------------------------
# DQ12 Year
# --------------------------------------------------


def test_dq12_year():

    df = pd.DataFrame({"company_id": ["ABC"], "year": ["2024"]})

    failures = dq12_year_format(df)

    assert len(failures) == 1


# --------------------------------------------------
# DQ13 Ticker
# --------------------------------------------------


def test_dq13_ticker():

    df = pd.DataFrame({"company_id": ["abc@123"], "year": ["2024-03"]})

    failures = dq13_ticker_format(df)

    assert len(failures) == 1


# --------------------------------------------------
# DQ14 Coverage
# --------------------------------------------------


def test_dq14_coverage():

    df = pd.DataFrame({"company_id": ["ABC", "ABC"], "year": ["2023-03", "2024-03"]})

    failures = dq14_coverage_check(df)

    assert len(failures) == 1


# --------------------------------------------------
# DQ15 Nulls
# --------------------------------------------------


def test_dq15_null():

    df = pd.DataFrame({"company_id": ["ABC"], "year": ["2024-03"], "sales": [None]})

    failures = dq15_null_critical_fields(df, "profitandloss", ["sales"])

    assert len(failures) == 1


# --------------------------------------------------
# DQ16 Duplicate Documents
# --------------------------------------------------


def test_dq16_documents():

    df = pd.DataFrame({"company_id": ["ABC", "ABC"], "Year": ["2024-03", "2024-03"]})

    failures = dq16_duplicate_documents(df)

    assert len(failures) == 2
