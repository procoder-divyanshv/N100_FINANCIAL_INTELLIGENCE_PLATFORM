import pandas as pd
import os

data_dir = "data"
files = [
    "companies.xlsx", "financial_ratios.xlsx", 
    "profitandloss.xlsx", "cashflow.xlsx", 
    "peer_groups.xlsx"
]

for file in files:
    path = os.path.join(data_dir, file)
    if os.path.exists(path):
        df = pd.read_excel(path)
        print(f"--- {file} ---")
        print(df.columns.tolist())
        print("\n")
    else:
        print(f"❌ Missing: {file}")