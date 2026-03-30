import mlflow
import mlflow.sklearn
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')

# ── MLflow setup ─────────────────────────────────────────────────
mlflow.set_tracking_uri("mlruns")

# ── Disease configs ───────────────────────────────────────────────
DISEASES = {
    'diabetes': {
        'data_path': 'data/diabetes.csv',
        'features': ['hbA1c_level', 'blood_glucose_level', 'age'],
        'target': 'diabetes',
        'model_path': 'models/diabetes_model.pkl',
        'scaler_path': 'models/diabetes_scaler.pkl'
    },
    'ckd': {
        'data_path': 'data/ckd_clean.csv',
        'features': ['age', 'hemo', 'pcv', 'rbcc', 'sc'],
        'target': 'class',
        'model_path': 'models/ckd_model.pkl',
        'scaler_path': 'models/ckd_scaler.pkl'
    },
    'cld': {
        'data_path': 'data/cld.csv',
        'features': ['alkphos', 'sgot', 'sgpt', 'total_bilirubin', 'total_proteins', 'albumin'],
        'target': 'Result',
        'model_path': 'models/cld_model.pkl',
        'scaler_path': 'models/cld_scaler.pkl'
    },
    'heart': {
        'data_path': 'data/heart.csv',
        'features': ['age', 'chol', 'trestbps', 'cp', 'thalachh'],
        'target': 'target',
        'model_path': 'models/heart_model.pkl',
        'scaler_path': 'models/heart_scaler.pkl'
    }
}

# ── Helper: load & prep data ──────────────────────────────────────
def load_data(disease, config):
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
                      'alkphos', 'sgpt', 'sgot', 'total_proteins', 'albumin',
                      'ag_ratio', 'Result']

    X = df[config['features']]
    y = df[config['target']]
    return X, y

# ── Register each model ───────────────────────────────────────────
for disease, config in DISEASES.items():
    print(f"\nRegistering {disease.upper()} model...")

    # Load model + scaler
    model  = joblib.load(config['model_path'])
    scaler = joblib.load(config['scaler_path'])

    # Load data for evaluation
    X, y = load_data(disease, config)
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    X_test_scaled = scaler.transform(X_test)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    f1       = f1_score(y_test, y_pred, average='weighted')
    try:
        roc_auc = roc_auc_score(y_test, y_prob)
    except:
        roc_auc = 0.0

    # MLflow experiment
    mlflow.set_experiment(f"{disease}_diagnosis")

    with mlflow.start_run(run_name=f"{disease}_v1"):
        # Log parameters
        mlflow.log_param("model_type", "RandomForestClassifier")
        mlflow.log_param("features", config['features'])
        mlflow.log_param("n_features", len(config['features']))
        mlflow.log_param("n_estimators", 300)
        mlflow.log_param("max_depth", 15)
        mlflow.log_param("class_weight", "balanced")

        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("roc_auc", roc_auc)

        # Log model
        mlflow.sklearn.log_model(
            model,
            artifact_path=f"{disease}_model",
            registered_model_name=f"{disease}_diagnosis_model"
        )

        # Log scaler as artifact
        joblib.dump(scaler, f"models/{disease}_scaler.pkl")
        mlflow.log_artifact(f"models/{disease}_scaler.pkl")

        print(f"  Accuracy : {accuracy:.4f}")
        print(f"  F1 Score : {f1:.4f}")
        print(f"  ROC-AUC  : {roc_auc:.4f}")
        print(f"  Logged to MLflow experiment: {disease}_diagnosis")

print("\nAll models registered in MLflow! ✅")