from fastapi import APIRouter, HTTPException

from src.api.database import get_connection

router = APIRouter(tags=["Peers"])


@router.get("/peers/{group_name}")
def get_peer_group(group_name: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            pg.company_id,
            c.company_name,
            pg.is_benchmark,

            fr.return_on_equity_pct,
            fr.return_on_capital_employed_pct,
            fr.debt_to_equity,
            fr.interest_coverage,
            fr.asset_turnover,
            fr.free_cash_flow_cr,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            fr.eps_cagr_5yr,
            fr.composite_quality_score

        FROM peer_groups pg

        JOIN companies c
            ON pg.company_id = c.id

        LEFT JOIN financial_ratios fr
            ON pg.company_id = fr.company_id
           AND fr.year = (
                SELECT MAX(year)
                FROM financial_ratios f2
                WHERE f2.company_id = pg.company_id
           )

        WHERE pg.peer_group_name = ?
    """,
        (group_name,),
    )

    rows = [dict(row) for row in cursor.fetchall()]

    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="Peer group not found")

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
        "composite_quality_score",
    ]

    # Percentile calculation
    for metric in metrics:

        values = sorted([r[metric] for r in rows if r[metric] is not None])

        if not values:
            continue

        for r in rows:

            value = r[metric]

            if value is None:
                r[f"{metric}_percentile"] = None
                continue

            rank = values.index(value) + 1

            percentile = round(rank / len(values) * 100, 2)

            r[f"{metric}_percentile"] = percentile

    return rows




@router.get("/companies/{ticker}/peers/compare")
def compare_with_peers(ticker: str):

    conn = get_connection()
    cursor = conn.cursor()

    # Find peer group
    cursor.execute(
        """
        SELECT peer_group_name
        FROM peer_groups
        WHERE company_id = ?
    """,
        (ticker,),
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        raise HTTPException(
            status_code=404, detail="Company not found in any peer group"
        )

    peer_group = row["peer_group_name"]

    # Fetch all companies in peer group
    cursor.execute(
        """
        SELECT
            pg.company_id,
            c.company_name,
            pg.is_benchmark,

            fr.return_on_equity_pct,
            fr.return_on_capital_employed_pct,
            fr.debt_to_equity,
            fr.interest_coverage,
            fr.asset_turnover,
            fr.free_cash_flow_cr,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr

        FROM peer_groups pg

        JOIN companies c
            ON pg.company_id = c.id

        LEFT JOIN financial_ratios fr
            ON pg.company_id = fr.company_id
           AND fr.year = (
                SELECT MAX(year)
                FROM financial_ratios f2
                WHERE f2.company_id = pg.company_id
           )

        WHERE pg.peer_group_name = ?
    """,
        (peer_group,),
    )

    peers = [dict(r) for r in cursor.fetchall()]

    conn.close()

    company = next((r for r in peers if r["company_id"] == ticker), None)
    benchmark = next((r for r in peers if r["is_benchmark"] == 1), None)

    metrics = [
        ("ROE", "return_on_equity_pct"),
        ("ROCE", "return_on_capital_employed_pct"),
        ("Debt_to_Equity", "debt_to_equity"),
        ("Interest_Coverage", "interest_coverage"),
        ("Asset_Turnover", "asset_turnover"),
        ("Free_Cash_Flow", "free_cash_flow_cr"),
        ("Revenue_CAGR", "revenue_cagr_5yr"),
        ("PAT_CAGR", "pat_cagr_5yr"),
    ]

    result = {}

    for label, field in metrics:

        values = [p[field] for p in peers if p[field] is not None]

        avg = round(sum(values) / len(values), 2) if values else None

        result[label] = {
            "company": company[field] if company else None,
            "peer_average": avg,
            "benchmark": benchmark[field] if benchmark else None,
        }

    return {
        "company": ticker,
        "peer_group": peer_group,
        "benchmark": benchmark["company_name"] if benchmark else None,
        "metrics": result,
    }
