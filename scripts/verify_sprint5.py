import os
from pathlib import Path

TEARSHEET_DIR = Path("output/tearsheets")
pdfs = list(TEARSHEET_DIR.glob("*.pdf"))

print(f"Tearsheets : {len(pdfs)}")

small = []

for pdf in pdfs:
    size = pdf.stat().st_size / 1024

    if size < 30:
        small.append((pdf.name, round(size, 2)))

if small:
    print("\nSmall PDFs:")
    for name, size in small:
        print(name, size, "KB")
else:
    print("✓ All PDFs >= 30 KB")
SECTOR_DIR = Path("reports/sector")

sector = list(SECTOR_DIR.glob("*.pdf"))

print(f"Sector Reports : {len(sector)}")
PORT = Path("reports/portfolio/portfolio_summary.pdf")

print(PORT.exists())
required = [

"pros_cons_generated.csv",
"analysis_parsed.csv",
"cashflow_intelligence.xlsx",
"distress_alerts.csv"

]

for file in required:

    path = Path("output") / file

    if path.exists():
        print("✓", file)

    else:
        print("✗", file)