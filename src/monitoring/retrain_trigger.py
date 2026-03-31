import pandas as pd
import numpy as np
import joblib
import sys
import subprocess
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently.metrics import DatasetDriftMetric
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

def check_and_trigger_retraining():
    """Check drift for all diseases and trigger retraining if needed."""
    
    retrained_models = []
    
    for disease, config in DISEASES.items():
        print(f"\nChecking drift for {disease.upper()}...")

        try:
            df = pd.read_csv(config['data_path'], encoding='latin-1')

            if disease == 'cld':
                df.columns = ['age', 'gender', 'total_bilirubin', 'direct_bilirubin',
                              'alkphos', 'sgpt', 'sgot', 'total_proteins',
                              'albumin', 'ag_ratio', 'Result']

            X = df[config['features']].dropna()
            if len(X) == 0:
                print(f"  ⚠️  No valid data for {disease}")
                continue
                
            ref     = X.iloc[:int(len(X) * 0.7)]
            current = X.iloc[int(len(X) * 0.7):]

            report = Report(metrics=[DatasetDriftMetric()])
            report.run(reference_data=ref, current_data=current)

            result      = report.as_dict()
            drift_score = result['metrics'][0]['result']['share_of_drifted_columns']

            print(f"  Drift score: {drift_score:.2%}")

            if drift_score > THRESHOLD:
                print(f"  🔴 DRIFT DETECTED! Drift ({drift_score:.2%}) > Threshold ({THRESHOLD:.2%})")
                print(f"  Triggering retrain for {disease}...")
                
                # Trigger retraining
                result = subprocess.run(
                    [sys.executable, 'src/training/register_models.py', disease],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print(f"  ✅ Retraining completed for {disease}")
                    retrained_models.append(disease)
                else:
                    print(f"  ❌ Retraining failed for {disease}")
                    print(f"  Error: {result.stderr}")
            else:
                print(f"  ✅ No significant drift. Model is stable.")
                
        except Exception as e:
            print(f"  ❌ Error processing {disease}: {str(e)}")
    
    return retrained_models


if __name__ == "__main__":
    retrained = check_and_trigger_retraining()
    if retrained:
        print(f"\n✅ Successfully retrained models: {', '.join(retrained)}")
    else:
        print(f"\n✅ All models are stable. No retraining needed.")