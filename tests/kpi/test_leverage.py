import pytest

from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage,
    interest_coverage_label,
    interest_coverage_warning,
    net_debt,
    asset_turnover
)


# --------------------------------------------------
# Debt to Equity
# --------------------------------------------------

def test_debt_to_equity_normal():

    assert debt_to_equity(
        borrowings=300,
        equity_capital=100,
        reserves=500
    ) == 0.5


def test_debt_to_equity_debt_free():

    assert debt_to_equity(
        borrowings=0,
        equity_capital=100,
        reserves=500
    ) == 0.0


def test_debt_to_equity_negative_equity():

    assert debt_to_equity(
        borrowings=100,
        equity_capital=-100,
        reserves=50
    ) is None


# --------------------------------------------------
# High Leverage Flag
# --------------------------------------------------

def test_high_leverage_flag_true():

    assert high_leverage_flag(
        debt_equity=6.5,
        broad_sector="Industrials"
    ) is True


def test_high_leverage_flag_financials():

    assert high_leverage_flag(
        debt_equity=8.0,
        broad_sector="Financials"
    ) is False


# --------------------------------------------------
# Interest Coverage Ratio
# --------------------------------------------------

def test_interest_coverage_normal():

    assert interest_coverage(
        operating_profit=200,
        other_income=50,
        interest=25
    ) == 10.0


def test_interest_coverage_zero_interest():

    assert interest_coverage(
        operating_profit=200,
        other_income=50,
        interest=0
    ) is None


# --------------------------------------------------
# Interest Coverage Label
# --------------------------------------------------

def test_interest_coverage_label_debt_free():

    assert interest_coverage_label(
        None
    ) == "Debt Free"


def test_interest_coverage_label_applicable():

    assert interest_coverage_label(
        8.5
    ) == "Applicable"


# --------------------------------------------------
# Interest Coverage Warning
# --------------------------------------------------

def test_interest_warning_true():

    assert interest_coverage_warning(
        1.2
    ) is True


def test_interest_warning_false():

    assert interest_coverage_warning(
        3.5
    ) is False


# --------------------------------------------------
# Net Debt
# --------------------------------------------------

def test_net_debt():

    assert net_debt(
        borrowings=500,
        investments=150
    ) == 350


# --------------------------------------------------
# Asset Turnover
# --------------------------------------------------

def test_asset_turnover_normal():

    assert asset_turnover(
        sales=1000,
        total_assets=500
    ) == 2.0


def test_asset_turnover_zero_assets():

    assert asset_turnover(
        sales=1000,
        total_assets=0
    ) is None