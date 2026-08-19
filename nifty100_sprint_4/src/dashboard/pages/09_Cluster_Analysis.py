# import streamlit as st
# import pandas as pd
# import os

# st.set_page_config(page_title="Company Archetypes & Clustering", layout="wide")

# st.title("🎯 Nifty 100 Machine Learning Clustering & Archetypes")
# st.markdown("Exploring company groupings based on ROE, Debt-to-Equity, Revenue CAGR, Free Cash Flow, and Operating Margins (KMeans $k=5$).")

# # Paths to Sprint 6 outputs
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# CLUSTER_CSV = os.path.join(BASE_DIR, "../../../output/cluster_labels.csv")
# ELBOW_PLOT = os.path.join(BASE_DIR, "../../../reports/elbow_plot.png")
# CORR_HEATMAP = os.path.join(BASE_DIR, "../../../reports/correlation_heatmap.png")

# tab1, tab2, tab3 = st.tabs(["Cluster Assignments", "Elbow & Optimization", "Correlation Heatmap"])

# # --- TAB 1: CLUSTER ASSIGNMENTS TABLE ---
# with tab1:
#     st.subheader("Assigned Financial Archetypes (92 Companies)")
#     if os.path.exists(CLUSTER_CSV):
#         df_cluster = pd.read_csv(CLUSTER_CSV)
        
#         # Filter by cluster name dropdown
#         selected_archetype = st.selectbox("Filter by Archetype:", ["All"] + list(df_cluster['cluster_name'].unique()))
#         if selected_archetype != "All":
#             df_cluster = df_cluster[df_cluster['cluster_name'] == selected_archetype]
            
#         st.dataframe(df_cluster, use_container_width=True)
#     else:
#         st.warning("⚠️ Cluster labels CSV not found. Run `python src/analytics/clustering.py` first.")

# # --- TAB 2: ELBOW PLOT ---
# with tab2:
#     st.subheader("KMeans Optimal $k$ Selection")
#     if os.path.exists(ELBOW_PLOT):
#         st.image(ELBOW_PLOT, caption="Elbow Method Curve (Confirming k=5)", use_container_width=True)
#     else:
#         st.warning("⚠️ Elbow plot image not found.")

# # --- TAB 3: CORRELATION HEATMAP ---
# with tab3:
#     st.subheader("KPI Pearson Correlation Matrix")
#     if os.path.exists(CORR_HEATMAP):
#         st.image(CORR_HEATMAP, caption="10 Key Financial Metrics Correlation Heatmap", use_container_width=True)
#     else:
#         st.warning("⚠️ Correlation heatmap image not found.")

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Company Archetypes & Clustering", layout="wide")

# Explicitly point to your Sprint 6 absolute folder path
SPRINT_6_DIR = "/home/divyansh-verma/Desktop/BlueStock Internship Tasks/N100 FINANCIAL INTELLIGENCE PLATFORM_PROJECT/nifty100_sprint_6"

CLUSTER_CSV = os.path.join(SPRINT_6_DIR, "output", "cluster_labels.csv")
ELBOW_PLOT = os.path.join(SPRINT_6_DIR, "reports", "elbow_plot.png")
CORR_HEATMAP = os.path.join(SPRINT_6_DIR, "reports", "correlation_heatmap.png")

st.title("🎯 Nifty 100 Machine Learning Clustering & Archetypes")
st.markdown("Exploring company groupings based on ROE, Debt-to-Equity, Revenue CAGR, Free Cash Flow, and Operating Margins (KMeans $k=5$).")

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
        st.warning(f"⚠️ Cluster labels CSV not found. Run `python src/analytics/clustering.py` inside nifty100_sprint_6 first.")

# --- TAB 2: ELBOW PLOT ---
with tab2:
    st.subheader("KMeans Optimal $k$ Selection")
    if os.path.exists(ELBOW_PLOT):
        st.image(ELBOW_PLOT, caption="Elbow Method Curve (Confirming k=5)", use_container_width=True)
    else:
        st.warning(f"⚠️ Elbow plot image not found at: {ELBOW_PLOT}")

# --- TAB 3: CORRELATION HEATMAP ---
with tab3:
    st.subheader("KPI Pearson Correlation Matrix")
    if os.path.exists(CORR_HEATMAP):
        st.image(CORR_HEATMAP, caption="10 Key Financial Metrics Correlation Heatmap", use_container_width=True)
    else:
        st.warning(f"⚠️ Correlation heatmap image not found at: {CORR_HEATMAP}")