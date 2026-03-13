# Production Deployment Checklist

A step-by-step guide to deploying the Disease Outbreak Prediction app safely.

---

## 1. Disable Debug Mode

**Never** run `debug=True` in production — it exposes the Werkzeug debugger.

```bash
# Set environment variable
export FLASK_ENV=production
```

The app reads `FLASK_ENV` in `server/app.py` and selects `ProductionConfig`,
which sets `DEBUG = False` automatically.

---

## 2. Bind to 127.0.0.1, Not 0.0.0.0

Flask's `host='0.0.0.0'` exposes the app to all network interfaces.
In production, bind to localhost and let **Nginx** (or another reverse proxy)
handle external traffic:

```
Client → Nginx (:443) → Gunicorn (127.0.0.1:5001)
```

---

## 3. Use Gunicorn as the WSGI Server

Flask's built-in `app.run()` server is single-threaded and not production-grade.

```bash
# Install (already in requirements.txt)
pip install gunicorn

# Start with 4 workers, binding to localhost only
gunicorn \
  --workers 4 \
  --bind 127.0.0.1:5001 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  app:app
```

**Worker count rule of thumb**: `(2 × CPU cores) + 1`

For the existing Docker setup, set this in `deploy/Dockerfile.server`'s CMD.

---

## 4. Set SECRET_KEY

The app's `ProductionConfig` warns if `SECRET_KEY` is the insecure default.

```bash
# Generate a strong key
python -c "import secrets; print(secrets.token_hex(32))"

# Set it
export SECRET_KEY="<paste-generated-key>"
```

---

## 5. Configure Redis for Rate Limiting

The default in-memory limiter **does not share state** across Gunicorn workers,
meaning each worker tracks limits independently — effectively multiplying
the allowed rate by the number of workers.

```bash
# Install Redis
sudo apt install redis-server   # or use Docker
redis-server --daemonize yes

# Point Flask-Limiter to Redis
export RATELIMIT_STORAGE_URI="redis://localhost:6379/0"
```

The app reads this env var in `server/src/extensions.py` automatically.

---

## 6. Pin Python Dependencies

All ML packages must match the versions used to train the `.pkl` models.
The `server/requirements.txt` is already pinned. On a new machine:

```bash
cd server
pip install -r requirements.txt
python -c "import sklearn; print(sklearn.__version__)"  # expect 1.5.2
```

---

## 7. Retrain Models on the Deployment Machine

If you get `ModuleNotFoundError: No module named 'numpy._core'` or sklearn
version warnings, the `.pkl` files were pickled under different library versions.

```bash
# Retrain just the kidney model (fast — small dataset)
python ml/scripts/retrain_kidney_model.py

# Retrain ALL models (slow — includes Optuna tuning)
python ml/scripts/train_all_models.py
```

---

## 8. Set CORS Origins

```bash
export CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

---

## 9. Use HTTPS

Terminate TLS at Nginx. Sample config is in `deploy/nginx.conf`.

```nginx
server {
    listen 443 ssl;
    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location /api/ {
        proxy_pass http://127.0.0.1:5001;
    }
}
```

---

## Quick-Start (All Commands)

```bash
# 1. Install deps
cd server && pip install -r requirements.txt

# 2. Retrain models (if needed)
cd .. && python ml/scripts/retrain_kidney_model.py

# 3. Set production env vars
export FLASK_ENV=production
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export RATELIMIT_STORAGE_URI=redis://localhost:6379/0
export CORS_ORIGINS=https://yourdomain.com

# 4. Start with Gunicorn
cd server
gunicorn --workers 4 --bind 127.0.0.1:5001 --timeout 120 app:app
```
