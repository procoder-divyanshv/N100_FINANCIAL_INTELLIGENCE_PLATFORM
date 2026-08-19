import pandas as pd
import os
import numpy as np

# Setup paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
OUTPUT_DIR = os.path.join(BASE_DIR, "../../output")

def _load_excel_smart(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path): return pd.DataFrame()
    df = pd.read_excel(path)
    if any("fintech" in str(col).lower() or "nifty" in str(col).lower() for col in df.columns):
        df = pd.read_excel(path, header=1)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df

def f_col(df, candidates):
    # Pass 1: Exact matches (priority)
    for cand in candidates:
        if cand in df.columns: return cand
    # Pass 2: Partial matches
    for cand in candidates:
        for col in df.columns:
            if cand in str(col): return col
    return None

def safe_merge(left_df, right_df, left_key, right_key, target_cols):
    """Surgically merges only the exact target columns to prevent suffix errors."""
    cols_to_keep = list(set([right_key] + target_cols))
    right_sub = right_df[[c for c in cols_to_keep if c in right_df.columns]].copy()
    
    # Convert keys to string to prevent datatype crashes
    left_df[left_key] = left_df[left_key].astype(str)
    right_sub[right_key] = right_sub[right_key].astype(str)
    
    # Rename right key to match left key 
    right_sub.rename(columns={right_key: left_key}, inplace=True)
    
    # Drop overlapping columns to prevent suffix duplicates
    for c in right_sub.columns:
        if c != left_key and c in left_df.columns:
            right_sub.drop(columns=[c], inplace=True)
            
    return pd.merge(left_df, right_sub, on=left_key, how='left')

def compute_valuations():
    print("⏳ Starting valuation generation...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Load Datasets
    companies = _load_excel_smart("companies.xlsx")
    sectors = _load_excel_smart("sectors.xlsx")
    ratios = _load_excel_smart("financial_ratios.xlsx")
    market_cap = _load_excel_smart("market_cap.xlsx")
    
    if companies.empty:
        print("❌ Error: companies.xlsx is missing.")
        return
        
    df = companies.copy()
    c_id = f_col(df, ['company_id', 'ticker', 'id'])
    name_col = f_col(df, ['company_name', 'name'])
    
    if not c_id:
        print("❌ Error: Could not find company ID column.")
        return
        
    df[c_id] = df[c_id].astype(str)
    
    # 2. Merge Sectors Safely
    if not sectors.empty:
        s_id = f_col(sectors, ['company_id', 'ticker', 'id'])
        sec_col = f_col(sectors, ['broad_sector', 'sector'])
        if s_id and sec_col:
            df = safe_merge(df, sectors, c_id, s_id, [sec_col])
    else:
        sec_col = 'sector'
        df['sector'] = 'Unknown'
        
    # 3. Merge Market Cap Safely
    if not market_cap.empty:
        m_id = f_col(market_cap, ['company_id', 'ticker', 'id'])
        mc_col = f_col(market_cap, ['market_cap', 'mcap'])
        if m_id and mc_col:
            df = safe_merge(df, market_cap, c_id, m_id, [mc_col])
    
    # 4. Merge Financial Ratios Safely
    if not ratios.empty:
        r_id = f_col(ratios, ['company_id', 'ticker', 'id'])
        y_col = f_col(ratios, ['year', 'fy'])
        fcf_col = f_col(ratios, ['free_cash_flow', 'fcf'])
        pe_col = f_col(ratios, ['p/e', 'pe_ratio', 'pe', 'p_e']) or 'p_e'
        pb_col = f_col(ratios, ['p/b', 'pb_ratio', 'pb', 'p_b']) or 'p_b'
        ev_col = f_col(ratios, ['ev/ebitda', 'ev_ebitda']) or 'ev_ebitda'
        
        for c in [pe_col, pb_col, ev_col]:
            if c not in ratios.columns: ratios[c] = np.nan
            
        if r_id: 
            ratios[r_id] = ratios[r_id].astype(str)
            # Compute Median PE
            median_pe = ratios.groupby(r_id)[pe_col].median().reset_index()
            median_pe.rename(columns={pe_col: '5yr_median_PE'}, inplace=True)
            df = safe_merge(df, median_pe, c_id, r_id, ['5yr_median_PE'])
            
            # Compute Latest Ratios
            latest_ratios = ratios.sort_values(y_col).groupby(r_id).tail(1)
            cols_to_merge = [c for c in [fcf_col, pe_col, pb_col, ev_col] if c]
            df = safe_merge(df, latest_ratios, c_id, r_id, cols_to_merge)
    
    # 5. Compute Calculations
    mc_col = f_col(df, ['market_cap', 'mcap'])
    fcf_col = f_col(df, ['free_cash_flow', 'fcf'])
    if mc_col and fcf_col:
        df['Market_Cap'] = pd.to_numeric(df[mc_col], errors='coerce')
        df['FCF'] = pd.to_numeric(df[fcf_col], errors='coerce')
        df['FCF_yield_pct'] = (df['FCF'] / df['Market_Cap']) * 100
    else:
        df['FCF_yield_pct'] = np.nan
        
    pe_col = f_col(df, ['p_e', 'pe_ratio', 'pe'])
    if sec_col and pe_col:
        df[pe_col] = pd.to_numeric(df[pe_col], errors='coerce')
        df['Sector_Median_PE'] = df.groupby(sec_col)[pe_col].transform('median')
        df['PE_vs_sector_median_pct'] = (df[pe_col] / df['Sector_Median_PE']) * 100
        
        def assign_flag(row):
            pe = row.get(pe_col)
            med = row.get('Sector_Median_PE')
            if pd.isna(pe) or pd.isna(med) or med == 0: return 'Fair'
            if pe > (med * 1.5): return 'Caution'
            if pe < (med * 0.7): return 'Discount'
            return 'Fair'
        
        df['flag'] = df.apply(assign_flag, axis=1)
    else:
        df['5yr_median_PE'] = np.nan
        df['PE_vs_sector_median_pct'] = np.nan
        df['flag'] = 'Fair'
        
    # 6. Format Final Outputs
    final_cols_mapping = {
        c_id: 'company_id',
        name_col: 'company_name',
        sec_col: 'sector',
        f_col(df, ['p_e', 'pe_ratio', 'pe']): 'P/E',
        f_col(df, ['p_b', 'pb_ratio', 'pb']): 'P/B',
        f_col(df, ['ev_ebitda']): 'EV/EBITDA',
        'FCF_yield_pct': 'FCF_yield_pct',
        '5yr_median_PE': '5yr_median_PE',
        'PE_vs_sector_median_pct': 'PE_vs_sector_median_pct',
        'flag': 'flag'
    }
    
    final_df = pd.DataFrame()
    for original, new_name in final_cols_mapping.items():
        if original and original in df.columns:
            final_df[new_name] = df[original]
        else:
            final_df[new_name] = np.nan
            
    # 7. Write to Excel and CSV
    summary_path = os.path.join(OUTPUT_DIR, "valuation_summary.xlsx")
    final_df.to_excel(summary_path, index=False)
    
    flags_path = os.path.join(OUTPUT_DIR, "valuation_flags.csv")
    flagged = final_df[final_df['flag'].isin(['Caution', 'Discount'])]
    flagged.to_csv(flags_path, index=False)
    
    print(f"✅ Success! Generated {len(final_df)} valuation records.")
    print(f"📁 Summary saved to: {summary_path}")
    print(f"📁 Flags saved to: {flags_path}")

if __name__ == "__main__":
    compute_valuations()