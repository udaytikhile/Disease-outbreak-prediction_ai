#!/bin/bash

# Activate virtual environment if it exists (optional)
# source venv/bin/activate

# Set environment to production
export FLASK_ENV=production
export FLASK_PORT=5001

# Run Gunicorn
# -w 4: 4 worker processes
# -b 0.0.0.0:5001: Bind to all interfaces on port 5001
# --access-logfile -: Log access to stdout
# --error-logfile -: Log errors to stdout
cd server
exec gunicorn -w 4 -b 0.0.0.0:5001 "app:create_app('production')"
