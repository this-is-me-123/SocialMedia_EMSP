# Production Dockerfile for Social Media Backend
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# --- Build frontend (React+Vite) ---
# Install node and npm
# Install curl if not present
RUN apt-get update && apt-get install -y curl
# Install Node.js (NodeSource 18.x)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*
# Copy frontend source
COPY frontend-modern /frontend-modern
WORKDIR /frontend-modern
RUN npm install && npm run build
WORKDIR /app
# Optionally clean up node/npm to reduce image size
RUN apt-get purge -y nodejs npm && apt-get autoremove -y && rm -rf /frontend-modern /var/lib/apt/lists/*

# Copy all backend code (automation_stack, content_creation, etc) after frontend build and cleanup
COPY backend/ /app/
# Copy wait-for-it script
COPY wait-for-it.sh /app/wait-for-it.sh
# Copy built frontend static files
COPY frontend-modern/dist /app/static

# Expose port
EXPOSE 8000

CMD ["/bin/sh", "-c", "until nc -z db 5432; do echo 'Waiting for Postgres...'; sleep 2; done; python -m automation_stack.auto_migrate && uvicorn automation_stack.main:app --host 0.0.0.0 --port 8000"]

# Entrypoint (use uvicorn with multiple workers)
