# Sunology VAULT - Home Assistant Integration

Home Assistant integration for [Sunology VAULT](https://sunology.eu/products/vault-batterie-solaire-maison) ([PLAY Max](https://sunology.eu/products/playmax-station-solaire-batterie) battery).

This integration connects to the [Sunology STREAM](https://sunology.eu/products/stream-pilotage-suivi-energie) backend API to retrieve battery information and control PLAY Max battery settings, which is currently only possible through Sunology STREAM Mobile App.

> **Note:** The [official Sunology integration](https://github.com/sunology-tech/sunology-ha) connects locally to the [STREAM Connect](https://sunology.eu/products/stream-pilotage-suivi-energie) hub via WebSocket, but PLAY Max is not visible through this interface. This integration uses the backend API instead.

## Use Cases

- **Build a dashboard** to monitor all your batteries at a glance (level, state of charge, preserve energy status)
- **Control battery settings** directly from Home Assistant (preserve energy mode, charge threshold)
- **Automate battery behavior** based on weather forecast, electricity rates (peak/off-peak hours), or real-time consumption from a smart meter (e.g., Shelly EM)
- **Sequential battery discharge** when you have multiple panels, discharge them one by one to match your energy needs and avoid sending excess energy back to the grid for free
- **Integrate with other smart devices** trigger actions based on battery status (e.g., start appliances when battery is full, send alerts when battery is low)

### Example Dashboard (French)

<img src="https://github.com/serahug/sunology-vault-ha/blob/main/ha-example-board-fr.png?raw=true" alt="Home Assistant Dashboard Example" width="600">

<details>
<summary>YAML configuration</summary>

```yaml
type: grid
column_span: 2
cards:
  - type: heading
    icon: mdi:battery-charging-wireless-80
    heading_style: title
    heading: Sunology VAULT
  - graph: line
    type: sensor
    entity: sensor.play_max_1_battery_level
    detail: 2
    name: "VAULT #1"
    hours_to_show: 24
  - graph: line
    type: sensor
    entity: sensor.play_max_2_battery_level
    detail: 2
    name: "VAULT #2"
    hours_to_show: 24
  - graph: line
    type: sensor
    entity: sensor.play_max_3_battery_level
    detail: 2
    name: "VAULT #3"
    hours_to_show: 24
  - graph: line
    type: sensor
    entity: sensor.play_max_4_battery_level
    detail: 2
    name: "VAULT #4"
    hours_to_show: 24
  - type: heading
    icon: mdi:battery-charging
    heading: État (En charge | En décharge | Inactif)
    heading_style: subtitle
  - show_name: false
    show_icon: true
    show_state: true
    type: glance
    entities:
      - entity: sensor.play_max_1_battery_state
        show_state: true
        name: "VAULT #1"
        show_last_changed: false
      - entity: sensor.play_max_2_battery_state
        name: "VAULT #2"
        tap_action:
          action: more-info
      - entity: sensor.play_max_3_battery_state
        name: "VAULT #3"
        tap_action:
          action: more-info
      - entity: sensor.play_max_4_battery_state
        name: "VAULT #4"
    grid_options:
      columns: full
      rows: auto
    state_color: false
  - type: heading
    icon: mdi:battery-arrow-up
    heading: Contrôle du seuil de charge (210W ➜ 450W)
    heading_style: subtitle
  - show_name: false
    show_icon: true
    show_state: true
    type: glance
    entities:
      - entity: number.play_max_1_charge_threshold
        show_state: true
        name: "VAULT #1"
        show_last_changed: false
      - entity: number.play_max_2_charge_threshold
        name: "VAULT #2"
        show_last_changed: false
        show_state: true
      - entity: number.play_max_3_charge_threshold
        name: "VAULT #3"
        show_state: true
        show_last_changed: false
      - entity: number.play_max_4_charge_threshold
        name: "VAULT #4"
        show_state: true
    grid_options:
      columns: full
      rows: 2
    state_color: false
  - type: heading
    icon: mdi:battery-charging-20
    heading: Contrôle de la conservation d'énergie (pendant 18h)
    heading_style: subtitle
  - show_name: false
    show_icon: true
    show_state: true
    type: glance
    entities:
      - entity: switch.play_max_1_preserve_energy
        show_state: true
        name: "VAULT #1"
        show_last_changed: false
      - entity: switch.play_max_2_preserve_energy
        name: "VAULT #2"
        show_last_changed: false
        show_state: true
      - entity: switch.play_max_3_preserve_energy
        name: "VAULT #3"
        show_state: true
      - entity: switch.play_max_4_preserve_energy
        name: "VAULT #4"
        show_state: true
    grid_options:
      columns: full
      rows: 2
    state_color: true
```

</details>

## Requirements

- Home Assistant
- [Sunology STREAM](https://sunology.eu/products/stream-pilotage-suivi-energie) account (same credentials as the mobile app)
- [Sunology VAULT](https://sunology.eu/products/vault-batterie-solaire-maison) ([PLAY Max](https://sunology.eu/products/playmax-station-solaire-batterie) battery)

> **Note:** A STREAM Connect hub is NOT required. The PLAY Max connects directly to the Sunology backend via Wi-Fi.

## Installation (HACS)

1. In HACS, go to **Integrations** > **...** (menu) > **Custom repositories**
2. Add `https://github.com/serahug/sunology-vault-ha` as **Integration**
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

This integration is not affiliated with Sunology. Use at your own risk. The API may change without notice, which could break this integration.

Sunology does not provide a public API, nor does the STREAM Connect hub expose PLAY Max data via its local WebSocket. I asked Sunology (December 2025) if they would accept open source contributions to their official HA integration — a common practice for projects hosted on GitHub — but they declined, preferring to keep control over their developments. They also indicated that adding PLAY Max battery (VAULT) support to their official HA integration is not planned. **If you're a Sunology user**, consider reaching out to them to request a public API or PLAY Max support in their official HA integration.
