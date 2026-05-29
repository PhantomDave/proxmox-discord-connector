from __future__ import annotations

import logging

import discord
from discord.ext import commands

from proxmox_discord_connector.config import Settings
from proxmox_discord_connector.slash_commands import build_cogs

logger = logging.getLogger(__name__)


class ProxmoxDiscordBot(commands.Bot):
    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.settings = settings

    async def setup_hook(self) -> None:
        for cog in build_cogs(self.settings):
            await self.add_cog(cog)

        if self.settings.discord_sync_guild_id is not None:
            guild = discord.Object(id=self.settings.discord_sync_guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info(
                "Synced %s slash command(s) to guild %s",
                len(synced),
                self.settings.discord_sync_guild_id,
            )
            return

        synced = await self.tree.sync()
        logger.info("Synced %s global slash command(s)", len(synced))

    async def on_ready(self) -> None:
        logger.info("Logged in as %s", self.user)
