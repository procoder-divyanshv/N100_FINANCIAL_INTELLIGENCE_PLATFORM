import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.dashboard.utils.db import get_companies, get_ratios, get_pl, get_cf, get_prosandcons, get_sectors

st.set_page_config(page_title="Company Profile | Nifty 100 Analytics", layout="wide")
st.title("🏢 Company Profile & Deep Dive")

companies_df = get_companies()
sectors_df = get_sectors()

if companies_df.empty:
    st.error("⚠️ `companies.xlsx` is missing or could not be loaded.")
    st.stop()

# Explicitly map the exact column names from your output
ticker_col = 'id'
name_col = 'company_name'
about_col = 'about_company'

# Build the dropdown with Company Name + Ticker
options_dict = {f"{row[name_col]} ({row[ticker_col]})": row[ticker_col] for _, row in companies_df.iterrows() if pd.notna(row[ticker_col])}
selected_label = st.selectbox("Search Company by Ticker or Name", options=list(options_dict.keys()))
selected_ticker = options_dict.get(selected_label)

if not selected_ticker:
    st.info("Please select a company.")
    st.stop()

# Fetch Company Data
info = companies_df[companies_df[ticker_col] == selected_ticker].iloc[0]

# Try to find sector data from sectors.xlsx
sector_name = "N/A"
if not sectors_df.empty:
    sec_match = sectors_df[sectors_df['company_id'] == selected_ticker] if 'company_id' in sectors_df.columns else pd.DataFrame()
    if not sec_match.empty:
        # Assuming the sector column is named 'sector' or 'sector_name'
        sec_col = next((c for c in sec_match.columns if 'sector' in c.lower()), None)
        if sec_col:
            sector_name = sec_match.iloc[0][sec_col]

# Header Card
st.subheader(f"{info[name_col]} ({selected_ticker})")
st.caption(f"**Sector:** {sector_name}")
st.write(info.get(about_col, 'No company summary available.'))

st.divider()

# Ratios and Financial KPIs
ratios_df = get_ratios()
if not ratios_df.empty:
    # ⬇️ FIX: Prioritize 'company_id' over 'id' to avoid matching against row numbers
    r_tick_col = 'company_id' if 'company_id' in ratios_df.columns else 'id'
    ratios_df = ratios_df[ratios_df[r_tick_col].astype(str).str.upper() == str(selected_ticker).upper()]

latest_ratios = ratios_df.iloc[-1] if not ratios_df.empty else pd.Series()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("ROE", f"{info.get('roe_percentage', 'N/A')}%")
k2.metric("ROCE", f"{info.get('roce_percentage', 'N/A')}%")
# ⬇️ FIX: Use exact column names from your terminal output
k3.metric("Net Margin", f"{latest_ratios.get('net_profit_margin_pct', 'N/A')}%")
k4.metric("D/E", f"{latest_ratios.get('debt_to_equity', 'N/A')}")
k5.metric("Book Value", f"₹{info.get('book_value', 'N/A')}")
k6.metric("Face Value", f"₹{info.get('face_value', 'N/A')}")

st.divider()

# Charts
c1, c2 = st.columns(2)
pl_df = get_pl(company_id=selected_ticker) 

with c1:
    st.subheader("10-Year Revenue & Net Profit")
    if not pl_df.empty and 'year' in pl_df.columns:
        pl_sorted = pl_df.sort_values('year')
        fig_bar = go.Figure()
        
        rev_col = next((c for c in pl_df.columns if 'revenue' in c or 'sales' in c), None)
        pat_col = next((c for c in pl_df.columns if 'profit' in c), None)
        
        if rev_col: fig_bar.add_trace(go.Bar(x=pl_sorted['year'], y=pl_sorted[rev_col], name="Revenue"))
        if pat_col: fig_bar.add_trace(go.Bar(x=pl_sorted['year'], y=pl_sorted[pat_col], name="Net Profit"))
        
        fig_bar.update_layout(barmode='group', height=350, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("P&L data not available.")

with c2:
    st.subheader("ROE Trend")
    # ⬇️ FIX: Check for the exact ROE column name
    if not ratios_df.empty and 'year' in ratios_df.columns and 'return_on_equity_pct' in ratios_df.columns:
        r_sorted = ratios_df.sort_values('year')
        fig_line = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_line.add_trace(go.Scatter(x=r_sorted['year'], y=r_sorted['return_on_equity_pct'], name="ROE (%)", mode='lines+markers'), secondary_y=False)
        fig_line.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Trend data not available.")