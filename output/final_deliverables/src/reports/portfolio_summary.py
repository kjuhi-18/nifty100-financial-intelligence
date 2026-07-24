import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas

# --------------------------------------------------
# Paths
# --------------------------------------------------

DB_PATH = "db/nifty100.db"

PORTFOLIO_DIR = Path("reports/portfolio")
PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = PORTFOLIO_DIR / "portfolio_summary.pdf"

PAGE_WIDTH = 595
PAGE_HEIGHT = 842

LEFT = 45
RIGHT = 45
TOP = 40

# --------------------------------------------------
# Database Loader
# --------------------------------------------------


class PortfolioLoader:

    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)

    def query(self, sql, params=None):
        return pd.read_sql(sql, self.conn, params=params)

    def get_companies(self):

        return self.query("""
            SELECT

                c.id,
                c.company_name,
                s.broad_sector

            FROM companies c

            JOIN sectors s
                ON c.id = s.company_id

            ORDER BY c.id
            """)

    def get_company_data(self, company_id):

        return self.query(
            """
            SELECT

                fr.year,

                fr.return_on_equity_pct,
                fr.return_on_capital_employed_pct,
                fr.earnings_per_share,
                fr.debt_to_equity,

                p.sales,
                p.net_profit

            FROM financial_ratios fr

            LEFT JOIN profitandloss p

                ON fr.company_id = p.company_id
               AND fr.year = p.year

            WHERE fr.company_id = ?

            ORDER BY fr.year
            """,
            [company_id],
        )

    def close(self):
        self.conn.close()


# --------------------------------------------------
# Helpers
# --------------------------------------------------


def safe(value, decimals=2):

    if pd.isna(value):
        return "N/A"

    try:
        return round(float(value), decimals)
    except Exception:
        return "N/A"


def trend_arrow(previous, latest):
    """
    ↑ improved
    ↓ declined
    → flat (within ±2%)
    """

    if pd.isna(previous) or pd.isna(latest):
        return "-"

    if previous == 0:
        return "→"

    change = ((latest - previous) / abs(previous)) * 100

    if change > 2:
        return "↑"

    if change < -2:
        return "↓"

    return "→"


# --------------------------------------------------
# Portfolio PDF
# --------------------------------------------------


class PortfolioSummary:

    def __init__(self, filename):

        self.canvas = canvas.Canvas(str(filename))

    def header(self, company, ticker, sector):

        c = self.canvas

        c.setFillColor(HexColor("#0B1F4D"))
        c.rect(0, PAGE_HEIGHT - 70, PAGE_WIDTH, 70, fill=1)

        c.setFillColor(white)

        c.setFont("Helvetica-Bold", 22)

        c.drawString(LEFT, PAGE_HEIGHT - 42, company)

        c.setFont("Helvetica", 12)

        c.drawRightString(PAGE_WIDTH - RIGHT, PAGE_HEIGHT - 42, ticker)

        c.setFillColor(HexColor("#1E3A8A"))

        c.setFont("Helvetica-Bold", 16)

        c.drawString(LEFT, PAGE_HEIGHT - 105, sector)

    def section_title(self, text, y):

        self.canvas.setFillColor(HexColor("#111827"))

        self.canvas.setFont("Helvetica-Bold", 15)

        self.canvas.drawString(LEFT, y, text)

        self.canvas.setStrokeColor(HexColor("#CBD5E1"))

        self.canvas.line(LEFT, y - 5, PAGE_WIDTH - RIGHT, y - 5)

    def draw_metric(self, y, name, value, arrow):

        self.canvas.setFillColor(black)

        self.canvas.setFont("Helvetica", 12)

        self.canvas.drawString(LEFT, y, name)

        self.canvas.drawRightString(330, y, str(value))

        self.canvas.setFont("Helvetica-Bold", 14)

        self.canvas.drawString(360, y, arrow)

    def footer(self):

        self.canvas.setStrokeColor(HexColor("#D1D5DB"))

        self.canvas.line(LEFT, 30, PAGE_WIDTH - RIGHT, 30)

        self.canvas.setFillColor(HexColor("#6B7280"))

        self.canvas.setFont("Helvetica", 8)

        self.canvas.drawString(LEFT, 15, "Portfolio Summary Report")

        self.canvas.drawRightString(
            PAGE_WIDTH - RIGHT, 15, f"Page {self.canvas.getPageNumber()}"
        )

    def save(self):
        self.canvas.save()

    # --------------------------------------------------


# Company Page
# --------------------------------------------------


def draw_company_page(pdf, company, history):

    latest = history.iloc[-1]

    if len(history) >= 2:
        previous = history.iloc[-2]
    else:
        previous = latest

    pdf.header(company["company_name"], company["id"], company["broad_sector"])

    pdf.section_title("Top 6 KPIs", 690)

    metrics = [
        (
            "Revenue",
            safe(latest["sales"]),
            trend_arrow(previous["sales"], latest["sales"]),
        ),
        (
            "Net Profit",
            safe(latest["net_profit"]),
            trend_arrow(previous["net_profit"], latest["net_profit"]),
        ),
        (
            "ROE %",
            safe(latest["return_on_equity_pct"]),
            trend_arrow(
                previous["return_on_equity_pct"], latest["return_on_equity_pct"]
            ),
        ),
        (
            "ROCE %",
            safe(latest["return_on_capital_employed_pct"]),
            trend_arrow(
                previous["return_on_capital_employed_pct"],
                latest["return_on_capital_employed_pct"],
            ),
        ),
        (
            "EPS",
            safe(latest["earnings_per_share"]),
            trend_arrow(previous["earnings_per_share"], latest["earnings_per_share"]),
        ),
        (
            "Debt / Equity",
            safe(latest["debt_to_equity"]),
            trend_arrow(previous["debt_to_equity"], latest["debt_to_equity"]),
        ),
    ]

    y = 640

    for name, value, arrow in metrics:

        pdf.draw_metric(y, name, value, arrow)

        y -= 55

    pdf.footer()

    pdf.canvas.showPage()


# --------------------------------------------------
# Generate Portfolio Summary
# --------------------------------------------------


def generate_portfolio_summary():

    print("Generating Portfolio Summary PDF...")

    loader = PortfolioLoader()

    companies = loader.get_companies()

    pdf = PortfolioSummary(OUTPUT_FILE)

    generated = 0

    for _, company in companies.iterrows():

        history = loader.get_company_data(company["id"])

        # Known data exceptions
        if company["id"] in ["SBIN", "ATGL"] and history.empty:

            pdf.header(company["company_name"], company["id"], company["broad_sector"])

            pdf.section_title("Top 6 KPIs", 690)

            pdf.canvas.setFont("Helvetica", 12)

            pdf.canvas.drawString(
                45, 650, "Financial KPI data is unavailable for this company."
            )

            pdf.footer()
            pdf.canvas.showPage()

            generated += 1
            print(f"✓ {company['id']} (placeholder page)")

            continue

        if history.empty:

            print(f"✗ No financial data : {company['id']}")
            continue

        draw_company_page(pdf, company, history)

        generated += 1

        print(f"✓ {company['id']}")

    pdf.save()

    loader.close()

    print("\n--------------------------------")
    print(f"Portfolio pages : {generated}")
    print(f"Saved to : {OUTPUT_FILE}")
    print("--------------------------------")


# --------------------------------------------------
# Main
# --------------------------------------------------


if __name__ == "__main__":

    generate_portfolio_summary()
