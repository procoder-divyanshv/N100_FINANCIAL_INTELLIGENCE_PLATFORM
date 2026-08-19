import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from normaliser import normalize_ticker, normalize_year
from validator import validate_dataframe

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/nifty100.db")
OUTPUT_DIR = "output"

def initialize_database():
    with open("config/schema.sql", "r") as f:
        schema = f.read()
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema)

def load_and_clean_excel(file_path: str, sheet_name, has_header_offset: bool = True) -> pd.DataFrame:
    header_idx = 1 if has_header_offset else 0
    # For supplementary files, sheet_name might just be 0 (first sheet)
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_idx)
    
    # Normalize IDs
    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].apply(normalize_ticker)
    elif "id" in df.columns and "company_name" in df.columns:
        df["id"] = df["id"].apply(normalize_ticker)
        
    # Normalize Years (only in core sheets where year is a string like Mar-23)
    if "year" in df.columns and df["year"].dtype == 'O':
        df["year"] = df["year"].apply(normalize_year)
        
    return df

def run_etl():
    initialize_database()
    all_failures = []
    audit_log = []

    # Dictionary defining how to load all 12 files
    files_to_load = [
        # CORE DATASETS (from data/raw)
        {"path": "data/raw/companies.xlsx", "sheet": "Companies", "table": "companies", "offset": True},
        {"path": "data/raw/profitandloss.xlsx", "sheet": "Profit & Loss", "table": "profitandloss", "offset": True},
        {"path": "data/raw/balancesheet.xlsx", "sheet": "Balance Sheet", "table": "balancesheet", "offset": True},
        {"path": "data/raw/cashflow.xlsx", "sheet": "Cash Flow", "table": "cashflow", "offset": True},
        {"path": "data/raw/analysis.xlsx", "sheet": 0, "table": "analysis", "offset": True},
        {"path": "data/raw/documents.xlsx", "sheet": 0, "table": "documents", "offset": True},
        {"path": "data/raw/prosandcons.xlsx", "sheet": 0, "table": "prosandcons", "offset": True},
        
        # SUPPLEMENTARY DATASETS (from data/supporting)
        {"path": "data/supporting/sectors.xlsx", "sheet": 0, "table": "sectors", "offset": False},
        {"path": "data/supporting/stock_prices.xlsx", "sheet": 0, "table": "stock_prices", "offset": False},
        {"path": "data/supporting/market_cap.xlsx", "sheet": 0, "table": "market_cap", "offset": False},
        {"path": "data/supporting/financial_ratios.xlsx", "sheet": 0, "table": "financial_ratios", "offset": False},
        {"path": "data/supporting/peer_groups.xlsx", "sheet": 0, "table": "peer_groups", "offset": False},
    ]

    with sqlite3.connect(DB_PATH) as conn:
        for item in files_to_load:
            if not os.path.exists(item["path"]):
                print(f"Skipping: {item['path']} not found.")
                continue

            print(f"Loading {item['path']}...")
            df = load_and_clean_excel(item["path"], item["sheet"], item["offset"])
            
            # Validation step
            failures = validate_dataframe(df, item["table"])
            all_failures.extend(failures)
            
            # Drop critical rows before inserting to DB
            critical_rows = [f["row"] for f in failures if f["severity"] == "CRITICAL"]
            valid_df = df.drop(index=critical_rows)
            
            # Insert into database
            valid_df.to_sql(item["table"], conn, if_exists="replace", index=False)
            
            audit_log.append({
                "table": item["table"],
                "rows_in": len(df),
                "rows_out": len(valid_df),
                "rejected": len(critical_rows)
            })

    # Save outputs
    pd.DataFrame(audit_log).to_csv(os.path.join(OUTPUT_DIR, "load_audit.csv"), index=False)
    pd.DataFrame(all_failures).to_csv(os.path.join(OUTPUT_DIR, "validation_failures.csv"), index=False)
    print("Sprint 1 ETL Complete! All tables loaded.")

if __name__ == "__main__":
    run_etl()