FROM python:3.12-slim AS builder

WORKDIR /app

# Install build deps only here
RUN apt-get update && apt-get install -y build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into a custom directory
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Final image
FROM python:3.12-slim

# Create non-root user
RUN useradd -m appuser

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Copy only installed packages (no build tools)
COPY --from=builder /install /usr/local

# Copy app code
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--bind", "0.0.0.0:8000", "--workers", "2"]
# Why this is better:
    # Gunicorn manages processes
    # Uvicorn handles async requests
    # More stable under real traffic