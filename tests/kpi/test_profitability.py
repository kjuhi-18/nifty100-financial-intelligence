import pytest

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets
)


# --------------------------------------------------
# Net Profit Margin
# --------------------------------------------------

def test_net_profit_margin_normal():

    assert net_profit_margin(
        100,
        1000
    ) == 10.0


def test_net_profit_margin_zero_sales():

    assert net_profit_margin(
        100,
        0
    ) is None


# --------------------------------------------------
# Operating Profit Margin
# --------------------------------------------------

def test_operating_profit_margin_normal():

    assert operating_profit_margin(
        250,
        1000
    ) == 25.0


def test_operating_profit_margin_crosscheck():

    result = operating_profit_margin(
        operating_profit=220,
        sales=1000,
        source_opm=25
    )

    assert result == 22.0


# --------------------------------------------------
# Return on Equity
# --------------------------------------------------

def test_return_on_equity_normal():

    assert return_on_equity(
        net_profit=120,
        equity_capital=100,
        reserves=500
    ) == 20.0


def test_return_on_equity_negative_equity():

    assert return_on_equity(
        net_profit=100,
        equity_capital=-50,
        reserves=25
    ) is None


# --------------------------------------------------
# Return on Capital Employed
# --------------------------------------------------

def test_return_on_capital_employed_normal():

    assert return_on_capital_employed(
        operating_profit=200,
        interest=20,
        equity_capital=100,
        reserves=500,
        borrowings=400
    ) == 22.0


def test_return_on_capital_employed_zero_capital():

    assert return_on_capital_employed(
        operating_profit=200,
        interest=20,
        equity_capital=0,
        reserves=0,
        borrowings=0
    ) is None


# --------------------------------------------------
# Return on Assets
# --------------------------------------------------

def test_return_on_assets_normal():

    assert return_on_assets(
        net_profit=150,
        total_assets=1000
    ) == 15.0


def test_return_on_assets_zero_assets():

    assert return_on_assets(
        net_profit=100,
        total_assets=0
    ) is None