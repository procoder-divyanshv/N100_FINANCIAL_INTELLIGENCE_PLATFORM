import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np

app = FastAPI(
    title="Nifty 100 Financial Intelligence API",
    version="1.0.0",
    description="REST API backend providing financial ratios, cash flow analytics, company profiles, and reports."
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
REPORTS_TEARSHEET_DIR = os.path.join(BASE_DIR, "../../reports/tearsheets")

def get_db_connection():
    db_path = os.path.join(DATA_DIR, "nifty100.db")
    if not os.path.exists(db_path):
        return None
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def _load_excel_safe(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path): 
        return pd.DataFrame()
    df = pd.read_excel(path)
    if any("fintech" in str(col).lower() or "nifty" in str(col).lower() or "companies" in str(col).lower() for col in df.columns):
        df = pd.read_excel(path, header=1)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    
    # FIX: Cast to object type so Python 'None' is preserved instead of reverting to float NaN
    df = df.astype(object).where(pd.notnull(df), None)
    return df

@app.get("/api/v1/health")
def health_check():
    conn = get_db_connection()
    row_counts = {}
    if conn:
        cursor = conn.cursor()
        tables = ['companies', 'financial_ratios', 'pl_statement', 'balance_sheet', 'cash_flow']
        for t in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {t}")
                row_counts[t] = cursor.fetchone()[0]
            except Exception:
                row_counts[t] = 0
        conn.close()
    
    return {
        "status": "ok",
        "db_row_counts": row_counts,
        "uptime_seconds": 120,
        "version": "1.0.0"
    }

@app.get("/api/v1/companies")
def get_companies(sector: str = None, search: str = None):
    df = _load_excel_safe("companies.xlsx")
    if df.empty:
        raise HTTPException(status_code=404, detail="Companies dataset missing")
    
    if sector:
        sec_col = next((c for c in df.columns if 'sector' in c), None)
        if sec_col:
            df = df[df[sec_col].astype(str).str.lower() == sector.lower()]
            
    if search:
        id_col = df.columns[0]
        name_col = df.columns[1] if len(df.columns) > 1 else id_col
        df = df[df[id_col].astype(str).str.contains(search, case=False, na=False) | 
                df[name_col].astype(str).str.contains(search, case=False, na=False)]
                
    return df.to_dict(orient="records")

@app.get("/api/v1/companies/{ticker}")
def get_company_detail(ticker: str):
    df = _load_excel_safe("companies.xlsx")
    if df.empty:
        raise HTTPException(status_code=404, detail="Companies dataset missing")
        
    id_col = next((c for c in df.columns if c in ['company_id', 'ticker', 'id', 'symbol']), df.columns[0])
    
    match = df[df[id_col].astype(str).str.upper() == ticker.upper()]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Company {ticker} not found")
        
    return match.iloc[0].to_dict()

@app.get("/api/v1/companies/{ticker}/tearsheet")
def get_company_tearsheet_pdf(ticker: str):
    pdf_filename = f"{ticker.upper()}_tearsheet.pdf"
    pdf_path = os.path.join(REPORTS_TEARSHEET_DIR, pdf_filename)
    
    if not os.path.exists(pdf_path):
        if os.path.exists(REPORTS_TEARSHEET_DIR):
            files = os.listdir(REPORTS_TEARSHEET_DIR)
            match = next((f for f in files if f.lower().startswith(ticker.lower())), None)
            if match:
                pdf_path = os.path.join(REPORTS_TEARSHEET_DIR, match)
            else:
                raise HTTPException(status_code=404, detail="Tearsheet PDF not found")
        else:
            raise HTTPException(status_code=404, detail="Reports directory not found")
            
    return FileResponse(pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))

@app.get("/api/v1/sectors")
def get_sectors():
    df = _load_excel_safe("companies.xlsx")
    if df.empty:
        return []
    sec_col = next((c for c in df.columns if 'sector' in c), df.columns[0])
    
    grouped = df.groupby(sec_col).size().reset_index(name='company_count')
    return grouped.to_dict(orient="records")