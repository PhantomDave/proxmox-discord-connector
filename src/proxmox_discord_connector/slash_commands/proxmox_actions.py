from __future__ import annotations

from collections.abc import Sequence
from typing import Callable

import discord

MAX_TABLE_ROWS = 20
MAX_SELECT_OPTIONS = 25
MAX_FIELD_VALUE_LENGTH = 1024


def _truncate_field_value(value: str) -> str:
    if len(value) <= MAX_FIELD_VALUE_LENGTH:
        return value
    return value[: MAX_FIELD_VALUE_LENGTH - 1] + "…"


def build_table_embed(
    *,
    title: str,
    columns: Sequence[tuple[str, Sequence[str]]],
    max_rows: int = MAX_TABLE_ROWS,
) -> discord.Embed:
    embed = discord.Embed(title=title)
    has_rows = any(column_values for _, column_values in columns)
    if not has_rows:
        return embed

    visible_rows = max_rows
    for _, column_values in columns:
        visible_rows = min(visible_rows, len(column_values))

    for column_name, column_values in columns:
        display_values = [str(value) for value in column_values[:visible_rows]]
        if len(column_values) > visible_rows:
            display_values.append("…")

        field_value = "\n".join(display_values) if display_values else "-"
        embed.add_field(
            name=column_name,
            value=_truncate_field_value(field_value),
            inline=True,
        )

    if any(len(column_values) > visible_rows for _, column_values in columns):
        embed.set_footer(text=f"Showing first {visible_rows} rows")

    return embed


class TargetSelect(discord.ui.Select["BaseTargetActionView"]):
    def __init__(self, targets: Sequence[str], parent: "BaseTargetActionView") -> None:
        options = [
            discord.SelectOption(label=target[:100], value=target)
            for target in targets[:MAX_SELECT_OPTIONS]
        ]
        super().__init__(
            placeholder="Select target",
            min_values=1,
            max_values=1,
            options=options,
        )
        self._action_view = parent
        

    async def callback(self, interaction: discord.Interaction) -> None:
        self._action_view.selected_target = self.values[0]
        self._action_view.update_action_buttons()
        await interaction.response.edit_message(view=self._action_view)


class BaseTargetActionView(discord.ui.View):
    def __init__(self, targets: Sequence[str], *, timeout: float = 180.0) -> None:
        super().__init__(timeout=timeout)
        self.selected_target = targets[0] if targets else None
        self.add_item(TargetSelect(targets, self))
        self.update_action_buttons()

    def primary_action_label(self, target: str) -> str:
        return "Shutdown"

    def primary_action_style(self, target: str) -> discord.ButtonStyle:
        return discord.ButtonStyle.danger

    async def on_primary_action(
        self,
        interaction: discord.Interaction,
        target: str,
    ) -> None:
        await self.on_shutdown(interaction, target)

    def is_reboot_enabled(self, target: str) -> bool:
        return True

    def update_action_buttons(self) -> None:
        target = self.selected_target
        if target is None:
            self.primary_action_button.disabled = True
            self.reboot_button.disabled = True
            return

        self.primary_action_button.disabled = False
        self.primary_action_button.label = self.primary_action_label(target)
        self.primary_action_button.style = self.primary_action_style(target)
        self.reboot_button.disabled = not self.is_reboot_enabled(target)

    async def on_shutdown(self, interaction: discord.Interaction, target: str) -> None:
        await interaction.response.send_message(
            f"TODO: shutdown flow for {target}",
            ephemeral=True,
        )

    async def on_start(self, interaction: discord.Interaction, target: str) -> None:
        await interaction.response.send_message(
            f"TODO: start flow for {target}",
            ephemeral=True,
        )

    async def on_reboot(self, interaction: discord.Interaction, target: str) -> None:
        await interaction.response.send_message(
            f"TODO: reboot flow for {target}",
            ephemeral=True,
        )

    @discord.ui.button(label="Shutdown", style=discord.ButtonStyle.danger)
    async def primary_action_button(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button["BaseTargetActionView"],
    ) -> None:
        target = self.selected_target
        if target is None:
            await interaction.response.send_message("No target selected.", ephemeral=True)
            return
        await self.on_primary_action(interaction, target)

    @discord.ui.button(label="Reboot", style=discord.ButtonStyle.primary)
    async def reboot_button(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button["BaseTargetActionView"],
    ) -> None:
        target = self.selected_target
        if target is None:
            await interaction.response.send_message("No target selected.", ephemeral=True)
            return
        await self.on_reboot(interaction, target)


class ProxmoxTargetActionView(BaseTargetActionView):
    pass


class ActionsLauncherView(discord.ui.View):
    def __init__(
        self,
        targets: Sequence[str],
        *,
        timeout: float = 180.0,
        action_view_factory: Callable[[Sequence[str]], BaseTargetActionView] | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._targets = list(targets)
        self._action_view_factory = action_view_factory or ProxmoxTargetActionView

    @discord.ui.button(label="Actions", style=discord.ButtonStyle.secondary)
    async def actions_button(
        self,
        interaction: discord.Interaction,
        _: discord.ui.Button["ActionsLauncherView"],
    ) -> None:
        if not self._targets:
            await interaction.response.send_message("No targets available.", ephemeral=True)
            return

        await interaction.response.send_message(
            "Choose a target and action:",
            view=self._action_view_factory(self._targets),
            ephemeral=True,
        )