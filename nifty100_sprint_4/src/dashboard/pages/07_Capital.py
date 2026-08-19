import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.dashboard.utils.db import get_companies, get_sectors

st.set_page_config(page_title="Capital Allocation | Nifty 100 Analytics", layout="wide")
st.title("🧩 Capital Allocation Map")

companies_df = get_companies()
sectors_df = get_sectors()

if companies_df.empty:
    st.error("Company data is missing.")
    st.stop()

comp_id = 'id'
merged = companies_df.copy()

# 1. Merge Sectors (for fallback grouping)
sec_id = 'company_id' if 'company_id' in sectors_df.columns else 'id'
if not sectors_df.empty and sec_id in sectors_df.columns:
    merged = pd.merge(merged, sectors_df, left_on=comp_id, right_on=sec_id, how='left')

# 2. Try to load 'analysis.xlsx' to find the Pattern column
analysis_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/analysis.xlsx"))
if os.path.exists(analysis_path):
    analysis_df = pd.read_excel(analysis_path)
    if any("fintech" in str(col).lower() or "nifty" in str(col).lower() for col in analysis_df.columns):
        analysis_df = pd.read_excel(analysis_path, header=1)
    analysis_df.columns = [str(c).strip().lower().replace(" ", "_") for c in analysis_df.columns]
    
    an_id = 'company_id' if 'company_id' in analysis_df.columns else 'id'
    if an_id in analysis_df.columns:
        merged = pd.merge(merged, analysis_df, left_on=comp_id, right_on=an_id, how='left')

# 3. Identify Grouping Column (Pattern first, fallback to Sector)
cap_col = next((c for c in merged.columns if 'capital' in c or 'allocation' in c or 'pattern' in c), None)
sec_col = next((c for c in merged.columns if 'sector' in c.lower() and c != 'sector_id'), None)

group_col = cap_col if cap_col else sec_col
name_col = 'company_name'

if group_col:
    group_title = group_col.replace('_', ' ').title()
    st.markdown(f"Treemap of Nifty 100 companies grouped by **{group_title}**.")
    
    df_tree = merged.dropna(subset=[group_col, name_col]).copy()
    df_tree['All'] = 'Nifty 100'
    
    fig = px.treemap(
        df_tree, 
        path=['All', group_col, name_col], 
        title=f"Company Distribution Map ({group_title})",
        height=600
    )
    fig.update_traces(root_color="lightgrey")
    fig.update_layout(margin=dict(t=40, l=10, r=10, b=10))
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Bottom Data Table
    patterns = df_tree[group_col].unique().tolist()
    selected_pattern = st.selectbox(f"View companies by {group_title}:", options=patterns)
    
    if selected_pattern:
        pattern_df = df_tree[df_tree[group_col] == selected_pattern]
        
        # Safely compile only the columns that exist in the dataframe
        desired_cols = [name_col, 'company_id', 'id', 'book_value', 'roce_percentage']
        disp_cols = [c for c in desired_cols if c in pattern_df.columns]
        
        st.dataframe(pattern_df[disp_cols].reset_index(drop=True), use_container_width=True)
else:
    st.warning("Could not find a valid grouping column (like Pattern or Sector) in the datasets.")