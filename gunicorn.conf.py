import os

# Gunicorn configuration for the news-getter Telegram bot.
#
# Quart is an ASGI framework, so gunicorn must use the Uvicorn worker
# class to serve the app (plain WSGI workers will not work).

worker_class = "uvicorn.workers.UvicornWorker"

# Host/port to bind on, overridable via the BIND_ADDR env var.
bind = os.environ.get("BIND_ADDR", "0.0.0.0:8000")

# Number of worker processes, overridable via WEB_CONCURRENCY env var.
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))

# Time in seconds to wait for a request to complete before killing the worker.
timeout = 30

# Time in seconds to wait for a graceful shutdown.
graceful_timeout = 30
