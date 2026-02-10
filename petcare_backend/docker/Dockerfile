FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        fastapi \
        uvicorn[standard] \
        sqlalchemy[asyncio] \
        asyncpg \
        alembic \
        pydantic \
        pydantic-settings \
        redis \
        passlib[bcrypt]

COPY app /app/app
COPY alembic.ini /app/alembic.ini
COPY alembic_petcare /app/alembic_petcare

EXPOSE 8000
