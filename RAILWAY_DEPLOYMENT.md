# 🚂 Railway Deployment Guide (Full Stack ML Ops)

This guide explains how to deploy the **Whole Body Diagnosis System** to Railway.

## 🚀 Step 1: Deploy Backend & Database

1.  Go to [Railway.app](https://railway.app) and log in.
2.  Click **New Project** -> **GitHub Repo** -> Select your repository.
3.  Railway will automatically detect the `Dockerfile` at the root.
4.  **Add PostgreSQL**:
    - Click **+ Add** -> **Database** -> **Add PostgreSQL**.
    - Railway will automatically inject the `DATABASE_URL` into your backend service.
5.  **Configure Environment Variables** (Backend):
    - Go to your Backend Service -> **Variables**.
    - Ensure `ALLOWED_ORIGINS` is set to `*` or your frontend URL.
    - Set `API_KEY` to your chosen production key.

## 🎨 Step 2: Deploy Frontend

1.  In your Railway project, click **New** -> **GitHub Repo** -> Select the **same repository**.
2.  **Crucial**: Go to this service's **Settings** -> **Root Directory** and set it to `/frontend`.
3.  Railway will use the `frontend/railway.json` to build and serve the app.
4.  **Configure Environment Variables** (Frontend):
    - Set `VITE_API_BASE_URL` to your Backend's **Static URL** (found in Backend -> Settings -> Networking).
    - Set `VITE_API_KEY` to the same key used in the backend.

## 🧪 Validation

Once both are live:
1. Check the Frontend. The "Connection" status in the navbar should be **Green/Online**.
2. Run a test assessment!

## 🛡️ Advantages over Render
- **No Sleep**: Railway doesn't spin down your free services like Render (if you use credits).
- **Service Mesh**: Easier communication between backend and database.
- **Unified Billing**: Simpler management.
