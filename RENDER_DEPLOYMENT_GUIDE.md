# Deploying Dead Time B2B to Render

This guide covers deploying the **FastAPI Backend** and **Next.js Frontend** to [Render](https://render.com).

---

## 🚀 Quick Overview

You will deploy 2 services on Render from your GitHub repository:
1. **`deadtime-backend`** (Python Web Service) → Ingests browser telemetry, detects patterns, generates blueprints & PDFs.
2. **`deadtime-frontend`** (Node.js Web Service) → The Executive Intelligence Dashboard.

---

## Step 1: Push Your Code to GitHub

If you haven't already initialized git and pushed to GitHub:

```bash
git init
git add .
git commit -m "Dead Time production ready"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dead-time-b2b.git
git push -u origin main
```

---

## Step 2: Deploy the Backend (FastAPI)

1. Log in to [dashboard.render.com](https://dashboard.render.com/).
2. Click **New +** → **Web Service**.
3. Select **Build and deploy from a Git repository** and pick your `dead-time-b2b` repo.
4. Fill in the service configuration:

| Setting | Value |
|---|---|
| **Name** | `deadtime-backend` |
| **Region** | Choose the one closest to you (e.g. Frankfurt, Singapore, Oregon) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && playwright install chromium --with-deps` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | Free (or Starter $7/mo for 0 sleep time) |

5. Scroll down to **Environment Variables** and add:
   - `GEMINI_API_KEY`: *(Your Google Gemini API Key from Google AI Studio)*
   - `PYTHON_VERSION`: `3.11.8`

*(Optional Persistent Database)*: If you want persistent telemetry data, click **New +** → **PostgreSQL** on Render (free tier), and copy the Internal Database URL into an environment variable named `DATABASE_URL` in your backend service. If not provided, it will default to SQLite automatically.

6. Click **Create Web Service**.
7. Render will build and deploy. Once live, you will get a URL like:
   `https://deadtime-backend.onrender.com`
8. Verify it works by opening:
   `https://deadtime-backend.onrender.com/health` (should return `{"status":"healthy","version":"4.0.0"}`)

---

## Step 3: Deploy the Frontend (Next.js Dashboard)

1. In Render Dashboard, click **New +** → **Web Service**.
2. Select the same Git repository.
3. Fill in the service configuration:

| Setting | Value |
|---|---|
| **Name** | `deadtime-frontend` |
| **Root Directory** | `frontend` |
| **Runtime** | `Node` |
| **Build Command** | `npm install && npm run build` |
| **Start Command** | `npm start` |
| **Instance Type** | Free |

4. Scroll down to **Environment Variables** and add:
   - `NEXT_PUBLIC_API_URL`: `https://deadtime-backend.onrender.com` *(use your actual backend URL from Step 2)*

5. Click **Create Web Service**.
6. Once deployed, open your frontend URL (e.g. `https://deadtime-frontend.onrender.com`). You will see your dashboard live on the internet!

---

## Step 4: Point the Chrome Extension to your Live Render URL

Now that your backend is on the cloud, update your Chrome extension so it streams telemetry to Render instead of `localhost`:

1. Open `extension/background.js`.
2. Update line 4:
   ```javascript
   const API_URL = "https://deadtime-backend.onrender.com/events";
   ```
3. Open `extension/popup.js`.
4. Update lines 41 and 58:
   ```javascript
   // Health check:
   fetch('https://deadtime-backend.onrender.com/health')
   ...
   // Open Dashboard button:
   chrome.tabs.create({ url: 'https://deadtime-frontend.onrender.com' });
   ```
5. Reload the extension in `chrome://extensions` (click the refresh icon on the Dead Time tile).

---

## 💡 Pro-Tip for Fast Free Pilots
Render's free tier spins down after 15 minutes of inactivity. When a client visits or sends an event, the first request takes ~30 seconds to wake up.
- For active client audits, either:
  1. Upgrade the backend to the $7/mo Starter plan (no sleep).
  2. Or set up a free uptime monitor (like [UptimeRobot.com](https://uptimerobot.com) or [Cron-Job.org](https://cron-job.org)) that pings `https://deadtime-backend.onrender.com/health` every 10 minutes to keep it awake 24/7!
