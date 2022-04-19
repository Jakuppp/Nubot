# Nubot's ping command

import discord
from discord import Embed
from discord.ext import commands

from Scripts.utilities import truncate

class Ping(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="p", aliases=["ping"])
    async def ping(self, ctx):
        await ctx.send(f"Pong! Nubot's response time is {truncate(self.bot.latency, 3)*1000}ms!")