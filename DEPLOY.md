# Deployment Guide — Medixa AI

Production deployment instructions for the Disease Outbreak Prediction system.

---

## Vercel (Frontend) + Render (Backend)

Deploy the client to Vercel and the server to Render using the **monorepo** approach.

### 1. Push Code to GitHub

```bash
git add .
git commit -m "Add Vercel + Render deployment config"
git push origin main
```

Repository: `https://github.com/udaytikhile/Disease-outbreak-prediction_ai` (or your fork).

---

### 2. Deploy Client → Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub.
2. Click **Add New → Project** and import `Disease-outbreak-prediction_ai`.
3. Configure:
   - **Root Directory:** `client`
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `dist`
4. Add environment variable:
   - `VITE_API_URL` = `https://YOUR-RENDER-APP.onrender.com/api`
   - *(Use your actual Render URL — add this after deploying the backend, then redeploy the frontend.)*
5. Deploy. Your frontend will be at `https://your-project.vercel.app`.

---

### 3. Deploy Server → Render

1. Go to [render.com](https://render.com) and sign in with GitHub.
2. Click **New → Web Service** and connect the same repository.
3. Configure:
   - **Name:** `medixa-api` (or any name)
   - **Region:** Choose closest to your users
   - **Root Directory:** *(leave empty — use repo root)*
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r server/requirements.txt`
   - **Start Command:** `cd server && gunicorn wsgi:app -w 2 -b 0.0.0.0:$PORT --timeout 120`
4. Instance type: Free (or paid for better performance).
5. Click **Create Web Service**. Render will build and deploy. Your API URL will be `https://medixa-api-xxxx.onrender.com`.

**Note:** Ensure `ml/models/` contains `.pkl` files. If missing, run `python ml/scripts/train_all_models.py` locally and commit the model files.

---

### 4. Environment Variables

#### Vercel (client)

| Variable         | Required | Description                                       |
|------------------|----------|---------------------------------------------------|
| `VITE_API_URL`   | Yes      | Full API URL, e.g. `https://medixa-api-xxxx.onrender.com/api` |

#### Render (server)

| Variable         | Required | Description                                       |
|------------------|----------|---------------------------------------------------|
| `SECRET_KEY`     | Yes      | Flask session key. Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `CORS_ORIGINS`   | Yes      | Comma-separated allowed origins. Example: `https://your-project.vercel.app,https://your-project-*.vercel.app` |
| `GEMINI_API_KEY` | No       | For LLM symptom checker. Get at [Google AI Studio](https://makersuite.google.com/app/apikey) |

**CORS note:** Vercel deployments use dynamic URLs. Use:
- `https://your-project.vercel.app`
- Or `https://*.vercel.app` if your Render/CORS setup supports it (some do not — use the exact Vercel URL).

---

### 5. Connect Frontend to Backend

1. After the Render backend is live, copy its URL (e.g. `https://medixa-api-xxxx.onrender.com`).
2. In Vercel: **Project → Settings → Environment Variables**.
3. Set `VITE_API_URL` = `https://medixa-api-xxxx.onrender.com/api` (include `/api`).
4. Redeploy the frontend (Deployments → ⋮ → Redeploy).

The frontend will now call your Render API. Verify via the app’s prediction or symptom checker features.

---

### 6. Optional: Blueprint Deploy

A `render.yaml` blueprint is included. To use it:

1. In Render Dashboard: **New → Blueprint**.
2. Connect the repo. Render will read `render.yaml` and create the web service.
3. Still set `SECRET_KEY`, `CORS_ORIGINS`, and `GEMINI_API_KEY` in the service’s Environment tab.

---

## Quick Deploy (Docker Compose)

### Prerequisites

- Docker & Docker Compose
- `SECRET_KEY` and `JWT_SECRET_KEY` (generate: `python -c "import secrets; print(secrets.token_hex(32))"`)
- Optional: `GEMINI_API_KEY` for symptom checker

### Steps

1. **Set environment variables** — copy and edit:
   ```bash
   cp deploy/.env.example .env
   # Edit .env and set SECRET_KEY, JWT_SECRET_KEY, GEMINI_API_KEY
   ```

2. **Build and run** (from project root):
   ```bash
   docker compose -f deploy/docker-compose.yml up -d --build
   ```

3. **Access the app**:
   - Frontend + API: http://localhost
   - API docs: http://localhost/apidocs

4. **View logs**:
   ```bash
   docker compose -f deploy/docker-compose.yml logs -f
   ```

---

## Architecture (Docker)

| Service | Port | Description |
|---------|------|-------------|
| **web** | 80 | Nginx serving React SPA + proxying `/api` to backend |
| **api** | 5001 | Flask + Gunicorn (internal) |
| **db** | 5432 | PostgreSQL 16 |
| **redis** | 6379 | Rate limiting & cache |

The frontend uses relative `/api` URLs, so everything is served from a single origin (port 80).

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Flask session signing. **Must change in production.** |
| `JWT_SECRET_KEY` | Yes | JWT signing (if auth enabled). **Must change.** |
| `GEMINI_API_KEY` | No | Enables LLM symptom checker. Get at [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `CORS_ORIGINS` | Yes* | Comma-separated allowed origins. Default in compose: `http://localhost,http://localhost:80` |
| `SENTRY_DSN` | No | Error monitoring |

\* When using the default Docker setup (same origin), CORS is less critical. Set for custom domains.

---

## Custom Domain / HTTPS

1. **Reverse proxy** — Put Nginx or Caddy in front, terminate TLS.
2. **Update CORS** — Set `CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com` in docker-compose.
3. **SSL certs** — Use Let's Encrypt (e.g. certbot) or your provider.

Example Nginx upstream:
```nginx
upstream medixa {
  server localhost:80;  # Docker web container
}
server {
  listen 443 ssl;
  server_name yourdomain.com;
  ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
  location / { proxy_pass http://medixa; proxy_set_header Host $host; proxy_set_header X-Forwarded-Proto $scheme; }
}
```

---

## Non-Docker (Manual) Deploy

See [docs/production_checklist.md](docs/production_checklist.md) for Gunicorn, Redis, PostgreSQL, and security setup.

---

## Health Checks

- API: `GET /api/health`
- Frontend: Root `/` (served by Nginx)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `SECRET_KEY` warning | Set `SECRET_KEY` in `.env` before `docker compose up` |
| Models not found | Ensure `ml/models/` has `.pkl` files. Run `python ml/scripts/train_all_models.py` if missing. |
| API 502 | Check `docker compose logs api` — DB/Redis may still be starting. Wait 30s and retry. |
| Symptom checker empty | Set `GEMINI_API_KEY` in `.env` |
