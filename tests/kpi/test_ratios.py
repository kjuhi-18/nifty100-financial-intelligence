import pytest

from src.analytics.ratios import (
    safe_divide,
    percentage,
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    debt_to_equity,
    high_leverage_flag,
    interest_coverage,
    interest_coverage_label,
    interest_coverage_warning,
    net_debt,
    asset_turnover,
)
def test_safe_divide():
    assert safe_divide(10, 2) == 5


def test_safe_divide_zero():
    assert safe_divide(10, 0) is None


def test_safe_divide_none():
    assert safe_divide(10, None) is None
def test_percentage():
    assert percentage(25, 100) == 25.00


def test_percentage_zero():
    assert percentage(25, 0) is None
def test_net_profit_margin():
    assert net_profit_margin(200, 1000) == 20.00


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(100, 0) is None
def test_operating_margin():
    assert operating_profit_margin(250, 1000) == 25.00


def test_operating_margin_zero_sales():
    assert operating_profit_margin(100, 0) is None
def test_roe():
    assert return_on_equity(
        100,
        200,
        300
    ) == 20.00


def test_roe_negative_equity():

    assert return_on_equity(
        100,
        -200,
        -300
    ) is None
def test_roce():

    assert return_on_capital_employed(
        100,
        20,
        100,
        300,
        200
    ) == 20.0


def test_roce_invalid():

    assert return_on_capital_employed(
        100,
        20,
        -500,
        -500,
        0
    ) is None
def test_roa():

    assert return_on_assets(
        100,
        1000
    ) == 10.0


def test_roa_zero_assets():

    assert return_on_assets(
        100,
        0
    ) is None
def test_de_ratio():

    assert debt_to_equity(
        200,
        100,
        300
    ) == 0.5


def test_debt_free():

    assert debt_to_equity(
        0,
        100,
        300
    ) == 0.0


def test_negative_equity():

    assert debt_to_equity(
        200,
        -500,
        -100
    ) is None
def test_high_leverage():

    assert high_leverage_flag(
        6,
        "Industrials"
    )


def test_financial_not_flagged():

    assert not high_leverage_flag(
        8,
        "Financials"
    )
def test_interest_coverage():

    assert interest_coverage(
        100,
        20,
        10
    ) == 12.0


def test_interest_zero():

    assert interest_coverage(
        100,
        20,
        0
    ) is None
def test_interest_label():

    assert interest_coverage_label(None) == "Debt Free"


def test_interest_label_applicable():

    assert interest_coverage_label(5) == "Applicable"
def test_interest_warning():

    assert interest_coverage_warning(1.0)


def test_interest_safe():

    assert not interest_coverage_warning(3.5)
def test_net_debt():

    assert net_debt(
        500,
        100
    ) == 400
def test_asset_turnover():

    assert asset_turnover(
        1000,
        500
    ) == 2.0


def test_asset_turnover_zero():

    assert asset_turnover(
        1000,
        0
    ) is None
