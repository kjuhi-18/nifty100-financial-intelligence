from pathlib import Path
from typing import Optional
import logging
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

    if pd.isna(operating_activity):
        return None

    if pd.isna(investing_activity):
        return None

    return round(
    operating_activity + investing_activity,
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

    if pd.isna(investing_activity):
        return {
        "value": None,
        "label": None
    }

    if pd.isna(sales):
        return {
        "value": None,
        "label": None
    }

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

    if pd.isna(free_cash_flow_value):
        return None

    if pd.isna(operating_profit):
        return None

    if operating_profit == 0:
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
    if pd.isna(operating_activity):
        return "Unknown"

    if pd.isna(investing_activity):
        return "Unknown"

    if pd.isna(financing_activity):
        return "Unknown"

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
# --------------------------------------------------
# Distress Signal
# --------------------------------------------------

def distress_signal(
    operating_activity: float,
    financing_activity: float
) -> bool:

    if pd.isna(operating_activity):
        return False

    if pd.isna(financing_activity):
        return False

    return (
        operating_activity < 0
        and financing_activity > 0
    )
# --------------------------------------------------
# Deleveraging Flag
# --------------------------------------------------

def deleveraging_flag(
    current_borrowings: float,
    previous_borrowings: float,
    financing_activity: float
) -> bool:

    if pd.isna(current_borrowings):
        return False

    if pd.isna(previous_borrowings):
        return False

    if pd.isna(financing_activity):
        return False

    return (
        financing_activity < 0
        and current_borrowings < previous_borrowings
    )
# --------------------------------------------------
# FCF CAGR
# --------------------------------------------------

def fcf_cagr(history):
    """
    Calculates 5-year CAGR of Free Cash Flow.
    Returns None if CAGR cannot be computed.
    """

    history = [x for x in history if pd.notna(x)]

    if len(history) < 5:
        return None

    start = history[-5]
    end = history[-1]

    # CAGR is not meaningful if either value is non-positive
    if start <= 0 or end <= 0:
        return None

    years = 4

    try:
        return round(
            ((end / start) ** (1 / years) - 1) * 100,
            2
        )
    except Exception:
        logger.info(
            f"Unable to calculate FCF CAGR. Start={start}, End={end}"
        )
        return None
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
        ))
    metrics["distress_flag"] = distress_signal(
    row.get("operating_activity", 0),
    row.get("financing_activity", 0)
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

# =====================================================
# Prepare Latest Financial Snapshot
# =====================================================

def prepare_latest_snapshot(
    cashflow_df,
    ratios_df,
    pnl_df
):

    latest_cf = (
        cashflow_df
        .sort_values("year")
        .groupby("company_id")
        .tail(1)
    )

    latest_ratios = (
        ratios_df
        .sort_values("year")
        .groupby("company_id")
        .tail(1)
    )

    latest_pnl = (
        pnl_df
        .sort_values("year")
        .groupby("company_id")
        .tail(1)
    )

    latest = (
        latest_cf

        .merge(
            latest_ratios,
            on=["company_id", "year"],
            how="left",
            suffixes=("", "_ratio")
        )

        .merge(
            latest_pnl,
            on=["company_id", "year"],
            how="left",
            suffixes=("", "_pnl")
        )
    )

    return latest
# =====================================================
# FCF CAGR (5 Years)
# =====================================================

def calculate_fcf_cagr(ratios_df):

    records = []

    for company, group in ratios_df.groupby("company_id"):

        group = (
            group
            .sort_values("year")
            .tail(5)
        )

        history = (
            group["free_cash_flow_cr"]
            .dropna()
            .tolist()
        )

        cagr = fcf_cagr(history)

        records.append({

            "company_id": company,

            "fcf_cagr_5yr": cagr

        })

    return pd.DataFrame(records)
# =====================================================
# Deleveraging Detection
# =====================================================

def calculate_deleveraging_flags(
    cashflow_df,
    ratios_df
):

    records = []

    latest_cf = (
        cashflow_df
        .sort_values("year")
        .groupby("company_id")
        .tail(1)
    )

    for company, group in ratios_df.groupby("company_id"):

        group = group.sort_values("year")

        if len(group) < 2:
            continue

        current = group.iloc[-1]
        previous = group.iloc[-2]

        cf = latest_cf[
            latest_cf.company_id == company
        ]

        if cf.empty:
            continue

        financing = cf.iloc[0]["financing_activity"]

        flag = (

            financing < 0

            and

            current["total_debt_cr"] < previous["total_debt_cr"]

        )

        records.append({

            "company_id": company,

            "deleveraging_flag": flag

        })

    return pd.DataFrame(records)
# =====================================================
# Cash Flow Intelligence Dataset
# =====================================================

def build_cashflow_intelligence(

    latest,

    fcf_df,

    deleveraging_df

):

    df = (

        latest

        .merge(

            fcf_df,

            on="company_id",

            how="left"

        )

        .merge(

            deleveraging_df,

            on="company_id",

            how="left"

        )

    )

    return df
# =====================================================
# Export Cash Flow Intelligence
# =====================================================

def export_cashflow_intelligence(
    intelligence_df,
    output_file="output/cashflow_intelligence.xlsx"
):

    columns = [

        "company_id",
        "broad_sector",
        "sub_sector",
        "market_cap_category",
        "cfo_quality_score",
        "cfo_quality_label",
        "capex_intensity_pct",
        "capex_label",
        "fcf_cagr_5yr",
        "fcf_conversion_rate",
        "distress_flag",
        "deleveraging_flag",
        "capital_allocation_pattern"

    ]

    export_df = intelligence_df.copy()

    for col in columns:
        if col not in export_df.columns:
            export_df[col] = None

    export_df = export_df[columns]

    export_df.to_excel(
        output_file,
        index=False
    )

    logger.info(
        f"Cash Flow Intelligence exported : {output_file}"
    )

    print("\nSaved :", output_file)
    print("Companies :", len(export_df))
# =====================================================
# Export Distress Alerts
# =====================================================

def export_distress_alerts(
    intelligence_df,
    output_file="output/distress_alerts.csv"
):

    alerts = intelligence_df[

        intelligence_df["distress_flag"] == True

    ].copy()

    columns = [

        "company_id",
        "operating_activity",
        "financing_activity",
        "net_profit"

    ]

    for col in columns:
        if col not in alerts.columns:
            alerts[col] = None

    alerts = alerts[columns]

    alerts.to_csv(
        output_file,
        index=False
    )

    logger.info(
        f"Distress Alerts exported : {output_file}"
    )

    print("Saved :", output_file)
    print("Alerts :", len(alerts))
# =====================================================
# Validation
# =====================================================

def validate_outputs(
    intelligence_df
):

    print("\n" + "=" * 70)
    print("DAY 31 VALIDATION")
    print("=" * 70)

    print()

    print("Companies Processed :",
          intelligence_df["company_id"].nunique())

    print()

    print("Distress Companies :",
          intelligence_df["distress_flag"].sum())

    print()

    print("Deleveraging Companies :",
          intelligence_df["deleveraging_flag"].sum())

    print()

    print("Average CFO Quality Score :",
          round(
              intelligence_df["cfo_quality_score"].dropna().mean(),
              2
          ))

    print()

    print("Capital Allocation")

    print(
        intelligence_df[
            "capital_allocation_pattern"
        ].value_counts()
    )

    print()

    print("PASS : Cash Flow Intelligence Generated")

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

    "generate_capital_allocation_csv",
    "prepare_latest_snapshot",
    "calculate_fcf_cagr",
    "calculate_deleveraging_flags",
    "build_cashflow_intelligence",
    "export_cashflow_intelligence",
    "export_distress_alerts",
    "validate_outputs"

]