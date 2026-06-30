from pathlib import Path
import logging
from typing import Optional
import pandas as pd

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
# Helper Functions
# --------------------------------------------------

def safe_divide(
    numerator: float,
    denominator: float
) -> Optional[float]:
    """
    Safely divide two numbers.

    Returns None if denominator is
    zero or None.
    """

    if denominator is None:
        return None

    if denominator == 0:
        return None

    return numerator / denominator


def percentage(
    numerator: float,
    denominator: float
) -> Optional[float]:
    """
    Computes percentage.

    Formula:
        numerator / denominator * 100
    """

    value = safe_divide(
        numerator,
        denominator
    )

    if value is None:
        return None

    return round(
        value * 100,
        2
    )


# --------------------------------------------------
# Net Profit Margin
# --------------------------------------------------

def net_profit_margin(
    net_profit: float,
    sales: float
) -> Optional[float]:
    """
    Net Profit Margin

    Formula:

    Net Profit / Sales * 100

    Returns None
    if sales == 0
    """

    return percentage(
        net_profit,
        sales
    )


# --------------------------------------------------
# Operating Profit Margin
# --------------------------------------------------

def operating_profit_margin(
    operating_profit: float,
    sales: float,
    source_opm: Optional[float] = None,
    tolerance: float = 1.0
) -> Optional[float]:
    """
    Operating Profit Margin

    Formula

    Operating Profit / Sales *100

    Cross checks
    against source OPM.
    """

    computed = percentage(
        operating_profit,
        sales
    )

    if computed is None:
        return None

    if source_opm is not None:

        difference = abs(
            computed - source_opm
        )

        if difference > tolerance:

            logger.warning(

                "OPM mismatch | "
                f"Computed={computed:.2f} | "
                f"Source={source_opm:.2f}"

            )

    return computed


# --------------------------------------------------
# Return on Equity
# --------------------------------------------------

def return_on_equity(
    net_profit: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:
    """
    Return On Equity

    ROE

    Formula

    Net Profit

    ------------------------
    Equity + Reserves

    x100
    """
    if pd.isna(equity_capital):
        return None

    if pd.isna(reserves):
        return None
    denominator = (
        equity_capital +
        reserves
    )

    if denominator <= 0:

        logger.info(
            "Negative Equity encountered."
        )

        return None

    return percentage(
        net_profit,
        denominator
    )


# --------------------------------------------------
# Return on Capital Employed
# --------------------------------------------------

def return_on_capital_employed(
    operating_profit: float,
    interest: float,
    equity_capital: float,
    reserves: float,
    borrowings: float,
    broad_sector: Optional[str] = None
) -> Optional[float]:
    """
    Return On Capital Employed

    EBIT

    -------------------------
    Equity
    +Reserves
    +Borrowings

    x100

    EBIT

    =
    Operating Profit
    +
    Interest
    """
    if pd.isna(operating_profit):
        return None

    if pd.isna(interest):
        return None

    if pd.isna(equity_capital):
        return None

    if pd.isna(reserves):
        return None

    if pd.isna(borrowings):
        return None
    ebit = (
        operating_profit +
        interest
    )

    capital = (
        equity_capital +
        reserves +
        borrowings
    )

    if capital <= 0:

        logger.info(
            "Invalid Capital Employed."
        )

        return None

    roce = percentage(
        ebit,
        capital
    )

    if (
        broad_sector is not None
        and broad_sector.lower()
        == "financials"
    ):

        logger.info(

            "Financial sector company. "
            "Sector-relative ROCE benchmark."

        )

    return roce
# --------------------------------------------------
# Return on Assets
# --------------------------------------------------

def return_on_assets(
    net_profit: float,
    total_assets: float
) -> Optional[float]:
    """
    Return On Assets

    Formula

    Net Profit
    ----------------
    Total Assets

    x100

    Returns None if
    total_assets <= 0
    """
    if pd.isna(total_assets):
        return None

    if total_assets <= 0:
        return None

    return percentage(
        net_profit,
        total_assets
    )


# --------------------------------------------------
# Combined Profitability Ratio Engine
# --------------------------------------------------

def calculate_profitability_ratios(
    row: dict
) -> dict:
    """
    Compute all profitability ratios
    for one company-year record.

    Expected Keys

    net_profit
    sales
    operating_profit
    opm_percentage
    interest
    equity_capital
    reserves
    borrowings
    total_assets
    broad_sector
    """

    ratios = {}

    ratios["net_profit_margin_pct"] = net_profit_margin(
        row.get("net_profit", 0),
        row.get("sales", 0)
    )

    ratios["operating_profit_margin_pct"] = operating_profit_margin(
        row.get("operating_profit", 0),
        row.get("sales", 0),
        row.get("opm_percentage")
    )

    ratios["return_on_equity_pct"] = return_on_equity(
        row.get("net_profit", 0),
        row.get("equity_capital", 0),
        row.get("reserves", 0)
    )

    ratios["return_on_capital_employed_pct"] = (
        return_on_capital_employed(
            row.get("operating_profit", 0),
            row.get("interest", 0),
            row.get("equity_capital", 0),
            row.get("reserves", 0),
            row.get("borrowings", 0),
            row.get("broad_sector")
        )
    )

    ratios["return_on_assets_pct"] = return_on_assets(
        row.get("net_profit", 0),
        row.get("total_assets", 0)
    )

    return ratios


# --------------------------------------------------
# Validation Helper
# --------------------------------------------------

def validate_ratio(
    value: Optional[float],
    ratio_name: str,
    company_id: Optional[str] = None,
    year: Optional[str] = None
) -> None:
    """
    Logs missing ratio values.
    """

    if value is None:

        logger.info(

            f"{ratio_name} unavailable | "
            f"Company={company_id} | "
            f"Year={year}"

        )


# --------------------------------------------------
# Demo
# --------------------------------------------------

if __name__ == "__main__":

    sample = {

        "company_id": "ABC",

        "year": "2024",

        "sales": 1000,

        "net_profit": 120,

        "operating_profit": 210,

        "opm_percentage": 21,

        "interest": 20,

        "equity_capital": 100,

        "reserves": 500,

        "borrowings": 150,

        "total_assets": 950,

        "broad_sector": "Industrials"

    }

    results = calculate_profitability_ratios(
        sample
    )

    print("\nProfitability Ratios\n")

    for key, value in results.items():

        print(
            f"{key:<35} {value}"
        )


# --------------------------------------------------
# Public Exports
# --------------------------------------------------

__all__ = [

    "safe_divide",

    "percentage",

    "net_profit_margin",

    "operating_profit_margin",

    "return_on_equity",

    "return_on_capital_employed",

    "return_on_assets",

    "calculate_profitability_ratios",

    "validate_ratio"

]
# --------------------------------------------------
# Debt to Equity
# --------------------------------------------------

def debt_to_equity(
    borrowings: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:
    """
    Debt to Equity Ratio

    Formula

    Borrowings
    -------------------------
    Equity + Reserves

    Rules

    Borrowings == 0
        return 0

    Equity <= 0
        return None
    """

    if pd.isna(borrowings):
        return None

    if pd.isna(equity_capital):
        return None

    if pd.isna(reserves):
        return None

    if borrowings == 0:
        return 0.0

    equity = equity_capital + reserves

    if equity <= 0:

        logger.info(
            "Invalid Equity for D/E"
        )

        return None

    return round(
        borrowings / equity,
        2
    )


# --------------------------------------------------
# High Leverage Flag
# --------------------------------------------------

def high_leverage_flag(
    debt_equity: Optional[float],
    broad_sector: Optional[str]
) -> bool:
    """
    Returns True if

    Debt Equity > 5

    except for Financial sector.
    """

    if debt_equity is None:
        return False

    if (
        broad_sector is not None
        and broad_sector.lower() == "financials"
    ):
        return False

    return debt_equity > 5


# --------------------------------------------------
# Interest Coverage Ratio
# --------------------------------------------------

def interest_coverage(
    operating_profit: float,
    other_income: float,
    interest: float
) -> Optional[float]:
    """
    Interest Coverage Ratio

    Formula

    Operating Profit + Other Income
    ------------------------------------
            Interest

    interest == 0

    return None
    """

    if pd.isna(interest):
        return None

    if pd.isna(operating_profit):
        return None

    if pd.isna(other_income):
        return None

    if interest == 0:
        return None

    return round(
        (
            operating_profit +
            other_income
        ) / interest,
        2
    )


# --------------------------------------------------
# Interest Coverage Label
# --------------------------------------------------

def interest_coverage_label(
    icr: Optional[float]
) -> str:
    """
    Display Label

    None

    =>
    Debt Free
    """

    if icr is None:
        return "Debt Free"

    return "Applicable"


# --------------------------------------------------
# Interest Coverage Warning
# --------------------------------------------------

def interest_coverage_warning(
    icr: Optional[float]
) -> bool:
    """
    Company may not be
    able to cover interest.

    Warning

    ICR < 1.5
    """

    if icr is None:
        return False

    return icr < 1.5
# --------------------------------------------------
# Net Debt
# --------------------------------------------------

def net_debt(
    borrowings: float,
    investments: float
) -> float:
    """
    Net Debt

    Formula

    Borrowings - Investments

    Investments are used as a
    proxy for liquid assets.
    """

    return round(
        borrowings - investments,
        2
    )


# --------------------------------------------------
# Asset Turnover
# --------------------------------------------------

def asset_turnover(
    sales: float,
    total_assets: float
) -> Optional[float]:
    """
    Asset Turnover

    Formula

    Sales
    ----------------
    Total Assets

    Returns None if
    total_assets <= 0
    """

    if pd.isna(sales):
        return None

    if pd.isna(total_assets):
        return None

    if total_assets <= 0:
        return None

    return round(
        sales / total_assets,
        2
    )


# --------------------------------------------------
# Combined Leverage & Efficiency Engine
# --------------------------------------------------

def calculate_leverage_ratios(
    row: dict
) -> dict:
    """
    Computes leverage
    and efficiency KPIs
    for a company-year.
    """

    ratios = {}

    de = debt_to_equity(
        row.get("borrowings", 0),
        row.get("equity_capital", 0),
        row.get("reserves", 0)
    )

    ratios["debt_to_equity"] = de

    ratios["high_leverage_flag"] = high_leverage_flag(
        de,
        row.get("broad_sector")
    )

    icr = interest_coverage(
        row.get("operating_profit", 0),
        row.get("other_income", 0),
        row.get("interest", 0)
    )

    ratios["interest_coverage"] = icr

    ratios["icr_label"] = interest_coverage_label(
        icr
    )

    ratios["interest_warning_flag"] = (
        interest_coverage_warning(
            icr
        )
    )

    ratios["net_debt"] = net_debt(
        row.get("borrowings", 0),
        row.get("investments", 0)
    )

    ratios["asset_turnover"] = asset_turnover(
        row.get("sales", 0),
        row.get("total_assets", 0)
    )

    return ratios


# --------------------------------------------------
# Update Public Exports
# --------------------------------------------------

__all__.extend(

    [

        "debt_to_equity",

        "high_leverage_flag",

        "interest_coverage",

        "interest_coverage_label",

        "interest_coverage_warning",

        "net_debt",

        "asset_turnover",

        "calculate_leverage_ratios"

    ]

)