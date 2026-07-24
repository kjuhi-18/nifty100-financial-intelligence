import time

from fastapi import APIRouter

from src.api.database import get_connection

router = APIRouter(tags=["Health"])

START_TIME = time.time()

TABLES = [
    "companies",
    "sectors",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "financial_ratios",
    "peer_groups",
    "documents",
    "analysis",
    "stock_prices",
]


@router.get("/health")
def health():

    conn = get_connection()
    cursor = conn.cursor()

    row_counts = {}

    for table in TABLES:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_counts[table] = cursor.fetchone()[0]

    conn.close()

    return {
        "status": "ok",
        "db_row_counts": row_counts,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "version": "1.0.0",
    }
