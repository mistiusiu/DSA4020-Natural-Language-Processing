# syntax=docker/dockerfile:1


# ============================================================
# BASE
# ============================================================

FROM python:3.14-slim AS base


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app/backend



# ============================================================
# BUILDER
# ============================================================

FROM base AS builder


ENV POETRY_VERSION=2.3.4 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true


ENV PATH="$POETRY_HOME/bin:$PATH"



RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        libpq-dev \
        python3-dev



RUN curl -sSL https://install.python-poetry.org \
    | python3 - --version $POETRY_VERSION



COPY pyproject.toml poetry.lock* ./



# ============================================================
# PROD DEPENDENCIES
# ============================================================

FROM builder AS prod-deps


RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install \
    --without dev,test \
    --no-root



# ============================================================
# DEVELOPMENT
# ============================================================

FROM builder AS dev-deps


RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install \
    --no-root



FROM dev-deps AS development


ENV PATH="/app/backend/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/backend/.venv"


COPY . .


RUN mkdir -p \
    logs \
    media \
    staticfiles \
    models



COPY entrypoint.sh /entrypoint.sh


RUN sed -i 's/\r$//' /entrypoint.sh \
    && chmod +x /entrypoint.sh



EXPOSE 8000


ENTRYPOINT ["/entrypoint.sh"]


CMD [
    "gunicorn",
    "config.wsgi:application",
    "--bind",
    "0.0.0.0:8000",
    "--workers",
    "1",
    "--threads",
    "4",
    "--timeout",
    "300"
]



# ============================================================
# PRODUCTION
# ============================================================

FROM base AS production


COPY --from=prod-deps \
    /app/backend/.venv \
    /app/backend/.venv



ENV PATH="/app/backend/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/backend/.venv"



COPY . .


RUN mkdir -p \
    logs \
    media \
    staticfiles \
    models



COPY entrypoint.sh /entrypoint.sh


RUN sed -i 's/\r$//' /entrypoint.sh \
    && chmod +x /entrypoint.sh



EXPOSE 8000


ENTRYPOINT ["/entrypoint.sh"]


CMD [
    "gunicorn",
    "config.wsgi:application",
    "--bind",
    "0.0.0.0:8000",
    "--workers",
    "1",
    "--threads",
    "4",
    "--timeout",
    "300"
]
