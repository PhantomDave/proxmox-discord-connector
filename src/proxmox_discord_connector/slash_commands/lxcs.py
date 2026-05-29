from __future__ import annotations

import asyncio
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
    BaseTargetActionView,
    build_table_embed,
)

logger = logging.getLogger(__name__)


class LxcTargetActionView(BaseTargetActionView):
    def __init__(
        self,
        proxmox_service: ProxmoxService,
        targets: list[str],
        target_statuses: dict[str, str],
    ) -> None:
        self._proxmox_service = proxmox_service
        self._target_statuses = target_statuses
        super().__init__(targets)
        self.update_action_buttons()

    def _is_running(self, target: str) -> bool:
        return self._target_statuses.get(target, "").lower() == "running"

    def primary_action_label(self, target: str) -> str:
        if self._is_running(target):
            return "Shutdown"
        return "Start"

    def primary_action_style(self, target: str) -> discord.ButtonStyle:
        if self._is_running(target):
            return discord.ButtonStyle.danger
        return discord.ButtonStyle.success

    async def on_primary_action(
        self,
        interaction: discord.Interaction,
        target: str,
    ) -> None:
        if self._is_running(target):
            await self.on_shutdown(interaction, target)
            return
        await self.on_start(interaction, target)

    def is_reboot_enabled(self, target: str) -> bool:
        return self._is_running(target)

    async def on_shutdown(self, interaction: discord.Interaction, target: str) -> None:
        try:
            await asyncio.to_thread(self._proxmox_service.shutdown_lxc, target)
        except ResourceException as exc:
            logger.exception("Proxmox API request failed during LXC shutdown: %s", exc)
            await interaction.response.send_message(
                "Failed to shut down LXC container via Proxmox API.",
                ephemeral=True,
            )
            return
        except RequestException as exc:
            logger.exception("Proxmox network request failed during LXC shutdown: %s", exc)
            await interaction.response.send_message(
                "Failed to reach Proxmox host for shutdown request.",
                ephemeral=True,
            )
            return
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return

        await interaction.response.send_message(
            f"Shutdown requested for {target}.",
            ephemeral=True,
        )

    async def on_start(self, interaction: discord.Interaction, target: str) -> None:
        try:
            await asyncio.to_thread(self._proxmox_service.start_lxc, target)
        except ResourceException as exc:
            logger.exception("Proxmox API request failed during LXC start: %s", exc)
            await interaction.response.send_message(
                "Failed to start LXC container via Proxmox API.",
                ephemeral=True,
            )
            return
        except RequestException as exc:
            logger.exception("Proxmox network request failed during LXC start: %s", exc)
            await interaction.response.send_message(
                "Failed to reach Proxmox host for start request.",
                ephemeral=True,
            )
            return
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return

        await interaction.response.send_message(
            f"Start requested for {target}.",
            ephemeral=True,
        )

    async def on_reboot(self, interaction: discord.Interaction, target: str) -> None:
        try:
            await asyncio.to_thread(self._proxmox_service.reboot_lxc, target)
        except ResourceException as exc:
            logger.exception("Proxmox API request failed during LXC reboot: %s", exc)
            await interaction.response.send_message(
                "Failed to reboot LXC container via Proxmox API.",
                ephemeral=True,
            )
            return
        except RequestException as exc:
            logger.exception("Proxmox network request failed during LXC reboot: %s", exc)
            await interaction.response.send_message(
                "Failed to reach Proxmox host for reboot request.",
                ephemeral=True,
            )
            return
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return

        await interaction.response.send_message(
            f"Reboot requested for {target}.",
            ephemeral=True,
        )


class LxcCog(commands.Cog):
    def __init__(self, settings: Settings, proxmox_service: ProxmoxService) -> None:
        self._settings = settings
        self._proxmox_service = proxmox_service

    @app_commands.command(name="lxcs", description="List Proxmox LXC containers")
    async def list_lxcs(self, interaction: discord.Interaction) -> None:
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
            lxcs = await asyncio.to_thread(self._proxmox_service.list_lxcs)
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

        if not lxcs:
            await interaction.response.send_message("No Proxmox LXC containers were returned.")
            return

        embed = build_table_embed(
            title="Proxmox LXC Containers",
            columns=[
                ("Node", [lxc.node for lxc in lxcs]),
                ("VMID", [str(lxc.vmid) if lxc.vmid is not None else "-" for lxc in lxcs]),
                ("Name", [lxc.name or "-" for lxc in lxcs]),
                ("Status", [lxc.status or "unknown" for lxc in lxcs]),
            ],
        )

        targets = [
            f"{lxc.name}/{lxc.vmid}"
            for lxc in lxcs
            if lxc.name is not None and lxc.vmid is not None
        ]
        target_statuses = {
            f"{lxc.name}/{lxc.vmid}": lxc.status or "unknown"
            for lxc in lxcs
            if lxc.name is not None and lxc.vmid is not None
        }

        if not targets:
            await interaction.response.send_message(
                embed=embed,
                content="No actionable LXC containers with both name and VMID were returned.",
            )
            return

        await interaction.response.send_message(
            embed=embed,
            view=ActionsLauncherView(
                targets,
                action_view_factory=lambda action_targets: LxcTargetActionView(
                    self._proxmox_service,
                    list(action_targets),
                    target_statuses,
                ),
            ),
        )

