# Cog with the help command

import discord
from discord import Embed
from discord.ext import commands

import asyncio

from Scripts.utilities import get_configs

configs = get_configs()

class Help(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='h', aliases=['help'])
    async def help(self, ctx):

        help_annoy_embed = Embed(title='Annoy commands', description='Commands that let you annoy other users', color=int(configs['colors']['annoy'],16))
        help_annoy_embed.add_field(name='annoy {user mention}', value='Stars mocking the chosen user', inline=False)
        help_annoy_embed.add_field(name='unannoy {user mention}', value='Stops mocking the chosen user', inline=False)
        help_annoy_embed.add_field(name='annoyed', value='Displays all of the users currently annoyed by the bot', inline=False)
        help_annoy_embed.add_field(name='distort {text}', value='Distorts given text', inline=False)

        help_economy_embed = Embed(title='Economy commands', description='Commands that let you use Nubot\'s economy', color=int(configs['colors']['economy'],16))
        help_economy_embed.add_field(name='money', value='Gives you a random amount of money between the range of 0 and 200', inline=False)
        help_economy_embed.add_field(name='balance {optional: user mention}', value='Shows how much money you have, and what\'s your current multiplier.\nYou must use the money command at least once for this to work', inline=False)
        help_economy_embed.add_field(name='economy', value='Shows the leaderboard of the guild, that you\'re in', inline=False)
        help_economy_embed.add_field(name='setcash {user mention} {amount}', value='Sets the balance of the chosen to user to the specified amount', inline=False)
        help_economy_embed.add_field(name='setmultiplier {user mention} {amount}', value='Sets the multiplier of the chosen to user to the specified amount', inline=False)

        help_shop_embed = Embed(title='Shop commands', description='Commands that let you use Nubot\'s shop', color=int(configs['colors']['shop'],16))
        help_shop_embed.add_field(name='shop', value='Displays the shop', inline=False)
        help_shop_embed.add_field(name='shop buy {item name}', value='Let\'s you buy an item from the shop', inline=False)

        help_arcade_embed = Embed(title='Arcade commands', description='Commands that let you play Nubot\'s games', color=int(configs['colors']['arcade'],16))
        help_arcade_embed.add_field(name='minesweeper', value='Let\'s you play Nubot\'s Minesweeper', inline=False)
        help_arcade_embed.add_field(name='snake', value='Let\'s you play Nubot\'s Snake. Only one game can be played at a time', inline=False)
        
        help_other_embed = Embed(title='Other commands', description='Commands with no category')
        help_other_embed.add_field(name='ping', value='Checks bot\'s latency', inline=False)

        help_embed_list = [

            help_annoy_embed,
            help_economy_embed,
            help_shop_embed,
            help_arcade_embed,
            help_other_embed

        ]

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

        page = 0

        message = await ctx.send(embed=help_embed_list[0])

        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == "▶️" and page < len(help_embed_list)-1:
                    page+=1
                    await message.edit(embed=help_embed_list[page])
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and page != 0:
                    page-=1
                    await message.edit(embed=help_embed_list[page])
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "▶️" and page == len(help_embed_list)-1:
                    page = 0
                    await message.edit(embed=help_embed_list[page])
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and page == 0:
                    page = len(help_embed_list)-1
                    await message.edit(embed=help_embed_list[page])
                    await message.remove_reaction(reaction, user)

                else:
                    await message.remove_reaction(reaction, user)

            except asyncio.TimeoutError:
                await message.delete()
                break