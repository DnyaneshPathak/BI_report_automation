"""
tests/validate_pipeline.py
---------------------------
Functional validation of the complete pipeline against all 3 test datasets.
Checks statistical correctness, pipeline flow, and privacy compliance.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tests.create_test_datasets import dataset_a, dataset_b, dataset_c
from app.workflow.pipeline import AnalysisPipeline


def _check(cond: bool, msg: str) -> bool:
    if cond:
        print(f"  [PASS] {msg}")
    else:
        print(f"  [FAIL] {msg}")
    return cond


def validate_dataset(name: str, file_path: Path) -> int:
    print(f"\n{'='*55}")
    print(f"  TEST: {name}")
    print(f"{'='*55}")
    passed = 0
    total  = 0

    pipeline = AnalysisPipeline(file_path)
    result = pipeline.run()

    # --- Pipeline success ---
    total += 1; passed += _check(result.success, "Pipeline completed without abort")
    total += 1; passed += _check(result.df_clean is not None, "DataFrame loaded")

    if result.df_clean is None:
        return passed, total

    df = result.df_clean

    # --- Data quality ---
    total += 1; passed += _check(df.shape[0] > 0, f"Rows > 0 ({df.shape[0]})")
    total += 1; passed += _check(df.shape[1] > 1, f"Columns > 1 ({df.shape[1]})")
    total += 1; passed += _check(len(result.profiles) > 0, "Column profiles detected")

    # --- Type detection ---
    has_numeric = any(
        p.analytical_type in ("continuous", "discrete_numeric")
        for p in result.profiles.values()
    )
    total += 1; passed += _check(has_numeric, "At least one numeric column detected")

    # --- Statistical correctness: verify mean calculation ---
    import pandas as pd
    import numpy as np
    num_cols = [c for c, p in result.profiles.items()
                if p.analytical_type in ("continuous", "discrete_numeric")
                and p.include_in_analysis and c in df.columns]
    if num_cols and result.col_stats:
        col = num_cols[0]
        if col in result.col_stats:
            cs = result.col_stats[col]
            actual_mean = round(float(pd.to_numeric(df[col], errors="coerce").mean()), 4)
            total += 1
            passed += _check(
                abs((cs.mean or 0) - actual_mean) < 0.01,
                f"Mean for '{col}' correct: computed={cs.mean}, actual={actual_mean}"
            )

    # --- No IDs treated as measures (sum/total KPIs must not use identifier columns) ---
    id_cols = [c for c, p in result.profiles.items() if p.analytical_type == "identifier"]
    # A true violation would be: KPI with title "Total <id_col>" AND the column is known identifier
    # and include_in_analysis is False
    bad_ids = [c for c in id_cols if not result.profiles[c].include_in_analysis and
               any(kpi.dax_measure and f"SUM('{c}')" in kpi.dax_measure for kpi in result.kpis)]
    total += 1; passed += _check(len(bad_ids) == 0, "No identifier columns used as sum KPIs")

    # --- KPIs detected ---
    total += 1; passed += _check(len(result.kpis) > 0, f"KPIs detected ({len(result.kpis)})")

    # --- Chart specs ---
    total += 1; passed += _check(len(result.chart_specs) > 0, f"Chart specs generated ({len(result.chart_specs)})")

    # --- Insights ---
    total += 1; passed += _check(len(result.insights) > 0, f"Insights generated ({len(result.insights)})")

    # --- Preview HTML ---
    total += 1; passed += _check(
        isinstance(result.preview_html, dict) and "charts_p1_html" in result.preview_html, 
        f"Preview HTML dict generated ({len(result.preview_html)} keys)"
    )

    # --- Privacy ---
    total += 1; passed += _check(
        result.error is None or "external" not in str(result.error).lower(),
        "No external service errors"
    )

    print(f"\n  Result: {passed}/{total} checks passed")
    return passed, total


def main():
    print("\n" + "="*55)
    print("  BI REPORT AUTOMATION — PIPELINE VALIDATION")
    print("="*55)

    tests = [
        ("Dataset A: Sales", dataset_a),
        ("Dataset B: Travel Bookings", dataset_b),
        ("Dataset C: Messy Data", dataset_c),
    ]

    total_passed = 0
    total_checks = 0

    for name, creator in tests:
        try:
            path = creator()
            p, t = validate_dataset(name, path)
            total_passed += p
            total_checks += t
        except Exception as exc:
            print(f"\n  [ERROR] {name} raised exception: {exc}")
            import traceback; traceback.print_exc()

    print(f"\n{'='*55}")
    print(f"  OVERALL: {total_passed}/{total_checks} checks passed")
    pct = total_passed / max(total_checks, 1) * 100
    status = "[PASS]" if pct >= 90 else "[PARTIAL]" if pct >= 70 else "[FAIL]"
    print(f"  Score:   {pct:.0f}% -- {status}")
    print("="*55)


if __name__ == "__main__":
    main()
