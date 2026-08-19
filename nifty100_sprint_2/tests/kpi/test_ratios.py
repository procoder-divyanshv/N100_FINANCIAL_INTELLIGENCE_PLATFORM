import sys
import os
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/analytics')))

from cagr import calculate_cagr

def test_cagr_normal():
    val, flag = calculate_cagr(100, 150, 5)
    assert val == 8.45
    assert flag is None

def test_cagr_insufficient():
    val, flag = calculate_cagr(100, 150, 0)
    assert val is None
    assert flag == "INSUFFICIENT"

def test_cagr_zero_base():
    val, flag = calculate_cagr(0, 150, 5)
    assert val is None
    assert flag == "ZERO_BASE"

def test_cagr_decline_to_loss():
    val, flag = calculate_cagr(100, -50, 5)
    assert val is None
    assert flag == "DECLINE_TO_LOSS"

def test_cagr_turnaround():
    val, flag = calculate_cagr(-50, 100, 5)
    assert val is None
    assert flag == "TURNAROUND"

def test_cagr_both_negative():
    val, flag = calculate_cagr(-50, -100, 5)
    assert val is None
    assert flag == "BOTH_NEGATIVE"