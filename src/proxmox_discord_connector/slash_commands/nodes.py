from __future__ import annotations

import logging

import discord
from discord import app_commands
from discord.ext import commands
from proxmoxer.core import ResourceException
from requests.exceptions import RequestException

from proxmox_discord_connector.config import Settings
from proxmox_discord_connector.services import ProxmoxService
from proxmox_discord_connector.slash_commands.proxmox_actions import (
    ActionsLauncherView,
    build_table_embed,
)

logger = logging.getLogger(__name__)


class NodesCog(commands.Cog):
    def __init__(self, settings: Settings, proxmox_service: ProxmoxService) -> None:
        self._settings = settings
        self._proxmox_service = proxmox_service

    @app_commands.command(name="nodes", description="List Proxmox nodes")
    async def list_nodes(self, interaction: discord.Interaction) -> None:
        if (
            self._settings.discord_allowed_user_ids
            and interaction.user.id not in self._settings.discord_allowed_user_ids
        ):
            await interaction.response.send_message(
                "You are not allowed to run this command.",
                ephemeral=True,
            )
            return

        try:
            nodes = self._proxmox_service.list_nodes()
        except ResourceException as exc:
            logger.exception("Proxmox API request failed: %s", exc)
            status_code = getattr(exc, "status_code", None)
            if status_code == 401:
                message = "Proxmox authentication failed. Check credentials."
            else:
                message = "Failed to query Proxmox API. Check host and API availability."
            await interaction.response.send_message(message, ephemeral=True)
            return
        except RequestException as exc:
            logger.exception("Proxmox network request failed: %s", exc)
            await interaction.response.send_message(
                "Failed to reach Proxmox host. Check network and host settings.",
                ephemeral=True,
            )
            return

        if not nodes:
            await interaction.response.send_message("No Proxmox nodes were returned.")
            return

        embed = build_table_embed(
            title="Proxmox Nodes",
            columns=[
                ("Node", [node.name for node in nodes]),
                ("Status", [node.status or "unknown" for node in nodes]),
            ],
        )
        await interaction.response.send_message(
            embed=embed,
            view=ActionsLauncherView([node.name for node in nodes]),
        )

