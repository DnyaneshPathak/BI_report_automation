import sys
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path("src").resolve()))

from bi_automation.dashboard.kpi_detector import KPIDetector
from bi_automation.preprocessing.datatype_detector import DataTypeDetector

df = pd.DataFrame({
    "Gender": ["Male", "Female", "Male"],
    "Monthly Charges": [10.5, 20.0, 15.5],
    "Tenure Months": [10, 20, 15],
})

detector = DataTypeDetector(df)
profiles = detector.detect_all()

goal = "kpi cards for monthly charges"
kpi_det = KPIDetector(df, profiles, {}, goal_description=goal)
kpis = kpi_det.detect()
for k in kpis:
    print(k.title, k.value, k.formatted_value)
