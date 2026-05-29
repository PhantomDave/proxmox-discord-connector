from __future__ import annotations

from proxmox_discord_connector.bot import ProxmoxDiscordBot
from proxmox_discord_connector.config import Settings


class ProxmoxDiscordApplication:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._bot = ProxmoxDiscordBot(settings)

    def run(self) -> None:
        self._bot.run(self._settings.discord_bot_token)
