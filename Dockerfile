# ==============================================================================
# Dockerfile — Sales AI Lead Intelligence Platform (Backend, Celery & ETL)
# ==============================================================================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY backend/ ./backend/
COPY etl/ ./etl/
COPY alembic.ini ./
COPY run.py ./

# Expose FastAPI backend port
EXPOSE 8000

# Default command: Launch FastAPI server
CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "8000"]
