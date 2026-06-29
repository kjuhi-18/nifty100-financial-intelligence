from pathlib import Path
from typing import Optional
import logging


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
# Free Cash Flow
# --------------------------------------------------

def free_cash_flow(
    operating_activity: float,
    investing_activity: float
) -> float:
    """
    Free Cash Flow

    Formula

    CFO + CFI

    Investing activity is
    usually negative.
    """

    return round(

        operating_activity +
        investing_activity,

        2

    )


# --------------------------------------------------
# CFO Quality Score
# --------------------------------------------------

def cfo_quality_score(
    cfo_history: list,
    pat_history: list
) -> dict:
    """
    Average

    CFO / PAT

    over five years.

    Returns

    score

    label
    """

    if len(cfo_history) < 5:

        return {

            "score": None,

            "label": None

        }

    ratios = []

    for cfo, pat in zip(

        cfo_history[-5:],

        pat_history[-5:]

    ):

        if pat == 0:

            logger.info(
                "PAT is zero."
            )

            return {

                "score": None,

                "label": None

            }

        ratios.append(

            cfo / pat

        )

    score = round(

        sum(ratios) / len(ratios),

        2

    )

    if score > 1:

        label = "High Quality"

    elif score >= 0.5:

        label = "Moderate"

    else:

        label = "Accrual Risk"

    return {

        "score": score,

        "label": label

    }


# --------------------------------------------------
# CapEx Intensity
# --------------------------------------------------

def capex_intensity(
    investing_activity: float,
    sales: float
) -> dict:
    """
    Formula

    abs(CFI)

    -----------

    Sales

    x100
    """

    if sales == 0:

        return {

            "value": None,

            "label": None

        }

    intensity = round(

        abs(

            investing_activity

        ) / sales * 100,

        2

    )

    if intensity < 3:

        label = "Asset Light"

    elif intensity <= 8:

        label = "Moderate"

    else:

        label = "Capital Intensive"

    return {

        "value": intensity,

        "label": label

    }


# --------------------------------------------------
# FCF Conversion Rate
# --------------------------------------------------

def fcf_conversion_rate(
    free_cash_flow_value: float,
    operating_profit: float
) -> Optional[float]:
    """
    Formula

    FCF

    -----------

    Operating Profit

    x100
    """

    if operating_profit == 0:

        logger.info(

            "Operating Profit is zero."

        )

        return None

    return round(

        (

            free_cash_flow_value /

            operating_profit

        ) * 100,

        2

    )
# --------------------------------------------------
# Capital Allocation Pattern
# --------------------------------------------------

def capital_allocation_pattern(
    operating_activity: float,
    investing_activity: float,
    financing_activity: float,
    cfo_pat_score: Optional[float] = None
) -> str:
    """
    Capital Allocation Pattern

    Signs

    + = Positive
    - = Negative
    """

    cfo = "+" if operating_activity >= 0 else "-"
    cfi = "+" if investing_activity >= 0 else "-"
    cff = "+" if financing_activity >= 0 else "-"

    # (+,-,-)
    if cfo == "+" and cfi == "-" and cff == "-":

        if (
            cfo_pat_score is not None
            and cfo_pat_score > 1
        ):
            return "Shareholder Returns"

        return "Reinvestor"

    # (+,+,-)

    if cfo == "+" and cfi == "+" and cff == "-":
        return "Liquidating Assets"

    # (-,+,+)

    if cfo == "-" and cfi == "+" and cff == "+":
        return "Distress Signal"

    # (-,-,+)

    if cfo == "-" and cfi == "-" and cff == "+":
        return "Growth Funded by Debt"

    # (+,+,+)

    if cfo == "+" and cfi == "+" and cff == "+":
        return "Cash Accumulator"

    # (-,-,-)

    if cfo == "-" and cfi == "-" and cff == "-":
        return "Pre-Revenue"

    # (+,-,+)

    if cfo == "+" and cfi == "-" and cff == "+":
        return "Mixed"

    return "Other"


# --------------------------------------------------
# Combined Cash Flow KPI Engine
# --------------------------------------------------

def calculate_cashflow_metrics(
    row: dict
) -> dict:
    """
    Computes all cash flow KPIs
    for one company-year.
    """

    metrics = {}

    fcf = free_cash_flow(
        row.get("operating_activity", 0),
        row.get("investing_activity", 0)
    )

    metrics["free_cash_flow_cr"] = fcf

    quality = cfo_quality_score(
        row.get("cfo_history", []),
        row.get("pat_history", [])
    )

    metrics["cfo_quality_score"] = quality["score"]
    metrics["cfo_quality_label"] = quality["label"]

    capex = capex_intensity(
        row.get("investing_activity", 0),
        row.get("sales", 0)
    )

    metrics["capex_intensity_pct"] = capex["value"]
    metrics["capex_label"] = capex["label"]

    metrics["fcf_conversion_rate"] = fcf_conversion_rate(
        fcf,
        row.get("operating_profit", 0)
    )

    metrics["capital_allocation_pattern"] = (
        capital_allocation_pattern(
            row.get("operating_activity", 0),
            row.get("investing_activity", 0),
            row.get("financing_activity", 0),
            quality["score"]
        )
    )

    return metrics


# --------------------------------------------------
# Capital Allocation CSV
# --------------------------------------------------

def generate_capital_allocation_csv(
    dataframe,
    output_file="output/capital_allocation.csv"
):
    """
    Generates

    output/capital_allocation.csv
    """

    import pandas as pd

    records = []

    for _, row in dataframe.iterrows():

        pattern = capital_allocation_pattern(

            row["operating_activity"],

            row["investing_activity"],

            row["financing_activity"]

        )

        records.append({

            "company_id": row["company_id"],

            "year": row["year"],

            "cfo_sign":
                "+" if row["operating_activity"] >= 0 else "-",

            "cfi_sign":
                "+" if row["investing_activity"] >= 0 else "-",

            "cff_sign":
                "+" if row["financing_activity"] >= 0 else "-",

            "pattern_label": pattern

        })

    pd.DataFrame(records).to_csv(

        output_file,

        index=False

    )

    logger.info(

        f"Capital allocation file created: {output_file}"

    )


# --------------------------------------------------
# Demo
# --------------------------------------------------

if __name__ == "__main__":

    sample = {

        "operating_activity": 500,

        "investing_activity": -250,

        "financing_activity": -100,

        "sales": 2000,

        "operating_profit": 400,

        "cfo_history": [

            450,
            500,
            520,
            550,
            600

        ],

        "pat_history": [

            400,
            420,
            430,
            470,
            500

        ]

    }

    metrics = calculate_cashflow_metrics(
        sample
    )

    print("\nCash Flow KPIs\n")

    for key, value in metrics.items():

        print(
            f"{key:<35} {value}"
        )


# --------------------------------------------------
# Public Exports
# --------------------------------------------------

__all__ = [

    "free_cash_flow",

    "cfo_quality_score",

    "capex_intensity",

    "fcf_conversion_rate",

    "capital_allocation_pattern",

    "calculate_cashflow_metrics",

    "generate_capital_allocation_csv"

]