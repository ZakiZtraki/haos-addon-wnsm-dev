# Wiener Netze Smart Meter Add-on

This add-on integrates your Wiener Netze Smart Meter data with Home Assistant via MQTT.

## Configuration

### Required parameters:

| Parameter | Description |
|-----------|-------------|
| WNSM_USERNAME | Your Wiener Netze portal username |
| WNSM_PASSWORD | Your Wiener Netze portal password |
| ZP | Your Zählpunkt (meter point number) |

### MQTT parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| MQTT_HOST | MQTT broker hostname | core-mosquitto |
| MQTT_PORT | MQTT broker port | 1883 |
| MQTT_USERNAME | MQTT username | |
| MQTT_PASSWORD | MQTT password | |
| MQTT_TOPIC | MQTT topic for publishing data | smartmeter/energy/state |

### Other parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| UPDATE_INTERVAL | Data update interval in seconds | 3600 (1 hour) |

## How it works

This add-on logs into your Wiener Netze portal, fetches your smart meter data, and publishes it to your Home Assistant MQTT broker. It automatically creates sensors in Home Assistant through MQTT discovery.

The data is updated according to the specified interval.

## Troubleshooting

If the add-on fails to start:
1. Check your credentials in the configuration
2. Verify that your MQTT broker is accessible
3. Check the add-on logs for detailed error messages