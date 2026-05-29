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
```

## Run

```bash
python -m proxmox_discord_connector.main
```