# gunicorn.conf.py
import multiprocessing

# Bind to the port Render provides
bind = "0.0.0.0:10000"

# Reduce worker count for free tier (default is too high)
workers = 2
worker_class = "sync"

# Timeout settings
timeout = 120
graceful_timeout = 30
keepalive = 5

# Memory limits
max_requests = 100
max_requests_jitter = 10

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Worker class options
threads = 2
worker_connections = 1000