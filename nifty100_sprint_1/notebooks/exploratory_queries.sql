-- 1. Total count of companies (Expected: 92)
SELECT COUNT(*) AS total_companies FROM companies;

-- 2. Sector-wise distribution of companies
SELECT broad_sector, COUNT(*) AS company_count 
FROM sectors 
GROUP BY broad_sector 
ORDER BY company_count DESC;

-- 3. Check year coverage for each company in P&L (Ideally 10+ years)
SELECT company_id, MIN(year) as start_year, MAX(year) as end_year, COUNT(*) as total_years_data 
FROM profitandloss 
GROUP BY company_id;

-- 4. Verify the Warning: Which company had Sales <= 0?
SELECT company_id, year, sales 
FROM profitandloss 
WHERE sales <= 0;

-- 5. Top 10 companies by latest Net Profit
SELECT company_id, year, net_profit 
FROM profitandloss 
WHERE year = '2024-03' OR year = '2023-03' 
ORDER BY net_profit DESC 
LIMIT 10;

-- 6. Check for Balance Sheet Data Completeness
SELECT COUNT(*) AS missing_assets_data 
FROM balancesheet 
WHERE total_assets IS NULL;

-- 7. Count of Debt-Free Companies (Borrowings = 0)
SELECT COUNT(DISTINCT company_id) as debt_free_companies 
FROM balancesheet 
WHERE borrowings = 0 OR borrowings IS NULL;

-- 8. Verify Foreign Key mapping for Cashflow table
SELECT COUNT(*) as unmapped_cashflows 
FROM cashflow c 
LEFT JOIN companies comp ON c.company_id = comp.id 
WHERE comp.id IS NULL;

-- 9. Check Market Cap Categories
SELECT market_cap_category, COUNT(*) as count 
FROM sectors 
GROUP BY market_cap_category;

-- 10. Average Operating Profit Margin (OPM) by Sector
SELECT s.broad_sector, ROUND(AVG(p.opm_percentage), 2) AS avg_opm 
FROM profitandloss p
JOIN sectors s ON p.company_id = s.company_id
GROUP BY s.broad_sector;