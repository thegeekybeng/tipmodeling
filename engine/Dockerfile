# --- 1. BASE IMAGE ---
FROM python:3.11-slim

# --- 2. SYSTEM DEPENDENCIES ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# --- 3. WORK DIRECTORY ---
WORKDIR /app

# --- 4. PYTHON DEPENDENCIES ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- 5. APPLICATION ASSETS ---
COPY . .

# Create data directory for SQLite
RUN mkdir -p data

# --- 6. EXECUTION ---
EXPOSE 8000
CMD npx prisma db push && python3 -u main.py
