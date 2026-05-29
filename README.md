# proxmox-discord-connector
Python Discord bot template that queries Proxmox via slash commands.

The codebase now follows an object-oriented structure:

- `ProxmoxDiscordApplication` handles app startup.
- `ProxmoxDiscordBot` subclasses `commands.Bot` and registers cogs in `setup_hook`.
- `NodesCog` and `RandomMessageCog` encapsulate slash command behavior.
- `ProxmoxService` encapsulates Proxmox API client access.

## Requirements

- Python 3.11+

## Setup

```bash
python -m venv .venv
cp .env.example .env
```

Activate the virtual environment:

```bash
# bash/zsh
source .venv/bin/activate

# fish
source .venv/bin/activate.fish
```

Install the project from the repository root (not `src/`):

```bash
python -m pip install -e .
```

Edit `.env` with your values.

`DISCORD_BOT_TOKEN`, `PROXMOX_HOST`, `PROXMOX_USER`, and `PROXMOX_PASSWORD` are required.
`DISCORD_ALLOWED_USER_IDS` is optional (comma-separated Discord user IDs).
`DISCORD_SYNC_GUILD_ID` is optional and recommended for development to get near-instant slash command updates.
`PROXMOX_VERIFY_SSL` defaults to `true`.

### Environment variables

- `DISCORD_BOT_TOKEN`: Discord bot token.
- `DISCORD_ALLOWED_USER_IDS`: Optional comma-separated allowlist for restricted commands (e.g. `123,456`).
- `DISCORD_SYNC_GUILD_ID`: Optional Discord server ID for development command sync (fast propagation).
- `PROXMOX_HOST`: Proxmox host or IP.
- `PROXMOX_USER`: Proxmox user (for example `root@pam`).
- `PROXMOX_PASSWORD`: Proxmox password.
- `PROXMOX_VERIFY_SSL`: `true` or `false` (defaults to `true`).

## Slash Command Sync Speed

Discord global slash command propagation can take a while.
For fast development updates, set `DISCORD_SYNC_GUILD_ID` to your server ID in `.env`.

Example:

```env
DISCORD_SYNC_GUILD_ID=123456789012345678
```

When this is set, the bot copies global commands to that guild and syncs there on startup, so new commands usually appear quickly after restart.

## Run

```bash
python -m proxmox_discord_connector.main
```

If activation is not working in your shell, run directly with the venv Python:

```bash
.venv/bin/python -m pip install -e .
.venv/bin/python -m proxmox_discord_connector.main
```

## Slash commands

- `/nodes` - List Proxmox nodes. Honors `DISCORD_ALLOWED_USER_IDS` when provided.
- `/lxcs` - List Proxmox LXC containers. Honors `DISCORD_ALLOWED_USER_IDS` when provided.
- `/randommsg` - Return a random greeting.

## Project structure

```text
src/proxmox_discord_connector/
	app.py                 # Application entry object
	bot.py                 # Bot subclass and setup_hook
	config.py              # Environment-backed settings
	main.py                # Executable module entrypoint
	services/
		proxmox_service.py   # Proxmox API service layer
	slash_commands/
		nodes.py             # NodesCog
		randommsg.py         # RandomMessageCog
```
