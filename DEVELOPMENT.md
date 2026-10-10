# Development

Technical notes for contributors and curious users. For installation and setup, see the [README](README.md).

## Architecture

The integration is a standard Home Assistant **cloud-polling** integration:

- **`config_flow.py`** — UI setup, re-auth and options flows. Validates credentials by logging in once.
- **`coordinator.py`** — a `DataUpdateCoordinator` that refreshes every hour. On each cycle it logs in, then fetches user info and meters.
- **`api_client.py`** — thin `requests` wrapper around the ISTA Online HTTP API.
- **`sensor.py`** — turns each meter into a device with reading, consumption and diagnostic sensors.
- **`const.py`** — domain, per-country base URLs, update interval.

## ISTA Online API

Base URL (Denmark): `https://prod.istaonlinebeta.dk`

| Call | Purpose |
|------|---------|
| `POST /token` | Log in. Form-encoded `grant_type=password` + `username` + `password`. Returns a bearer `access_token` (valid ~1 h; no refresh token — just log in again). |
| `GET /api/GetUserInfo` | Account/address info. Header `Authorization: bearer <token>`. |
| `GET /api/Meters` | List of meters and their latest readings. Same auth header. |

Notes:
- Bad credentials return **HTTP 400** with `{"error": "invalid_grant", ...}`. The coordinator maps this to `ConfigEntryAuthFailed`, which triggers Home Assistant's re-auth flow (and avoids hammering the login endpoint, which can lock the account after repeated failures).
- Responses wrap their payload in an envelope: `{ "errorMessage": {...}, "Meters": { "Value": [ ... ] } }`.
- Historical consumption graphs live on a separate host (`graphs.istaonlinebeta.dk`) and use the **same token** in an `istaauthentication` header. The integration does not use these yet (see Ideas below).

## Entities

Entities use `has_entity_name`, so Home Assistant shows them as `{device name} {entity name}`.

- Device name: `{MeterText} - Meter {METER_NO}` (e.g. `Energi - Meter 708226610`)
- `unique_id`s are derived from `METER_NO` / `METER_ID` and are stable across renames.

## Manual installation

Copy the component into your config directory instead of using HACS:

```bash
mkdir -p /config/custom_components
cp -R custom_components/ista_online /config/custom_components/
```

Then restart Home Assistant and add the integration from the UI.

## Debug logging

Add to `configuration.yaml` and restart:

```yaml
logger:
  default: info
  logs:
    custom_components.ista_online: debug
```

Detailed output then appears in `home-assistant.log`.

## Requirements

- Home Assistant **2023.12.0** or newer
- Python dependency: `requests`

## Ideas / roadmap

- **Historical statistics import.** ISTA publishes data in 3–5 day batches, so it could be back-filled into Home Assistant's long-term statistics (via `async_add_external_statistics`) using the daily consumption endpoint on `graphs.istaonlinebeta.dk` — enabling correct Energy dashboard history despite the delay.
- Additional countries (only Denmark is wired up in `const.py` today).
