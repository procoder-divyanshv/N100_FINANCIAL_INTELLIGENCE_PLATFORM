import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
OUTPUT_DIR = os.path.join(BASE_DIR, "../../output")
REPORTS_DIR = os.path.join(BASE_DIR, "../../reports")

def run_clustering():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    print("⏳ Running KMeans Clustering & Portfolio Statistics...")
    
    # Load data
    ratios_path = os.path.join(DATA_DIR, "financial_ratios.xlsx")
    comp_path = os.path.join(DATA_DIR, "companies.xlsx")
    
    if not os.path.exists(ratios_path) or not os.path.exists(comp_path):
        print("❌ Error: Required data files missing.")
        return

    df_ratios = pd.read_excel(ratios_path)
    df_comp = pd.read_excel(comp_path)
    
    # Normalize column names
    df_ratios.columns = [str(c).strip().lower().replace(" ", "_") for c in df_ratios.columns]
    df_comp.columns = [str(c).strip().lower().replace(" ", "_") for c in df_comp.columns]

    # Select latest year per company for clustering features
    id_col = next((c for c in df_ratios.columns if c in ['company_id', 'ticker', 'id']), df_ratios.columns[0])
    y_col = next((c for c in df_ratios.columns if c in ['year', 'fy']), None)
    
    if y_col:
        df_latest = df_ratios.sort_values(by=y_col).groupby(id_col).tail(1)
    else:
        df_latest = df_ratios.groupby(id_col).last()

    features = ['return_on_equity_pct', 'debt_to_equity', 'revenue_cagr_5yr', 'fcf_cagr_5yr', 'operating_profit_margin_pct']
    
    # Ensure features exist
    available_features = [f for f in features if f in df_latest.columns]
    if not available_features:
        print("❌ Error: Required feature columns not found in ratios.")
        return

    cluster_df = df_latest[[id_col] + available_features].copy()
    
    # Impute missing values with sector median if sector is available
    if 'sector' in df_comp.columns:
        merged = cluster_df.merge(df_comp[[id_col, 'sector']], on=id_col, how='left')
        for f in available_features:
            cluster_df[f] = merged.groupby('sector')[f].transform(lambda x: x.fillna(x.median()))
    cluster_df = cluster_df.fillna(cluster_df.median(numeric_only=True))

    # Standardize features
    X = cluster_df[available_features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Elbow Plot generation
    inertias = []
    K = range(2, 10)
    for k in K:
        kmeanModel = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeanModel.fit(X_scaled)
        inertias.append(kmeanModel.inertia_)

    plt.figure(figsize=(8, 4))
    plt.plot(K, inertias, 'bx-', marker='o')
    plt.xlabel('Values of k')
    plt.ylabel('Inertia')
    plt.title('The Elbow Method using Inertia (k=5 target)')
    plt.savefig(os.path.join(REPORTS_DIR, "elbow_plot.png"))
    plt.close()

    # Fit KMeans with k=5
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    cluster_df['cluster_id'] = cluster_labels
    
    # Calculate distance from centroid
    distances = kmeans.transform(X_scaled)
    cluster_df['distance_from_centroid'] = [distances[i, label] for i, label in enumerate(cluster_labels)]

    # Map descriptive cluster names
    cluster_names = {
        0: "High-Quality Compounders",
        1: "Defensive Dividend Payers",
        2: "Value Cyclicals",
        3: "Distressed or Turnaround",
        4: "Emerging Growth"
    }
    cluster_df['cluster_name'] = cluster_df['cluster_id'].map(cluster_names)

    # Save cluster labels CSV
    out_csv = os.path.join(OUTPUT_DIR, "cluster_labels.csv")
    cluster_df[[id_col, 'cluster_id', 'cluster_name', 'distance_from_centroid']].to_csv(out_csv, index=False)
    print(f"✅ Saved cluster labels to {out_csv}")

    # Generate Portfolio Stats (P10, P25, P50, P75, P90, Mean, Std)
    numeric_ratios = df_ratios.select_dtypes(include=[np.number])
    stats_rows = []
    for col in numeric_ratios.columns:
        s = numeric_ratios[col].dropna()
        stats_rows.append({
            'metric': col,
            'p10': s.quantile(0.10),
            'p25': s.quantile(0.25),
            'p50': s.quantile(0.50),
            'p75': s.quantile(0.75),
            'p90': s.quantile(0.90),
            'mean': s.mean(),
            'std': s.std()
        })
    pd.DataFrame(stats_rows).to_csv(os.path.join(OUTPUT_DIR, "portfolio_stats.csv"), index=False)
    print("✅ Saved portfolio stats to output/portfolio_stats.csv")

    # Correlation Matrix Heatmap
    plt.figure(figsize=(10, 8))
    corr = numeric_ratios.corr()
    sns.heatmap(corr, annot=False, cmap='coolwarm', fmt=".2f")
    plt.title("KPI Correlation Matrix Heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, "correlation_heatmap.png"))
    plt.close()
    print("✅ Saved correlation heatmap to reports/correlation_heatmap.png")

if __name__ == "__main__":
    run_clustering()
    