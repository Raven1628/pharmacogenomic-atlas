FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for pandas and numpy
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create data directory if needed
RUN mkdir -p data/processed

# Expose the port
EXPOSE 8050

# Run the application
CMD ["gunicorn", "09_web_atlas:server", "--bind", "0.0.0.0:8050"]
