# Use Python as the base image for easier dependency management
FROM python:3.11-alpine

# Install required system packages for Home Assistant
RUN apk add --no-cache bash jq tzdata ca-certificates git

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY wnsm_sync/ ./wnsm_sync/
COPY run.py ./

# Create directory structure for rootfs
RUN mkdir -p /etc/services.d/wnsm/

# Copy root filesystem
COPY rootfs /

# Make service scripts executable
RUN chmod a+x /etc/services.d/wnsm/*

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run
CMD ["python", "/app/run.py"]

# Labels
LABEL \
    io.hass.name="Wiener Netze Smart Meter" \
    io.hass.description="Integration for Wiener Netze Smart Meter data" \
    io.hass.version="0.1.0" \
    io.hass.type="addon" \
    io.hass.arch="amd64"