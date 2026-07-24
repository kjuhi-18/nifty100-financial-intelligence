import csv
import sqlite3
import traceback
from pathlib import Path

import pandas as pd
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

PAGE_WIDTH = 595
PAGE_HEIGHT = 842

LEFT_MARGIN = 35
RIGHT_MARGIN = 35

TOP_MARGIN = 35

REPORT_DIR = Path("reports/tearsheets")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SECTOR_REPORT_DIR = Path("reports/sector")
SECTOR_REPORT_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = "db/nifty100.db"

styles = getSampleStyleSheet()

TITLE_STYLE = styles["Heading1"]
TITLE_STYLE.alignment = TA_CENTER

BODY_STYLE = styles["BodyText"]

BODY_STYLE.leading = 15


def safe_value(value, decimals=2):
    """
    Safely format numeric values for display.
    Returns 'N/A' for missing values.
    """
    if pd.isna(value):
        return "N/A"

    try:
        return round(float(value), decimals)
    except (TypeError, ValueError):
        return "N/A"


class CompanyDataLoader:

    def __init__(self, db_path=DB_PATH):

        self.conn = sqlite3.connect(db_path)

    def query(self, sql, params=None):

        return pd.read_sql(sql, self.conn, params=params)

    def get_sectors(self):

        return self.query("""

        SELECT DISTINCT
            broad_sector
        FROM sectors
        ORDER BY broad_sector

    """)

    def get_sector_companies(self, sector):

        return self.query(
            """

        SELECT

            c.id,
            c.company_name,

            s.broad_sector,

            fr.return_on_equity_pct,
            fr.return_on_capital_employed_pct,
            fr.earnings_per_share,
            fr.debt_to_equity,

            p.sales,
            p.net_profit

        FROM companies c

        JOIN sectors s
            ON c.id = s.company_id

        LEFT JOIN financial_ratios fr
            ON c.id = fr.company_id

        LEFT JOIN profitandloss p
            ON c.id = p.company_id
            AND fr.year = p.year

        WHERE s.broad_sector = ?

        ORDER BY c.company_name

    """,
            [sector],
        )

    def close(self):

        self.conn.close()


def load_company_data(loader, company):

    data = {}

    data["company"] = loader.query(
        """
        SELECT *
        FROM companies
        WHERE id=?
        """,
        [company],
    )

    data["pnl"] = loader.query(
        """
        SELECT *
        FROM profitandloss
        WHERE company_id=?
        ORDER BY year
        """,
        [company],
    )

    data["balance"] = loader.query(
        """
        SELECT *
        FROM balancesheet
        WHERE company_id=?
        ORDER BY year
        """,
        [company],
    )

    data["cashflow"] = loader.query(
        """
        SELECT *
        FROM cashflow
        WHERE company_id=?
        ORDER BY year
        """,
        [company],
    )

    data["ratios"] = loader.query(
        """
        SELECT *
        FROM financial_ratios
        WHERE company_id=?
        ORDER BY year
        """,
        [company],
    )

    data["pros"] = loader.query(
        """
        SELECT *
        FROM prosandcons
        WHERE company_id=?
        """,
        [company],
    )

    return data


class Tearsheet:

    def __init__(self, filename):

        self.canvas = canvas.Canvas(filename)

        self.width = PAGE_WIDTH
        self.height = PAGE_HEIGHT

    def draw_header(self, company_name, company_id):

        c = self.canvas

        c.setFillColor(HexColor("#0B1F4D"))

        c.rect(0, PAGE_HEIGHT - 70, PAGE_WIDTH, 70, fill=1)

        c.setFillColor(colors.white)

        c.setFont("Helvetica-Bold", 22)

        c.drawString(35, PAGE_HEIGHT - 40, company_name)

        c.setFont("Helvetica", 12)

        c.drawRightString(PAGE_WIDTH - 35, PAGE_HEIGHT - 40, company_id)

    def section_title(self, text, y):

        self.canvas.setFillColor(HexColor("#0F172A"))

        self.canvas.setFont("Helvetica-Bold", 15)

        self.canvas.drawString(LEFT_MARGIN, y, text)

        self.canvas.setStrokeColor(HexColor("#CBD5E1"))

        self.canvas.line(LEFT_MARGIN, y - 6, PAGE_WIDTH - RIGHT_MARGIN, y - 6)

    def save(self):

        self.canvas.save()

    def draw_kpi_tile(self, x, y, width, height, title, value, color="#1E3A8A"):

        c = self.canvas

        c.setFillColor(HexColor("#F8FAFC"))
        c.roundRect(x, y, width, height, 8, fill=1, stroke=0)

        c.setStrokeColor(HexColor(color))
        c.roundRect(x, y, width, height, 8, fill=0)

        c.setFillColor(HexColor("#64748B"))
        c.setFont("Helvetica", 9)
        c.drawString(x + 10, y + height - 18, title)

        c.setFillColor(HexColor(color))
        c.setFont("Helvetica-Bold", 16)
        c.drawString(x + 10, y + 16, str(value))

    def draw_kpi_section(self, latest):

        tile_w = 155
        tile_h = 60

        start_x = 35
        start_y = 620

        gap_x = 15
        gap_y = 15

        kpis = [
            ("Revenue", safe_value(latest.get("sales"))),
            ("Net Profit", safe_value(latest.get("net_profit"))),
            ("ROE %", safe_value(latest.get("return_on_equity_pct"))),
            ("ROCE %", safe_value(latest.get("return_on_capital_employed_pct"))),
            ("EPS", safe_value(latest.get("earnings_per_share"))),
            ("Debt/Equity", safe_value(latest.get("debt_to_equity"))),
        ]

        for i, (title, value) in enumerate(kpis):

            row = i // 3
            col = i % 3

            self.draw_kpi_tile(
                start_x + col * (tile_w + gap_x),
                start_y - row * (tile_h + gap_y),
                tile_w,
                tile_h,
                title,
                value,
            )

    def revenue_chart(self, pnl):

        drawing = Drawing(250, 170)

        chart = VerticalBarChart()

        chart.x = 35
        chart.y = 25

        chart.width = 180
        chart.height = 120

        chart.data = [pnl["sales"].tail(10).tolist()]

        chart.categoryAxis.categoryNames = [str(x)[-2:] for x in pnl["year"].tail(10)]

        drawing.add(chart)

        renderPDF.draw(drawing, self.canvas, 35, 290)

    def profit_chart(self, pnl):

        drawing = Drawing(250, 170)

        chart = VerticalBarChart()

        chart.x = 35
        chart.y = 25

        chart.width = 180
        chart.height = 120

        chart.data = [pnl["net_profit"].tail(10).tolist()]

        chart.categoryAxis.categoryNames = [str(x)[-2:] for x in pnl["year"].tail(10)]

        drawing.add(chart)

        renderPDF.draw(drawing, self.canvas, 310, 290)

    def roe_roce_chart(self, ratios):

        drawing = Drawing(520, 170)

        chart = HorizontalLineChart()

        chart.x = 40
        chart.y = 30
        chart.width = 420
        chart.height = 100

        # Keep only rows where BOTH values exist
        df = ratios[
            ["year", "return_on_equity_pct", "return_on_capital_employed_pct"]
        ].dropna()

        # Need at least 2 points to draw a line
        if len(df) < 2:
            self.canvas.setFont("Helvetica", 11)
            self.canvas.drawString(
                35, 120, "ROE / ROCE trend unavailable (insufficient data)"
            )
        return

        roe = df["return_on_equity_pct"].tolist()
        roce = df["return_on_capital_employed_pct"].tolist()

        chart.data = [roe, roce]

        chart.categoryAxis.categoryNames = [str(y)[-2:] for y in df["year"]]

        drawing.add(chart)

        renderPDF.draw(drawing, self.canvas, 35, 80)

    def balance_sheet_chart(self, balance):

        self.section_title("Balance Sheet Composition", 770)

        latest = balance.iloc[-1]

        labels = ["Equity", "Reserves", "Borrowings", "Other Liabilities"]

        values = [
            latest["equity_capital"],
            latest["reserves"],
            latest["borrowings"],
            latest["other_liabilities"],
        ]

        y = 730

        total = sum(v for v in values if pd.notna(v))

        for label, value in zip(labels, values):

            value = 0 if pd.isna(value) else value

            pct = value / total if total else 0

            self.canvas.setFont("Helvetica", 10)

            self.canvas.drawString(40, y, label)

            self.canvas.setFillColor(HexColor("#2563EB"))

            self.canvas.rect(140, y - 5, pct * 250, 12, fill=1, stroke=0)

            self.canvas.setFillColor(colors.black)

            self.canvas.drawRightString(430, y, f"{value:,.0f}")

            y -= 28

    def cashflow_summary(self, cashflow):

        self.section_title("Cash Flow Summary", 560)

        if cashflow.empty:
            self.canvas.drawString(40, 530, "No cash flow data available")
            return

        latest = cashflow.iloc[-1]

        rows = [
            ["Operating", safe_value(latest.get("operating_activity"))],
            ["Investing", safe_value(latest.get("investing_activity"))],
            ["Financing", safe_value(latest.get("financing_activity"))],
            ["Net Cash Flow", safe_value(latest.get("net_cash_flow"))],
        ]

        table = Table([["Type", "Value"]] + rows, colWidths=[180, 120])

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E3A8A")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ]
            )
        )

        table.wrapOn(self.canvas, 0, 0)
        table.drawOn(self.canvas, 40, 360)

    def pros_cons_section(self, pros_df):

        self.section_title("Pros", 310)

        if pros_df.empty:
            self.canvas.drawString(40, 285, "No data available")
            return

        row = pros_df.iloc[0]

        pros = str(row["pros"]) if pd.notna(row["pros"]) else "None"
        cons = str(row["cons"]) if pd.notna(row["cons"]) else "None"

        p = Paragraph(pros, BODY_STYLE)
        p.wrapOn(self.canvas, 230, 120)
        p.drawOn(self.canvas, 40, 170)

        self.section_title("Cons", 310)

        p = Paragraph(cons, BODY_STYLE)
        p.wrapOn(self.canvas, 230, 120)
        p.drawOn(self.canvas, 310, 170)

    # ==========================
    # PART 3
    # ==========================

    def balance_sheet_chart(self, balance):

        self.section_title("Balance Sheet Composition", 770)

        if balance.empty:
            self.canvas.drawString(40, 740, "No Balance Sheet Data")
            return

        latest = balance.iloc[-1]

        labels = ["Equity Capital", "Reserves", "Borrowings", "Other Liabilities"]

        values = [
            latest.get("equity_capital", 0),
            latest.get("reserves", 0),
            latest.get("borrowings", 0),
            latest.get("other_liabilities", 0),
        ]

        values = [0 if pd.isna(v) else float(v) for v in values]

        total = sum(values)

        y = 730

        for label, value in zip(labels, values):

            pct = value / total if total > 0 else 0

            self.canvas.setFillColor(colors.black)
            self.canvas.setFont("Helvetica", 10)

            self.canvas.drawString(40, y, label)

            self.canvas.setFillColor(HexColor("#2563EB"))

            self.canvas.rect(170, y - 5, pct * 220, 12, fill=1, stroke=0)

            self.canvas.setFillColor(colors.black)

            self.canvas.drawRightString(470, y, f"{value:,.0f}")

            y -= 28

    def cashflow_summary(self, cashflow):

        self.section_title("Cash Flow Summary", 560)

        if cashflow.empty:
            self.canvas.drawString(40, 530, "No Cash Flow Data")
            return

        latest = cashflow.iloc[-1]

        rows = [
            ["Operating Activity", safe_value(latest.get("operating_activity"))],
            ["Investing Activity", safe_value(latest.get("investing_activity"))],
            ["Financing Activity", safe_value(latest.get("financing_activity"))],
            ["Net Cash Flow", safe_value(latest.get("net_cash_flow"))],
        ]

        table = Table([["Type", "Value"]] + rows, colWidths=[210, 120])

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E3A8A")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), HexColor("#F8FAFC")),
                ]
            )
        )

        table.wrapOn(self.canvas, 0, 0)
        table.drawOn(self.canvas, 40, 360)

    def pros_cons_section(self, pros_df):

        self.section_title("Pros", 310)

        if pros_df.empty:

            self.canvas.drawString(40, 285, "No Pros / Cons Available")
            return

        row = pros_df.iloc[0]

        pros = str(row.get("pros", "")) if pd.notna(row.get("pros")) else "None"

        cons = str(row.get("cons", "")) if pd.notna(row.get("cons")) else "None"

        pros = pros.replace(".", ".<br/>• ")
        cons = cons.replace(".", ".<br/>• ")

        Paragraph("• " + pros, BODY_STYLE).wrapOn(self.canvas, 220, 130)

        p = Paragraph("• " + pros, BODY_STYLE)

        p.wrapOn(self.canvas, 220, 130)
        p.drawOn(self.canvas, 40, 160)

        self.section_title("Cons", 310)

        c = Paragraph("• " + cons, BODY_STYLE)

        c.wrapOn(self.canvas, 220, 130)
        c.drawOn(self.canvas, 310, 160)

    def draw_footer(self):

        self.canvas.setStrokeColor(HexColor("#D1D5DB"))

        self.canvas.line(35, 25, PAGE_WIDTH - 35, 25)

        self.canvas.setFillColor(HexColor("#6B7280"))

        self.canvas.setFont("Helvetica", 8)

        self.canvas.drawString(
            35, 12, "Generated using N100 Financial Analytics Pipeline"
        )

        self.canvas.drawRightString(
            PAGE_WIDTH - 35, 12, f"Page {self.canvas.getPageNumber()}"
        )


class SectorReport(Tearsheet):
    def draw_sector_summary(self, sector, df):

        self.section_title("Sector Summary", 700)

        self.canvas.setFont("Helvetica", 12)

        metrics = [
            ("Companies", len(df)),
            ("Median Revenue", round(df["sales"].median(), 2)),
            ("Median Net Profit", round(df["net_profit"].median(), 2)),
            ("Median ROE", round(df["return_on_equity_pct"].median(), 2)),
            ("Median ROCE", round(df["return_on_capital_employed_pct"].median(), 2)),
            ("Median EPS", round(df["earnings_per_share"].median(), 2)),
            ("Median Debt/Equity", round(df["debt_to_equity"].median(), 2)),
        ]

        y = 660

        for label, value in metrics:

            self.canvas.drawString(50, y, label)

            self.canvas.drawRightString(300, y, str(value))

            y -= 30

    def draw_company_table(self, df):

        self.canvas.showPage()

        self.draw_header("Sector Companies", "")

        self.section_title("Company Metrics", 780)

        table_data = [["Company", "Revenue", "Profit", "ROE", "ROCE", "EPS", "D/E"]]

        for _, row in df.iterrows():

            table_data.append(
                [
                    row["company_name"],
                    safe_value(row["sales"]),
                    safe_value(row["net_profit"]),
                    safe_value(row["return_on_equity_pct"]),
                    safe_value(row["return_on_capital_employed_pct"]),
                    safe_value(row["earnings_per_share"]),
                    safe_value(row["debt_to_equity"]),
                ]
            )

        table = Table(table_data, colWidths=[120, 70, 70, 45, 45, 45, 45])

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E3A8A")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("BACKGROUND", (0, 1), (-1, -1), HexColor("#F8FAFC")),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ]
            )
        )

        table.wrapOn(self.canvas, 0, 0)
        table.drawOn(self.canvas, 25, 80)

        self.draw_footer()


def create_tearsheet(company_id):
    loader = CompanyDataLoader()

    data = load_company_data(loader, company_id)

    pdf = Tearsheet(str(REPORT_DIR / f"{company_id}_tearsheet.pdf"))

    company = data["company"].iloc[0]

    pdf.draw_header(company["company_name"], company["id"])
    # ---------------- KPI + Charts ----------------

    if not data["ratios"].empty:

        latest = data["ratios"].iloc[-1].copy()

        if not data["pnl"].empty:
            latest["sales"] = data["pnl"].iloc[-1]["sales"]
            latest["net_profit"] = data["pnl"].iloc[-1]["net_profit"]

        pdf.draw_kpi_section(latest)
        pdf.roe_roce_chart(data["ratios"])

    else:

        pdf.section_title("Financial Summary", 690)

        pdf.canvas.setFont("Helvetica", 12)

        pdf.canvas.drawString(40, 660, "Financial ratio data not available.")

        if not data["pnl"].empty:
            pdf.revenue_chart(data["pnl"])
            pdf.profit_chart(data["pnl"])
            pdf.draw_footer()  # if you added it
            pdf.canvas.showPage()

            pdf.draw_header(company["company_name"], company["id"])

            pdf.balance_sheet_chart(data["balance"])
            pdf.cashflow_summary(data["cashflow"])
            pdf.pros_cons_section(data["pros"])

            pdf.draw_footer()  # if you added it
            pdf.save()
            loader.close()


def create_sector_report(sector):

    print(f"Generating sector report : {sector}")

    loader = CompanyDataLoader()

    df = loader.get_sector_companies(sector)

    loader.close()

    pdf = SectorReport(str(SECTOR_REPORT_DIR / f"{sector}_report.pdf"))

    pdf.draw_header(sector, "Sector Report")

    pdf.draw_sector_summary(sector, df)
    pdf.draw_company_table(df)

    pdf.draw_footer()

    pdf.save()


if __name__ == "__main__":

    loader = CompanyDataLoader()

    try:

        companies = loader.query("""

            SELECT DISTINCT id
            FROM companies
            ORDER BY id

        """)

        total = len(companies)

        print(f"Generating {total} tearsheets...\n")

        success = 0
        skipped = []
        failed = []

        for company_id in companies["id"]:

            try:
                loader2 = CompanyDataLoader()

                data = load_company_data(loader2, company_id)

                years = len(data["pnl"])

                loader2.close()

                if years < 3:

                    skipped.append([company_id, years])

                    print(f"Skipped {company_id} ({years} years)")

                    continue

                create_tearsheet(company_id)

                print(f"✓ {company_id}")

                success += 1

            except Exception:

                print(f"\n✗ {company_id}")
                traceback.print_exc()

                failed.append(company_id)
        with open(OUTPUT_DIR / "skipped_tearsheets.csv", "w", newline="") as f:

            writer = csv.writer(f)

            writer.writerow(["Ticker", "Years Available"])

            writer.writerows(skipped)
        print("\n==============================")
        print(f"Generated : {success}")
        print(f"Failed    : {len(failed)}")

        if failed:

            print("\nFailed Companies:")

            for c in failed:

                print(c)
        print("\nGenerating sector reports...\n")

        sectors = loader.get_sectors()
        for sector in sectors["broad_sector"]:

            try:

                create_sector_report(sector)

                print(f"✓ {sector}")

            except Exception:

                print(f"✗ {sector}")

                traceback.print_exc()
    finally:

        loader.close()
