from __future__ import annotations

import discord
from discord.ext import commands
from proxmoxer import ProxmoxAPI

from proxmox_discord_connector.config import load_settings


def create_bot() -> commands.Bot:
    settings = load_settings()
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready() -> None:
        print(f"Logged in as {bot.user}")

    @bot.command(name="nodes")
    async def list_nodes(ctx: commands.Context) -> None:
        auth_kwargs = {
            "user": settings.proxmox_user,
            "verify_ssl": settings.proxmox_verify_ssl,
        }
        auth_kwargs["password"] = settings.proxmox_password

        try:
            proxmox = ProxmoxAPI(settings.proxmox_host, **auth_kwargs)
            nodes = [node["node"] for node in proxmox.nodes.get()]
        except Exception:
            await ctx.send("Failed to connect to Proxmox or read nodes.")
            return

        await ctx.send("Proxmox nodes: " + ", ".join(nodes))

    return bot


def main() -> None:
    settings = load_settings()
    if not settings.discord_bot_token:
        raise RuntimeError("DISCORD_BOT_TOKEN is required.")
    bot = create_bot()
    bot.run(settings.discord_bot_token)


if __name__ == "__main__":
    main()
