# 🚀 Render Deployment Guide (Production MLOps)

This guide explains how to deploy the **Whole Body Diagnosis System** to Render with a full CI/CD/CT pipeline.

## 📋 Prerequisites

1.  A [Render](https://render.com) account.
2.  A [GitHub](https://github.com) repository with your code.
3.  Models in the `models/` directory (already included in your repo).

## 🛠️ Step 1: Deploy with Blueprint (Recommended)

The easiest way to deploy is using the `render.yaml` blueprint I created.

1.  Log in to the [Render Dashboard](https://dashboard.render.com).
2.  Click **New +** and select **Blueprint**.
3.  Connect your GitHub repository.
4.  Render will automatically detect `render.yaml` and show you the services to be created:
    - **whole-body-diagnosis-api** (Web Service)
    - **mlops-db** (PostgreSQL Database)
5.  Click **Apply**.

Render will:
- Spin up a PostgreSQL database.
- Build your Docker image.
- Run `python scripts/seed_db.py` to initialize the database metadata.
- Start the FastAPI server on port 8000.

## 🧪 Step 2: Setup CI/CD/CT on GitHub

I have created a GitHub Action workflow in `.github/workflows/mlops.yml` that handles the 3 layers of ML deployment:

### 1. CI (Continuous Integration)
Automatically runs every time you push code.
- Installs dependencies.
- Runs `pytest` to ensure the API and models are working correctly.

### 2. CD (Continuous Deployment)
- Automatically triggers a Render deploy when tests pass on the `main` branch.
- **Action Required**: 
  - Go to your Render Web Service -> **Settings** -> **Deploy Hook**.
  - Copy the Hook URL.
  - Go to your GitHub Repo -> **Settings** -> **Secrets and variables** -> **Actions**.
  - Create a new secret named `RENDER_DEPLOY_HOOK_URL` and paste the URL.

### 3. CT (Continuous Training)
- Runs weekly (Sunday) or can be triggered manually in the "Actions" tab.
- Runs `src/training/register_models.py` to retrain models if new data is available.
- Checks for model drift using `src/monitoring/drift_monitor.py`.

## 🛡️ Step 3: Security & API Keys

- Render will automatically generate a random `API_KEY` for you (check the **Environment** tab in Render).
- Use this key in the `x-api-key` header for all requests.

## 🔍 Validation

Once deployed, you can verify the deployment:

1.  **Health Check**: `https://your-app-name.onrender.com/health`
2.  **Interactive Docs**: `https://your-app-name.onrender.com/api/docs`
3.  **Test Prediction**:
    ```bash
    curl -X POST https://your-app-name.onrender.com/predict/diabetes \
      -H "x-api-key: YOUR_GENERATED_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"hbA1c_level": 7.5, "blood_glucose_level": 150, "age": 45}'
    ```

## 🔄 Updating Models

If you retrain models locally and want to deploy them:
1. Update weights in `models/*.pkl`.
2. Commit and push to GitHub.
3. CI/CD will trigger, run tests, and deploy to Render.

---
**Status**: Render-Ready ✅
**Pipeline**: CI/CD/CT Enabled 🚀
