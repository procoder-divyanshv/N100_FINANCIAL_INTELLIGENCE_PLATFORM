PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
    id VARCHAR PRIMARY KEY,
    company_logo TEXT,
    company_name VARCHAR NOT NULL,
    chart_link TEXT,
    about_company TEXT,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    face_value NUMERIC,
    book_value NUMERIC,
    roce_percentage NUMERIC,
    roe_percentage NUMERIC
);

CREATE TABLE IF NOT EXISTS profitandloss (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    sales NUMERIC NOT NULL,
    expenses NUMERIC NOT NULL,
    operating_profit NUMERIC NOT NULL,
    opm_percentage NUMERIC NOT NULL,
    other_income NUMERIC,
    interest NUMERIC,
    depreciation NUMERIC,
    profit_before_tax NUMERIC,
    tax_percentage NUMERIC,
    net_profit NUMERIC,
    eps NUMERIC,
    dividend_payout NUMERIC,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    UNIQUE (company_id, year)
);

CREATE TABLE IF NOT EXISTS balancesheet (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    equity_capital NUMERIC NOT NULL,
    reserves NUMERIC,
    borrowings NUMERIC,
    other_liabilities NUMERIC,
    total_liabilities NUMERIC NOT NULL,
    fixed_assets NUMERIC,
    cwip NUMERIC,
    investments NUMERIC,
    other_asset NUMERIC,
    total_assets NUMERIC NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    UNIQUE (company_id, year)
);

CREATE TABLE IF NOT EXISTS cashflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    operating_activity NUMERIC,
    investing_activity NUMERIC,
    financing_activity NUMERIC,
    net_cash_flow NUMERIC,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    UNIQUE (company_id, year)
);

CREATE TABLE IF NOT EXISTS analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr TEXT,
    roe TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    Year INTEGER,
    Annual_Report TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS prosandcons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    pros TEXT,
    cons TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS sectors (
    company_id VARCHAR PRIMARY KEY,
    broad_sector VARCHAR,
    sub_sector VARCHAR,
    index_weight_pct NUMERIC,
    market_cap_category VARCHAR,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS stock_prices (
    company_id VARCHAR NOT NULL,
    date VARCHAR,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    close_price NUMERIC,
    volume INTEGER,
    adjusted_close NUMERIC,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS market_cap (
    company_id VARCHAR NOT NULL,
    year INTEGER,
    market_cap_crore NUMERIC,
    enterprise_value_crore NUMERIC,
    pe_ratio NUMERIC,
    pb_ratio NUMERIC,
    ev_ebitda NUMERIC,
    dividend_yield_pct NUMERIC,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS financial_ratios (
    company_id VARCHAR NOT NULL,
    year VARCHAR,
    net_profit_margin_pct NUMERIC,
    operating_profit_margin_pct NUMERIC,
    return_on_equity_pct NUMERIC,
    debt_to_equity NUMERIC,
    interest_coverage NUMERIC,
    asset_turnover NUMERIC,
    free_cash_flow_cr NUMERIC,
    capex_cr NUMERIC,
    earnings_per_share NUMERIC,
    book_value_per_share NUMERIC,
    dividend_payout_ratio_pct NUMERIC,
    total_debt_cr NUMERIC,
    cash_from_operations_cr NUMERIC,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS peer_groups (
    peer_group_name VARCHAR,
    company_id VARCHAR,
    is_benchmark BOOLEAN,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);