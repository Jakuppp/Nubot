import discord, datetime
from discord.ext import commands

from Scripts.utilities import get_configs, activity

from Scripts.Cogs.Help import Help
from Scripts.Cogs.Mocking import Mocking
from Scripts.Cogs.Economy import Economy
from Scripts.Cogs.Shop import Shop
from Scripts.Cogs.Minesweeper import Minesweeper
from Scripts.Cogs.Snake import Snake
from Scripts.Cogs.Ping import Ping
from Scripts.Cogs.Presence_Change import Presence_Change

# Intents
intents = discord.Intents.default()
intents.members = True
intents.presences = True

configs = get_configs()
bot_status, bot_activity = activity(configs['status'], configs['activity_type'], configs['activity_name'])

# Initialize the bot
bot = commands.Bot(
    command_prefix=configs['prefix'],
    intents=intents,
    help_command=None,
    case_insensitive=bool(configs['case_insensitive']),
    status=bot_status,
    activity=bot_activity
)

# Before using the guilds parameter, use update()
class Bot_data:
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.guilds = len(bot.guilds)
        self.status = bot_status
    def uptime(self):
        return datetime.datetime.now()-self.start_time
    def brief_uptime(self):
        uptime = self.uptime()
        if uptime.days != 0:
            return f'{uptime.days} days'
        else:
            hours, minutes, seconds = str(uptime).split(':')
            if hours != '0':
                if hours == '1':
                    return hours + ' hour'
                return hours + ' hours'
            elif minutes != '00':
                if minutes == '01':
                    return f'{int(minutes)} minute'
                return f'{int(minutes)} minutes'
            else:
                if seconds == '01':
                    return f'{int(seconds)} second'
                return f'{int(seconds)} seconds'
    def update(self):
        self.guilds = len(bot.guilds)

bot_data = Bot_data()

bot.add_cog(Help(bot))
bot.add_cog(Mocking(bot))
bot.add_cog(Economy(bot))
bot.add_cog(Shop(bot))
bot.add_cog(Minesweeper(bot))
bot.add_cog(Snake(bot))
bot.add_cog(Ping(bot))
if configs['dynamic presence'] == 'true':
    bot.add_cog(Presence_Change(bot, bot_data))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'Woah, slow down there buckaroo. You have to wait {int(error.retry_after)} seconds!')
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f'sorry {ctx.author.name}, you don\'t have the permission to use this command.')
    else:
        raise error

if __name__ == "__main__":
    bot.run(configs['token'])