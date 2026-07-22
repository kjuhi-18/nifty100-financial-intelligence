from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.api.database import get_connection

router = APIRouter(tags=["Companies"])


@router.get("/companies")
def get_companies(
    sector: Optional[str] = Query(None),
    market_cap_category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    SELECT
        c.id,
        c.company_name,
        s.broad_sector,
        s.sub_sector,
        s.market_cap_category,
        fr.return_on_equity_pct AS roe_pct,
        fr.return_on_capital_employed_pct AS roce_pct

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

    if sector:
        sql += " AND s.broad_sector = ?"
        params.append(sector)

    if market_cap_category:
        sql += " AND s.market_cap_category = ?"
        params.append(market_cap_category)

    if search:
        sql += " AND c.company_name LIKE ?"
        params.append(f"%{search}%")

    sql += " ORDER BY c.company_name"

    cursor.execute(sql, params)

    rows = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return rows
@router.get("/companies/{company_id}")
def get_company(company_id: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            c.*,
            s.broad_sector,
            s.sub_sector,
            s.market_cap_category,
            fr.*

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

        WHERE c.id = ?
        """,
        (company_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    return dict(row)
@router.get("/companies/{company_id}/pl")
def get_profit_loss(company_id: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year DESC
    """, (company_id,))

    rows = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return rows
@router.get("/companies/{company_id}/bs")
def get_balance_sheet(company_id: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year DESC
    """, (company_id,))

    rows = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return rows
@router.get("/companies/{company_id}/cashflow")
def get_cashflow(company_id: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year DESC
    """, (company_id,))

    rows = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return rows
@router.get("/companies/{company_id}/ratios")
def get_ratios(company_id: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year DESC
    """, (company_id,))

    rows = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return rows
@router.get("/companies/{company_id}/tearsheet")
def get_tearsheet(company_id: str):

    conn = get_connection()
    cursor = conn.cursor()

    # Company Details
    cursor.execute("""
        SELECT
            c.*,
            s.broad_sector,
            s.sub_sector,
            s.market_cap_category
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        WHERE c.id = ?
    """, (company_id,))
    company = cursor.fetchone()

    if company is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")

    # Latest Ratios
    cursor.execute("""
        SELECT *
        FROM financial_ratios
        WHERE company_id = ?
        ORDER BY year DESC
        LIMIT 1
    """, (company_id,))
    ratios = cursor.fetchone()

    # Profit & Loss History
    cursor.execute("""
        SELECT *
        FROM profitandloss
        WHERE company_id = ?
        ORDER BY year DESC
    """, (company_id,))
    pl = [dict(row) for row in cursor.fetchall()]

    # Balance Sheet History
    cursor.execute("""
        SELECT *
        FROM balancesheet
        WHERE company_id = ?
        ORDER BY year DESC
    """, (company_id,))
    bs = [dict(row) for row in cursor.fetchall()]

    # Cash Flow History
    cursor.execute("""
        SELECT *
        FROM cashflow
        WHERE company_id = ?
        ORDER BY year DESC
    """, (company_id,))
    cf = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "company": dict(company),
        "ratios": dict(ratios) if ratios else {},
        "profit_loss": pl,
        "balance_sheet": bs,
        "cash_flow": cf
    }