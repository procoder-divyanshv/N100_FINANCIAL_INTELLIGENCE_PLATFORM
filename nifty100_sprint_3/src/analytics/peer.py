import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "data/nifty100.db")

def get_peer_data(conn):
    query = """
    SELECT 
        f.*, p.peer_group_name, p.is_benchmark
    FROM financial_ratios f
    JOIN peer_groups p ON f.company_id = p.company_id
    WHERE f.year = (SELECT MAX(year) FROM financial_ratios)
    """
    return pd.read_sql(query, conn)

def compute_percentiles(df):
    metrics = [
        'return_on_equity_pct', 'net_profit_margin_pct', 'debt_to_equity', 
        'free_cash_flow_cr', 'revenue_cagr_5yr', 'pat_cagr_5yr', 
        'eps_cagr_5yr', 'interest_coverage', 'asset_turnover'
    ]
    
    percentile_records = []
    
    for group, group_df in df.groupby('peer_group_name'):
        for metric in metrics:
            if metric in group_df.columns:
                ranks = group_df[metric].rank(pct=True)
                if metric == 'debt_to_equity':
                    ranks = 1 - ranks
                    
                for _, row in group_df.iterrows():
                    percentile_records.append({
                        'company_id': row['company_id'],
                        'peer_group_name': group,
                        'metric': metric,
                        'value': row[metric],
                        'percentile_rank': ranks.loc[row.name],
                        'year': row['year']
                    })
                    
    return pd.DataFrame(percentile_records)

def generate_radar_charts(percentile_df):
    metrics = ['return_on_equity_pct', 'net_profit_margin_pct', 'debt_to_equity', 
               'free_cash_flow_cr', 'revenue_cagr_5yr', 'pat_cagr_5yr']
               
    for group, group_df in percentile_df.groupby('peer_group_name'):
        group_avg = group_df.groupby('metric')['percentile_rank'].mean()
        
        for company in group_df['company_id'].unique():
            company_data = group_df[group_df['company_id'] == company].set_index('metric')['percentile_rank']
            
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            angles += angles[:1]
            
            comp_values = [company_data.get(m, 0) for m in metrics]
            comp_values += comp_values[:1]
            
            avg_values = [group_avg.get(m, 0) for m in metrics]
            avg_values += avg_values[:1]
            
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            ax.fill(angles, comp_values, color='blue', alpha=0.25)
            ax.plot(angles, comp_values, color='blue', linewidth=2, label=company)
            ax.plot(angles, avg_values, color='red', linestyle='dashed', linewidth=2, label='Peer Avg')
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics, size=8)
            plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
            
            plt.savefig(f"reports/radar_charts/{company}_radar.png", bbox_inches='tight')
            plt.close()

def generate_peer_report(df, percentile_df):
    with pd.ExcelWriter("output/peer_comparison.xlsx", engine="openpyxl") as writer:
        for group in df['peer_group_name'].unique():
            group_data = df[df['peer_group_name'] == group]
            group_data.to_excel(writer, sheet_name=group[:31], index=False)

def run_peer_engine():
    with sqlite3.connect(DB_PATH) as conn:
        df = get_peer_data(conn)
        
    percentiles = compute_percentiles(df)
    
    with sqlite3.connect(DB_PATH) as conn:
        percentiles.to_sql('peer_percentiles', conn, if_exists='replace', index=False)
        
    generate_radar_charts(percentiles)
    generate_peer_report(df, percentiles)
    
    print("Peer Engine Complete. Radar charts and peer_comparison.xlsx generated.")

if __name__ == "__main__":
    run_peer_engine()