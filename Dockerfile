FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings_production

EXPOSE 8000

RUN addgroup -g 1000 python \
    && adduser -u 1000 -G python -D python

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

USER python

WORKDIR /app

RUN mkdir ./static

COPY . .

CMD ["python3", "-m", "uvicorn", "core.asgi:application", "--host=0.0.0.0", "--port=8000"]
