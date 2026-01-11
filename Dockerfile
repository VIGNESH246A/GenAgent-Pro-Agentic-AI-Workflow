# GenAgent Pro Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/memory_store data/logs data/uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Expose Streamlit port
EXPOSE 8501

# Default command (can be overridden)
CMD ["python", "main.py"]

# Alternative commands:
# For Streamlit UI: CMD ["streamlit", "run", "app.py"]
# For interactive: CMD ["python", "-i", "main.py"]