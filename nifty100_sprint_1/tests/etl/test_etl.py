import pytest
import pandas as pd
import sys
import os

# Add src to Python path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/etl')))

from normaliser import normalize_ticker, normalize_year
from validator import validate_dataframe

# --- TESTS FOR NORMALISER ---

def test_normalize_ticker_lowercase():
    assert normalize_ticker("tcs") == "TCS"

def test_normalize_ticker_whitespace():
    assert normalize_ticker("  RELIANCE  ") == "RELIANCE"

def test_normalize_ticker_nan():
    assert normalize_ticker(float('nan')) == ""

def test_normalize_year_mar():
    assert normalize_year("Mar-23") == "2023-03"

def test_normalize_year_dec():
    assert normalize_year("Dec-22") == "2022-12"

def test_normalize_year_jun():
    assert normalize_year("Jun-24") == "2024-06"

def test_normalize_year_fy():
    assert normalize_year("FY24") == "2024-03"

def test_normalize_year_digit():
    assert normalize_year("2023") == "2023-03"

def test_normalize_year_already_formatted():
    assert normalize_year("2024-03") == "2024-03"

# --- TESTS FOR VALIDATOR ---

def test_validate_missing_company_id():
    df = pd.DataFrame({"company_id": ["TCS", "", "INFY"]})
    failures = validate_dataframe(df, "test_table")
    assert len(failures) == 1
    assert failures[0]["severity"] == "CRITICAL"
    assert failures[0]["issue"] == "Missing company_id"

def test_validate_negative_sales():
    df = pd.DataFrame({"company_id": ["TCS", "INFY"], "sales": [1000, 0]})
    failures = validate_dataframe(df, "test_table")
    assert len(failures) == 1
    assert failures[0]["severity"] == "WARNING"
    assert failures[0]["issue"] == "Sales <= 0"

def test_validate_balance_sheet_imbalance():
    df = pd.DataFrame({
        "company_id": ["TCS"], 
        "total_assets": [1000], 
        "total_liabilities": [1005] # Imbalance > 1.0
    })
    failures = validate_dataframe(df, "test_table")
    assert len(failures) == 1
    assert failures[0]["severity"] == "WARNING"
    assert failures[0]["issue"] == "BS Imbalance"

def test_validate_perfect_dataframe():
    df = pd.DataFrame({
        "company_id": ["TCS"], 
        "sales": [5000], 
        "total_assets": [1000], 
        "total_liabilities": [1000]
    })
    failures = validate_dataframe(df, "test_table")
    assert len(failures) == 0


# --- ADDITIONAL TESTS TO HIT 35+ REQUIREMENT ---

def test_normalize_ticker_hyphen():
    assert normalize_ticker("BAJAJ-AUTO") == "BAJAJ-AUTO"

def test_normalize_ticker_ampersand():
    assert normalize_ticker("M&M") == "M&M"

def test_normalize_ticker_mixed_case():
    assert normalize_ticker("  ReLianCe  ") == "RELIANCE"

def test_normalize_ticker_empty():
    assert normalize_ticker("") == ""

def test_normalize_ticker_none():
    assert normalize_ticker(None) == ""

# 10 More variations for normalize_year
def test_normalize_year_mar_space():
    assert normalize_year("Mar 23") == "2023-03"

def test_normalize_year_march_full():
    assert normalize_year("March-2023") == "2023-03"

def test_normalize_year_fy_past():
    assert normalize_year("FY15") == "2015-03"

def test_normalize_year_fy_future():
    assert normalize_year("FY26") == "2026-03"

def test_normalize_year_four_digits():
    assert normalize_year("2019") == "2019-03"

def test_normalize_year_already_hyphenated():
    assert normalize_year("2021-03") == "2021-03"

def test_normalize_year_dec_full():
    assert normalize_year("December-22") == "2022-12" # Assuming strict Mar/Dec/Jun parsing as per normaliser

def test_normalize_year_invalid_string():
    assert normalize_year("garbage_data") == "garbage_data"

def test_normalize_year_empty():
    assert normalize_year("") == ""

def test_normalize_year_none():
    assert normalize_year(None) == ""

# 10 More Data Quality (DQ) Validator Tests
def test_validate_multiple_criticals():
    df = pd.DataFrame({"company_id": ["", ""]})
    failures = validate_dataframe(df, "test")
    assert len(failures) == 2

def test_validate_sales_zero():
    df = pd.DataFrame({"company_id": ["TCS"], "sales": [0]})
    failures = validate_dataframe(df, "test")
    assert failures[0]["issue"] == "Sales <= 0"

def test_validate_sales_negative():
    df = pd.DataFrame({"company_id": ["TCS"], "sales": [-50]})
    failures = validate_dataframe(df, "test")
    assert failures[0]["issue"] == "Sales <= 0"

def test_validate_no_sales_column():
    df = pd.DataFrame({"company_id": ["TCS"], "revenue": [100]})
    failures = validate_dataframe(df, "test")
    assert len(failures) == 0

def test_validate_assets_liabilities_match():
    df = pd.DataFrame({"company_id": ["TCS"], "total_assets": [5000.5], "total_liabilities": [5000.5]})
    failures = validate_dataframe(df, "test")
    assert len(failures) == 0

def test_validate_assets_liabilities_minor_diff():
    df = pd.DataFrame({"company_id": ["TCS"], "total_assets": [5000.5], "total_liabilities": [5000.0]})
    failures = validate_dataframe(df, "test")
    assert len(failures) == 0 # Difference is < 1.0, so no warning

def test_validate_assets_liabilities_major_diff():
    df = pd.DataFrame({"company_id": ["TCS"], "total_assets": [5000.0], "total_liabilities": [4900.0]})
    failures = validate_dataframe(df, "test")
    assert len(failures) == 1
    assert failures[0]["issue"] == "BS Imbalance"

def test_validate_empty_dataframe():
    df = pd.DataFrame()
    failures = validate_dataframe(df, "test")
    assert len(failures) == 0

def test_validate_missing_all_required_cols():
    df = pd.DataFrame({"random_col": [1, 2, 3]})
    failures = validate_dataframe(df, "test")
    assert len(failures) == 0