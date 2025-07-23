import uuid
from pathlib import Path

from .settings import *  # noqa: F403

DEBUG = False

DATABASES: dict[str, dict[str, str | Path]] = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    },
}

SECRET_KEY = uuid.uuid4()
