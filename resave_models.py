import joblib
import warnings
warnings.filterwarnings('ignore')

models_path = 'models/'
diseases = ['diabetes', 'ckd', 'cld', 'heart']

for d in diseases:
    # Load old model
    model  = joblib.load(f'{models_path}{d}_model.pkl')
    scaler = joblib.load(f'{models_path}{d}_scaler.pkl')

    # Resave with current sklearn version
    joblib.dump(model,  f'{models_path}{d}_model.pkl')
    joblib.dump(scaler, f'{models_path}{d}_scaler.pkl')
    print(f"{d} resaved ✅")

print("All models resaved with current sklearn version!")