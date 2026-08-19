import numpy as np
import pandas as pd

def classify_capital_allocation(row):
    cfo = row.get('operating_activity', 0)
    cfi = row.get('investing_activity', 0)
    cff = row.get('financing_activity', 0)
    cfo_pat_ratio = row.get('cfo_quality_score', 0)
    
    cfo_sign = np.sign(cfo) if pd.notna(cfo) else 0
    cfi_sign = np.sign(cfi) if pd.notna(cfi) else 0
    cff_sign = np.sign(cff) if pd.notna(cff) else 0

    if cfo_sign > 0 and cfi_sign < 0 and cff_sign < 0:
        if pd.notna(cfo_pat_ratio) and cfo_pat_ratio > 1.0:
            return "Shareholder Returns"
        return "Reinvestor"
    elif cfo_sign > 0 and cfi_sign > 0 and cff_sign < 0:
        return "Liquidating Assets"
    elif cfo_sign < 0 and cfi_sign > 0 and cff_sign > 0:
        return "Distress Signal"
    elif cfo_sign < 0 and cfi_sign < 0 and cff_sign > 0:
        return "Growth Funded by Debt"
    elif cfo_sign > 0 and cfi_sign > 0 and cff_sign > 0:
        return "Cash Accumulator"
    elif cfo_sign < 0 and cfi_sign < 0 and cff_sign < 0:
        return "Pre-Revenue"
    return "Mixed"