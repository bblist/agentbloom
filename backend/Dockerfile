FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files (production)
# RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Use daphne ASGI server for HTTP + WebSocket support
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "agentbloom.asgi:application"]
