from typing import Optional
import logging
from pathlib import Path


# --------------------------------------------------
# Logging
# --------------------------------------------------

LOG_DIR = Path("output")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "ratio_edge_cases.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# CAGR Flags
# --------------------------------------------------

NORMAL = None

TURNAROUND = "TURNAROUND"

DECLINE_TO_LOSS = "DECLINE_TO_LOSS"

BOTH_NEGATIVE = "BOTH_NEGATIVE"

ZERO_BASE = "ZERO_BASE"

INSUFFICIENT = "INSUFFICIENT"


# --------------------------------------------------
# Generic CAGR Formula
# --------------------------------------------------

def calculate_cagr(
    start_value: float,
    end_value: float,
    years: int
) -> dict:
    """
    CAGR Formula

    ((End / Start)^(1/n)-1)*100

    Returns

    {
        value
        flag
    }
    """

    # --------------------------
    # Invalid years
    # --------------------------

    if years <= 0:

        logger.warning(
            "Invalid CAGR period."
        )

        return {

            "value": None,

            "flag": INSUFFICIENT

        }

    # --------------------------
    # Zero base
    # --------------------------

    if start_value == 0:

        logger.info(
            "CAGR Zero Base."
        )

        return {

            "value": None,

            "flag": ZERO_BASE

        }

    # --------------------------
    # Positive -> Negative
    # --------------------------

    if start_value > 0 and end_value < 0:

        logger.info(
            "Decline to Loss."
        )

        return {

            "value": None,

            "flag": DECLINE_TO_LOSS

        }

    # --------------------------
    # Negative -> Positive
    # --------------------------

    if start_value < 0 and end_value > 0:

        logger.info(
            "Turnaround."
        )

        return {

            "value": None,

            "flag": TURNAROUND

        }

    # --------------------------
    # Negative -> Negative
    # --------------------------

    if start_value < 0 and end_value < 0:

        logger.info(
            "Both Negative."
        )

        return {

            "value": None,

            "flag": BOTH_NEGATIVE

        }

    # --------------------------
    # Positive -> Positive
    # --------------------------

    cagr = (

        (
            end_value /
            start_value
        ) ** (

            1 / years

        ) - 1

    ) * 100

    return {

        "value": round(
            cagr,
            2
        ),

        "flag": NORMAL

    }


# --------------------------------------------------
# History Validation
# --------------------------------------------------

def has_sufficient_history(
    values: list,
    years_required: int
) -> bool:
    """
    Checks if enough history exists.
    """

    return len(values) >= years_required + 1


# --------------------------------------------------
# Helper
# --------------------------------------------------

def compute_cagr(
    values: list,
    years: int
) -> dict:
    """
    Computes CAGR
    from a historical series.

    Example

    [100,120,140,170]

    years=3
    """

    if not has_sufficient_history(
        values,
        years
    ):

        return {

            "value": None,

            "flag": INSUFFICIENT

        }

    start = values[-(years + 1)]

    end = values[-1]

    return calculate_cagr(

        start,

        end,

        years

    )
# --------------------------------------------------
# Revenue CAGR
# --------------------------------------------------

def compute_revenue_cagr(
    revenue_history: list,
    years: int
) -> dict:
    """
    Computes Revenue CAGR
    for the given window.

    Example

    3 Year
    5 Year
    10 Year
    """

    return compute_cagr(
        revenue_history,
        years
    )


# --------------------------------------------------
# PAT CAGR
# --------------------------------------------------

def compute_pat_cagr(
    pat_history: list,
    years: int
) -> dict:
    """
    Computes Net Profit CAGR.
    """

    return compute_cagr(
        pat_history,
        years
    )


# --------------------------------------------------
# EPS CAGR
# --------------------------------------------------

def compute_eps_cagr(
    eps_history: list,
    years: int
) -> dict:
    """
    Computes EPS CAGR.
    """

    return compute_cagr(
        eps_history,
        years
    )


# --------------------------------------------------
# Growth Engine
# --------------------------------------------------

def calculate_growth_metrics(
    revenue_history: list,
    pat_history: list,
    eps_history: list
) -> dict:
    """
    Computes all CAGR metrics
    required for Sprint 2.
    """

    results = {}

    # --------------------------
    # Revenue CAGR
    # --------------------------

    for years in (3, 5, 10):

        revenue = compute_revenue_cagr(
            revenue_history,
            years
        )

        results[f"revenue_cagr_{years}yr"] = revenue["value"]
        results[f"revenue_cagr_{years}yr_flag"] = revenue["flag"]

    # --------------------------
    # PAT CAGR
    # --------------------------

    for years in (3, 5, 10):

        pat = compute_pat_cagr(
            pat_history,
            years
        )

        results[f"pat_cagr_{years}yr"] = pat["value"]
        results[f"pat_cagr_{years}yr_flag"] = pat["flag"]

    # --------------------------
    # EPS CAGR
    # --------------------------

    for years in (3, 5, 10):

        eps = compute_eps_cagr(
            eps_history,
            years
        )

        results[f"eps_cagr_{years}yr"] = eps["value"]
        results[f"eps_cagr_{years}yr_flag"] = eps["flag"]

    return results


# --------------------------------------------------
# Demo
# --------------------------------------------------

if __name__ == "__main__":

    revenue = [
        100,
        120,
        145,
        180,
        220,
        275,
        320,
        390,
        470,
        550,
        650
    ]

    pat = [
        20,
        25,
        30,
        36,
        42,
        50,
        59,
        71,
        84,
        99,
        120
    ]

    eps = [
        5,
        6,
        7,
        8,
        10,
        12,
        14,
        16,
        18,
        20,
        23
    ]

    metrics = calculate_growth_metrics(
        revenue,
        pat,
        eps
    )

    print("\nGrowth Metrics\n")

    for key, value in metrics.items():

        print(
            f"{key:<30} {value}"
        )


# --------------------------------------------------
# Public Exports
# --------------------------------------------------

__all__ = [

    "NORMAL",

    "TURNAROUND",

    "DECLINE_TO_LOSS",

    "BOTH_NEGATIVE",

    "ZERO_BASE",

    "INSUFFICIENT",

    "calculate_cagr",

    "compute_cagr",

    "compute_revenue_cagr",

    "compute_pat_cagr",

    "compute_eps_cagr",

    "calculate_growth_metrics"

]