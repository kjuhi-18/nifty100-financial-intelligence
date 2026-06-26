from pathlib import Path
import logging
from typing import Optional


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

    if total_assets <= 0:

        logger.info(
            "Invalid Total Assets."
        )

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