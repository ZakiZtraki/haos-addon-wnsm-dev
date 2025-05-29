# Wiener Netze Smartmeter Sync Add-on for Home Assistant

This Home Assistant add-on fetches 15-minute interval consumption data from the Wiener Netze Smart Meter portal and injects it into Home Assistant's long-term statistics.

## Features
- Authenticates with Wiener Netze login
- Retrieves Bewegungsdaten (quarter-hourly history)
- Automatically pushes to HA statistics via REST API
- Integrates with Energy Dashboard and cost sensors
- Can be scheduled to run daily at 04:00 via automation

## Add-ons

### Wiener Netze Smart Meter Integration

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FZakiZtraki%2Fhaos-addon-wnsm-dev)

This add-on synchronizes your Wiener Netze Smart Meter data to Home Assistant via MQTT.

## Installation

1. Click the button above to add this repository to your Home Assistant instance.
2. Navigate to the Add-on Store.
3. Find the "Wiener Netze Smart Meter" add-on and click it.
4. Click "Install".

## Configuration

The add-on requires the following configuration:

```yaml
WNSM_USERNAME: your_wiener_netze_username
WNSM_PASSWORD: your_wiener_netze_password
ZP: your_zaehlpunkt_number  # e.g., AT0010000000000000001000004392265
MQTT_HOST: core-mosquitto  # or your MQTT broker address
MQTT_PORT: 1883
MQTT_USERNAME: your_mqtt_username  # if required
MQTT_PASSWORD: your_mqtt_password  # if required
MQTT_TOPIC: smartmeter/energy/state
UPDATE_INTERVAL: 3600  # in seconds (default: 1 hour)
USE_MOCK_DATA: false  # set to true for testing without real API access
```

### Mock Data Mode

If you're testing the add-on or don't have access to the Wiener Netze API, you can enable mock data mode:

1. Set `USE_MOCK_DATA: true` in your configuration
2. The add-on will generate simulated data instead of making real API calls
3. This is useful for development, testing, or demonstration purposes

When mock data mode is enabled, you'll see a warning in the logs indicating that simulated data is being used.

## Troubleshooting

If you encounter issues with the API connection:

1. Check your credentials (username, password, and Zählpunkt number)
2. Verify that your Wiener Netze account has access to the Smart Meter portal
3. Try enabling mock data mode temporarily to verify that the rest of the integration works
4. Check the add-on logs for detailed error messages

## API Authentication

The add-on supports two authentication methods:

1. API Key authentication (default)
2. OAuth authentication (fallback)

The add-on will automatically use the appropriate method based on the API response.
