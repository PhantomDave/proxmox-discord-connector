from __future__ import annotations

import logging

import discord
from discord.ext import commands
from proxmoxer.core import ResourceException
from proxmoxer import ProxmoxAPI

from proxmox_discord_connector.config import load_settings

logger = logging.getLogger(__name__)


def create_bot() -> commands.Bot:
    settings = load_settings()
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready() -> None:
        logger.info("Logged in as %s", bot.user)

    @bot.command(name="nodes")
    async def list_nodes(ctx: commands.Context) -> None:
        auth_kwargs = {
            "user": settings.proxmox_user,
            "verify_ssl": settings.proxmox_verify_ssl,
        }
        auth_kwargs["password"] = settings.proxmox_password

        try:
            proxmox = ProxmoxAPI(settings.proxmox_host, **auth_kwargs)
            nodes = [node.get("node") for node in proxmox.nodes.get() if node.get("node")]
        except ResourceException as exc:
            logger.exception("Proxmox API request failed: %s", exc)
            await ctx.send("Failed to query Proxmox API. Check host and credentials.")
            return

        if not nodes:
            await ctx.send("No Proxmox nodes were returned.")
            return

        await ctx.send("Proxmox nodes: " + ", ".join(nodes))

    return bot


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    if not settings.discord_bot_token:
        raise RuntimeError("DISCORD_BOT_TOKEN is required.")
    bot = create_bot()
    bot.run(settings.discord_bot_token)


if __name__ == "__main__":
    main()
