import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Company Archetypes & Clustering", layout="wide")

st.title("🎯 Nifty 100 Machine Learning Clustering & Archetypes")
st.markdown("Exploring company groupings based on ROE, Debt-to-Equity, Revenue CAGR, Free Cash Flow, and Operating Margins (KMeans $k=5$).")

# Helper function to check multiple possible relative locations automatically
def find_file(possible_paths):
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return possible_paths[0] # Fallback

# Define possible relative locations for the files
CLUSTER_CSV = find_file([
    "nifty100_sprint_6/output/cluster_labels.csv",
    "output/cluster_labels.csv",
    "../nifty100_sprint_6/output/cluster_labels.csv",
    "../../nifty100_sprint_6/output/cluster_labels.csv",
    "../../../nifty100_sprint_6/output/cluster_labels.csv"
])

ELBOW_PLOT = find_file([
    "nifty100_sprint_6/reports/elbow_plot.png",
    "reports/elbow_plot.png",
    "../nifty100_sprint_6/reports/elbow_plot.png",
    "../../nifty100_sprint_6/reports/elbow_plot.png",
    "../../../nifty100_sprint_6/reports/elbow_plot.png"
])

CORR_HEATMAP = find_file([
    "nifty100_sprint_6/reports/correlation_heatmap.png",
    "reports/correlation_heatmap.png",
    "../nifty100_sprint_6/reports/correlation_heatmap.png",
    "../../nifty100_sprint_6/reports/correlation_heatmap.png",
    "../../../nifty100_sprint_6/reports/correlation_heatmap.png"
])

tab1, tab2, tab3 = st.tabs(["Cluster Assignments", "Elbow & Optimization", "Correlation Heatmap"])

# --- TAB 1: CLUSTER ASSIGNMENTS TABLE ---
with tab1:
    st.subheader("Assigned Financial Archetypes (92 Companies)")
    if os.path.exists(CLUSTER_CSV):
        df_cluster = pd.read_csv(CLUSTER_CSV)
        
        selected_archetype = st.selectbox("Filter by Archetype:", ["All"] + list(df_cluster['cluster_name'].unique()))
        if selected_archetype != "All":
            df_cluster = df_cluster[df_cluster['cluster_name'] == selected_archetype]
            
        st.dataframe(df_cluster, use_container_width=True)
    else:
        st.warning("⚠️ Cluster labels CSV not found.")

# --- TAB 2: ELBOW PLOT ---
with tab2:
    st.subheader("KMeans Optimal $k$ Selection")
    if os.path.exists(ELBOW_PLOT):
        st.image(ELBOW_PLOT, caption="Elbow Method Curve (Confirming k=5)", use_container_width=True)
    else:
        st.warning("⚠️ Elbow plot image not found.")

# --- TAB 3: CORRELATION HEATMAP ---
with tab3:
    st.subheader("KPI Pearson Correlation Matrix")
    if os.path.exists(CORR_HEATMAP):
        st.image(CORR_HEATMAP, caption="10 Key Financial Metrics Correlation Heatmap", use_container_width=True)
    else:
        st.warning("⚠️ Correlation heatmap image not found.")