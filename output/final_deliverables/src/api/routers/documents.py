from fastapi import APIRouter, HTTPException

from src.api.database import get_connection

router = APIRouter(tags=["Documents"])


@router.get("/companies/{ticker}/documents")
def get_company_documents(ticker: str):

    conn = get_connection()
    cursor = conn.cursor()

    # Check if company exists
    cursor.execute(
        """
        SELECT company_name
        FROM companies
        WHERE id = ?
    """,
        (ticker,),
    )

    company = cursor.fetchone()

    if company is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")

    cursor.execute(
        """
        SELECT
            company_id,
            year,
            annual_report
        FROM documents
        WHERE company_id = ?
        ORDER BY year DESC
    """,
        (ticker,),
    )

    rows = []

    for row in cursor.fetchall():

        report = row["annual_report"]

        rows.append(
            {
                "company_id": row["company_id"],
                "year": row["year"],
                "annual_report": report,
                "is_url_valid": report is not None
                and report.startswith(("http://", "https://")),
            }
        )

    conn.close()

    return rows
