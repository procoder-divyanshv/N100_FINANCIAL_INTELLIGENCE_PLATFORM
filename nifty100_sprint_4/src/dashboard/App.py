import streamlit as st

# Set Streamlit page configuration
st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Nifty 100 Analytics Dashboard")

st.markdown("""
Welcome to the **Nifty 100 Financial Analytics & Valuation System**. 

This multi-page application provides a comprehensive suite for fundamental analysis, valuation tracking, and peer comparisons across the Nifty 100 universe.

### 🧭 Available Modules:
* **Home:** Macro-level market overview, KPI summaries, and sector distributions.
* **Profile:** Deep dive into individual company balance sheets, ROCE/ROE trajectories, and P&L histories.
* **Screener:** Custom multi-factor screening using real-time metric sliders and preset filters.
* **Peers:** Industry group peer benchmarking and interactive radar charts.
* **Trends:** Multi-metric overlay analysis for tracking YoY financial growth.
* **Sectors:** Bubble chart risk/reward analysis mapped against market capitalizations.
* **Capital:** Treemap layout mapping structural allocations across companies.
* **Reports:** Direct access portal for official annual report filings.
* **Cluster Analysis:** Machine learning-driven archetype clustering and correlation heatmaps.
""")

st.info("👈 Use the sidebar navigation on the left to select a screen and begin your analysis.")