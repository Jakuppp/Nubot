# Nubot's dynamic presence changer

import discord
from discord.ext import commands, tasks

from Scripts.utilities import activity

class Presence_Change(commands.Cog):

    def __init__(self, bot, bot_data):
        self.bot = bot
        self.data = bot_data
        self.current_presence = 0
        self.presence_changers = (
            self.help_presence,
            self.guild_presence,
            self.uptime_presence
        )

    async def help_presence(self):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='0help'), status=self.data.status)

    async def guild_presence(self):
        self.data.update()
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{self.data.guilds} servers'), status=self.data.status)

    async def uptime_presence(self):
        await self.bot.change_presence(activity=discord.Game(name=f'for {self.data.brief_uptime()}'), status=self.data.status)

    @tasks.loop(minutes=1)
    async def status_change(self):
        if self.current_presence >= len(self.presence_changers):
            self.current_presence = 0
        await self.presence_changers[self.current_presence]()
        self.current_presence+=1

    @commands.Cog.listener()
    async def on_ready(self):
        self.data.update()
        self.status_change.start()
