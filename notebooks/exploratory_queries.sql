-- Q1 Total Companies
SELECT COUNT(*) AS total_companies
FROM companies;

-- Q2 Total Stock Price Records
SELECT COUNT(*) AS total_price_records
FROM stock_prices;

-- Q3 Top 10 Companies by Sales
SELECT company_id, sales
FROM profitandloss
ORDER BY sales DESC
LIMIT 10;

-- Q4 Top 10 Companies by Market Cap
SELECT company_id, market_cap_crore
FROM market_cap
ORDER BY market_cap_crore DESC
LIMIT 10;

-- Q5 Companies by Sector
SELECT broad_sector,
       COUNT(*) AS company_count
FROM sectors
GROUP BY broad_sector
ORDER BY company_count DESC;

-- Q6 Highest ROE
SELECT company_id,
       return_on_equity_pct
FROM financial_ratios
ORDER BY return_on_equity_pct DESC
LIMIT 10;

-- Q7 Highest Debt Companies
SELECT company_id,
       total_debt_cr
FROM financial_ratios
ORDER BY total_debt_cr DESC
LIMIT 10;

-- Q8 Price Records per Company
SELECT company_id,
       COUNT(*) AS records
FROM stock_prices
GROUP BY company_id
ORDER BY records DESC;

-- Q9 Companies with Highest Net Profit Margin
SELECT company_id,
       net_profit_margin_pct
FROM financial_ratios
ORDER BY net_profit_margin_pct DESC
LIMIT 10;

-- Q10 Peer Group Distribution
SELECT peer_group_name,
       COUNT(*) AS companies
FROM peer_groups
GROUP BY peer_group_name
ORDER BY companies DESC;