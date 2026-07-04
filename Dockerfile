FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml ./
COPY src ./src

RUN pip install --upgrade pip \
    && pip install .

COPY alembic.ini ./
COPY alembic ./alembic

RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "tickethub.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]