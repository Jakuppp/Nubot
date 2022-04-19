# Cog containing commands, that let the privileged mock other users.

import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands.core import has_role

from Scripts.utilities import distort_text, get_configs
from Scripts.database import Database

configs = get_configs()

class Mocking(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = Database("database")

    @commands.command(name='dt', aliases=['distort'])
    async def distort_message(self, ctx, *, message):
        """
        Send an identical message, but distorted, eg. Hello! -> hElLO!
        """
        message_to_str = str(message)
        await ctx.send(distort_text(message_to_str))

    @commands.command(name='an', aliases=['annoy'])
    @has_role(configs['privileged_rank_name'])
    async def annoy_user(self, ctx, user: discord.User):
        """
        Insert the chosen user into the database,
        when they'll send a message, the message will be duplicated and distorted and then sent back
        """
        self.db.save_in_table(server_id=str(ctx.guild.id), type='annoy', user_id=str(user.id))

        annoy_embed = Embed(title='Currently annoying:', description=f'{user.name}#{user.discriminator}', color=int(configs['colors']['annoy'],16))
        annoy_embed.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=annoy_embed)

    @commands.command(name='un', aliases=['unannoy'])
    @has_role(configs['privileged_rank_name'])
    async def unannoy_user(self, ctx, user: discord.User):
        """
        Delete the chosen user from the list of users to annoy
        """
        self.db.delete_from_table(type='annoy', user_id=str(user.id), server_id=str(ctx.guild.id))

        unannoy_embed = Embed(title='Currently unannoying:', description=f'{user.name}#{user.discriminator}', color=int(configs['colors']['annoy'],16))
        unannoy_embed.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=unannoy_embed)

    @commands.command(name='sa', aliases=['annoyed'])
    async def show_annoyed(self, ctx):
        """
        Send an embed showing all the people that the bot is currently annoying
        """
        annoyed = self.db.view_table(str(ctx.guild.id), "annoy")
        annoyed_embed = Embed(title='Annoy list', description=f'People, that I\'m currently annoying:', color=int(configs['colors']['annoy'],16))
        for user_id, data in annoyed.items():
            user = self.bot.get_user(int(user_id))
            annoyed_embed.add_field(name=f'{user.name}#{user.discriminator}', value='-------------------------------', inline=False)

        await ctx.send(embed=annoyed_embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """
        Annoy the chosen users
        """
        table = self.db.view_table(server_id=str(message.guild.id), type='annoy')
        
        for annoy_victim_id, other in table.items():
            if annoy_victim_id == str(message.author.id):
                await message.channel.send(distort_text(message.content))