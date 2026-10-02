"""
tests/conftest.py
Shared pytest fixtures.
ALL test data is generated synthetically here — no real files are ever read.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure src/ is importable
_src = Path(__file__).resolve().parents[1] / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

# Also ensure project root is importable (for legacy imports)
_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


@pytest.fixture(scope="session")
def synthetic_sales_df() -> pd.DataFrame:
    """2,000-row sales dataset (seeded, reproducible)."""
    rng = np.random.default_rng(42)
    n = 2000
    return pd.DataFrame({
        "OrderID":    [f"ORD-{i:05d}" for i in range(n)],
        "Date":       pd.date_range("2022-01-01", periods=n, freq="6h"),
        "Product":    rng.choice(["Widget A", "Widget B", "Gadget", "Tool"], n),
        "Region":     rng.choice(["North", "South", "East", "West"], n),
        "Quantity":   rng.integers(1, 50, n),
        "UnitPrice":  rng.uniform(10.0, 500.0, n).round(2),
        "Revenue":    rng.uniform(100.0, 25000.0, n).round(2),
        "Cost":       rng.uniform(50.0, 12000.0, n).round(2),
        "Discount":   rng.uniform(0.0, 0.3, n).round(3),
        "CustomerAge": rng.integers(18, 75, n),
    })


@pytest.fixture(scope="session")
def synthetic_churn_df() -> pd.DataFrame:
    """
    1,500-row churn-like dataset (seeded).
    Contains: binary target in 2 encodings, outcome-only column,
    near-perfect leak column, ID, constant, lat/long, strong driver,
    numeric driver, noise, text-typed numeric with blanks.
    """
    rng = np.random.default_rng(99)
    n = 1500

    # Strong driver: Contract (Month-to-month churns ~42%, Two-year ~3%)
    contract = rng.choice(["Month-to-month", "One year", "Two year"],
                          n, p=[0.55, 0.25, 0.20])
    churn_prob = np.where(contract == "Month-to-month", 0.42,
                 np.where(contract == "One year",       0.12, 0.03))
    churn_bool = rng.random(n) < churn_prob

    # Numeric driver: Tenure (churners have shorter tenure)
    tenure = np.where(churn_bool,
                      rng.integers(1, 24, n),
                      rng.integers(6, 72, n))

    # Noise column (no real signal)
    noise = rng.normal(0, 1, n).round(4)

    # Text-typed numeric with 11 blanks
    charges_raw = rng.uniform(20.0, 120.0, n).round(2).astype(str)
    blank_idx = rng.choice(n, 11, replace=False)
    charges_raw[blank_idx] = ""

    # Outcome-only column (blank for non-churners)
    churn_reason = np.where(churn_bool,
                            rng.choice(["Price", "Service", "Moved"], n),
                            "")

    return pd.DataFrame({
        "CustomerID":      [f"C{i:06d}" for i in range(n)],     # ID
        "Churn":           churn_bool.astype(int),              # target (0/1)
        "ChurnLabel":      np.where(churn_bool, "Yes", "No"),   # twin
        "ChurnScore":      np.where(churn_bool,
                                    rng.uniform(0.7, 1.0, n),
                                    rng.uniform(0.0, 0.3, n)).round(3),  # leak
        "ChurnReason":     churn_reason,                        # outcome-only
        "Contract":        contract,                            # strong driver
        "Tenure":          tenure,                              # numeric driver
        "MonthlyCharges":  charges_raw,                         # text-typed numeric
        "Country":         ["USA"] * n,                         # constant
        "Latitude":        rng.uniform(25.0, 49.0, n).round(4), # coordinate
        "Longitude":       rng.uniform(-125.0, -66.0, n).round(4),
        "Noise":           noise,
    })


@pytest.fixture(scope="session")
def synthetic_messy_df() -> pd.DataFrame:
    """850-row messy dataset with missing values, duplicates, mixed types."""
    rng = np.random.default_rng(7)
    n = 850
    df = pd.DataFrame({
        "Name":     [f"Customer {i}" for i in range(n)],
        "Score":    np.where(rng.random(n) < 0.1, np.nan, rng.uniform(0, 100, n)),
        "Category": rng.choice(["A", "B", "C", None], n, p=[0.4, 0.3, 0.2, 0.1]),
        "Value":    rng.integers(0, 1000, n).astype(float),
        "Date":     pd.date_range("2023-01-01", periods=n, freq="8h"),
    })
    # Add 50 duplicate rows
    dupes = df.sample(50, random_state=7)
    return pd.concat([df, dupes], ignore_index=True)
