#!/usr/bin/env python3
"""Entry point for the Wiener Netze Smart Meter Home Assistant Add-on."""
import os
import sys
import logging
import time

# Set log level based on DEBUG environment variable
log_level = logging.DEBUG if os.environ.get("DEBUG", "").lower() in ("true", "1", "yes") else logging.INFO

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("wnsm-addon")

if log_level == logging.DEBUG:
    logger.debug("Debug logging enabled")

try:
    from wnsm_sync.sync_bewegungsdaten_to_ha import (
        fetch_bewegungsdaten,
        publish_mqtt_discovery,
        publish_mqtt_data
    )
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def load_config_from_env():
    """Load configuration from environment variables set by Home Assistant."""
    # Debug: Print all environment variables to help diagnose issues
    logger.debug("Environment variables:")
    for key, value in os.environ.items():
        logger.debug(f"  {key}: {value if 'PASSWORD' not in key else '****'}")
    
    config = {
        "WNSM_USERNAME": os.environ.get("WNSM_USERNAME"),
        "WNSM_PASSWORD": os.environ.get("WNSM_PASSWORD"),
        "ZP": os.environ.get("ZP"),
        "MQTT_HOST": os.environ.get("MQTT_HOST"),
        "MQTT_PORT": int(os.environ.get("MQTT_PORT", 1883)),
        "MQTT_USERNAME": os.environ.get("MQTT_USERNAME"),
        "MQTT_PASSWORD": os.environ.get("MQTT_PASSWORD"),
        "MQTT_TOPIC": os.environ.get("MQTT_TOPIC"),
        "UPDATE_INTERVAL": int(os.environ.get("UPDATE_INTERVAL", 3600))
    }
    
    # Debug: Print loaded config
    logger.debug("Loaded configuration:")
    for key, value in config.items():
        logger.debug(f"  {key}: {value if 'PASSWORD' not in key else '****'}")
    
    return config

def main():
    try:
        config = load_config_from_env()

        required_fields = ["WNSM_USERNAME", "WNSM_PASSWORD", "ZP", "MQTT_HOST"]
        missing_fields = [field for field in required_fields if not config.get(field)]

        if missing_fields:
            logger.error(f"Missing required configuration: {', '.join(missing_fields)}")
            sys.exit(1)

        logger.info("Wiener Netze Smart Meter Add-on started")

        while True:
            logger.info("Publishing MQTT discovery configuration")
            publish_mqtt_discovery(config)

            logger.info("Fetching Bewegungsdaten from Wiener Netze")
            statistics = fetch_bewegungsdaten(config)

            if statistics:
                logger.info(f"Fetched {len(statistics)} data points")
                publish_mqtt_data(statistics, config)
            else:
                logger.warning("No data fetched from Wiener Netze")

            logger.info(f"Sleeping for {config['UPDATE_INTERVAL']} seconds")
            time.sleep(config["UPDATE_INTERVAL"])

    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()