import pandas as pd
import numpy as np
import joblib
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently.metrics import DatasetDriftMetric
import json
import subprocess
import warnings
warnings.filterwarnings('ignore')

THRESHOLD = 0.3  # retrain if drift score > 30%

DISEASES = {
    'diabetes': {
        'data_path': 'data/diabetes.csv',
        'features': ['hbA1c_level', 'blood_glucose_level', 'age']
    },
    'ckd': {
        'data_path': 'data/ckd_clean.csv',
        'features': ['age', 'hemo', 'pcv', 'rbcc', 'sc']
    },
    'cld': {
        'data_path': 'data/cld.csv',
        'features': ['alkphos', 'sgot', 'sgpt',
                     'total_bilirubin', 'total_proteins', 'albumin']
    },
    'heart': {
        'data_path': 'data/heart.csv',
        'features': ['age', 'chol', 'trestbps', 'cp', 'thalachh']
    }
}

for disease, config in DISEASES.items():
    print(f"\nChecking drift for {disease.upper()}...")

    df = pd.read_csv(config['data_path'], encoding='latin-1')

    if disease == 'cld':
        df.columns = ['age', 'gender', 'total_bilirubin', 'direct_bilirubin',
                      'alkphos', 'sgpt', 'sgot', 'total_proteins',
                      'albumin', 'ag_ratio', 'Result']

    X = df[config['features']].dropna()
    ref     = X.iloc[:int(len(X) * 0.7)]
    current = X.iloc[int(len(X) * 0.7):]

    report = Report(metrics=[DatasetDriftMetric()])
    report.run(reference_data=ref, current_data=current)

    result      = report.as_dict()
    drift_score = result['metrics'][0]['result']['share_of_drifted_columns']

    print(f"  Drift score: {drift_score:.2f}")

    if drift_score > THRESHOLD:
        print(f"  DRIFT DETECTED! Triggering retrain for {disease}...")
        import sys
        subprocess.run([sys.executable, 'src/training/register_models.py'])
    else:
        print(f"  No significant drift. Model is stable.")