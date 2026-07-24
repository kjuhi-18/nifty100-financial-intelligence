from fastapi import APIRouter, HTTPException

from src.api.database import get_connection

router = APIRouter(tags=["Sectors"])


@router.get("/sectors/{sector}/companies")
def get_sector_companies(sector: str):

    conn = get_connection()
    cursor = conn.cursor()

    # Check if sector exists
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM sectors
        WHERE broad_sector = ?
    """,
        (sector,),
    )

    if cursor.fetchone()[0] == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Sector not found")

    cursor.execute(
        """
        SELECT
            c.id,
            c.company_name,

            s.broad_sector,
            s.sub_sector,
            s.market_cap_category,

            fr.return_on_equity_pct,
            fr.return_on_capital_employed_pct,
            fr.debt_to_equity,
            fr.free_cash_flow_cr,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            fr.eps_cagr_5yr,
            fr.composite_quality_score

        FROM companies c

        JOIN sectors s
            ON c.id = s.company_id

        LEFT JOIN financial_ratios fr
            ON c.id = fr.company_id
           AND fr.year = (
                SELECT MAX(year)
                FROM financial_ratios f2
                WHERE f2.company_id = c.id
           )

        WHERE s.broad_sector = ?

        ORDER BY c.company_name
    """,
        (sector,),
    )

    rows = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return rows
