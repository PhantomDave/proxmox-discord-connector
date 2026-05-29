from __future__ import annotations

from discord.ext import commands

from proxmox_discord_connector.config import Settings
from proxmox_discord_connector.services import ProxmoxService
from proxmox_discord_connector.slash_commands.lxcs import LxcCog
from proxmox_discord_connector.slash_commands.nodes import NodesCog
from proxmox_discord_connector.slash_commands.randommsg import RandomMessageCog


def build_cogs(settings: Settings) -> list[commands.Cog]:
    proxmox_service = ProxmoxService.from_settings(settings)
    return [
        NodesCog(settings=settings, proxmox_service=proxmox_service),
        LxcCog(settings=settings, proxmox_service=proxmox_service),
        RandomMessageCog(),
    ]

