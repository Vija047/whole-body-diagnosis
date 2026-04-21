"""
Retrain all models and save with Python 3.10 / NumPy 1.x compatible pickle.

Usage (from project root):
    python retrain_models.py

Requirements:
    pip install scikit-learn joblib pandas numpy
"""
import os
import joblib
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import warnings
warnings.filterwarnings('ignore')

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
DATA_DIR   = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(MODELS_DIR, exist_ok=True)

print(f"NumPy version  : {np.__version__}")
print(f"Models dir     : {MODELS_DIR}")
print()

# ─────────────────────────────────────────────
# Helper: save with explicit pickle protocol 4
# (max protocol supported by Python 3.7-3.10)
# ─────────────────────────────────────────────
def save(obj, path):
    joblib.dump(obj, path, protocol=4)
    print(f"  ✅ Saved → {os.path.basename(path)}")


# ─────────────────────────────────────────────
# 1. DIABETES
# ─────────────────────────────────────────────
print("── Training DIABETES model ──────────────────")
df = pd.read_csv(os.path.join(DATA_DIR, "diabetes.csv"))
print(f"   Shape: {df.shape}  | Target col: diabetes")

X = df[['hbA1c_level', 'blood_glucose_level', 'age']].values
y = df['diabetes'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

clf = RandomForestClassifier(n_estimators=100, max_depth=8,
                              class_weight='balanced', random_state=42)
clf.fit(X_train_s, y_train)
print(classification_report(y_test, clf.predict(X_test_s), digits=3))

save(clf,    os.path.join(MODELS_DIR, "diabetes_model.pkl"))
save(scaler, os.path.join(MODELS_DIR, "diabetes_scaler.pkl"))


# ─────────────────────────────────────────────
# 2. CKD
# ─────────────────────────────────────────────
print("\n── Training CKD model ───────────────────────")
df = pd.read_csv(os.path.join(DATA_DIR, "ckd_clean.csv"))
print(f"   Shape: {df.shape}")

# Try multiple possible target column names
target_col = None
for col in ['classification', 'class', 'ckd', 'target']:
    if col in df.columns:
        target_col = col
        break

if target_col is None:
    # Assume last column is target
    target_col = df.columns[-1]

print(f"   Target col: {target_col}")

# Encode target if string
df[target_col] = df[target_col].astype(str).str.strip()
df[target_col] = (df[target_col].isin(['ckd', '1', 'yes', 'positive'])).astype(int)

features = ['age', 'hemo', 'pcv', 'rbcc', 'sc']
available = [f for f in features if f in df.columns]
print(f"   Features used: {available}")

df_clean = df[available + [target_col]].dropna()
X = df_clean[available].values
y = df_clean[target_col].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

clf = RandomForestClassifier(n_estimators=100, max_depth=8,
                              class_weight='balanced', random_state=42)
clf.fit(X_train_s, y_train)
print(classification_report(y_test, clf.predict(X_test_s), digits=3))

save(clf,    os.path.join(MODELS_DIR, "ckd_model.pkl"))
save(scaler, os.path.join(MODELS_DIR, "ckd_scaler.pkl"))


# ─────────────────────────────────────────────
# 3. CLD (Chronic Liver Disease)
# ─────────────────────────────────────────────
print("\n── Training CLD model ───────────────────────")
df = pd.read_csv(os.path.join(DATA_DIR, "cld.csv"))
print(f"   Shape: {df.shape}")

target_col = None
for col in ['Dataset', 'class', 'cld', 'target', 'liver_disease']:
    if col in df.columns:
        target_col = col
        break
if target_col is None:
    target_col = df.columns[-1]

print(f"   Target col: {target_col}")
df[target_col] = (df[target_col].astype(str).str.strip().isin(['1', 'yes', '1.0'])).astype(int)

features = ['alkphos', 'sgot', 'sgpt', 'total_bilirubin', 'total_proteins', 'albumin']
# Also try alternative column names
alternatives = {
    'alkphos': ['Alkphos', 'alk_phosphate', 'Alkaline_Phosphotase'],
    'sgot': ['Sgot', 'AST', 'ast'],
    'sgpt': ['Sgpt', 'ALT', 'alt'],
    'total_bilirubin': ['Total_Bilirubin', 'tot_bilirubin', 'TotalBilirubin'],
    'total_proteins': ['Total_Protiens', 'Total_Proteins', 'tot_proteins'],
    'albumin': ['Albumin', 'Albumin_and_Globulin_Ratio', 'alb']
}

col_map = {}
for feat, alts in alternatives.items():
    if feat in df.columns:
        col_map[feat] = feat
    else:
        for alt in alts:
            if alt in df.columns:
                col_map[feat] = alt
                break

print(f"   Column mapping: {col_map}")
available = list(col_map.keys())
df_renamed = df.rename(columns={v: k for k, v in col_map.items()})
df_clean = df_renamed[available + [target_col]].replace('', np.nan).dropna()
X = df_clean[available].astype(float).values
y = df_clean[target_col].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

clf = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
clf.fit(X_train_s, y_train)
print(classification_report(y_test, clf.predict(X_test_s), digits=3))

save(clf,    os.path.join(MODELS_DIR, "cld_model.pkl"))
save(scaler, os.path.join(MODELS_DIR, "cld_scaler.pkl"))


# ─────────────────────────────────────────────
# 4. HEART
# ─────────────────────────────────────────────
print("\n── Training HEART model ─────────────────────")
df = pd.read_csv(os.path.join(DATA_DIR, "heart.csv"))
print(f"   Shape: {df.shape}")

target_col = None
for col in ['target', 'output', 'heart_disease', 'HeartDiseaseorAttack']:
    if col in df.columns:
        target_col = col
        break
if target_col is None:
    target_col = df.columns[-1]
print(f"   Target col: {target_col}")

features = ['age', 'chol', 'trestbps', 'cp', 'thalachh']
alternatives = {
    'age': ['Age', 'AGE'],
    'chol': ['Chol', 'cholesterol'],
    'trestbps': ['trestbps', 'RestingBP'],
    'cp': ['cp', 'ChestPainType'],
    'thalachh': ['thalach', 'MaxHR', 'thalachh']
}
col_map = {}
for feat, alts in alternatives.items():
    if feat in df.columns:
        col_map[feat] = feat
    else:
        for alt in alts:
            if alt in df.columns:
                col_map[feat] = alt
                break

print(f"   Column mapping: {col_map}")
available = list(col_map.keys())
df_renamed = df.rename(columns={v: k for k, v in col_map.items()})
df_clean = df_renamed[available + [target_col]].dropna()
X = df_clean[available].astype(float).values
y = df_clean[target_col].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

clf = RandomForestClassifier(n_estimators=100, max_depth=8,
                              class_weight='balanced', random_state=42)
clf.fit(X_train_s, y_train)
print(classification_report(y_test, clf.predict(X_test_s), digits=3))

save(clf,    os.path.join(MODELS_DIR, "heart_model.pkl"))
save(scaler, os.path.join(MODELS_DIR, "heart_scaler.pkl"))


print("\n" + "="*50)
print("✅ All 4 models retrained and saved with protocol=4")
print("   Compatible with Python 3.7 – 3.10 and NumPy 1.x/2.x")
print("="*50)
