#!/usr/bin/env python3
"""
Wiener Netze Smart Meter Sync Add-on for Home Assistant
Fetches 15-minute smart meter data and pushes to Home Assistant statistics.
"""
import os
import sys
import json
import logging
import time
from datetime import datetime, timedelta, date
from decimal import Decimal
import paho.mqtt.publish as publish
import requests
from pathlib import Path

# Set log level based on DEBUG environment variable
log_level = logging.DEBUG if os.environ.get("DEBUG", "").lower() in ("true", "1", "yes") else logging.INFO

# Configure logging
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("wnsm_smartmeter")

if log_level == logging.DEBUG:
    logger.debug("Debug logging enabled")

# === CONFIGURATION ===
# Configuration from options.json with fallbacks to environment variables
def load_config():
    """Load configuration from options.json or environment variables."""
    config = {}
    
    # First try to load from options.json (preferred method for Home Assistant addons)
    options_file = "/data/options.json"
    if os.path.exists(options_file):
        try:
            logger.info(f"Loading configuration from {options_file}")
            with open(options_file, 'r') as f:
                options = json.loads(f.read())
                logger.debug(f"Loaded options: {', '.join(options.keys())}")
                
                # Map options.json keys to our config keys
                key_mapping = {
                    "WNSM_USERNAME": "USERNAME",
                    "WNSM_PASSWORD": "PASSWORD",
                    "ZP": "ZP",
                    "MQTT_HOST": "MQTT_HOST",
                    "MQTT_PORT": "MQTT_PORT",
                    "MQTT_USERNAME": "MQTT_USERNAME",
                    "MQTT_PASSWORD": "MQTT_PASSWORD",
                    "MQTT_TOPIC": "MQTT_TOPIC",
                    "UPDATE_INTERVAL": "UPDATE_INTERVAL",
                    "HISTORY_DAYS": "HISTORY_DAYS",
                    "RETRY_COUNT": "RETRY_COUNT",
                    "RETRY_DELAY": "RETRY_DELAY",
                    "HA_URL": "HA_URL",
                    "STAT_ID": "STATISTIC_ID",
                    "DEBUG": "DEBUG"
                }
                
                # Transfer all options to our config using the mapping
                for options_key, config_key in key_mapping.items():
                    if options_key in options and options[options_key] is not None:
                        config[config_key] = options[options_key]
                        logger.debug(f"Using {options_key} from options.json for {config_key}")
                
        except Exception as e:
            logger.error(f"Failed to load options.json: {e}")
    else:
        logger.warning(f"Options file {options_file} not found, falling back to environment variables")
    
    # Debug: Print all environment variables to help diagnose issues
    logger.debug("Environment variables:")
    for key, value in os.environ.items():
        logger.debug(f"  {key}: {value if 'PASSWORD' not in key else '****'}")
    
    # Fall back to environment variables for any missing values
    env_mappings = {
        "USERNAME": ["WNSM_USERNAME", "USERNAME"],
        "PASSWORD": ["WNSM_PASSWORD", "PASSWORD"],
        "ZP": ["WNSM_ZP", "ZP"],
        "USE_EXTERNAL_MQTT": ["USE_EXTERNAL_MQTT"],
        "HA_URL": ["HA_URL"],
        "STATISTIC_ID": ["STAT_ID", "STATISTIC_ID"],
        "MQTT_HOST": ["MQTT_HOST"],
        "MQTT_PORT": ["MQTT_PORT"],
        "MQTT_TOPIC": ["MQTT_TOPIC"],
        "MQTT_USERNAME": ["MQTT_USERNAME"],
        "MQTT_PASSWORD": ["MQTT_PASSWORD"],
        "HISTORY_DAYS": ["HISTORY_DAYS"],
        "RETRY_COUNT": ["RETRY_COUNT"],
        "RETRY_DELAY": ["RETRY_DELAY"],
        "UPDATE_INTERVAL": ["UPDATE_INTERVAL"],
        "SESSION_FILE": ["SESSION_FILE"]
    }
    
    # For each config key, try all possible environment variable names
    for config_key, env_vars in env_mappings.items():
        if config_key not in config or config[config_key] is None:
            for env_var in env_vars:
                if env_var in os.environ and os.environ[env_var]:
                    value = os.environ[env_var]
                    # Convert numeric values
                    if config_key in ["MQTT_PORT", "UPDATE_INTERVAL", "HISTORY_DAYS", "RETRY_COUNT", "RETRY_DELAY"]:
                        try:
                            value = int(value)
                        except ValueError:
                            logger.warning(f"Could not convert {env_var}='{value}' to integer")
                    config[config_key] = value
                    logger.debug(f"Using environment variable {env_var} for {config_key}")
                    break
    
    # Set defaults for optional parameters
    defaults = {
        "HA_URL": "http://homeassistant:8123",
        "STATISTIC_ID": "sensor.wiener_netze_energy",
        "MQTT_HOST": "core-mosquitto",
        "MQTT_PORT": 1883,
        "MQTT_TOPIC": "smartmeter/energy/state",
        "HISTORY_DAYS": 1,
        "RETRY_COUNT": 3,
        "RETRY_DELAY": 5,
        "UPDATE_INTERVAL": 86400,
        "SESSION_FILE": "/data/wnsm_session.json"
    }
    
    for key, default_value in defaults.items():
        if key not in config or config[key] is None:
            config[key] = default_value
            logger.debug(f"Using default value for {key}: {default_value}")
    
    # Debug: Print final config
    logger.debug("Final configuration:")
    for key, value in config.items():
        logger.debug(f"  {key}: {value if 'PASSWORD' not in key else '****'}")
    
    # Ensure we have the critical values
    required_keys = ["USERNAME", "PASSWORD", "ZP"]
    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        logger.error(f"Missing required configuration: {', '.join(missing_keys)}")
        sys.exit(1)
        
    return config

def with_retry(func, config, *args, **kwargs):
    """Execute function with retry logic."""
    for attempt in range(1, config["RETRY_COUNT"] + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt < config["RETRY_COUNT"]:
                delay = config["RETRY_DELAY"] * attempt  # Exponential backoff
                logger.warning(f"Attempt {attempt} failed: {str(e)}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"All {config['RETRY_COUNT']} attempts failed: {str(e)}")
                raise

def save_session(client, config):
    """Save session data for future use."""
    try:
        session_data = client.export_session()
        session_path = Path(config["SESSION_FILE"])
        
        # Ensure directory exists
        session_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(session_path, 'w') as f:
            json.dump(session_data, f)
        logger.info(f"Session saved to {session_path}")
    except Exception as e:
        logger.error(f"Failed to save session: {e}")

def load_session(client, config):
    """Try to load a previous session."""
    try:
        session_path = Path(config["SESSION_FILE"])
        if session_path.exists():
            with open(session_path, 'r') as f:
                session_data = json.load(f)
            client.restore_session(session_data)
            logger.info("Previous session restored")
            return True
    except Exception as e:
        logger.error(f"Failed to load session: {e}")
    return False

def parse_mqtt_host(mqtt_host):
    """Parse MQTT host string to extract protocol, hostname and port."""
    if not mqtt_host:
        return "localhost", 1883
        
    # If it's a URL format (mqtt://host:port)
    if "://" in mqtt_host:
        parts = mqtt_host.split("://")
        # protocol = parts[0]  # mqtt or mqtts
        host_port = parts[1]
        
        if ":" in host_port:
            host, port = host_port.split(":")
            return host, int(port)
        return host_port, 1883
    
    # If it's just a hostname or hostname:port
    if ":" in mqtt_host:
        host, port = mqtt_host.split(":")
        return host, int(port)
    
    return mqtt_host, 1883

# Function moved to a more comprehensive implementation below

def publish_mqtt_discovery(config):
    """Publish MQTT discovery configuration for Home Assistant."""
    try:
        device_id = config["ZP"].lower().replace("0", "")
        discovery_topic = f"homeassistant/sensor/wnsm_sync_{device_id}/config"
        discovery_payload = {
            "name": "Wiener Netze Smartmeter Sync",
            "state_topic": config["MQTT_TOPIC"],
            "unit_of_measurement": "kWh",
            "device_class": "energy",
            "state_class": "total_increasing",
            "unique_id": f"wnsm_sync_energy_sensor_{device_id}",
            "value_template": "{{ value_json.value }}",
            "timestamp_template": "{{ value_json.timestamp }}",
            "device": {
                "identifiers": [f"wnsm_sync_{device_id}"],
                "name": "Wiener Netze Smart Meter",
                "manufacturer": "Wiener Netze",
                "model": "Smart Meter"
            }
        }
        
        publish_mqtt_message(discovery_topic, discovery_payload, config)
        logger.info("MQTT discovery configuration published")
    except Exception as e:
        logger.error(f"Failed to publish MQTT discovery: {e}")


def publish_mqtt_message(topic, payload, config):
    """Publish a message to MQTT with appropriate configuration."""
    try:
        # Always use direct MQTT connection
        import paho.mqtt.publish as publish

        # Extract host and port
        mqtt_host = config.get("MQTT_HOST", "localhost")
        mqtt_port = int(config.get("MQTT_PORT", 1883))

        # Prepare auth if credentials provided
        auth = None
        if config.get("MQTT_USERNAME") or config.get("MQTT_PASSWORD"):
            auth = {
                "username": config.get("MQTT_USERNAME", ""),
                "password": config.get("MQTT_PASSWORD", "")
            }

        publish.single(
            topic=topic,
            payload=json.dumps(payload),
            hostname=mqtt_host,
            port=mqtt_port,
            auth=auth,
            retain=True
        )
        return True
    except Exception as e:

        logger.error(f"Failed to publish to {topic}: {e}", exc_info=True)
        return False

def publish_mqtt_data(statistics, config):
    """Publish energy data to MQTT."""
    if not statistics:
        logger.warning("No statistics to publish")
        return

    # Check if statistics is a dictionary with 'data' key (from bewegungsdaten API)
    if isinstance(statistics, dict) and 'data' in statistics:
        logger.info(f"Converting API response format to statistics format")
        data_points = statistics['data']
        logger.info(f"Processing {len(data_points)} data points from API response")
        
        processed_stats = []
        total = 0
        
        # Convert API format to expected format
        for point in data_points:
            if isinstance(point, dict) and 'timestamp' in point and 'value' in point:
                total += float(point['value'])
                processed_stats.append({
                    "start": point['timestamp'],
                    "sum": total,
                    "state": float(point['value'])
                })
        
        statistics = processed_stats
        logger.info(f"Converted {len(statistics)} data points to expected format")

    logger.info(f"Publishing {len(statistics)} entries to MQTT")

    for s in statistics:
        if not isinstance(s, dict):
            logger.warning(f"Skipping invalid data point (not a dictionary): {s}")
            continue
            
        if 'start' not in s or 'sum' not in s:
            logger.warning(f"Skipping data point with missing fields: {s}")
            continue
            
        topic = f"{config['MQTT_TOPIC']}/{s['start'][:16]}"  # e.g. smartmeter/energy/state/2025-05-16T00:15
        payload = {
            "value": s["sum"],
            "timestamp": s["start"]
        }

        publish_mqtt_message(topic, payload, config)

    # Publish latest value to main topic for current state
    try:
        if statistics:
            latest = statistics[-1]
            publish_mqtt_message(
                config["MQTT_TOPIC"],
                {
                    "value": latest["sum"],
                    "timestamp": latest["start"]
                },
                config
            )
            logger.info("✅ All entries published to MQTT")
        else:
            logger.warning("No valid statistics to publish as latest value")
    except Exception as e:
        logger.error(f"Failed to publish latest value: {e}")

def main():
    """Main function to run the sync process."""
    logger.info("==== Wiener Netze Smart Meter Sync starting ====")
    
    # Load configuration
    config = load_config()
    logger.info(f"Configuration loaded, using username: {config['USERNAME']}")
    
    # Import here to avoid early import errors
    try:
        from api.client import Smartmeter
        from api import constants as const
    except ImportError as e:
        logger.critical(f"Failed to import required modules: {e}")
        sys.exit(1)
    # Initialize Smartmeter client
    client = Smartmeter(config["USERNAME"], config["PASSWORD"])
    
    # Try to restore session first
    session_loaded = load_session(client, config)
    
    # Login if needed
    try:
        if not session_loaded or not client.is_logged_in():
            logger.info("Logging in to Wiener Netze...")
            with_retry(client.login, config)
            save_session(client, config)
        else:
            logger.info("Using existing session")
    except Exception as e:
        logger.error(f"Login failed: {e}")
        sys.exit(1)
    
    # Calculate date range based on configuration
    end_date = date.today() - timedelta(days=1)  # Yesterday
    start_date = end_date - timedelta(days=config["HISTORY_DAYS"] - 1)
    
    logger.info(f"Fetching data from {start_date} to {end_date}")
    
    # Fetch bewegungsdaten with retry
    try:
        bewegungsdaten = with_retry(
            client.bewegungsdaten,
            config,
            zaehlpunktnummer=config["ZP"],
            date_from=start_date,
            date_until=end_date,
            aggregat="NONE"
        )
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        sys.exit(1)
    
    # Process the data
    total = Decimal(0)
    statistics = []
    
    logger.info(f"Processing {len(bewegungsdaten.get('values', []))} data points")
    
    for entry in bewegungsdaten.get("values", []):
        try:
            ts = datetime.fromisoformat(entry["zeitpunktVon"].replace("Z", "+00:00"))
            value_kwh = Decimal(str(entry["wert"]))
            total += value_kwh
            statistics.append({
                "start": ts.isoformat(),
                "sum": float(total),
                "state": float(value_kwh)
            })
        except (KeyError, ValueError) as e:
            logger.warning(f"Error processing entry {entry}: {e}")
    
    # Publish MQTT discovery for Home Assistant integration
    publish_mqtt_discovery(config)
    
    # Publish data to MQTT
    publish_mqtt_data(statistics, config)
    
    logger.info("==== Wiener Netze Smart Meter Sync completed ====")

def fetch_bewegungsdaten(config):
    """
    Fetch energy consumption data from Wiener Netze API.
    
    Args:
        config (dict): Configuration dictionary with credentials and settings
        
    Returns:
        list: List of statistics dictionaries containing energy data
    """
    # Import your client here to avoid circular imports
    from wnsm_sync.api.client import Smartmeter
    
    try:
        # Initialize the client
        client = Smartmeter(
            username=config.get("WNSM_USERNAME", config.get("USERNAME")),
            password=config.get("WNSM_PASSWORD", config.get("PASSWORD"))
        )
        
        # Login to the service
        logger.info("Logging in to Wiener Netze service")
        client.login()
        
        # Fetch the data
        zp = config.get("ZP")
        days = int(config.get("HISTORY_DAYS", 1))
        
        # Fetch data from API
        from datetime import date, timedelta
        date_until = date.today()
        date_from = date_until - timedelta(days=days)
        logger.info(f"Fetching data from {date_from} to {date_until}")
        statistics = client.bewegungsdaten(zp, date_from=date_from, date_until=date_until)
        
        return statistics
    except Exception as e:
        logger.error(f"Error fetching Bewegungsdaten: {e}")
        return []

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

