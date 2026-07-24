
from fastapi import APIRouter, HTTPException, Query

from src.api.database import get_connection

router = APIRouter(tags=["Screener"])


@router.get("/screener")
def screener(
    min_roe: float | None = Query(None),
    max_de: float | None = Query(None),
    min_fcf: float | None = Query(None),
    sector: str | None = Query(None),
    min_rev_cagr_5yr: float | None = Query(None),
    min_pat_cagr_5yr: float | None = Query(None),
    max_pe: float | None = Query(None),
):

    # -------- Validation --------

    if min_roe is not None and min_roe < 0:
        raise HTTPException(status_code=400, detail="min_roe must be >= 0")

    if max_de is not None and max_de < 0:
        raise HTTPException(status_code=400, detail="max_de must be >= 0")

    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    SELECT
        c.id,
        c.company_name,

        s.broad_sector,

        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.free_cash_flow_cr,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr

    FROM companies c

    LEFT JOIN sectors s
        ON c.id = s.company_id

    LEFT JOIN financial_ratios fr
        ON c.id = fr.company_id
       AND fr.year = (
            SELECT MAX(year)
            FROM financial_ratios f2
            WHERE f2.company_id = c.id
       )

    WHERE 1=1
    """

    params = []

    if min_roe is not None:
        sql += " AND fr.return_on_equity_pct >= ?"
        params.append(min_roe)

    if max_de is not None:
        sql += " AND fr.debt_to_equity <= ?"
        params.append(max_de)

    if min_fcf is not None:
        sql += " AND fr.free_cash_flow_cr >= ?"
        params.append(min_fcf)

    if sector:
        sql += " AND s.broad_sector = ?"
        params.append(sector)

    if min_rev_cagr_5yr is not None:
        sql += " AND fr.revenue_cagr_5yr >= ?"
        params.append(min_rev_cagr_5yr)

    if min_pat_cagr_5yr is not None:
        sql += " AND fr.pat_cagr_5yr >= ?"
        params.append(min_pat_cagr_5yr)

    # Ignore max_pe for now if your database doesn't have a PE column

    sql += """
    ORDER BY
        fr.return_on_equity_pct DESC
    """

    cursor.execute(sql, params)

    rows = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return rows
