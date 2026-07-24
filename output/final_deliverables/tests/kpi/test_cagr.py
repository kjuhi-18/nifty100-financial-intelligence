
from src.analytics.cagr import (
    DECLINE_TO_LOSS,
    INSUFFICIENT,
    TURNAROUND,
    ZERO_BASE,
    calculate_cagr,
    compute_cagr,
    compute_eps_cagr,
    compute_pat_cagr,
    compute_revenue_cagr,
    has_sufficient_history,
)

# -----------------------------
# calculate_cagr
# -----------------------------


def test_calculate_cagr_positive():

    result = calculate_cagr(100, 200, 5)

    assert result["value"] == 14.87
    assert result["flag"] is None


def test_calculate_cagr_same():

    result = calculate_cagr(100, 100, 5)

    assert result["value"] == 0.0
    assert result["flag"] is None


def test_turnaround():

    result = calculate_cagr(-100, 200, 5)

    assert result["value"] is None
    assert result["flag"] == TURNAROUND


def test_decline_to_loss():

    result = calculate_cagr(100, -50, 5)

    assert result["flag"] == DECLINE_TO_LOSS


def test_zero_base():

    result = calculate_cagr(0, 100, 5)

    assert result["flag"] == ZERO_BASE


def test_invalid_years():

    result = calculate_cagr(100, 200, 0)

    assert result["flag"] == INSUFFICIENT


# -----------------------------
# History
# -----------------------------


def test_history_true():

    values = [1, 2, 3, 4, 5, 6]

    assert has_sufficient_history(values, 5)


def test_history_false():

    values = [1, 2]

    assert not has_sufficient_history(values, 5)


# -----------------------------
# compute_cagr
# -----------------------------


def test_compute_cagr():

    values = [100, 120, 150, 180]

    result = compute_cagr(values, 3)

    assert result["value"] > 0


def test_compute_cagr_insufficient():

    result = compute_cagr([100], 3)

    assert result["flag"] == INSUFFICIENT


# -----------------------------
# Revenue CAGR
# -----------------------------


def test_revenue_cagr():

    values = [100, 120, 150, 180]

    result = compute_revenue_cagr(values, 3)

    assert result["value"] > 0


# -----------------------------
# PAT CAGR
# -----------------------------


def test_pat_cagr():

    values = [20, 25, 30, 40]

    result = compute_pat_cagr(values, 3)

    assert result["value"] > 0


# -----------------------------
# EPS CAGR
# -----------------------------


def test_eps_cagr():

    values = [5, 7, 8, 10]

    result = compute_eps_cagr(values, 3)

    assert result["value"] > 0
