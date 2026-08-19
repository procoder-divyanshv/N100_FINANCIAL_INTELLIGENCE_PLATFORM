import os
import pandas as pd
import streamlit as st

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
POSSIBLE_PATHS = [
    os.path.abspath(os.path.join(CURRENT_DIR, "../../../data")),
    os.path.abspath(os.path.join(os.getcwd(), "data")),
    os.path.abspath("data")
]

DATA_DIR = next((p for p in POSSIBLE_PATHS if os.path.exists(p)), POSSIBLE_PATHS[0])

def _load_excel_smart(filename: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        df = pd.read_excel(path)
        if any("fintech" in str(col).lower() or "nifty" in str(col).lower() or "records" in str(col).lower() for col in df.columns):
            df = pd.read_excel(path, header=1)
        
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_companies() -> pd.DataFrame:
    return _load_excel_smart("companies.xlsx")

@st.cache_data(ttl=600)
def get_ratios(ticker: str = None, company_id: str = None, year: int = None) -> pd.DataFrame:
    df = _load_excel_smart("financial_ratios.xlsx")
    if df.empty:
        return df
    
    companies = get_companies()
    if not companies.empty and 'ticker' in companies.columns and 'company_id' in companies.columns:
        df = pd.merge(df, companies[['company_id', 'ticker', 'company_name', 'sector', 'broad_sector']], on='company_id', how='left')

    if ticker and 'ticker' in df.columns:
        df = df[df['ticker'].astype(str).str.upper() == str(ticker).upper()]
    
    # ⬇️ FIXED: Cast to string for safety instead of integer
    if company_id and 'company_id' in df.columns:
        df = df[df['company_id'].astype(str).str.upper() == str(company_id).upper()]
        
    if year and 'year' in df.columns:
        df = df[df['year'].astype(str).str.contains(str(year))]
    return df

@st.cache_data(ttl=600)
def get_pl(ticker: str = None, company_id: str = None) -> pd.DataFrame:
    df = _load_excel_smart("profitandloss.xlsx")
    companies = get_companies()
    if not companies.empty and 'ticker' in companies.columns and 'company_id' in df.columns:
        df = pd.merge(df, companies[['company_id', 'ticker']], on='company_id', how='left')
    
    if ticker and 'ticker' in df.columns:
        df = df[df['ticker'].astype(str).str.upper() == str(ticker).upper()]
    
    # ⬇️ FIXED: Cast to string for safety instead of integer
    if company_id and 'company_id' in df.columns:
        df = df[df['company_id'].astype(str).str.upper() == str(company_id).upper()]
    return df

@st.cache_data(ttl=600)
def get_bs(ticker: str = None, company_id: str = None) -> pd.DataFrame:
    df = _load_excel_smart("balancesheet.xlsx")
    companies = get_companies()
    if not companies.empty and 'ticker' in companies.columns and 'company_id' in df.columns:
        df = pd.merge(df, companies[['company_id', 'ticker']], on='company_id', how='left')
    
    if ticker and 'ticker' in df.columns:
        df = df[df['ticker'].astype(str).str.upper() == str(ticker).upper()]
        
    # ⬇️ FIXED: Cast to string for safety instead of integer
    if company_id and 'company_id' in df.columns:
        df = df[df['company_id'].astype(str).str.upper() == str(company_id).upper()]
    return df

@st.cache_data(ttl=600)
def get_cf(ticker: str = None, company_id: str = None) -> pd.DataFrame:
    df = _load_excel_smart("cashflow.xlsx")
    companies = get_companies()
    if not companies.empty and 'ticker' in companies.columns and 'company_id' in df.columns:
        df = pd.merge(df, companies[['company_id', 'ticker']], on='company_id', how='left')
    
    if ticker and 'ticker' in df.columns:
        df = df[df['ticker'].astype(str).str.upper() == str(ticker).upper()]
        
    # ⬇️ FIXED: Cast to string for safety instead of integer
    if company_id and 'company_id' in df.columns:
        df = df[df['company_id'].astype(str).str.upper() == str(company_id).upper()]
    return df

@st.cache_data(ttl=600)
def get_sectors() -> pd.DataFrame:
    return _load_excel_smart("sectors.xlsx")

@st.cache_data(ttl=600)
def get_peers(group_name: str = None) -> pd.DataFrame:
    df = _load_excel_smart("peer_groups.xlsx")
    companies = get_companies()
    if not companies.empty and 'company_id' in companies.columns:
        df = pd.merge(df, companies, on='company_id', how='left')
    
    if group_name and 'peer_group_name' in df.columns:
        df = df[df['peer_group_name'].astype(str).str.lower() == str(group_name).lower()]
    return df

@st.cache_data(ttl=600)
def get_prosandcons(ticker: str = None) -> pd.DataFrame:
    df = _load_excel_smart("prosandcons.xlsx")
    companies = get_companies()
    if not companies.empty and 'ticker' in companies.columns and 'company_id' in df.columns:
        df = pd.merge(df, companies[['company_id', 'ticker']], on='company_id', how='left')
    if ticker and 'ticker' in df.columns:
        df = df[df['ticker'].astype(str).str.upper() == str(ticker).upper()]
    return df

@st.cache_data(ttl=600)
def get_documents(ticker: str = None) -> pd.DataFrame:
    df = _load_excel_smart("documents.xlsx")
    companies = get_companies()
    if not companies.empty and 'ticker' in companies.columns and 'company_id' in df.columns:
        df = pd.merge(df, companies[['company_id', 'ticker']], on='company_id', how='left')
    if ticker and 'ticker' in df.columns:
        df = df[df['ticker'].astype(str).str.upper() == str(ticker).upper()]
    return df