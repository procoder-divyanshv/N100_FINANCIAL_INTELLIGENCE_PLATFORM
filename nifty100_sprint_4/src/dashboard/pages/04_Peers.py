# import streamlit as st
# import pandas as pd
# import plotly.graph_objects as go
# import sys
# import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
# from src.dashboard.utils.db import get_companies, get_ratios, get_peers

# st.set_page_config(page_title="Peer Comparison | Nifty 100 Analytics", layout="wide")
# st.title("⚖️ Peer Comparison")

# peers_df = get_peers()
# if peers_df.empty:
#     st.error("Peer groups data is missing.")
#     st.stop()

# # Helper to find columns
# def f_col(df, options):
#     for col in df.columns:
#         if col.lower().replace(" ", "_") in options:
#             return col
#     return None

# group_col = f_col(peers_df, ['peer_group', 'group', 'industry_group'])
# if not group_col:
#     st.error("Could not identify peer group column.")
#     st.stop()

# groups = peers_df[group_col].dropna().unique().tolist()
# selected_group = st.selectbox("Select Peer Group", options=groups)

# group_data = get_peers(selected_group)
# ticker_col = f_col(group_data, ['ticker', 'symbol'])
# group_tickers = group_data[ticker_col].tolist() if ticker_col else []

# selected_company = st.selectbox("Select Benchmark Company", options=group_tickers)

# # Load Financial Ratios for these tickers (Year 2024)
# ratios = get_ratios(year=2024)
# r_ticker = f_col(ratios, ['ticker', 'symbol'])

# if r_ticker and not ratios.empty:
#     group_ratios = ratios[ratios[r_ticker].isin(group_tickers)]
    
#     metrics = [f_col(ratios, ['roe']), f_col(ratios, ['roce']), f_col(ratios, ['opm']), 
#                f_col(ratios, ['npm']), f_col(ratios, ['pe']), f_col(ratios, ['pb'])]
#     valid_metrics = [m for m in metrics if m]
    
#     if valid_metrics and not group_ratios.empty:
#         c1, c2 = st.columns([1, 1.5])
        
#         with c1:
#             st.subheader("Radar Comparison")
#             # Calculate peer average
#             peer_avg = group_ratios[valid_metrics].mean().tolist()
            
#             # Get selected company data
#             company_data = group_ratios[group_ratios[r_ticker] == selected_company]
#             comp_vals = company_data[valid_metrics].iloc[0].tolist() if not company_data.empty else [0]*len(valid_metrics)
            
#             fig = go.Figure()
#             fig.add_trace(go.Scatterpolar(
#                 r=comp_vals, theta=valid_metrics, fill='toself', name=selected_company
#             ))
#             fig.add_trace(go.Scatterpolar(
#                 r=peer_avg, theta=valid_metrics, fill='toself', name='Peer Average'
#             ))
#             fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, height=400)
#             st.plotly_chart(fig, use_container_width=True)
            
#         with c2:
#             st.subheader("Peer Group KPI Table")
#             display_cols = [r_ticker] + valid_metrics
            
#             # Highlight selected row using pandas styling
#             def highlight_row(row):
#                 return ['background-color: rgba(46, 204, 113, 0.2)'] * len(row) if row[r_ticker] == selected_company else [''] * len(row)
            
#             styled_df = group_ratios[display_cols].style.apply(highlight_row, axis=1)
#             st.dataframe(styled_df, use_container_width=True, height=400)
#     else:
#         st.info("Insufficient metric columns available for comparison.")
# else:
#     st.warning("Ratio data missing for selected group.")


import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.dashboard.utils.db import get_peers, get_ratios

st.title("⚖️ Peer Comparison")

peers_df = get_peers()
if peers_df.empty:
    st.error("⚠️ peer_groups.xlsx is missing or could not be loaded.")
    st.stop()

# Group selection
groups = peers_df['peer_group_name'].dropna().unique().tolist()
selected_group = st.selectbox("Select Peer Group", options=groups)

group_data = get_peers(selected_group)
ticker_col = 'ticker' if 'ticker' in group_data.columns else 'company_id'
tickers = group_data[ticker_col].dropna().unique().tolist()

selected_company = st.selectbox("Select Benchmark Company", options=tickers)

# Metrics comparison
ratios_df = get_ratios(year=2024)
if ratios_df.empty:
    ratios_df = get_ratios()

if not ratios_df.empty and ticker_col in ratios_df.columns:
    group_ratios = ratios_df[ratios_df[ticker_col].isin(tickers)]
    
    metric_cols = [c for c in ['return_on_equity_pct', 'operating_profit_margin_pct', 'net_profit_margin_pct', 'debt_to_equity', 'interest_coverage'] if c in group_ratios.columns]
    
    if metric_cols and not group_ratios.empty:
        c1, c2 = st.columns([1, 1.3])
        
        with c1:
            st.subheader("Radar Comparison")
            peer_avg = group_ratios[metric_cols].mean().tolist()
            comp_row = group_ratios[group_ratios[ticker_col] == selected_company]
            comp_vals = comp_row[metric_cols].iloc[0].tolist() if not comp_row.empty else [0]*len(metric_cols)
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=comp_vals, theta=metric_cols, fill='toself', name=str(selected_company)))
            fig.add_trace(go.Scatterpolar(r=peer_avg, theta=metric_cols, fill='toself', name="Peer Average"))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, height=380)
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.subheader("Peer Group Metrics Table")
            display_cols = [c for c in ['company_name', ticker_col] + metric_cols if c in group_ratios.columns]
            st.dataframe(group_ratios[display_cols].reset_index(drop=True), use_container_width=True)