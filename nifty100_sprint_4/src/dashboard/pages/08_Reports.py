# import streamlit as st
# import pandas as pd
# import sys
# import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
# from src.dashboard.utils.db import get_companies, get_documents

# st.set_page_config(page_title="Annual Reports | Nifty 100 Analytics", layout="wide")
# st.title("📄 Annual Reports & Filings")

# companies = get_companies()
# docs = get_documents()

# if companies.empty or docs.empty:
#     st.error("Documents dataset is missing or empty.")
#     st.stop()

# # Search box
# id_col = 'id' if 'id' in companies.columns else 'company_id'
# options_dict = {f"{row.get('company_name', row[id_col])} ({row[id_col]})": row[id_col] for _, row in companies.iterrows()}
# selected_label = st.selectbox("Search Company", options=list(options_dict.keys()))
# selected_ticker = options_dict.get(selected_label)

# if selected_ticker:
#     doc_id_col = 'company_id' if 'company_id' in docs.columns else 'id'
#     company_docs = docs[docs[doc_id_col].astype(str).str.upper() == str(selected_ticker).upper()]
    
#     if not company_docs.empty:
#         st.subheader(f"Available Filings for {selected_label.split('(')[0].strip()}")
        
#         # Broader search for column names
#         year_col = next((c for c in company_docs.columns if 'year' in c.lower() or 'fy' in c.lower()), None)
#         link_col = next((c for c in company_docs.columns if 'link' in c.lower() or 'url' in c.lower() or 'pdf' in c.lower() or 'report' in c.lower()), None)
        
#         if year_col and link_col:
#             company_docs = company_docs.sort_values(year_col, ascending=False)
            
#             for _, row in company_docs.iterrows():
#                 col1, col2 = st.columns([1, 4])
#                 col1.markdown(f"**FY {row[year_col]}**")
                
#                 link = str(row[link_col])
#                 if link.startswith('http'):
#                     col2.markdown(f"[🔗 View Annual Report PDF]({link})")
#                 else:
#                     col2.markdown("🔴 *Report unavailable (404)*")
#                 st.divider()
#         else:
#             # Fallback: Just show the raw data table so it isn't a blank error
#             st.info("Could not automatically format the document links. Here is the raw filing data:")
#             st.dataframe(company_docs, use_container_width=True)
#     else:
#         st.info("No annual reports found for this company in the database.")





import streamlit as st
import os
import base64

st.set_page_config(page_title="Reports & Tearsheets", layout="wide")

# Paths setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_TEARSHEET_DIR = os.path.join(BASE_DIR, "../../../reports/tearsheets")
REPORTS_PORTFOLIO_DIR = os.path.join(BASE_DIR, "../../../reports/portfolio")
REPORTS_SECTOR_DIR = os.path.join(BASE_DIR, "../../../reports/sector")

st.title("📄 Nifty 100 Intelligence Reports & PDF Tearsheets")
st.markdown("Access, preview, and download programmatically generated 2-page company tearsheets and sector intelligence reports.")

tabs = st.tabs(["Company Tearsheets", "Sector Reports", "Master Portfolio Summary"])

# --- TAB 1: COMPANY TEARSHEETS ---
with tabs[0]:
    st.subheader("Individual Company PDF Tearsheets")
    
    if os.path.exists(REPORTS_TEARSHEET_DIR):
        pdf_files = [f for f in os.listdir(REPORTS_TEARSHEET_DIR) if f.endswith(".pdf")]
        pdf_files.sort()
        
        if pdf_files:
            # Clean up display names for dropdown
            company_options = {f.replace("_tearsheet.pdf", ""): f for f in pdf_files}
            selected_company_key = st.selectbox("Select Company Ticker/Name:", list(company_options.keys()))
            
            selected_filename = company_options[selected_company_key]
            file_path = os.path.join(REPORTS_TEARSHEET_DIR, selected_filename)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**Target Company:** `{selected_company_key}`")
                st.markdown(f"**File Size:** {os.path.getsize(file_path) / 1024:.1f} KB")
                
                with open(file_path, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Download Company Tearsheet PDF",
                        data=pdf_file,
                        file_name=selected_filename,
                        mime="application/pdf"
                    )
            with col2:
                st.info("💡 Tip: Click the download button above to save the structured 2-page ReportLab PDF report containing live financial ratios, cash flow intelligence, and AI-generated pros & cons.")
        else:
            st.warning("⚠️ No company tearsheets found in `reports/tearsheets/`. Run `batch_reports.py` first.")
    else:
        st.error("❌ Tearsheet directory not found.")

# --- TAB 2: SECTOR REPORTS ---
with tabs[1]:
    st.subheader("Sector Intelligence Reports")
    if os.path.exists(REPORTS_SECTOR_DIR):
        sector_files = [f for f in os.listdir(REPORTS_SECTOR_DIR) if f.endswith(".pdf")]
        sector_files.sort()
        
        if sector_files:
            sec_options = {f.replace("_report.pdf", "").upper(): f for f in sector_files}
            selected_sec_key = st.selectbox("Select Sector Group:", list(sec_options.keys()))
            
            sec_filename = sec_options[selected_sec_key]
            sec_path = os.path.join(REPORTS_SECTOR_DIR, sec_filename)
            
            with open(sec_path, "rb") as sec_file:
                st.download_button(
                    label=f"⬇️ Download {selected_sec_key} Sector PDF Report",
                    data=sec_file,
                    file_name=sec_filename,
                    mime="application/pdf"
                )
        else:
            st.warning("⚠️ No sector reports found.")
    else:
        st.error("❌ Sector reports directory not found.")

# --- TAB 3: MASTER PORTFOLIO SUMMARY ---
with tabs[2]:
    st.subheader("Master Portfolio Summary PDF")
    portfolio_pdf = os.path.join(REPORTS_PORTFOLIO_DIR, "portfolio_summary.pdf")
    
    if os.path.exists(portfolio_pdf):
        st.markdown("Download the complete multi-page compiled portfolio summary containing alphabetical listings and fundamental indicators across all analyzed entities.")
        with open(portfolio_pdf, "rb") as port_file:
            st.download_button(
                label="⬇️ Download Master Portfolio PDF",
                data=port_file,
                file_name="portfolio_summary.pdf",
                mime="application/pdf"
            )
    else:
        st.warning("⚠️ Master portfolio summary PDF not found. Run `portfolio_summary.py` first.")