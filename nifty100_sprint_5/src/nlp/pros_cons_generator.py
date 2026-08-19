import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
OUTPUT_DIR = os.path.join(BASE_DIR, "../../output")

def generate_pros_cons():
    print("⏳ Generating Pros & Cons...")
    
    # Load required data
    ratios = pd.read_excel(os.path.join(DATA_DIR, "financial_ratios.xlsx"))
    # Handle the banner row
    if "fintech" in str(ratios.columns[0]).lower(): ratios = pd.read_excel(os.path.join(DATA_DIR, "financial_ratios.xlsx"), header=1)
    ratios.columns = [str(c).lower().replace(" ", "_") for c in ratios.columns]
    
    cagr_data = pd.read_csv(os.path.join(OUTPUT_DIR, "analysis_parsed.csv"))
    
    results = []
    
    # Get unique companies
    company_ids = ratios['company_id'].unique()
    
    for c_id in company_ids:
        # Get data for this company
        comp_ratios = ratios[ratios['company_id'] == c_id].iloc[-1] # Latest year
        
        # --- PRO RULES ---
        # Rule 1: ROE > 20%
        if comp_ratios.get('return_on_equity_pct', 0) > 20:
            results.append({'company_id': c_id, 'type': 'pro', 'rule_id': 'PRO_01', 
                            'text': 'Consistently high return on equity above 20% demonstrates exceptional capital efficiency', 
                            'confidence_pct': 90})
            
        # Rule 3: Debt Free (D/E = 0)
        if comp_ratios.get('debt_to_equity', 1) == 0:
            results.append({'company_id': c_id, 'type': 'pro', 'rule_id': 'PRO_03', 
                            'text': 'Debt-free balance sheet provides financial flexibility and eliminates interest burden', 
                            'confidence_pct': 100})

        # --- CON RULES ---
        # Rule 10: ROCE < 10%
        if comp_ratios.get('roce_percentage', 20) < 10:
            results.append({'company_id': c_id, 'type': 'con', 'rule_id': 'CON_10', 
                            'text': 'Return on capital employed below 10% suggests the business is not generating sufficient returns', 
                            'confidence_pct': 85})

    # Save
    pd.DataFrame(results).to_csv(os.path.join(OUTPUT_DIR, "pros_cons_generated.csv"), index=False)
    print(f"✅ Generated {len(results)} signals into 'output/pros_cons_generated.csv'")

if __name__ == "__main__":
    generate_pros_cons()