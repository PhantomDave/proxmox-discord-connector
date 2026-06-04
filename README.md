# proxmox-discord-connector

Discord slash-command bot for Proxmox VE. It connects to your Proxmox API and exposes commands in Discord (nodes, LXC list, and actions).

## What This Project Does

- Connects to Proxmox using `proxmoxer`
- Runs a Discord bot using `discord.py`
- Loads configuration from `.env`
- Provides slash commands such as `/nodes` and `/lxcs`

## Prerequisites

- Python 3.11+
- A Discord bot token
- Network access to your Proxmox host/API

## Installation With pip

### Option 1: Install from source checkout (recommended for local edits)

```bash
git clone https://github.com/PhantomDave/proxmox-discord-connector.git
cd proxmox-discord-connector

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

For fish shell:

```bash
source .venv/bin/activate.fish
```

### Option 2: Install as a regular package (non-editable)

```bash
python -m pip install .
```

## Installation With Docker

Use the prebuilt image from GHCR:

```bash
docker pull ghcr.io/phantomdave/proxmox-discord-connector:latest
```

Run it with your environment file:

```bash
docker run --rm \
  --name proxmox-discord-connector \
  --env-file .env \
  ghcr.io/phantomdave/proxmox-discord-connector:latest
```

If you want to build locally instead:

```bash
docker build -t proxmox-discord-connector:latest .
docker run --rm --env-file .env proxmox-discord-connector:latest
```

### Docker Compose Example

An example compose file is included at `docker-compose.example.yml`.

```bash
cp docker-compose.example.yml docker-compose.yml
docker compose up -d
```

## Configuration

Copy the example file and edit values:

```bash
cp .env.example .env
```

If you installed only via `pip` and do not have the repo checkout, extract the packaged example:

```bash
python -c "import pathlib, proxmox_discord_connector as p; print(pathlib.Path(p.__file__).with_name('.env.example'))"
```

Then copy that file to your working directory as `.env`.

### Environment variables

| Variable | Required | Description | Example |
|---|---|---|---|
| `DISCORD_BOT_TOKEN` | Yes | Discord bot token | `your_token_here` |
| `PROXMOX_HOST` | Yes | Proxmox host (with or without port) | `192.168.1.14:8006` |
| `PROXMOX_USER` | Yes | Proxmox user | `root@pam` |
| `PROXMOX_PASSWORD` | Yes | Proxmox password | `super_secret_password` |
| `PROXMOX_VERIFY_SSL` | No | TLS verification flag (`true/false`, `1/0`, `yes/no`) | `true` |
| `DISCORD_ALLOWED_USER_IDS` | No | Comma-separated allowlist of Discord user IDs | `1234567890,9876543210` |
| `DISCORD_SYNC_GUILD_ID` | No | Guild ID for fast command sync in development | `123456789012345678` |

Notes:

- `DISCORD_ALLOWED_USER_IDS` can be empty to allow everyone to run command checks that use this list.
- `DISCORD_SYNC_GUILD_ID` is strongly recommended in development because global slash command propagation can be slow.
- `PROXMOX_VERIFY_SSL` defaults to `true` if not set.

## Run

Local (pip/venv):

```bash
python -m proxmox_discord_connector.main
```

Docker:

```bash
docker run --rm --env-file .env ghcr.io/phantomdave/proxmox-discord-connector:latest
```

## Available Slash Commands

- `/nodes` - List Proxmox nodes
- `/lxcs` - List Proxmox LXC containers
- `/randommsg` - Return a random greeting

## Security

- Do not commit `.env` to source control.
- Treat `DISCORD_BOT_TOKEN` and `PROXMOX_PASSWORD` as secrets.
- If a token/password is exposed, rotate it immediately.
