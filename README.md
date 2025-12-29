# Sunology VAULT - Home Assistant Integration

**Unofficial** Home Assistant integration for [Sunology VAULT](https://sunology.eu/products/vault-batterie-solaire-maison) ([PLAY Max](https://sunology.eu/products/playmax-station-solaire-batterie) battery).

This integration connects to the [Sunology STREAM](https://sunology.eu/products/stream-pilotage-suivi-energie) backend API to retrieve battery information and control PLAY Max battery settings, which is currently only possible through Sunology STREAM Mobile App.

> **Note:** The [official Sunology integration](https://github.com/sunology-tech/sunology-ha) connects locally to the [STREAM Connect](https://sunology.eu/products/stream-pilotage-suivi-energie) hub via WebSocket, but PLAY Max is not visible through this interface. This integration uses the backend API instead.

## Use Cases

- **Build a dashboard** to monitor all your batteries at a glance (level, state of charge, preserve energy status)
- **Control battery settings** directly from Home Assistant (preserve energy mode, charge threshold)
- **Automate battery behavior** based on weather forecast, electricity rates (peak/off-peak hours), or real-time consumption from a smart meter (e.g., Shelly EM)
- **Sequential battery discharge** when you have multiple panels, discharge them one by one to match your energy needs and avoid sending excess energy back to the grid for free
- **Integrate with other smart devices** trigger actions based on battery status (e.g., start appliances when battery is full, send alerts when battery is low)

### Example Dashboard

![Home Assistant Dashboard Example](ha-example-board.png)

## Requirements

- Home Assistant
- [Sunology STREAM](https://sunology.eu/products/stream-pilotage-suivi-energie) account (same credentials as the mobile app)
- [Sunology VAULT](https://sunology.eu/products/vault-batterie-solaire-maison) ([PLAY Max](https://sunology.eu/products/playmax-station-solaire-batterie) battery)

> **Note:** A STREAM Connect hub is NOT required. The PLAY Max connects directly to the Sunology backend via Wi-Fi.

## Installation (HACS)

1. In HACS, go to **Integrations** > **...** (menu) > **Custom repositories**
2. Add `https://github.com/Serahug/SunologyVault-HA` as **Integration**
3. Install **Sunology VAULT**
4. Restart Home Assistant
5. Go to **Settings** > **Devices & Services** > **Add Integration** > **Sunology VAULT**
6. Enter your Sunology STREAM credentials

## Entities

### Sensors

| Sensor | Description |
|--------|-------------|
| Battery Level | Current battery level (%) |
| Battery State | Current state (Idle, Charging, Discharging) |
| Available Energy | Available energy in the battery (Wh) |

### Controls

| Entity | Type | Description |
|--------|------|-------------|
| Preserve Energy | Switch | Enable/disable battery preservation mode (18h) |
| Charge Threshold | Number | Charge threshold (210-450W) |

> **Note:** Changes to controls may take up to 5 minutes to be applied to the solar panels (same delay as via the mobile app). Changes are visible immediately in the Sunology STREAM app. You can safely use both the app and this integration simultaneously.

## Configuration

After installation, you can configure the polling interval in the integration options (default: 60 seconds, range: 30-300 seconds).

## Compatibility

This integration can be installed alongside the [official Sunology integration](https://github.com/sunology-tech/sunology-ha). They use different connection methods (backend API vs local WebSocket) and do not conflict.

## Disclaimer

This is an unofficial integration not affiliated with Sunology. Use at your own risk. The API may change without notice, which could break this integration.

Sunology does not provide a public API, nor does the STREAM Connect hub expose PLAY Max data via its local WebSocket. I asked Sunology (December 2025) if they would accept open source contributions to their official HA integration — a common practice for projects hosted on GitHub — but they declined, preferring to keep control over their developments. They also indicated that adding PLAY Max battery (VAULT) support to their official HA integration is not planned. **If you're a Sunology user**, consider reaching out to them to request a public API or PLAY Max support in their official HA integration.
