import sqlite3

conn = sqlite3.connect("db/nifty100.db")
cursor = conn.cursor()

cursor.executescript("""
CREATE INDEX IF NOT EXISTS idx_pl_company_year
ON profitandloss(company_id, year);

CREATE INDEX IF NOT EXISTS idx_bs_company_year
ON balancesheet(company_id, year);

CREATE INDEX IF NOT EXISTS idx_cf_company_year
ON cashflow(company_id, year);

CREATE INDEX IF NOT EXISTS idx_ratios_company_year
ON financial_ratios(company_id, year);

CREATE INDEX IF NOT EXISTS idx_sector_company
ON sectors(company_id);

CREATE INDEX IF NOT EXISTS idx_documents_company_year
ON documents(company_id, year);

CREATE INDEX IF NOT EXISTS idx_peer_company
ON peer_groups(company_id);

CREATE INDEX IF NOT EXISTS idx_stock_company_date
ON stock_prices(company_id, date);
""")

conn.commit()
conn.close()

print("✅ All indexes created successfully!")