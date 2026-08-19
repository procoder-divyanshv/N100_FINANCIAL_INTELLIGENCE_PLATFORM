import pandas as pd
import os
import numpy as np

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
OUTPUT_DIR = os.path.join(BASE_DIR, "../../output")

def compute_cashflow_intelligence():
    print("⏳ Starting Cash Flow Intelligence processing...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def _load_excel_smart(filename):
        path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(path): return pd.DataFrame()
        df = pd.read_excel(path)
        if any("fintech" in str(col).lower() or "nifty" in str(col).lower() for col in df.columns):
            df = pd.read_excel(path, header=1)
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
        return df

    cf = _load_excel_smart("cashflow.xlsx")
    sectors = _load_excel_smart("sectors.xlsx")
    
    if cf.empty:
        print("❌ Error: cash_flow.xlsx is missing from data/")
        return

    def f_col(df, candidates):
        for cand in candidates:
            if cand in df.columns: return cand
        for cand in candidates:
            for col in df.columns:
                if cand in str(col): return col
        return None

    c_id = f_col(cf, ['company_id', 'ticker', 'id'])
    y_col = f_col(cf, ['year', 'fy'])
    cfo_col = f_col(cf, ['cash_from_operating_activity', 'cfo', 'operating_cash_flow'])
    cfi_col = f_col(cf, ['cash_from_investing_activity', 'cfi', 'investing_activity'])
    cff_col = f_col(cf, ['cash_from_financing_activity', 'cff', 'financing_activity'])
    pat_col = f_col(cf, ['net_profit', 'pat'])
    sales_col = f_col(cf, ['sales', 'revenue'])

    if not c_id:
        print("❌ Error: Could not find company ID column in cash_flow.xlsx")
        return

    results = []
    grouped = cf.groupby(cf[c_id].astype(str))

    for comp_id, group in grouped:
        if y_col:
            group = group.sort_values(by=y_col)
        
        # 1. CFO Quality Score (CFO / PAT ratio averaged over available years)
        ratios_list = []
        for _, row in group.iterrows():
            cfo = pd.to_numeric(row.get(cfo_col), errors='coerce')
            pat = pd.to_numeric(row.get(pat_col), errors='coerce')
            if pd.notna(cfo) and pd.notna(pat) and pat != 0:
                ratios_list.append(cfo / pat)
        
        cfo_quality_score = np.mean(ratios_list) if ratios_list else np.nan
        
        if pd.isna(cfo_quality_score):
            cfo_quality_label = 'Unknown'
        elif cfo_quality_score > 1.0:
            cfo_quality_label = 'High Quality'
        elif cfo_quality_score >= 0.5:
            cfo_quality_label = 'Moderate'
        else:
            cfo_quality_label = 'Accrual Risk'

        # 2. CapEx Intensity: abs(investing_activity) / sales * 100
        capex_list = []
        if cfi_col and sales_col:
            for _, row in group.iterrows():
                cfi = pd.to_numeric(row.get(cfi_col), errors='coerce')
                sales = pd.to_numeric(row.get(sales_col), errors='coerce')
                if pd.notna(cfi) and pd.notna(sales) and sales != 0:
                    capex_list.append((abs(cfi) / sales) * 100)
        
        capex_intensity_pct = np.mean(capex_list) if capex_list else np.nan
        
        if pd.isna(capex_intensity_pct):
            capex_label = 'Unknown'
        elif capex_intensity_pct < 3:
            capex_label = 'Asset Light'
        elif capex_intensity_pct <= 8:
            capex_label = 'Moderate'
        else:
            capex_label = 'Capital Intensive'

        # Latest year indicators
        latest = group.iloc[-1]
        latest_cfo = pd.to_numeric(latest.get(cfo_col), errors='coerce')
        latest_cff = pd.to_numeric(latest.get(cff_col), errors='coerce')
        latest_pat = pd.to_numeric(latest.get(pat_col), errors='coerce')

        # Distress Signal: CFO < 0 AND CFF > 0
        distress_flag = bool(pd.notna(latest_cfo) and pd.notna(latest_cff) and latest_cfo < 0 and latest_cff > 0)
        
        # Deleveraging flag: CFF < 0 (raising less or paying down financing)
        deleveraging_flag = bool(pd.notna(latest_cff) and latest_cff < 0)

        results.append({
            'company_id': comp_id,
            'cfo_quality_score': round(cfo_quality_score, 2) if pd.notna(cfo_quality_score) else np.nan,
            'cfo_quality_label': cfo_quality_label,
            'capex_intensity_pct': round(capex_intensity_pct, 2) if pd.notna(capex_intensity_pct) else np.nan,
            'capex_label': capex_label,
            'distress_flag': distress_flag,
            'deleveraging_flag': deleveraging_flag,
            'latest_cfo': latest_cfo,
            'latest_cff': latest_cff,
            'latest_pat': latest_pat
        })

    res_df = pd.DataFrame(results)

    # Merge Sector data if available
    if not sectors.empty:
        s_id = f_col(sectors, ['company_id', 'ticker', 'id'])
        sec_col = f_col(sectors, ['broad_sector', 'sector'])
        if s_id and sec_col:
            sectors[s_id] = sectors[s_id].astype(str)
            res_df['company_id'] = res_df['company_id'].astype(str)
            res_df = pd.merge(res_df, sectors[[s_id, sec_col]], left_on='company_id', right_on=s_id, how='left')
            res_df.rename(columns={sec_col: 'sector'}, inplace=True)
            
    if 'sector' not in res_df.columns:
        res_df['sector'] = 'Unknown'

    # Export to cashflow_intelligence.xlsx
    final_cols = [
        'company_id', 'sector', 'cfo_quality_score', 'cfo_quality_label',
        'capex_intensity_pct', 'capex_label', 'distress_flag', 'deleveraging_flag'
    ]
    output_xlsx = os.path.join(OUTPUT_DIR, "cashflow_intelligence.xlsx")
    res_df[[c for c in final_cols if c in res_df.columns]].to_excel(output_xlsx, index=False)

    # Export Distress Alerts CSV
    distress_df = res_df[res_df['distress_flag'] == True][['company_id', 'sector', 'latest_cfo', 'latest_cff', 'latest_pat']]
    output_csv = os.path.join(OUTPUT_DIR, "distress_alerts.csv")
    distress_df.to_csv(output_csv, index=False)

    print(f"✅ Success! Processed cash flow records for {len(res_df)} companies.")
    print(f"📁 Saved summary to: {output_xlsx}")
    print(f"📁 Saved distress alerts to: {output_csv} ({len(distress_df)} alerts found)")

if __name__ == "__main__":
    compute_cashflow_intelligence()