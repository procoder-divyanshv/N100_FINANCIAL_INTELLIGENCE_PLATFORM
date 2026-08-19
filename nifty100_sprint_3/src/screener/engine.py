import os
import sqlite3
import pandas as pd
import numpy as np
import yaml
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "data/nifty100.db")

def load_config():
    with open("config/screener_config.yaml", "r") as f:
        return yaml.safe_load(f)

def get_screener_data(conn):
    query = """
    SELECT 
        f.*, s.broad_sector, m.pe_ratio, m.pb_ratio, m.dividend_yield_pct, p.sales
    FROM financial_ratios f
    LEFT JOIN sectors s ON f.company_id = s.company_id
    LEFT JOIN market_cap m ON f.company_id = m.company_id AND f.year = CAST(m.year AS VARCHAR)
    LEFT JOIN profitandloss p ON f.company_id = p.company_id AND f.year = p.year
    """
    df = pd.read_sql(query, conn)
    
    # FIX: Ensure all numeric columns are actually floats, not strings
    numeric_cols = [
        'return_on_equity_pct', 'debt_to_equity', 'free_cash_flow_cr', 
        'revenue_cagr_5yr', 'pe_ratio', 'pb_ratio', 'dividend_yield_pct', 
        'dividend_payout_ratio_pct', 'pat_cagr_5yr', 'sales'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df.sort_values(['company_id', 'year'])

def compute_composite_score(df):
    metrics = {
        'return_on_equity_pct': 0.15,
        'operating_profit_margin_pct': 0.10,
        'revenue_cagr_5yr': 0.10,
        'pat_cagr_5yr': 0.10,
        'free_cash_flow_cr': 0.05
    }
    
    score_df = df.copy()
    score_df['composite_quality_score'] = 0
    
    for metric, weight in metrics.items():
        if metric in score_df.columns:
            p10 = score_df[metric].quantile(0.10)
            p90 = score_df[metric].quantile(0.90)
            score_df[metric] = score_df[metric].clip(lower=p10, upper=p90)
            
            min_val = score_df[metric].min()
            max_val = score_df[metric].max()
            
            if max_val > min_val:
                normalized = (score_df[metric] - min_val) / (max_val - min_val) * 100
                score_df['composite_quality_score'] += normalized * weight

    return score_df

def apply_filters(df, filters):
    filtered = df.copy()
    
    # 1. Latest year filter
    latest_year = filtered['year'].max()
    filtered = filtered[filtered['year'] == latest_year]
    print(f"\n--- Debug: Starting with {len(filtered)} companies ---")

    # 2. Convert to numeric (Force text to numbers, errors become NaN)
    numeric_cols = ['return_on_equity_pct', 'debt_to_equity', 'free_cash_flow_cr', 
                    'revenue_cagr_5yr', 'pe_ratio', 'pb_ratio', 'dividend_yield_pct', 
                    'dividend_payout_ratio_pct', 'pat_cagr_5yr', 'sales']
    
    for col in numeric_cols:
        if col in filtered.columns:
            filtered[col] = pd.to_numeric(filtered[col], errors='coerce')

    # 3. Apply Filters with Debug Prints
    if 'min_roe' in filters:
        # Keep NaNs as is or drop them? Drop them for ROE.
        filtered = filtered.dropna(subset=['return_on_equity_pct'])
        filtered = filtered[filtered['return_on_equity_pct'] >= filters['min_roe']]
        print(f"After ROE >= {filters['min_roe']}: {len(filtered)} companies left.")

    if 'max_de' in filters:
        # Financials sector ko ignore karo D/E filter se
        mask = (filtered['debt_to_equity'] <= filters['max_de']) | (filtered['broad_sector'] == 'Financials')
        filtered = filtered[mask]
        print(f"After D/E <= {filters['max_de']}: {len(filtered)} companies left.")

    if 'min_fcf' in filters:
        filtered = filtered.fillna({'free_cash_flow_cr': 0})
        filtered = filtered[filtered['free_cash_flow_cr'] >= filters['min_fcf']]
        print(f"After FCF >= {filters['min_fcf']}: {len(filtered)} companies left.")

    if 'min_revenue_cagr_5yr' in filters:
        filtered = filtered.fillna({'revenue_cagr_5yr': 0})
        filtered = filtered[filtered['revenue_cagr_5yr'] >= filters['min_revenue_cagr_5yr']]
        print(f"After Rev CAGR >= {filters['min_revenue_cagr_5yr']}: {len(filtered)} companies left.")

    if 'max_pe' in filters:
        filtered = filtered[filtered['pe_ratio'] <= filters['max_pe']]
        print(f"After PE <= {filters['max_pe']}: {len(filtered)} companies left.")

    if 'max_pb' in filters:
        filtered = filtered[filtered['pb_ratio'] <= filters['max_pb']]
        print(f"After PB <= {filters['max_pb']}: {len(filtered)} companies left.")

    if 'min_dividend_yield' in filters:
        filtered = filtered.fillna({'dividend_yield_pct': 0})
        filtered = filtered[filtered['dividend_yield_pct'] >= filters['min_dividend_yield']]
        print(f"After Div Yield >= {filters['min_dividend_yield']}: {len(filtered)} companies left.")

    if 'max_dividend_payout' in filters:
        filtered = filtered.fillna({'dividend_payout_ratio_pct': 0})
        filtered = filtered[filtered['dividend_payout_ratio_pct'] <= filters['max_dividend_payout']]
        print(f"After Div Payout <= {filters['max_dividend_payout']}: {len(filtered)} companies left.")

    if 'min_pat_cagr_5yr' in filters:
        filtered = filtered.fillna({'pat_cagr_5yr': 0})
        filtered = filtered[filtered['pat_cagr_5yr'] >= filters['min_pat_cagr_5yr']]
        print(f"After PAT CAGR >= {filters['min_pat_cagr_5yr']}: {len(filtered)} companies left.")

    if 'min_sales' in filters:
        filtered = filtered.fillna({'sales': 0})
        filtered = filtered[filtered['sales'] >= filters['min_sales']]
        print(f"After Sales >= {filters['min_sales']}: {len(filtered)} companies left.")
        
    return filtered.sort_values('composite_quality_score', ascending=False)

def generate_screener_report():
    config = load_config()
    with sqlite3.connect(DB_PATH) as conn:
        df = get_screener_data(conn)
    
    df = compute_composite_score(df)
    
    with pd.ExcelWriter("output/screener_output.xlsx", engine="openpyxl") as writer:
        for preset_name, filters in config['presets'].items():
            result = apply_filters(df, filters)
            if not result.empty:
                result.to_excel(writer, sheet_name=preset_name[:31], index=False)
                print(f"Preset '{preset_name}' added: {len(result)} companies found.")
            else:
                print(f"Preset '{preset_name}' skipped: No companies found (Criteria too strict).")

if __name__ == "__main__":
    generate_screener_report()
    print("Screener Engine Complete. Output saved to screener_output.xlsx")