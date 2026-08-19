import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.dashboard.utils.db import get_companies, get_ratios, get_sectors

st.set_page_config(page_title="Sector Analysis | Nifty 100 Analytics", layout="wide")
st.title("🏭 Sector Analysis")

companies_df = get_companies()
sectors_df = get_sectors()
ratios_df = get_ratios(year=2024)
if ratios_df.empty:
    ratios_df = get_ratios()

if sectors_df.empty or companies_df.empty:
    st.error("Missing required datasets.")
    st.stop()

# 1. Safely Merge Companies and Ratios
merged = companies_df.copy()
comp_id = 'id'
rat_id = 'company_id' if 'company_id' in ratios_df.columns else 'id'

if not ratios_df.empty and rat_id in ratios_df.columns:
    merged = pd.merge(merged, ratios_df, left_on=comp_id, right_on=rat_id, how='inner', suffixes=('', '_ratio'))

# 2. Safely Merge Sectors
sec_id = 'company_id' if 'company_id' in sectors_df.columns else 'id'
if not sectors_df.empty and sec_id in sectors_df.columns:
    merged = pd.merge(merged, sectors_df, left_on=comp_id, right_on=sec_id, how='left', suffixes=('', '_sec'))

sec_col = next((c for c in merged.columns if 'sector' in c.lower() and c != 'sector_id'), None)
available_sectors = merged[sec_col].dropna().unique().tolist() if sec_col else []
selected_sector = st.selectbox("Select Sector Filter", options=["All Sectors"] + available_sectors)

# 3. Safely Load & Merge Market Cap
mc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/market_cap.xlsx"))
if os.path.exists(mc_path):
    mc_df = pd.read_excel(mc_path)
    # Check for banner row
    if any("fintech" in str(col).lower() or "nifty" in str(col).lower() for col in mc_df.columns):
        mc_df = pd.read_excel(mc_path, header=1)
    mc_df.columns = [str(c).strip().lower().replace(" ", "_") for c in mc_df.columns]
    
    mc_id = 'company_id' if 'company_id' in mc_df.columns else 'id'
    if mc_id in mc_df.columns:
        merged = pd.merge(merged, mc_df, left_on=comp_id, right_on=mc_id, how='left', suffixes=('', '_mc'))

# Apply Sector Filter
if selected_sector != "All Sectors" and sec_col:
    merged = merged[merged[sec_col] == selected_sector]

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Risk vs Reward")
    roe_c = next((c for c in merged.columns if 'roe' in c), None)
    mc_c = next((c for c in merged.columns if 'market_cap' in c or 'mcap' in c), None)
    
    x_axis = 'book_value' if 'book_value' in merged.columns else roe_c
    
    if roe_c and x_axis:
        # Prevent scaling errors with NaN sizes
        if mc_c:
            merged[mc_c] = pd.to_numeric(merged[mc_c], errors='coerce').fillna(100)
            
        fig = px.scatter(
            merged, x=x_axis, y=roe_c, 
            size=mc_c if mc_c else None,
            color=sec_col if sec_col else None,
            hover_name='company_name',
            title="Bubble Size = Market Cap (or Book Value)" if mc_c else "Sector Analysis",
            size_max=45
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient metrics available for the scatter chart.")

with col2:
    st.subheader("Median Sector KPIs")
    if sec_col and roe_c:
        medians = merged.groupby(sec_col)[roe_c].median().reset_index().sort_values(roe_c, ascending=False)
        fig_bar = px.bar(medians, x=sec_col, y=roe_c, title="Median ROE by Sector")
        st.plotly_chart(fig_bar, use_container_width=True)