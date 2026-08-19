import os
import sqlite3
import pandas as pd
import numpy as np
import logging
from dotenv import load_dotenv
from cagr import apply_cagr_window
from cashflow_kpis import classify_capital_allocation

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "data/nifty100.db")

logging.basicConfig(
    filename='output/ratio_edge_cases.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fetch_data(conn):
    query = """
    SELECT 
        c.id as company_id, s.broad_sector,
        p.year, p.sales, p.operating_profit, p.other_income, p.interest, p.net_profit, p.eps, p.dividend_payout, p.opm_percentage,
        b.equity_capital, b.reserves, b.borrowings, b.total_assets, b.investments,
        cf.operating_activity, cf.investing_activity, cf.financing_activity
    FROM companies c
    LEFT JOIN sectors s ON c.id = s.company_id
    LEFT JOIN profitandloss p ON c.id = p.company_id
    LEFT JOIN balancesheet b ON c.id = b.company_id AND p.year = b.year
    LEFT JOIN cashflow cf ON c.id = cf.company_id AND p.year = cf.year
    """
    return pd.read_sql(query, conn)

def compute_profitability_returns(df):
    df['total_equity'] = df['equity_capital'] + df['reserves']
    
    df['net_profit_margin_pct'] = np.where(df['sales'] > 0, (df['net_profit'] / df['sales']) * 100, None)
    df['operating_profit_margin_pct'] = np.where(df['sales'] > 0, (df['operating_profit'] / df['sales']) * 100, None)
    
    opm_diff = abs(df['operating_profit_margin_pct'] - df['opm_percentage'])
    anomalies = df[opm_diff > 1.0]
    for _, row in anomalies.iterrows():
        logging.warning(f"OPM Mismatch: {row['company_id']} {row['year']} - Computed: {row['operating_profit_margin_pct']}, Source: {row['opm_percentage']}")

    df['return_on_equity_pct'] = np.where(df['total_equity'] > 0, (df['net_profit'] / df['total_equity']) * 100, None)
    
    ebit = df['operating_profit']
    capital_employed = df['total_equity'] + df['borrowings'].fillna(0)
    df['roce_pct'] = np.where(capital_employed > 0, (ebit / capital_employed) * 100, None)
    
    df['return_on_assets_pct'] = np.where(df['total_assets'] > 0, (df['net_profit'] / df['total_assets']) * 100, None)
    
    return df

def compute_leverage_efficiency(df):
    df['borrowings'] = df['borrowings'].fillna(0)
    
    df['debt_to_equity'] = np.where(df['total_equity'] > 0, df['borrowings'] / df['total_equity'], None)
    df['debt_to_equity'] = np.where(df['borrowings'] == 0, 0, df['debt_to_equity'])
    
    df['high_leverage_flag'] = np.where((df['debt_to_equity'] > 5) & (df['broad_sector'] != 'Financials'), True, False)
    
    op_income = df['operating_profit'] + df['other_income'].fillna(0)
    df['interest_coverage'] = np.where(df['interest'] > 0, op_income / df['interest'], None)
    df['icr_label'] = np.where(df['interest'] == 0, 'Debt Free', None)
    df['icr_warning'] = np.where(df['interest_coverage'] < 1.5, True, False)
    
    df['net_debt'] = df['borrowings'] - df['investments'].fillna(0)
    df['asset_turnover'] = np.where(df['total_assets'] > 0, df['sales'] / df['total_assets'], None)
    
    return df

def compute_growth_cagr(df):
    for window in [3, 5, 10]:
        for metric in ['sales', 'net_profit', 'eps']:
            col_name = f"{'revenue' if metric == 'sales' else 'pat' if metric == 'net_profit' else metric}_cagr_{window}yr"
            flag_name = f"{col_name}_flag"
            
            cagr_vals = []
            cagr_flags = []
            
            for _, group in df.groupby('company_id'):
                vals, flags = apply_cagr_window(group, metric, window)
                cagr_vals.extend(vals)
                cagr_flags.extend(flags)
                
            df[col_name] = cagr_vals
            df[flag_name] = cagr_flags
            
    return df

def compute_cashflow(df):
    df['free_cash_flow_cr'] = df['operating_activity'] + df['investing_activity']
    
    df['cfo_quality_score'] = np.where(df['net_profit'] != 0, df['operating_activity'] / df['net_profit'], None)
    
    df['capex_cr'] = df['investing_activity'].abs()
    df['capex_intensity_pct'] = np.where(df['sales'] > 0, (df['capex_cr'] / df['sales']) * 100, None)
    
    df['fcf_conversion_pct'] = np.where(df['operating_profit'] > 0, (df['free_cash_flow_cr'] / df['operating_profit']) * 100, None)
    
    df['pattern_label'] = df.apply(classify_capital_allocation, axis=1)
    
    return df

def run_ratio_engine():
    with sqlite3.connect(DB_PATH) as conn:
        df = fetch_data(conn)
        
        df = compute_profitability_returns(df)
        df = compute_leverage_efficiency(df)
        df = compute_growth_cagr(df)
        df = compute_cashflow(df)
        
        cap_alloc_df = df[['company_id', 'year', 'operating_activity', 'investing_activity', 'financing_activity', 'pattern_label']].copy()
        cap_alloc_df['cfo_sign'] = np.sign(cap_alloc_df['operating_activity'])
        cap_alloc_df['cfi_sign'] = np.sign(cap_alloc_df['investing_activity'])
        cap_alloc_df['cff_sign'] = np.sign(cap_alloc_df['financing_activity'])
        cap_alloc_df.to_csv('output/capital_allocation.csv', index=False)
        
        df['composite_quality_score'] = None
        df['earnings_per_share'] = df['eps']
        df['book_value_per_share'] = np.where(df['total_equity'] > 0, df['total_equity'] / 1, None)
        df['dividend_payout_ratio_pct'] = df['dividend_payout']
        df['total_debt_cr'] = df['borrowings']
        df['cash_from_operations_cr'] = df['operating_activity']
        
        final_cols = [
            'company_id', 'year', 'net_profit_margin_pct', 'operating_profit_margin_pct',
            'return_on_equity_pct', 'debt_to_equity', 'interest_coverage', 'asset_turnover',
            'free_cash_flow_cr', 'capex_cr', 'earnings_per_share', 'book_value_per_share',
            'dividend_payout_ratio_pct', 'total_debt_cr', 'cash_from_operations_cr',
            'revenue_cagr_5yr', 'pat_cagr_5yr', 'eps_cagr_5yr', 'composite_quality_score'
        ]
        
        final_ratios = df[final_cols]
        final_ratios.to_sql('financial_ratios', conn, if_exists='replace', index=False)
        print("Sprint 2 Financial Ratio Engine Complete.")

if __name__ == "__main__":
    run_ratio_engine()