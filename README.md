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
