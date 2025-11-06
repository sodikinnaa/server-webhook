# Gunakan Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy file project ke container
COPY . .

# Install dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Expose port Flask
EXPOSE 5003

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=api/index.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5003 \
    FLASK_ENV=development \
    FLASK_DEBUG=1

# Jalankan Flask (gunakan auto-reload)
CMD ["flask", "run", "--reload"]
