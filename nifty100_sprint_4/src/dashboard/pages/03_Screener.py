# # import streamlit as st
# # import pandas as pd
# # import sys
# # import os

# # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
# # from src.dashboard.utils.db import get_companies, get_ratios

# # st.set_page_config(page_title="Screener | Nifty 100 Analytics", layout="wide")
# # st.title("🔎 Stock Screener")

# # # Initialize session state for sliders if not exists
# # slider_keys = ['roe_min', 'de_max', 'fcf_min', 'rev_cagr_min', 'pat_cagr_min', 'opm_min', 'pe_max', 'pb_max', 'div_min', 'icr_min']
# # default_vals = [0.0, 5.0, -1000.0, 0.0, 0.0, 0.0, 100.0, 20.0, 0.0, 0.0]

# # for key, val in zip(slider_keys, default_vals):
# #     if key not in st.session_state:
# #         st.session_state[key] = val

# # # Preset button logic
# # def apply_preset(preset):
# #     if preset == "Quality":
# #         st.session_state.update({'roe_min': 15.0, 'de_max': 0.5, 'opm_min': 15.0, 'icr_min': 5.0})
# #     elif preset == "Value":
# #         st.session_state.update({'pe_max': 15.0, 'pb_max': 2.0, 'div_min': 2.0})
# #     elif preset == "Growth":
# #         st.session_state.update({'rev_cagr_min': 15.0, 'pat_cagr_min': 15.0, 'roe_min': 12.0})
# #     elif preset == "Dividend":
# #         st.session_state.update({'div_min': 4.0, 'fcf_min': 100.0})
# #     elif preset == "Debt-Free":
# #         st.session_state.update({'de_max': 0.0})
# #     elif preset == "Turnaround":
# #         st.session_state.update({'rev_cagr_min': -5.0, 'pat_cagr_min': 20.0, 'pb_max': 3.0})

# # # Layout: Sidebar for controls, Main for results
# # st.sidebar.header("Filter Presets")
# # c1, c2 = st.sidebar.columns(2)
# # c1.button("Quality", on_click=apply_preset, args=("Quality",))
# # c2.button("Value", on_click=apply_preset, args=("Value",))
# # c1.button("Growth", on_click=apply_preset, args=("Growth",))
# # c2.button("Dividend", on_click=apply_preset, args=("Dividend",))
# # c1.button("Debt-Free", on_click=apply_preset, args=("Debt-Free",))
# # c2.button("Turnaround", on_click=apply_preset, args=("Turnaround",))

# # st.sidebar.header("Custom Filters")
# # st.slider("ROE Min (%)", -50.0, 50.0, key='roe_min')
# # st.slider("D/E Max", 0.0, 10.0, key='de_max')
# # st.slider("FCF Min (Cr)", -5000.0, 10000.0, key='fcf_min')
# # st.slider("Rev CAGR Min (%)", -20.0, 50.0, key='rev_cagr_min')
# # st.slider("PAT CAGR Min (%)", -20.0, 50.0, key='pat_cagr_min')
# # st.slider("OPM Min (%)", -20.0, 50.0, key='opm_min')
# # st.slider("P/E Max", 0.0, 200.0, key='pe_max')
# # st.slider("P/B Max", 0.0, 50.0, key='pb_max')
# # st.slider("Div Yield Min (%)", 0.0, 15.0, key='div_min')
# # st.slider("ICR Min", -10.0, 50.0, key='icr_min')

# # # Load and merge data (using latest year for screening)
# # companies = get_companies()
# # ratios = get_ratios(year=2024) # Assuming 2024 is the latest

# # if companies.empty or ratios.empty:
# #     st.warning("Data not available. Check data files.")
# #     st.stop()

# # # Helper to find columns safely
# # def f_col(df, options):
# #     for col in df.columns:
# #         if col.lower().replace(" ", "_").replace("/", "") in [o.replace("/", "") for o in options]:
# #             return col
# #     return None

# # t_col_c = f_col(companies, ['ticker', 'symbol'])
# # t_col_r = f_col(ratios, ['ticker', 'symbol'])

# # if t_col_c and t_col_r:
# #     df = pd.merge(companies, ratios, left_on=t_col_c, right_on=t_col_r, how='inner')
# # else:
# #     df = pd.DataFrame()

# # if not df.empty:
# #     # Filter Logic
# #     roe_c = f_col(df, ['roe'])
# #     de_c = f_col(df, ['de', 'debtequity'])
# #     pe_c = f_col(df, ['pe', 'peratio'])
    
# #     # Apply filters safely if columns exist
# #     filtered_df = df.copy()
# #     if roe_c: filtered_df = filtered_df[filtered_df[roe_c] >= st.session_state.roe_min]
# #     if de_c: filtered_df = filtered_df[filtered_df[de_c] <= st.session_state.de_max]
# #     if pe_c: filtered_df = filtered_df[filtered_df[pe_c] <= st.session_state.pe_max]
    
# #     st.write(f"### {len(filtered_df)} companies match your filters")
    
# #     display_cols = [c for c in [f_col(df, ['company_id']), f_col(df, ['company_name', 'name']), t_col_c, f_col(df, ['sector', 'broad_sector']), roe_c, pe_c, de_c] if c]
    
# #     st.dataframe(filtered_df[display_cols], use_container_width=True)
    
# #     # CSV Download
# #     csv = filtered_df[display_cols].to_csv(index=False).encode('utf-8')
# #     st.download_button(
# #         label="📥 Download Results as CSV",
# #         data=csv,
# #         file_name='screener_results.csv',
# #         mime='text/csv',
# #     )
# # else:
# #     st.info("Unable to merge datasets for screening.")




# import streamlit as st
# import pandas as pd
# import sys
# import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
# from src.dashboard.utils.db import get_companies, get_ratios

# st.set_page_config(page_title="Screener | Nifty 100 Analytics", layout="wide")
# st.title("🔎 Stock Screener")

# # Presets callback
# def apply_preset(preset):
#     if preset == "Quality":
#         st.session_state['roe_min'] = 15.0
#         st.session_state['de_max'] = 0.5
#         st.session_state['opm_min'] = 15.0
#     elif preset == "Value":
#         st.session_state['de_max'] = 2.0
#     elif preset == "Growth":
#         st.session_state['roe_min'] = 12.0
#         st.session_state['opm_min'] = 10.0
#     elif preset == "Dividend":
#         st.session_state['roe_min'] = 10.0
#     elif preset == "Debt-Free":
#         st.session_state['de_max'] = 0.0
#     elif preset == "Turnaround":
#         st.session_state['roe_min'] = -10.0

# # Initialize session state keys
# defaults = {'roe_min': 0.0, 'de_max': 5.0, 'opm_min': 0.0, 'npm_min': 0.0, 'fcf_min': -5000.0, 'icr_min': 0.0}
# for k, v in defaults.items():
#     if k not in st.session_state:
#         st.session_state[k] = v

# # Sidebar: Preset Buttons
# st.sidebar.header("🎯 Filter Presets")
# p1, p2 = st.sidebar.columns(2)
# p1.button("Quality", on_click=apply_preset, args=("Quality",), use_container_width=True)
# p2.button("Value", on_click=apply_preset, args=("Value",), use_container_width=True)
# p1.button("Growth", on_click=apply_preset, args=("Growth",), use_container_width=True)
# p2.button("Dividend", on_click=apply_preset, args=("Dividend",), use_container_width=True)
# p1.button("Debt-Free", on_click=apply_preset, args=("Debt-Free",), use_container_width=True)
# p2.button("Turnaround", on_click=apply_preset, args=("Turnaround",), use_container_width=True)

# st.sidebar.divider()
# st.sidebar.header("⚙️ Custom Metric Sliders")
# st.sidebar.slider("ROE Min (%)", -50.0, 50.0, key='roe_min')
# st.sidebar.slider("D/E Max", 0.0, 10.0, key='de_max')
# st.sidebar.slider("OPM Min (%)", -20.0, 60.0, key='opm_min')
# st.sidebar.slider("NPM Min (%)", -20.0, 50.0, key='npm_min')
# st.sidebar.slider("FCF Min (Cr)", -10000.0, 20000.0, key='fcf_min')
# st.sidebar.slider("ICR Min", -10.0, 50.0, key='icr_min')

# # Load Latest Ratios (2024 or latest available)
# ratios_df = get_ratios(year=2024)
# if ratios_df.empty:
#     ratios_df = get_ratios()

# if ratios_df.empty:
#     st.error("No ratio data available for screening.")
#     st.stop()

# # Helper
# def f_col(df, candidates):
#     for col in df.columns:
#         clean = str(col).lower().strip().replace(" ", "_")
#         for cand in candidates:
#             if cand in clean:
#                 return col
#     return None

# roe_c = f_col(ratios_df, ['return_on_equity', 'roe'])
# de_c = f_col(ratios_df, ['debt_to_equity', 'de'])
# opm_c = f_col(ratios_df, ['operating_profit_margin', 'opm'])
# npm_c = f_col(ratios_df, ['net_profit_margin', 'npm'])
# fcf_c = f_col(ratios_df, ['free_cash_flow', 'fcf'])
# icr_c = f_col(ratios_df, ['interest_coverage', 'icr'])

# filtered = ratios_df.copy()
# if roe_c: filtered = filtered[filtered[roe_c] >= st.session_state['roe_min']]
# if de_c: filtered = filtered[filtered[de_c] <= st.session_state['de_max']]
# if opm_c: filtered = filtered[filtered[opm_c] >= st.session_state['opm_min']]
# if npm_c: filtered = filtered[filtered[npm_c] >= st.session_state['npm_min']]
# if fcf_c: filtered = filtered[filtered[fcf_c] >= st.session_state['fcf_min']]
# if icr_c: filtered = filtered[filtered[icr_c] >= st.session_state['icr_min']]

# # Main Screen Results
# st.subheader(f"📊 {len(filtered)} companies match your filters")

# display_cols = [c for c in ['company_name', 'ticker', roe_c, de_c, opm_c, npm_c, fcf_c, icr_c] if c and c in filtered.columns]
# st.dataframe(filtered[display_cols].reset_index(drop=True), use_container_width=True, height=450)

# # CSV Export
# csv_data = filtered[display_cols].to_csv(index=False).encode('utf-8')
# st.download_button(
#     label="📥 Download Filtered Results (CSV)",
#     data=csv_data,
#     file_name="screener_results.csv",
#     mime="text/csv"
# )


import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.dashboard.utils.db import get_companies, get_ratios

st.set_page_config(page_title="Screener | Nifty 100 Analytics", layout="wide")
st.title("🔎 Stock Screener")

def apply_preset(preset):
    if preset == "Quality":
        st.session_state['roe_min'], st.session_state['de_max'], st.session_state['opm_min'] = 15.0, 0.5, 15.0
    elif preset == "Value":
        st.session_state['de_max'] = 2.0
    elif preset == "Growth":
        st.session_state['roe_min'], st.session_state['opm_min'] = 12.0, 10.0
    elif preset == "Dividend":
        st.session_state['roe_min'] = 10.0
    elif preset == "Debt-Free":
        st.session_state['de_max'] = 0.0
    elif preset == "Turnaround":
        st.session_state['roe_min'] = -10.0

defaults = {'roe_min': 0.0, 'de_max': 5.0, 'opm_min': 0.0, 'npm_min': 0.0, 'fcf_min': -5000.0, 'icr_min': 0.0}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.sidebar.header("🎯 Filter Presets")
p1, p2 = st.sidebar.columns(2)
p1.button("Quality", on_click=apply_preset, args=("Quality",), use_container_width=True)
p2.button("Value", on_click=apply_preset, args=("Value",), use_container_width=True)
p1.button("Growth", on_click=apply_preset, args=("Growth",), use_container_width=True)
p2.button("Dividend", on_click=apply_preset, args=("Dividend",), use_container_width=True)
p1.button("Debt-Free", on_click=apply_preset, args=("Debt-Free",), use_container_width=True)
p2.button("Turnaround", on_click=apply_preset, args=("Turnaround",), use_container_width=True)

st.sidebar.divider()
st.sidebar.header("⚙️ Custom Metric Sliders")
st.sidebar.slider("ROE Min (%)", -50.0, 50.0, key='roe_min')
st.sidebar.slider("D/E Max", 0.0, 10.0, key='de_max')
st.sidebar.slider("OPM Min (%)", -20.0, 60.0, key='opm_min')
st.sidebar.slider("NPM Min (%)", -20.0, 50.0, key='npm_min')
st.sidebar.slider("FCF Min (Cr)", -10000.0, 20000.0, key='fcf_min')
st.sidebar.slider("ICR Min", -10.0, 50.0, key='icr_min')

companies_df = get_companies()
ratios_df = get_ratios(year=2024)
if ratios_df.empty:
    ratios_df = get_ratios()

if ratios_df.empty or companies_df.empty:
    st.error("Data missing for screening.")
    st.stop()

# Force merge Company Name and Ticker ID 
comp_col = 'id' if 'id' in companies_df.columns else 'company_id'
ratio_col = 'company_id' if 'company_id' in ratios_df.columns else 'id'

merged_df = pd.merge(ratios_df, companies_df[[comp_col, 'company_name']], left_on=ratio_col, right_on=comp_col, how='left')
merged_df.rename(columns={comp_col: 'Ticker'}, inplace=True)

def f_col(df, candidates):
    for col in df.columns:
        if any(cand in str(col).lower().strip().replace(" ", "_") for cand in candidates):
            return col
    return None

roe_c = f_col(merged_df, ['return_on_equity', 'roe'])
de_c = f_col(merged_df, ['debt_to_equity', 'de'])
opm_c = f_col(merged_df, ['operating_profit_margin', 'opm'])
npm_c = f_col(merged_df, ['net_profit_margin', 'npm'])
fcf_c = f_col(merged_df, ['free_cash_flow', 'fcf'])
icr_c = f_col(merged_df, ['interest_coverage', 'icr'])

filtered = merged_df.copy()
if roe_c: filtered = filtered[filtered[roe_c] >= st.session_state['roe_min']]
if de_c: filtered = filtered[filtered[de_c] <= st.session_state['de_max']]
if opm_c: filtered = filtered[filtered[opm_c] >= st.session_state['opm_min']]
if npm_c: filtered = filtered[filtered[npm_c] >= st.session_state['npm_min']]
if fcf_c: filtered = filtered[filtered[fcf_c] >= st.session_state['fcf_min']]
if icr_c: filtered = filtered[filtered[icr_c] >= st.session_state['icr_min']]

st.subheader(f"📊 {len(filtered)} companies match your filters")

display_cols = [c for c in ['company_name', 'Ticker', roe_c, de_c, opm_c, npm_c, fcf_c, icr_c] if c and c in filtered.columns]
st.dataframe(filtered[display_cols].reset_index(drop=True), use_container_width=True, height=450)

csv_data = filtered[display_cols].to_csv(index=False).encode('utf-8')
st.download_button(label="📥 Download Filtered Results (CSV)", data=csv_data, file_name="screener_results.csv", mime="text/csv")