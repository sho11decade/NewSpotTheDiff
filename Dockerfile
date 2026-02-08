# Dockerfile for Hugging Face Spaces
# Optimized for 16GB RAM environment with 1.3GB FastSAM model

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and Japanese fonts
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /tmp/spotdiff/uploads /tmp/spotdiff/outputs /tmp/spotdiff/models

# Set environment variables for production
ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1 \
    YOLO_CONFIG_DIR=/tmp/.config/Ultralytics \
    TORCH_HOME=/tmp/.cache/torch

# Download FastSAM model during build (no timeout limit)
RUN python scripts/download_model.py || echo "Model will be downloaded on first request"

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/', timeout=5)"

# Start application with gunicorn
# Using port 7860 for Hugging Face Spaces compatibility
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "--timeout", "300", "--max-requests", "200", "run:app"]
