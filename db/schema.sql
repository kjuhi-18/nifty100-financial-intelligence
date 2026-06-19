PRAGMA foreign_keys = ON;

-- =====================================================
-- COMPANIES
-- =====================================================

CREATE TABLE IF NOT EXISTS companies (
    id TEXT PRIMARY KEY,
    company_logo TEXT,
    company_name TEXT NOT NULL,
    chart_link TEXT,
    about_company TEXT,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    face_value REAL,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL
);

-- =====================================================
-- PROFIT AND LOSS
-- =====================================================

CREATE TABLE IF NOT EXISTS profitandloss (
    id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,

    sales REAL,
    expenses REAL,
    operating_profit REAL,
    opm_percentage REAL,
    other_income REAL,
    interest REAL,
    depreciation REAL,
    profit_before_tax REAL,
    tax_percentage REAL,
    net_profit REAL,
    eps REAL,
    dividend_payout REAL,

    UNIQUE(company_id, year),

    FOREIGN KEY (company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- BALANCE SHEET
-- =====================================================

CREATE TABLE IF NOT EXISTS balancesheet (
    id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,

    equity_capital REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL,

    fixed_assets REAL,
    cwip REAL,
    investments REAL,
    other_asset REAL,
    total_assets REAL,

    UNIQUE(company_id, year),

    FOREIGN KEY (company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- CASH FLOW
-- =====================================================

CREATE TABLE IF NOT EXISTS cashflow (
    id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,
    year TEXT NOT NULL,

    operating_activity REAL,
    investing_activity REAL,
    financing_activity REAL,
    net_cash_flow REAL,

    UNIQUE(company_id, year),

    FOREIGN KEY (company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- ANALYSIS
-- =====================================================

CREATE TABLE IF NOT EXISTS analysis (
    id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,

    compounded_sales_growth REAL,
    compounded_profit_growth REAL,
    stock_price_cagr REAL,
    roe REAL,

    FOREIGN KEY (company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- DOCUMENTS
-- =====================================================

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,
    year TEXT,
    annual_report TEXT,

    FOREIGN KEY (company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- PROS AND CONS
-- =====================================================

CREATE TABLE IF NOT EXISTS prosandcons (
    id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,
    pros TEXT,
    cons TEXT,

    FOREIGN KEY (company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- SECTORS
-- =====================================================

CREATE TABLE IF NOT EXISTS sectors (
    id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,
    sector_name TEXT NOT NULL,

    FOREIGN KEY (company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- STOCK PRICES
-- =====================================================

CREATE TABLE IF NOT EXISTS stock_prices (
    id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,

    trade_date TEXT NOT NULL,
    open_price REAL,
    high_price REAL,
    low_price REAL,
    close_price REAL,
    volume INTEGER,

    FOREIGN KEY (company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- FINANCIAL RATIOS
-- =====================================================

CREATE TABLE IF NOT EXISTS financial_ratios (
    id INTEGER PRIMARY KEY,
    company_id TEXT NOT NULL,

    ratio_name TEXT NOT NULL,
    ratio_value REAL,

    FOREIGN KEY (company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- PEER GROUPS
-- =====================================================

CREATE TABLE IF NOT EXISTS peer_groups (
    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,
    peer_company_id TEXT NOT NULL,

    FOREIGN KEY (company_id)
        REFERENCES companies(id),

    FOREIGN KEY (peer_company_id)
        REFERENCES companies(id)
);

-- =====================================================
-- INDEXES
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_pl_company
ON profitandloss(company_id);

CREATE INDEX IF NOT EXISTS idx_bs_company
ON balancesheet(company_id);

CREATE INDEX IF NOT EXISTS idx_cf_company
ON cashflow(company_id);

CREATE INDEX IF NOT EXISTS idx_docs_company
ON documents(company_id);

CREATE INDEX IF NOT EXISTS idx_prices_company
ON stock_prices(company_id);

CREATE INDEX IF NOT EXISTS idx_ratios_company
ON financial_ratios(company_id);

CREATE INDEX IF NOT EXISTS idx_peer_company
ON peer_groups(company_id);