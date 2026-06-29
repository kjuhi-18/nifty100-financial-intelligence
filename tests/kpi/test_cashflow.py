import pytest

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern
)


# --------------------------------------------------
# Free Cash Flow
# --------------------------------------------------

def test_free_cash_flow():

    assert free_cash_flow(
        operating_activity=500,
        investing_activity=-200
    ) == 300


# --------------------------------------------------
# CFO Quality Score
# --------------------------------------------------

def test_cfo_quality_high():

    result = cfo_quality_score(
        cfo_history=[100, 120, 140, 160, 180],
        pat_history=[80, 100, 110, 130, 150]
    )

    assert result["label"] == "High Quality"


def test_cfo_quality_moderate():

    result = cfo_quality_score(
        cfo_history=[60, 60, 60, 60, 60],
        pat_history=[100, 100, 100, 100, 100]
    )

    assert result["label"] == "Moderate"


def test_cfo_quality_accrual():

    result = cfo_quality_score(
        cfo_history=[20, 20, 20, 20, 20],
        pat_history=[100, 100, 100, 100, 100]
    )

    assert result["label"] == "Accrual Risk"


def test_cfo_quality_zero_pat():

    result = cfo_quality_score(
        cfo_history=[100, 100, 100, 100, 100],
        pat_history=[100, 100, 0, 100, 100]
    )

    assert result["score"] is None
    assert result["label"] is None


# --------------------------------------------------
# CapEx Intensity
# --------------------------------------------------

def test_capex_asset_light():

    result = capex_intensity(
        investing_activity=-20,
        sales=1000
    )

    assert result["label"] == "Asset Light"


def test_capex_moderate():

    result = capex_intensity(
        investing_activity=-50,
        sales=1000
    )

    assert result["label"] == "Moderate"


def test_capex_capital_intensive():

    result = capex_intensity(
        investing_activity=-150,
        sales=1000
    )

    assert result["label"] == "Capital Intensive"


# --------------------------------------------------
# FCF Conversion
# --------------------------------------------------

def test_fcf_conversion():

    assert fcf_conversion_rate(
        free_cash_flow_value=300,
        operating_profit=600
    ) == 50.0


def test_fcf_conversion_zero_operating_profit():

    assert fcf_conversion_rate(
        free_cash_flow_value=300,
        operating_profit=0
    ) is None


# --------------------------------------------------
# Capital Allocation Patterns
# --------------------------------------------------

def test_reinvestor():

    assert capital_allocation_pattern(
        100,
        -50,
        -20
    ) == "Reinvestor"


def test_shareholder_returns():

    assert capital_allocation_pattern(
        100,
        -50,
        -20,
        cfo_pat_score=1.5
    ) == "Shareholder Returns"


def test_liquidating_assets():

    assert capital_allocation_pattern(
        100,
        50,
        -20
    ) == "Liquidating Assets"


def test_distress_signal():

    assert capital_allocation_pattern(
        -100,
        50,
        20
    ) == "Distress Signal"


def test_growth_funded():

    assert capital_allocation_pattern(
        -100,
        -50,
        30
    ) == "Growth Funded by Debt"


def test_cash_accumulator():

    assert capital_allocation_pattern(
        100,
        50,
        30
    ) == "Cash Accumulator"


def test_pre_revenue():

    assert capital_allocation_pattern(
        -100,
        -50,
        -30
    ) == "Pre-Revenue"


def test_mixed():

    assert capital_allocation_pattern(
        100,
        -50,
        30
    ) == "Mixed"