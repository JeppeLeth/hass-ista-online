# ISTA Online Integration for Home Assistant

**Repository:** https://github.com/JeppeLeth/hass-ista-online

## Overview

Custom integration (HACS-ready) for ISTA Denmark.  
Allows users to authenticate with username/password (two-factor authentication **must be disabled**), fetch user info and meters.

Each meter becomes a device in Home Assistant.  
Sensors expose the latest reading and unit.  
Device attributes include address and city.

## Table of Contents

- [Installation](#installation)
  - [Installation through HACS](#installation-through-hacs)
  - [Manual installation](#manual-installation)
- [Configuration](#configuration)
- [Entities](#entities)
- [Device Information](#device-information)
- [Requirements & Notes](#requirements--notes)
- [Development](#development)

## Installation

### Installation through HACS

1. In Home Assistant, go to **HACS > Integrations**.
2. Click the three dots in the top-right and select **Custom repositories**.
3. Add the URL of this repository, choose type **Integration**, and click **ADD**.
4. Search for **ISTA Online** in HACS and install it.
5. Restart Home Assistant.
6. Go to **Configuration > Integrations** and add **ISTA Online** via the UI (uses config flow).

### Manual installation

Copy the `custom_components/ista_online` directory into your Home Assistant configuration's `custom_components` directory:

```bash
mkdir -p /config/custom_components
cp -R custom_components/ista_online /config/custom_components/
```

Then restart Home Assistant and configure the integration through the UI.

## Configuration

The integration uses a UI config flow. Required fields:
- **Country**: currently only `Denmark` (defines base URL)
- **Username / Password**: credentials for ISTA Denmark account (two-factor authentication must be disabled)

## Entities

For each meter:
- Sensor for last meter reading (`Last Meter Reading`) with entity ID like `ista_meter_{METER_NO}_last_meter_reading`
- Sensor for last meter consumption (`Last Meter Consumption`) with entity ID like `ista_meter_{METER_NO}_last_meter_consumption`

Diagnostic sensors:
- Activation date
- Deactivation date
- Message
- Headline
- Meter type
- Meter code
- Meter text
- Reading date

## Device Information

Each meter creates a device with:
- **Serial**: `METER_NO`
- **Device type/model**: `METCAT_LABEL`
- **Address** and **city** attached as attributes.

## Requirements & Notes

- Requires Home Assistant **2023.12.0** or newer.
- Python dependency: `requests`
- Two-factor authentication must be disabled on the ISTA account for this integration to work.
- Update `manifest.json` and `hacs.json` fields such as repository URLs, codeowners, and issue tracker to reflect your actual GitHub repository.

## Development

To enable debug logging in Home Assistant's `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.ista_online: debug
```

After a restart, detailed log output will appear in `home-assistant.log`.
