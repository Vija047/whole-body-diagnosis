import shap
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

import os
os.makedirs('reports/shap', exist_ok=True)

DISEASES = {
    'diabetes': {
        'data_path': 'data/diabetes.csv',
        'features': ['hbA1c_level', 'blood_glucose_level', 'age'],
        'target': 'diabetes'
    },
    'ckd': {
        'data_path': 'data/ckd_clean.csv',
        'features': ['age', 'hemo', 'pcv', 'rbcc', 'sc'],
        'target': 'class'
    },
    'cld': {
        'data_path': 'data/cld.csv',
        'features': ['alkphos', 'sgot', 'sgpt',
                     'total_bilirubin', 'total_proteins', 'albumin'],
        'target': 'Result'
    },
    'heart': {
        'data_path': 'data/heart.csv',
        'features': ['age', 'chol', 'trestbps', 'cp', 'thalachh'],
        'target': 'target'
    }
}

for disease, config in DISEASES.items():
    print(f"\nGenerating SHAP for {disease.upper()}...")

    model  = joblib.load(f'models/{disease}_model.pkl')
    scaler = joblib.load(f'models/{disease}_scaler.pkl')

    df = pd.read_csv(config['data_path'], encoding='latin-1')

    if disease == 'ckd':
        df.replace('?', np.nan, inplace=True)
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip().str.lower()
        df['class'] = df['class'].replace('no', 'notckd')
        df['class'] = LabelEncoder().fit_transform(df['class'])
        for col in config['features']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df[config['features']] = SimpleImputer(
            strategy='mean').fit_transform(df[config['features']])

    elif disease == 'cld':
        df.columns = ['age', 'gender', 'total_bilirubin', 'direct_bilirubin',
                      'alkphos', 'sgpt', 'sgot', 'total_proteins',
                      'albumin', 'ag_ratio', 'Result']

    X = df[config['features']]
    X_scaled = scaler.transform(X)

    # SHAP explainer
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_scaled[:100])

    # Summary plot
    plt.figure()
    shap.summary_plot(
        shap_values[1] if isinstance(shap_values, list) else shap_values,
        X_scaled[:100],
        feature_names=config['features'],
        show=False
    )
    plt.title(f"SHAP Summary — {disease.upper()}")
    plt.tight_layout()
    plt.savefig(f'reports/shap/{disease}_shap.png', dpi=100)
    plt.close()
    print(f"  Saved reports/shap/{disease}_shap.png ✅")

print("\nAll SHAP reports generated!")