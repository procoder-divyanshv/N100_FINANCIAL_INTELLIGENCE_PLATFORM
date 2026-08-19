import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.dashboard.utils.db import get_companies, get_pl

st.set_page_config(page_title="Trend Analysis | Nifty 100 Analytics", layout="wide")
st.title("📈 YoY Trend Analysis")

companies = get_companies()
if companies.empty:
    st.error("Company data missing.")
    st.stop()

# Search box
id_col = 'id' if 'id' in companies.columns else 'company_id'
options_dict = {f"{row.get('company_name', row[id_col])} ({row[id_col]})": row[id_col] for _, row in companies.iterrows()}
selected_label = st.selectbox("Search Company", options=list(options_dict.keys()))
selected_ticker = options_dict.get(selected_label)

if not selected_ticker:
    st.stop()

# Load P&L Data
pl_df = get_pl(company_id=selected_ticker)

if not pl_df.empty and 'year' in pl_df.columns:
    pl_df = pl_df.sort_values('year')
    
    # Identify available metrics for the multiselect
    skip_cols = ['id', 'company_id', 'ticker', 'year', 'unnamed']
    available_metrics = [c for c in pl_df.columns if not any(skip in c.lower() for skip in skip_cols)]
    
    selected_metrics = st.multiselect("Select up to 3 metrics to overlay", options=available_metrics, default=available_metrics[:2] if len(available_metrics) >= 2 else available_metrics)
    
    if selected_metrics:
        if len(selected_metrics) > 3:
            st.warning("Please select a maximum of 3 metrics for optimal viewing.")
            selected_metrics = selected_metrics[:3]
            
        fig = px.line(pl_df, x='year', y=selected_metrics, markers=True, title=f"10-Year Financial Trends for {selected_ticker}")
        fig.update_layout(xaxis_title="Financial Year", yaxis_title="Value (Cr)", hovermode="x unified", height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least one metric to display the chart.")
else:
    st.warning("Trend data is currently unavailable for this company.")