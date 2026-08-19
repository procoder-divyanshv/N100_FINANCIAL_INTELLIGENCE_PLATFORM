import pandas as pd
import re
import os

# Paths setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
OUTPUT_DIR = os.path.join(BASE_DIR, "../../output")

def parse_cagr_metrics():
    print("⏳ Starting NLP Parsing of analysis.xlsx...")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    file_path = os.path.join(DATA_DIR, "analysis.xlsx")
    if not os.path.exists(file_path):
        print(f"❌ Error: analysis.xlsx not found at {file_path}")
        return

    # Load data
    df = pd.read_excel(file_path)
    df.columns = [str(c).lower().strip().replace(" ", "_") for c in df.columns]
    
    # Identify the ID column
    id_col = next((c for c in df.columns if c in ['id', 'company_id', 'ticker']), df.columns[0])
    
    parsed_records = []
    failed_records = []
    
    # Regex Pattern: Captures digits for years and digits/decimals for percentage
    # Matches strings like "10 Years: 21%" or "5 years 15%"
    pattern = re.compile(r"(\d+)\s*years?:?\s*([\d.]+)%", re.IGNORECASE)
    
    # Process text columns
    text_cols = [c for c in df.columns if c not in [id_col, 'company_name']]
    
    for _, row in df.iterrows():
        comp_id = row[id_col]
        
        for col in text_cols:
            text = str(row[col])
            matches = pattern.findall(text)
            
            if matches:
                # Capture all matches found in a single cell (e.g. "10Y:21%, 5Y:15%")
                for period, value in matches:
                    parsed_records.append({
                        'company_id': comp_id,
                        'metric_type': col,
                        'period_years': int(period),
                        'value_pct': float(value)
                    })
            elif len(text) > 10: # Only log failures for meaningful text blocks
                failed_records.append({
                    'company_id': comp_id,
                    'column': col,
                    'text_snippet': text[:50]
                })

    # Save Results
    pd.DataFrame(parsed_records).to_csv(os.path.join(OUTPUT_DIR, "analysis_parsed.csv"), index=False)
    pd.DataFrame(failed_records).to_csv(os.path.join(OUTPUT_DIR, "parse_failures.csv"), index=False)
    
    print(f"✅ Success! Parsed {len(parsed_records)} metrics into 'output/analysis_parsed.csv'.")
    print(f"⚠️ {len(failed_records)} entries failed to parse (logged to 'output/parse_failures.csv').")

if __name__ == "__main__":
    parse_cagr_metrics()