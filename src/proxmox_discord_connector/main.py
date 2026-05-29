from __future__ import annotations

import logging

import discord
from discord.ext import commands
from proxmoxer.core import ResourceException
from proxmoxer import ProxmoxAPI
from requests.exceptions import RequestException

from proxmox_discord_connector.config import Settings, load_settings

logger = logging.getLogger(__name__)


def create_bot(settings: Settings) -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready() -> None:
        logger.info("Logged in as %s", bot.user)

    auth_kwargs = {
        "user": settings.proxmox_user,
        "password": settings.proxmox_password,
        "verify_ssl": settings.proxmox_verify_ssl,
    }
    proxmox = None

    @bot.command(name="nodes")
    async def list_nodes(ctx: commands.Context) -> None:
        if (
            settings.discord_allowed_user_ids
            and ctx.author.id not in settings.discord_allowed_user_ids
        ):
            await ctx.send("You are not allowed to run this command.")
            return

        try:
            nonlocal proxmox
            if proxmox is None:
                proxmox = ProxmoxAPI(settings.proxmox_host, **auth_kwargs)
            nodes = [node.get("node") for node in proxmox.nodes.get() if node.get("node")]
        except ResourceException as exc:
            logger.exception("Proxmox API request failed: %s", exc)
            status_code = getattr(exc, "status_code", None)
            if status_code == 401:
                await ctx.send("Proxmox authentication failed. Check credentials.")
            else:
                await ctx.send("Failed to query Proxmox API. Check host and API availability.")
            return
        except RequestException as exc:
            logger.exception("Proxmox network request failed: %s", exc)
            await ctx.send("Failed to reach Proxmox host. Check network and host settings.")
            return

        if not nodes:
            await ctx.send("No Proxmox nodes were returned.")
            return

        await ctx.send("Proxmox nodes: " + ", ".join(nodes))

    return bot


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    bot = create_bot(settings)
    bot.run(settings.discord_bot_token)


if __name__ == "__main__":
    main()
