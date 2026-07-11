FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py runner.py ./
COPY data/ ./data/
COPY models/ ./models/
COPY routers/ ./routers/
COPY fxti/ ./fxti/
COPY static/ ./static/
COPY test_results/ ./test_results/
COPY README.md ./

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
