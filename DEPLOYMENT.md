# VeritasAI Single-Site Vercel Deployment Guide

This guide details how **VeritasAI** is configured to run both the **React Frontend SPA** and the **FastAPI Python Backend API** on a **single Vercel domain**.

---

## ⚡ Single-Site Architecture on Vercel

```text
                                 ┌─────────────────────────────────┐
                                 │       Single Vercel Domain      │
                                 │   https://veritas-ai.vercel.app │
                                 └────────────────┬────────────────┘
                                                  │
                         ┌────────────────────────┴────────────────────────┐
                         ▼                                                 ▼
        ┌──────────────────────────────────┐             ┌──────────────────────────────────┐
        │        Vite React SPA            │             │  Serverless Python Function      │
        │        (All / routes)            │             │        (All /api/* routes)       │
        │      frontend/dist/index.html    │             │           api/index.py           │
        └──────────────────────────────────┘             └──────────────────────────────────┘
```

---

## 🛠️ Step-by-Step Vercel Deployment Instructions

### Step 1: Import Project into Vercel
1. Log into your [Vercel Account](https://vercel.com/new).
2. Click **Add New...** → **Project**.
3. Import your GitHub repository: `DEEPAK21072005/Fake-News-Detector`.

### Step 2: Configure Build & Project Settings
1. **Framework Preset**: Select `Other` (or `Vite`).
2. **Root Directory**: Leave blank (`./`).
3. Vercel will automatically read [`vercel.json`](file:///c:/Users/polis/OneDrive/Desktop/Personal/.vscode/FakeNewsDetection_NLP/vercel.json) to handle both the static frontend build and the Python serverless entrypoint `api/index.py`.

### Step 3: Set Environment Variables on Vercel
Add the following Environment Variables under **Project Settings** → **Environment Variables**:

| Variable Name | Recommended Value | Description |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | `gemini` | Enable Google Gemini AI explanations |
| `GEMINI_API_KEY` | `<YOUR_GEMINI_API_KEY>` | Your Gemini 2.5 Flash API Key |
| `APP_ENV` | `production` | Set production environment |
| `DEFAULT_INFERENCE_MODE` | `BALANCED` | Fast, high-accuracy verification mode |

### Step 4: Click Deploy!
Vercel will automatically build the React bundle and deploy the Python serverless backend on a single unified URL (e.g. `https://veritas-ai.vercel.app`).

---

## 🧪 Local Testing

To test the single-site serverless function locally:
```powershell
python -c "import api.index; print('Vercel Serverless Entrypoint Imported Successfully:', api.index.app.title)"
```
Output:
```text
Vercel Serverless Entrypoint Imported Successfully: VeritasAI API
```
