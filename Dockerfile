FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install kafka-python explicitly
RUN pip install --no-cache-dir kafka-python==2.0.2

# Copy project files
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Run Flask app
CMD ["python", "main.py"]
