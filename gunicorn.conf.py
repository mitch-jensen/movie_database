import os

DJANGO_SETTINGS_MODULE = os.getenv("DJANGO_SETTINGS_MODULE")

bind = "0.0.0.0:8000"
worker_class = "uvicorn.workers.UvicornWorker"
workers = 4
reload = DJANGO_SETTINGS_MODULE == "core.settings_development"
