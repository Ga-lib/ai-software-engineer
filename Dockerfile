# ---- Base image ----
FROM python:3.12-slim

# Prevents Python from writing .pyc files and buffers stdout/stderr immediately,
# which makes container logs show up in real time instead of being buffered.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Working directory inside the container
WORKDIR /app

# Install system dependencies needed to build some Python packages (e.g. psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (separate layer so Docker caches this step
# and only re-installs packages when requirements.txt actually changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Render (and most platforms) inject the port to listen on via $PORT
ENV PORT=8000
EXPOSE 8000

# Run database migrations, then start the server
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}