# proxmox-discord-connector
Basic Python project template for a Discord bot that can query Proxmox.

## Requirements

- Python 3.11+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
set -a && source .env && set +a
```

`DISCORD_BOT_TOKEN`, `PROXMOX_HOST`, `PROXMOX_USER`, and `PROXMOX_PASSWORD` are required.
`DISCORD_ALLOWED_USER_IDS` is optional (comma-separated Discord user IDs).

## Run

```bash
python -m proxmox_discord_connector.main
```