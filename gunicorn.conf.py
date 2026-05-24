# gunicorn.conf.py
import multiprocessing
import os

# Bind to the port Render provides (use $PORT when available)
port = os.environ.get('PORT', '10000')
bind = f"0.0.0.0:{port}"

# Reduce worker count for free tier
workers = 1
threads = 2
worker_class = "gthread"

# Timeout settings
timeout = 60
graceful_timeout = 30
keepalive = 5

# Memory limits
max_requests = 50
max_requests_jitter = 10

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Preload app to save memory
# Don't preload app to avoid import-time side effects (DB connections)
preload_app = False