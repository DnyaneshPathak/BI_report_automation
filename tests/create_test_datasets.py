"""
tests/create_test_datasets.py
------------------------------
Creates synthetic test Excel datasets A, B, C for validation.
All data is synthetic — no real PII.
"""

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import numpy as np

OUTPUT_DIR = Path(__file__).parent.parent / "temp"
OUTPUT_DIR.mkdir(exist_ok=True)


def dataset_a() -> Path:
    """Sales dataset."""
    rng    = np.random.default_rng(42)
    n      = 2000
    regions    = ["North", "South", "East", "West", "Central"]
    products   = ["Product A", "Product B", "Product C", "Product D", "Product E"]
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Food & Beverage"]
    channels   = ["Online", "Retail", "Wholesale", "Direct"]

    start = date(2022, 1, 1)
    dates = [start + timedelta(days=int(d)) for d in rng.integers(0, 730, n)]

    sales  = rng.normal(5000, 2000, n).clip(100)
    costs  = sales * rng.uniform(0.4, 0.7, n)
    profit = sales - costs
    qty    = rng.integers(1, 200, n)

    df = pd.DataFrame({
        "Order ID"       : [f"ORD-{i:05d}" for i in range(1, n+1)],
        "Order Date"     : dates,
        "Region"         : rng.choice(regions, n),
        "Product"        : rng.choice(products, n),
        "Category"       : rng.choice(categories, n),
        "Channel"        : rng.choice(channels, n),
        "Sales"          : sales.round(2),
        "Cost"           : costs.round(2),
        "Profit"         : profit.round(2),
        "Quantity"       : qty,
        "Customer ID"    : [f"CUST-{rng.integers(1, 500):04d}" for _ in range(n)],
    })
    path = OUTPUT_DIR / "test_sales.xlsx"
    df.to_excel(str(path), index=False, engine="openpyxl")
    print(f"Dataset A created: {path} ({len(df)} rows)")
    return path


def dataset_b() -> Path:
    """Travel booking dataset."""
    rng  = np.random.default_rng(99)
    n    = 1500
    destinations = ["Paris", "London", "New York", "Tokyo", "Dubai", "Sydney", "Bangkok", "Rome"]
    channels     = ["Online", "Travel Agent", "Mobile App", "Corporate"]
    cust_types   = ["Leisure", "Business", "Group", "Family"]
    statuses     = ["Confirmed", "Cancelled", "Pending", "Completed"]
    status_wts   = [0.55, 0.15, 0.08, 0.22]

    start = date(2023, 1, 1)
    booking_dates = [start + timedelta(days=int(d)) for d in rng.integers(0, 500, n)]
    travel_dates  = [bd + timedelta(days=int(d)) for bd, d in zip(booking_dates, rng.integers(14, 180, n))]

    amounts = rng.lognormal(7.5, 0.8, n).round(2)
    # Add some correlation: Business customers pay more
    is_business = rng.choice(range(len(cust_types)), n, p=[0.45, 0.30, 0.15, 0.10])
    amounts = (amounts * (1 + is_business * 0.3)).round(2)

    df = pd.DataFrame({
        "Booking ID"      : [f"BKG-{i:06d}" for i in range(1, n+1)],
        "Booking Date"    : booking_dates,
        "Travel Date"     : travel_dates,
        "Destination"     : rng.choice(destinations, n),
        "Customer Type"   : [cust_types[i] for i in is_business],
        "Channel"         : rng.choice(channels, n),
        "Status"          : rng.choice(statuses, n, p=status_wts),
        "Booking Amount"  : amounts,
        "Nights"          : rng.integers(1, 14, n),
    })
    path = OUTPUT_DIR / "test_bookings.xlsx"
    df.to_excel(str(path), index=False, engine="openpyxl")
    print(f"Dataset B created: {path} ({len(df)} rows)")
    return path


def dataset_c() -> Path:
    """Messy dataset with data quality issues."""
    rng = np.random.default_rng(7)
    n   = 800

    values = rng.normal(1000, 400, n)
    # Inject outliers
    values[rng.integers(0, n, 20)] = rng.uniform(5000, 20000, 20)
    # Numbers stored as strings
    str_values = [str(round(v, 2)) if rng.random() > 0.1 else f"${v:,.2f}" for v in values]

    categories = rng.choice(["A", "B", "C", "D", None, "N/A", "Unknown", ""], n)

    df = pd.DataFrame({
        "ID"        : range(1, n+1),
        "Value"     : str_values,
        "Category"  : categories,
        "Date"      : [f"2023-{rng.integers(1,13):02d}-{rng.integers(1,29):02d}" if rng.random() > 0.05 else None for _ in range(n)],
        "Score"     : [rng.integers(1, 6) if rng.random() > 0.08 else None for _ in range(n)],
        "Flag"      : rng.choice(["Yes", "No", "yes", "NO", None], n),
        "Region"    : rng.choice(["North", "South", "East", "West", None], n),
    })
    # Add exact duplicate rows
    dups = df.sample(50, random_state=42)
    df = pd.concat([df, dups], ignore_index=True)

    path = OUTPUT_DIR / "test_messy.xlsx"
    df.to_excel(str(path), index=False, engine="openpyxl")
    print(f"Dataset C created: {path} ({len(df)} rows, with quality issues)")
    return path


if __name__ == "__main__":
    a = dataset_a()
    b = dataset_b()
    c = dataset_c()
    print("\nAll test datasets created successfully.")
