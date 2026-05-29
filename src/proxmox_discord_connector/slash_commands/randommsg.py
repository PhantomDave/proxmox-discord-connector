from __future__ import annotations

import random

import discord
from discord import app_commands
from discord.ext import commands


class RandomMessageCog(commands.Cog):
    _MESSAGES = ("Hello!", "Hi there!", "Greetings!", "Howdy!")

    @app_commands.command(name="randommsg", description="Get a random message")
    async def random_message(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            random.choice(self._MESSAGES)
        )

