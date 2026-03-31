import optuna
import mlflow
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

mlflow.set_tracking_uri("mlruns")

def tune_disease(disease, X_train, y_train):
    def objective(trial):
        params = {
            'n_estimators':     trial.suggest_int('n_estimators', 100, 500),
            'max_depth':        trial.suggest_int('max_depth', 5, 30),
            'min_samples_split':trial.suggest_int('min_samples_split', 2, 10),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 5),
            'class_weight':     'balanced',
            'random_state':     42
        }
        model = RandomForestClassifier(**params)
        score = cross_val_score(model, X_train, y_train,
                                cv=3, scoring='f1_weighted').mean()
        return score

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=20, show_progress_bar=True)

    print(f"\n{disease.upper()} best params: {study.best_params}")
    print(f"{disease.upper()} best F1: {study.best_value:.4f}")

    # Log to MLflow
    mlflow.set_experiment(f"{disease}_tuning")
    with mlflow.start_run(run_name=f"{disease}_optuna"):
        mlflow.log_params(study.best_params)
        mlflow.log_metric("best_f1", study.best_value)

    return study.best_params

# Run tuning for diabetes as example
print("Loading diabetes data...")
df = pd.read_csv('data/diabetes.csv')
X  = df[['hbA1c_level', 'blood_glucose_level', 'age']]
y  = df['diabetes']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler       = StandardScaler()
X_train_s    = scaler.fit_transform(X_train)
sm           = SMOTE(random_state=42)
X_res, y_res = sm.fit_resample(X_train_s, y_train)

best_params = tune_disease('diabetes', X_res, y_res)
print("\nTuning complete! Best params logged to MLflow ✅")