# Vonage (`vonage`)

Send SMS notifications via the Vonage (formerly Nexmo) SMS API.

## Overview

| | |
|---|---|
| Addon ID | `vonage` |
| Category | notification |
| Channels | sms |
| Version | 1.0.0 |
| Category guide | [../README.md](../README.md) |

Only **one** notification provider per channel can be active at a time.

## Enable and configure

1. Install this package under `app/addons/notifications/vonage/`
2. Open **Admin → Notifications → Vonage** at `/admin/notifications/vonage`
3. Enter API key, API secret, and sender ID or number
4. Enable the provider checkbox and save

## Configuration schema

| Field | Type | Description |
|-------|------|-------------|
| `api_key` | string | Vonage API key |
| `api_secret` | secret | Vonage API secret |
| `from_number` | string | Sender phone number (E.164) or alphanumeric sender ID |

Secrets are stored in `addon_configs`, not in `.env`.

## Routes

### Admin

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/notifications/vonage` | Config form |
| POST | `/admin/notifications/vonage/save` | Save config |

### Public API

None — core calls `send_sms()` when applicable.

## Provider setup

1. Sign up at [Vonage](https://www.vonage.com/) and create an application.
2. Copy **API Key** and **API Secret** from the dashboard.
3. Configure a virtual number or approved alphanumeric sender ID for your region.
4. Enter credentials and sender in admin config.
5. Enable the addon.

Uses `POST https://rest.nexmo.com/sms/json`.

Email and push are not supported.

## Package layout

```
vonage/
├── README.md
├── addon.py
├── routes.py
└── templates/
    └── vonage_config.html
```

## See also

- [Notification addon development](../README.md)
- [Oshkelosh addon guide](../../README.md)
