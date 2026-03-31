import pandas as pd
import numpy as np
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import os
import warnings
warnings.filterwarnings('ignore')

os.makedirs('reports/drift', exist_ok=True)

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
    print(f"\nRunning drift detection for {disease.upper()}...")

    df = pd.read_csv(config['data_path'], encoding='latin-1')

    if disease == 'ckd':
        df.replace('?', np.nan, inplace=True)
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip().str.lower()
        for col in config['features']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df[config['features']] = SimpleImputer(
            strategy='mean').fit_transform(df[config['features']])

    elif disease == 'cld':
        df.columns = ['age', 'gender', 'total_bilirubin', 'direct_bilirubin',
                      'alkphos', 'sgpt', 'sgot', 'total_proteins',
                      'albumin', 'ag_ratio', 'Result']

    X = df[config['features']].dropna()

    # Split into reference and current
    ref     = X.iloc[:int(len(X) * 0.7)]
    current = X.iloc[int(len(X) * 0.7):]

    # Evidently drift report
    report = Report(metrics=[DataDriftPreset(), DataQualityPreset()])
    report.run(reference_data=ref, current_data=current)
    report.save_html(f'reports/drift/{disease}_drift.html')
    print(f"  Saved reports/drift/{disease}_drift.html ✅")

print("\nAll drift reports generated!")