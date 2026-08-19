# import streamlit as st
# import plotly.express as px
# import sys
# import os
# from src.dashboard.utils.db import get_sectors

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
# from src.dashboard.utils.db import get_companies, get_ratios

# st.title("📈 Market Overview & Key Metrics")

# companies_df = get_companies()
# if companies_df.empty:
#     st.error("⚠️ companies.xlsx could not be loaded.")
#     st.stop()

# # Sidebar Year Filter
# selected_year = st.sidebar.selectbox("Select Financial Year", options=[2024, 2023, 2022, 2021, 2020, 2019], index=0)
# ratios_df = get_ratios(year=selected_year)
# if ratios_df.empty:
#     ratios_df = get_ratios()

# # 6 KPI Tiles
# col1, col2, col3, col4, col5, col6 = st.columns(6)
# col1.metric("Total Companies", len(companies_df))

# avg_roe = ratios_df['return_on_equity_pct'].dropna().mean() if not ratios_df.empty and 'return_on_equity_pct' in ratios_df else None
# col2.metric("Avg ROE", f"{avg_roe:.2f}%" if avg_roe is not None else "N/A")

# med_de = ratios_df['debt_to_equity'].dropna().median() if not ratios_df.empty and 'debt_to_equity' in ratios_df else None
# col3.metric("Median D/E", f"{med_de:.2f}" if med_de is not None else "N/A")

# debt_free = (ratios_df['debt_to_equity'] == 0).sum() if not ratios_df.empty and 'debt_to_equity' in ratios_df else 0
# col4.metric("Debt-Free Companies", int(debt_free))

# npm_med = ratios_df['net_profit_margin_pct'].dropna().median() if not ratios_df.empty and 'net_profit_margin_pct' in ratios_df else None
# col5.metric("Median NPM", f"{npm_med:.2f}%" if npm_med is not None else "N/A")

# opm_med = ratios_df['operating_profit_margin_pct'].dropna().median() if not ratios_df.empty and 'operating_profit_margin_pct' in ratios_df else None
# col6.metric("Median OPM", f"{opm_med:.2f}%" if opm_med is not None else "N/A")

# st.divider()

# col_left, col_right = st.columns([1, 1])

# # Sector Breakdown Donut Chart
# with col_left:
#     st.subheader("Sector Breakdown")
#     sectors_df = get_sectors()
    
#     if not sectors_df.empty:
#         # Find the sector name column dynamically
#         sec_col = next((c for c in sectors_df.columns if 'sector' in c.lower()), None)
        
#         if sec_col:
#             sector_counts = sectors_df[sec_col].value_counts().reset_index()
#             sector_counts.columns = ['Sector', 'Count']
#             fig = px.pie(sector_counts, names='Sector', values='Count', hole=0.45, title="Companies by Sector")
#             st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.info("Could not identify sector column in sectors.xlsx.")
#     else:
#         st.info("Sector dataset is empty or missing.")
# # Top Companies Table
# with col_right:
#     st.subheader("Top Performers (by ROE)")
#     if not ratios_df.empty and 'return_on_equity_pct' in ratios_df:
#         top_5 = ratios_df.sort_values(by='return_on_equity_pct', ascending=False).head(5)
#         display_cols = [c for c in ['company_name', 'ticker', 'return_on_equity_pct', 'net_profit_margin_pct'] if c in top_5.columns]
#         st.dataframe(top_5[display_cols].reset_index(drop=True), use_container_width=True)
#     else:
#         st.info("Performance metrics unavailable.")



import sys
import os
import streamlit as st
import plotly.express as px
import pandas as pd

# MUST be before the src imports!
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.dashboard.utils.db import get_companies, get_ratios, get_sectors

st.title("📈 Market Overview & Key Metrics")

companies_df = get_companies()
if companies_df.empty:
    st.error("⚠️ companies.xlsx could not be loaded.")
    st.stop()

# Sidebar Year Filter
selected_year = st.sidebar.selectbox("Select Financial Year", options=[2024, 2023, 2022, 2021, 2020, 2019], index=0)
ratios_df = get_ratios(year=selected_year)
if ratios_df.empty:
    ratios_df = get_ratios()

# 6 KPI Tiles
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Total Companies", len(companies_df))

avg_roe = ratios_df['return_on_equity_pct'].dropna().mean() if not ratios_df.empty and 'return_on_equity_pct' in ratios_df else None
col2.metric("Avg ROE", f"{avg_roe:.2f}%" if avg_roe is not None else "N/A")

med_de = ratios_df['debt_to_equity'].dropna().median() if not ratios_df.empty and 'debt_to_equity' in ratios_df else None
col3.metric("Median D/E", f"{med_de:.2f}" if med_de is not None else "N/A")

debt_free = (ratios_df['debt_to_equity'] == 0).sum() if not ratios_df.empty and 'debt_to_equity' in ratios_df else 0
col4.metric("Debt-Free Companies", int(debt_free))

npm_med = ratios_df['net_profit_margin_pct'].dropna().median() if not ratios_df.empty and 'net_profit_margin_pct' in ratios_df else None
col5.metric("Median NPM", f"{npm_med:.2f}%" if npm_med is not None else "N/A")

opm_med = ratios_df['operating_profit_margin_pct'].dropna().median() if not ratios_df.empty and 'operating_profit_margin_pct' in ratios_df else None
col6.metric("Median OPM", f"{opm_med:.2f}%" if opm_med is not None else "N/A")

st.divider()

col_left, col_right = st.columns([1, 1])

# Sector Breakdown Donut Chart
with col_left:
    st.subheader("Sector Breakdown")
    sectors_df = get_sectors()
    
    if not sectors_df.empty:
        sec_col = next((c for c in sectors_df.columns if 'sector' in c.lower()), None)
        if sec_col:
            sector_counts = sectors_df[sec_col].value_counts().reset_index()
            sector_counts.columns = ['Sector', 'Count']
            fig = px.pie(sector_counts, names='Sector', values='Count', hole=0.45, title="Companies by Sector")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Could not identify sector column.")
    else:
        st.info("Sector dataset is empty.")

# Top Companies Table
with col_right:
    st.subheader("Top Performers (by ROE)")
    if not ratios_df.empty and 'return_on_equity_pct' in ratios_df:
        top_5 = ratios_df.sort_values(by='return_on_equity_pct', ascending=False).head(5)
        display_cols = [c for c in ['company_name', 'company_id', 'id', 'return_on_equity_pct', 'net_profit_margin_pct'] if c in top_5.columns]
        st.dataframe(top_5[display_cols].reset_index(drop=True), use_container_width=True)
    else:
        st.info("Performance metrics unavailable.")