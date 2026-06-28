import pytest

from src.analytics.cagr import (
    calculate_cagr,
    compute_revenue_cagr,
    compute_pat_cagr,
    compute_eps_cagr,
    TURNAROUND,
    DECLINE_TO_LOSS,
    BOTH_NEGATIVE,
    ZERO_BASE,
    INSUFFICIENT
)


# --------------------------------------------------
# Generic CAGR
# --------------------------------------------------

def test_cagr_normal():

    result = calculate_cagr(
        start_value=100,
        end_value=200,
        years=5
    )

    assert round(result["value"], 2) == 14.87
    assert result["flag"] is None


def test_turnaround():

    result = calculate_cagr(
        start_value=-100,
        end_value=100,
        years=5
    )

    assert result["value"] is None
    assert result["flag"] == TURNAROUND


def test_decline_to_loss():

    result = calculate_cagr(
        start_value=100,
        end_value=-50,
        years=5
    )

    assert result["value"] is None
    assert result["flag"] == DECLINE_TO_LOSS


def test_both_negative():

    result = calculate_cagr(
        start_value=-100,
        end_value=-50,
        years=5
    )

    assert result["value"] is None
    assert result["flag"] == BOTH_NEGATIVE


def test_zero_base():

    result = calculate_cagr(
        start_value=0,
        end_value=100,
        years=5
    )

    assert result["value"] is None
    assert result["flag"] == ZERO_BASE


def test_insufficient_years():

    result = calculate_cagr(
        start_value=100,
        end_value=200,
        years=0
    )

    assert result["value"] is None
    assert result["flag"] == INSUFFICIENT


# --------------------------------------------------
# Revenue CAGR
# --------------------------------------------------

def test_revenue_cagr():

    history = [
        100,
        120,
        140,
        170,
        210,
        260
    ]

    result = compute_revenue_cagr(
        history,
        5
    )

    assert result["flag"] is None
    assert result["value"] > 0


# --------------------------------------------------
# PAT CAGR
# --------------------------------------------------

def test_pat_cagr():

    history = [
        10,
        12,
        15,
        18,
        22,
        28
    ]

    result = compute_pat_cagr(
        history,
        5
    )

    assert result["flag"] is None
    assert result["value"] > 0


# --------------------------------------------------
# EPS CAGR
# --------------------------------------------------

def test_eps_cagr():

    history = [
        5,
        6,
        7,
        8,
        9,
        10
    ]

    result = compute_eps_cagr(
        history,
        5
    )

    assert result["flag"] is None
    assert result["value"] > 0


# --------------------------------------------------
# Insufficient History
# --------------------------------------------------

def test_insufficient_history():

    history = [
        100,
        120,
        150
    ]

    result = compute_revenue_cagr(
        history,
        5
    )

    assert result["value"] is None
    assert result["flag"] == INSUFFICIENT