import pandas as pd

def normalize_ticker(ticker: str) -> str:
    if pd.isna(ticker):
        return ""
    return str(ticker).strip().upper()

def normalize_year(year_val) -> str:
    if pd.isna(year_val):
        return ""
    year_str = str(year_val).strip()
    
    year_str = year_str.replace(" ", "-")
    
    year_str = year_str.replace("March", "Mar").replace("December", "Dec").replace("June", "Jun")
    
    if year_str.startswith("Mar-") or year_str.startswith("Dec-") or year_str.startswith("Jun-"):
        parts = year_str.split("-")
        if len(parts) == 2:
            month_map = {"Mar": "03", "Dec": "12", "Jun": "06"}
            month = month_map.get(parts[0], "03")
            # If year is 2 digits (23), add "20". If it's 4 digits (2023), leave it.
            year = "20" + parts[1] if len(parts[1]) == 2 else parts[1]
            return f"{year}-{month}"
    
    if year_str.startswith("FY"):
        return f"20{year_str[2:]}-03"
        
    
    if year_str.isdigit():
        return f"{year_str}-03"
        
    return year_str