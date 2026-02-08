# Deploy to Render (free, indefinite)

This guide deploys the app to **Render** (free tier, indefinite, but data resets on deploy).

---

## What you need

| Thing | Where to get it |
|-------|------------------|
| **GitHub repo** | Your code pushed to GitHub (e.g. `your-username/Tutor-Chatbot`) |
| **Render account** | Sign up at [render.com](https://render.com) (free) |
| **GITHUB_MODEL_KEY** | Your LLM API key (same as in `.env`) |

---

## Step 1: Push your code to GitHub

Make sure your project is on GitHub:

```bash
git add .
git commit -m "Ready for Render deploy"
git push origin main
```

Ensure these files are in the repo:
- `Dockerfile`
- `requirements.txt`
- `api.py`, `qa.py`, `db_setup.py`
- `frontend/` (all files)
- `.env.example` (optional, for reference)

**Do not** push `.env` (keep secrets out of the repo).

---

## Step 2: Create a Render account and connect GitHub

1. Go to [render.com](https://render.com) → **Sign Up** (use GitHub to sign in).
2. Authorize Render to access your GitHub account/repos.

---

## Step 3: Create a new Web Service

1. In Render Dashboard → **New +** → **Web Service**.
2. **Connect** your GitHub repo (e.g. `Tutor-Chatbot`).
3. Render will detect the `Dockerfile` automatically.

---

## Step 4: Configure the service

**Basic Settings:**

- **Name:** e.g. `tutor-chatbot` (or whatever you want).
- **Region:** Pick one close to you (e.g. `Oregon (US West)`).
- **Branch:** `main` (or your default branch).
- **Root Directory:** Leave empty (or `.` if your Dockerfile is in the root).

**Build & Deploy:**

- **Build Command:** Leave empty (Render uses Dockerfile, so it runs `docker build` automatically).
- **Start Command:** Leave empty (Dockerfile has `CMD ["python", "api.py"]`).

**Environment:**

- **Environment Variables:** Click **Add Environment Variable** and add:
  - **Key:** `GITHUB_MODEL_KEY`  
    **Value:** Your actual API key (same as in your local `.env`).
  - **Key:** `PORT`  
    **Value:** `8080` (Render sets this automatically, but setting it explicitly ensures the app listens correctly).

**Advanced:**

- **Auto-Deploy:** **Yes** (so every push to `main` triggers a new deploy).
- **Plan:** **Free** (750 hours/month, spins down after ~15 min idle).

---

## Step 5: Deploy

Click **Create Web Service**. Render will:

1. Clone your repo.
2. Build the Docker image (from your `Dockerfile`).
3. Start the container.
4. Give you a URL (e.g. `https://tutor-chatbot.onrender.com`).

The first build can take **10–20 minutes** (installing PyTorch, sentence-transformers, etc.). You can watch the build logs in Render’s dashboard.

---

## Step 6: Test

1. Open your Render URL (e.g. `https://tutor-chatbot.onrender.com`).
2. If it’s the first request after idle, wait ~30 seconds (cold start).
3. Upload a PDF, run Ingest, then ask a question.

**Note:** Data (PDFs, Chroma DB) is **ephemeral** – it resets on every deploy or restart. So after you push new code, users will need to re-upload and re-ingest.

---

## Important: Render limitations (free tier)

| Limitation | What it means |
|------------|---------------|
| **Ephemeral disk** | Each deploy = fresh filesystem. Uploads and Chroma DB are **lost** on deploy. |
| **Spins down** | After ~15 min idle, the app stops. First request after that is slow (cold start ~30s). |
| **750 hours/month** | Enough for one always-on service if you stay within that. |
| **No persistent storage** | Can’t add a volume to keep data across deploys (paid plans have this). |

So: **free indefinitely**, but **data doesn’t persist** – users re-upload/re-ingest after each deploy.

---

## Auto-deploy from GitHub

Once connected, **every push to `main`** triggers a new deploy:

1. You change code → commit → push.
2. Render detects the push.
3. Render builds a new image (from latest code).
4. Render deploys the new container.
5. Data resets (ephemeral disk).

So you don’t need to manually deploy; just push code and Render handles it.

---

## Troubleshooting

**Build fails:**

- Check build logs in Render Dashboard → **Logs** tab.
- Common issues: missing `requirements.txt`, Dockerfile syntax error, or network timeout during pip install.

**App crashes:**

- Check **Runtime Logs** in Render Dashboard.
- Common causes: missing `GITHUB_MODEL_KEY` env var, wrong port (should be 8080), or import error.

**502 / app not responding:**

- First request after idle can take ~30 seconds (cold start). Wait and refresh.
- Check logs for errors.

**Data missing after deploy:**

- Expected on free tier (ephemeral disk). Users need to re-upload and re-ingest after each deploy.

---

## Summary

- **Push code** → Render builds from Dockerfile → deploys → app is live.
- **Data resets** on every deploy (free tier limitation).
- **Auto-deploy** on every push to `main`.
- **Free indefinitely** (within 750 hours/month).
