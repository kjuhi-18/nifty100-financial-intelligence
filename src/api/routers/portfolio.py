from fastapi import APIRouter
import statistics

from src.api.database import get_connection

router = APIRouter(tags=["Portfolio"])


@router.get("/portfolio/stats")
def portfolio_stats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            return_on_equity_pct,
            return_on_capital_employed_pct,
            debt_to_equity,
            interest_coverage,
            asset_turnover,
            free_cash_flow_cr,
            revenue_cagr_5yr,
            pat_cagr_5yr,
            eps_cagr_5yr,
            composite_quality_score
        FROM financial_ratios
    """)

    rows = [dict(r) for r in cursor.fetchall()]

    conn.close()

    metrics = [
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score"
    ]

    percentiles = [10,20,30,40,50,60,70,80,90]

    result = {}

    for metric in metrics:

        values = sorted(
            r[metric]
            for r in rows
            if r[metric] is not None
        )

        if not values:
            result[metric] = {}
            continue

        metric_stats = {}

        for p in percentiles:

            k = round((p/100) * (len(values)-1))

            metric_stats[f"P{p}"] = values[k]

        result[metric] = metric_stats

    return result