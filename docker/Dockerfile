FROM python:3.13-alpine AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

RUN addgroup -g 1000 python \
    && adduser -u 1000 -G python -D python

FROM base AS production

ENV DJANGO_SETTINGS_MODULE=core.settings_production

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

USER python

WORKDIR /app

RUN mkdir ./static

COPY . .

CMD ["python3", "-m", "uvicorn", "core.asgi:application", "--host=0.0.0.0", "--port=8000"]

FROM base AS development

ENV DJANGO_SETTINGS_MODULE=core.settings_development \
    # Use the system Python environment
    UV_PROJECT_ENVIRONMENT="/usr/local/"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --locked

USER python

WORKDIR /app

COPY . .

CMD ["python3", "-m", "uvicorn", "core.asgi:application", "--host=0.0.0.0", "--port=8000", "--reload"]
