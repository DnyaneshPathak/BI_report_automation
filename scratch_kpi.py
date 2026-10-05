import sys
import os
sys.path.append(os.path.abspath(os.path.join('src', 'bi_automation')))
import pandas as pd
from dashboard.kpi_detector import KPIDetector
from preprocessing.datatype_detector import DataTypeDetector, ColumnProfile

def test():
    df = pd.DataFrame({
        'Sales': [100, 200, 300],
        'Category': ['A', 'B', 'A']
    })
    
    profiles = {
        'Sales': ColumnProfile(name='Sales', analytical_type='continuous', feature_role='Financial Measure', include_in_analysis=True),
        'Category': ColumnProfile(name='Category', analytical_type='categorical_nominal', feature_role='Dimension', include_in_analysis=True)
    }
    
    detector = KPIDetector(df, profiles, col_stats={})
    kpis = detector.detect()
    print("Detected KPIs (default):")
    for k in kpis:
        print(k.title, k.value, k.dax_measure)

    print("\nWith goal: 'generate kpis'")
    detector_nlp = KPIDetector(df, profiles, col_stats={}, goal_description="generate kpis")
    kpis_nlp = detector_nlp.detect()
    for k in kpis_nlp:
        print(k.title, k.value, k.dax_measure)

if __name__ == "__main__":
    test()
