# gunicorn.conf.py
import multiprocessing

# Bind to the port Render provides
bind = "0.0.0.0:10000"

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
preload_app = True