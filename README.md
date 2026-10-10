[![GitHub release](https://img.shields.io/github/v/release/JeppeLeth/hass-ista-online?style=flat-square)](https://github.com/JeppeLeth/hass-ista-online/releases)
[![Downloads](https://img.shields.io/github/downloads/JeppeLeth/hass-ista-online/total?style=flat-square)](https://github.com/JeppeLeth/hass-ista-online/releases)
[![HACS Integration](https://img.shields.io/badge/HACS-Integration-41BDF5?style=flat-square)](https://hacs.xyz)

# ISTA Online for Home Assistant 🇩🇰

Bring your **ISTA Online (Denmark)** heating, water and energy meter readings into Home Assistant.

> **Unofficial integration.** This project is not affiliated with, endorsed by, or supported by ista. It is a community project.
>
> The official **ista EcoTrend** integration built into Home Assistant does **not** work in Denmark — it targets ista's German service. This integration fills that gap by talking to the Danish **ISTA Online** service instead.

Each of your meters appears as a device in Home Assistant, with sensors for its latest reading and consumption.

## ⚠️ Your data is delayed

ISTA does not report in real time. This integration shows exactly the same data as the official ISTA app — which for most users means meter readings are **3–5 days behind**, and new readings arrive in batches. This is how ISTA publishes the data, not a limitation of the integration.

## Installation

This integration is installed through [HACS](https://hacs.xyz).

1. Open **HACS** in Home Assistant.
2. Search for **ISTA Online**.
3. Select it and click **Download**.
4. **Restart** Home Assistant.

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=JeppeLeth&repository=hass-ista-online&category=integration)

<details>
<summary>Don't see it in the HACS search?</summary>

Add it as a custom repository: in HACS, open the **⋮** menu → **Custom repositories**, enter
`https://github.com/JeppeLeth/hass-ista-online`, choose category **Integration**, click **Add** — then search for **ISTA Online** again.

Prefer to install by hand? See [DEVELOPMENT.md](DEVELOPMENT.md#manual-installation).
</details>

## Setup

After installing and restarting:

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **ISTA Online** and follow the prompts.

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=ista_online)

You'll be asked for:

| Field | Value |
|-------|-------|
| **Country** | Denmark |
| **Username** | Your ISTA Online username |
| **Password** | Your ISTA Online password |

> **Two-factor authentication must be turned off** on your ISTA account for the integration to sign in.

## What you get

For each meter, a device named like **`Energi - Meter 708226610`** with:

- **Last Meter Reading** — the latest absolute meter value (kWh, m³, …)
- **Last Meter Consumption** — consumption since the previous reading
- Diagnostic sensors: meter type, meter text, reading date, activation/deactivation date, and your address

<img width="661" alt="ISTA Online device in Home Assistant" src="https://github.com/user-attachments/assets/9c9e25b0-cff4-4eaf-8480-b4cf6624094e" />

## Troubleshooting

- **Can't sign in?** Make sure two-factor authentication is disabled, and that your username/password work in the official ISTA app.
- **Readings look old?** That's expected — see [the delay note above](#️-your-data-is-delayed).
- **Need logs?** See [DEVELOPMENT.md](DEVELOPMENT.md#debug-logging).

## Contributing & development

Bug reports and pull requests are welcome — please use the [issue tracker](https://github.com/JeppeLeth/hass-ista-online/issues). Technical details (architecture, the ISTA API, manual install, debug logging) live in [DEVELOPMENT.md](DEVELOPMENT.md).

## Disclaimer

Provided "as is", with no warranty. "ISTA" and "EcoTrend" are trademarks of their respective owners; this project is an independent community integration and is not affiliated with ista.
