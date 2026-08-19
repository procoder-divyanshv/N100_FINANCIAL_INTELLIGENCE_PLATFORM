import pandas as pd
from typing import List, Dict

def validate_dataframe(df: pd.DataFrame, table_name: str) -> List[Dict]:
    failures = []
    
    if "company_id" in df.columns:
        null_ids = df[df["company_id"] == ""]
        for idx in null_ids.index:
            failures.append({"table": table_name, "row": idx, "issue": "Missing company_id", "severity": "CRITICAL"})

    if "sales" in df.columns:
        invalid_sales = df[df["sales"] <= 0]
        for idx in invalid_sales.index:
            failures.append({"table": table_name, "row": idx, "issue": "Sales <= 0", "severity": "WARNING"})

    if "total_assets" in df.columns and "total_liabilities" in df.columns:
        imbalance = df[abs(df["total_assets"] - df["total_liabilities"]) > 1.0]
        for idx in imbalance.index:
            failures.append({"table": table_name, "row": idx, "issue": "BS Imbalance", "severity": "WARNING"})

    return failures