import pandas as pd
import numpy as np

def calculate_cagr(start_val, end_val, periods):
    if pd.isna(start_val) or pd.isna(end_val) or periods <= 0:
        return None, "INSUFFICIENT"
    
    if start_val == 0:
        return None, "ZERO_BASE"
        
    if start_val > 0 and end_val > 0:
        cagr = (((end_val / start_val) ** (1 / periods)) - 1) * 100
        return round(cagr, 2), None
        
    if start_val > 0 and end_val < 0:
        return None, "DECLINE_TO_LOSS"
        
    if start_val < 0 and end_val > 0:
        return None, "TURNAROUND"
        
    if start_val < 0 and end_val < 0:
        return None, "BOTH_NEGATIVE"
        
    return None, "UNKNOWN"

def apply_cagr_window(group_df, metric_col, periods):
    group_df = group_df.sort_values('year')
    start_val = group_df[metric_col].shift(periods)
    end_val = group_df[metric_col]
    
    results = []
    flags = []
    
    for s, e in zip(start_val, end_val):
        val, flag = calculate_cagr(s, e, periods)
        results.append(val)
        flags.append(flag)
        
    return results, flags