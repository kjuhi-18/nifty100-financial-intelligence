import pytest

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
    distress_signal,
    deleveraging_flag,
    fcf_cagr,
)


# --------------------------------------------------
# Free Cash Flow
# --------------------------------------------------

def test_free_cash_flow():

    # CFO + Investing Activity
    assert free_cash_flow(500, -100) == 400


def test_negative_fcf():

    assert free_cash_flow(100, -300) == -200


# --------------------------------------------------
# CFO Quality Score
# --------------------------------------------------

def test_cfo_quality_high():

    result = cfo_quality_score(
        [500,520,540,560,600],
        [400,420,430,450,500]
    )

    assert result["score"] > 1
    assert result["label"] == "High Quality"


def test_cfo_quality_insufficient():

    result = cfo_quality_score(
        [100],
        [100]
    )

    assert result["score"] is None
    assert result["label"] is None


# --------------------------------------------------
# CapEx Intensity
# --------------------------------------------------

def test_capex_intensity():

    result = capex_intensity(
        -100,
        1000
    )

    assert result["value"] == 10
    assert result["label"] == "Capital Intensive"


def test_capex_zero_sales():

    result = capex_intensity(
        -100,
        0
    )

    assert result["value"] is None
    assert result["label"] is None


# --------------------------------------------------
# FCF Conversion
# --------------------------------------------------

def test_fcf_conversion():

    assert fcf_conversion_rate(
        300,
        150
    ) == 200.0


def test_fcf_conversion_zero():

    assert fcf_conversion_rate(
        300,
        0
    ) is None


# --------------------------------------------------
# Capital Allocation
# --------------------------------------------------

def test_capital_allocation():

    assert capital_allocation_pattern(
        500,
        -100,
        -50
    ) == "Reinvestor"


# --------------------------------------------------
# Distress Signal
# --------------------------------------------------

def test_distress():

    assert distress_signal(
        -100,
        50
    )


def test_not_distress():

    assert not distress_signal(
        100,
        -50
    )


# --------------------------------------------------
# Deleveraging
# --------------------------------------------------

def test_deleveraging():

    assert deleveraging_flag(
        80,
        100,
        -50
    )


def test_not_deleveraging():

    assert not deleveraging_flag(
        120,
        100,
        -50
    )


# --------------------------------------------------
# FCF CAGR
# --------------------------------------------------

def test_fcf_cagr():

    history = [
        100,
        120,
        150,
        180,
        220
    ]

    assert fcf_cagr(history) > 0


def test_fcf_cagr_insufficient():

    assert fcf_cagr([100,120]) is None