# Wiener Netze Smartmeter – Home Assistant Custom Component

A Home Assistant custom component (HACS-compatible) for integrating
[Wiener Netze Smart Meter](https://www.wienernetze.at/smartmeter) data,
including full support for the **Energy Dashboard cost calculation**.

Forked and extended from [DarwinsBuddy/WienerNetzeSmartmeter](https://github.com/DarwinsBuddy/WienerNetzeSmartmeter).

---

## What's different from the upstream

### Cost calculation support

The upstream integration imports historical consumption data using
`async_add_external_statistics` (HA source = `"wnsm"`). External statistics
are visible in the Energy Dashboard timeline but **cannot be linked to a
tariff/price entity** for cost calculation.

This fork switches to `async_import_statistics` with `source="homeassistant"`
and a `statistic_id` that matches the sensor entity. This means:

- The sensor appears as a normal HA entity with `device_class: energy` and
  `state_class: total_increasing`.
- Full 3-year historical backfill is stored as **entity-owned statistics**.
- The Energy Dashboard can select the sensor as a grid consumption source
  **and** calculate costs via any configured tariff/price entity.
- The running `sum` is initialised from the actual meter reading at the start
  of the import window, so there is no discontinuity between historical stats
  and the real-time sensor value.

### Other fixes

| Issue | Fix |
|---|---|
| `__init__.py` and `sensor.py` imported `DOMAIN` from `homeassistant.core` (= `"homeassistant"`) instead of `const.py` (= `"wnsm"`) | Corrected import |
| Meter-reading loop always overwrote the value with the older reading | Loop now breaks on first valid reading |
| `StatisticData.state` was set to the hourly delta, not the cumulative value | Now uses cumulative total, consistent with `total_increasing` semantics |

---

## Installation

### HACS (recommended)

1. Add this repository as a custom HACS repository (type: *Integration*).
2. Install **Wiener Netze Smart Meter** from HACS.
3. Restart Home Assistant.

### Manual

Copy `custom_components/wnsm` into `<config>/custom_components/`.

---

## Configuration

After installation, go to **Settings → Devices & Services → Add Integration**
and search for **Wiener Netze Smartmeter**.

Enter your Wiener Netze portal credentials (the same ones you use on
[smartmeter-web.wienernetze.at](https://smartmeter-web.wienernetze.at)).

All active Zählpunkte in your account are automatically created as sensors.

### Manual (configuration.yaml)

```yaml
sensor:
  - platform: wnsm
    username: !secret wnsm_username
    password: !secret wnsm_password
    device_id: "AT0010000000000000001000004392265"
```

---

## Energy Dashboard setup

1. Go to **Settings → Dashboards → Energy**.
2. Under **Grid consumption**, click **Add consumption**.
3. Select the **Wiener Netze** sensor (named after your Zählpunkt number).
4. Optionally configure a static price or link a tariff entity for cost
   calculation.

Historical data (up to 3 years) is automatically backfilled on the first run.

---

## How it works

```
Wiener Netze API
      │
      │  bewegungsdaten (15-min / hourly intervals)
      │  historical_data (absolute meter readings)
      ▼
  AsyncSmartmeter
      │
      ├──► WNSMSensor.async_update()
      │        │  Sets native_value = latest absolute meter reading (kWh)
      │        │  Sensor entity: device_class=energy, state_class=total_increasing
      │        │
      │        └──► Importer.async_import()
      │                 │  source="homeassistant", statistic_id=entity_id
      │                 │  Backfills hourly statistics into HA recorder
      │                 └──► async_import_statistics()
      │
      ▼
  HA Energy Dashboard
      ├── Historical chart (from imported statistics)
      └── Cost calculation (entity-based stats + tariff entity)
```

---

## Migration from upstream (DarwinsBuddy) version

If you were using the upstream version, your HA database contains external
statistics under the ID `wnsm:at001…`. These will remain in the database but
will no longer be updated.

After installing this version:

1. The new sensor entity will be created (e.g. `sensor.at001…`).
2. On first update, up to 3 years of history is backfilled as entity-based
   statistics.
3. In the Energy Dashboard, **remove** the old `wnsm:at001…` source and **add**
   the new `sensor.at001…` entity.

---

## Credits

- [DarwinsBuddy](https://github.com/DarwinsBuddy) – original integration
- [platysma](https://github.com/platysma) – vienna-smartmeter library
- [florianL21](https://github.com/florianL21) – PKCE login fork

All API rights reserved by [Wiener Netze](https://www.wienernetze.at/impressum).
