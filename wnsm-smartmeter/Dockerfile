ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.15
FROM ${BUILD_FROM}

# Install required packages
RUN apk add --no-cache python3 py3-pip

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY wnsm_sync/ ./wnsm_sync/
COPY run.py ./

# Copy root filesystem
COPY rootfs /

# Make service scripts executable
RUN chmod a+x /etc/services.d/wnsm/*

CMD [ "/usr/bin/with-contenv", "bashio" ]

# Labels
LABEL \
    io.hass.name="Wiener Netze Smart Meter" \
    io.hass.description="Integration for Wiener Netze Smart Meter data" \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="addon" \
    io.hass.arch="${BUILD_ARCH}"