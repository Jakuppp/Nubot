# Cog containing commands, that let users use bot's economy

import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands.core import has_role

from Scripts.utilities import RNG, truncate, get_configs, get_quotes
from Scripts.database import Database

configs = get_configs()

class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = Database("database")
        self.quotes = get_quotes()

    @commands.cooldown(1, 8, commands.BucketType.user)
    @commands.command(name='eco', aliases=['economy', 'leadearboards'])
    async def show_economy(self, ctx):
        """
        Show the leaderboard of users, based on money
        """
        economy_cells = self.db.view_table(server_id=str(ctx.guild.id), type='economy')

        # Get all of user's IDs and their balances
        list_of_balances = []
        for user, data in economy_cells.items():
            user = self.bot.get_user(int(user))
            user_and_balance = [user, float(data['val'])]
            list_of_balances.append(user_and_balance)

        # Sort the balances
        get_second_element = lambda l : l[1]
        list_of_balances = sorted(list_of_balances, key=get_second_element, reverse=True)

        leaderboard_embed = discord.Embed(title=f'Leaderboard of {ctx.guild.name}', color=int(configs['colors']['economy'],16))
        leaderboard_embed.add_field(name='Most money:', value=f'{list_of_balances[0][0].name}')
        leaderboard_embed.set_thumbnail(url=list_of_balances[0][0].avatar_url)

        i=1
        for user_info in list_of_balances:
            leaderboard_embed.add_field(name=f'{i}. {user_info[0].name}',value=f'**{user_info[1]}**<:dollars:899250630919606324>', inline=False)
            i+=1

        await ctx.send(embed=leaderboard_embed)

    @commands.cooldown(1, 8, commands.BucketType.user)
    @commands.command(name='mn', aliases=['money', 'cash'])
    async def get_cash(self, ctx):
        """
        A roulette command
        """
        economy_cells = self.db.view_table(server_id=str(ctx.guild.id), type='economy')
        try:
            user_multiplier = self.db.view_table(server_id=str(ctx.guild.id), type='multiplier')[str(ctx.author.id)]['val']
        except:
            user_multiplier=0

        bet = RNG(-200, 200)
        if bet <= 0:
            plus_cash=0
        else:
            plus_cash=bet

        # Choose a custom quote based on money earned
        if plus_cash <= 0:
            title, body = self.quotes[0][0], self.quotes[0][1]
        elif plus_cash <= 25:
            title, body = self.quotes[1][0], self.quotes[1][1]
        elif plus_cash <= 85:
            title, body = self.quotes[2][0], self.quotes[2][1]
        elif plus_cash <= 150:
            title, body = self.quotes[3][0], self.quotes[3][1]
        elif plus_cash <= 200:
            title, body = self.quotes[4][0], self.quotes[4][1]
        
        if user_multiplier != 'None':
            plus_cash = plus_cash*(1+float(user_multiplier))
            plus_cash = truncate(plus_cash,1)

        try:
            if economy_cells[str(ctx.author.id)]['val'] != 'None':
                self.db.save_in_table(server_id=str(ctx.guild.id), user_id=str(ctx.author.id), val=str(truncate(float(economy_cells[str(ctx.author.id)]['val']) + plus_cash)), type='economy')
            else:
                # If balance is "None", set the balance to won money
                self.db.save_in_table(server_id=str(ctx.guild.id), user_id=str(ctx.author.id), val=str(plus_cash), type='economy')
        except:
            # The user wasn't in the database
            self.db.save_in_table(server_id=str(ctx.guild.id), user_id=str(ctx.author.id), val=str(plus_cash), type='economy')

        spin_embed = discord.Embed(title=title, description=f'{body} **{plus_cash}**<:dollars:899250630919606324>!', color=int(configs['colors']['economy'],16))
        await ctx.send(embed=spin_embed)

    @commands.cooldown(1, 8, commands.BucketType.user)
    @commands.command(name='b', aliases=['bal', 'balance', 'wallet'])
    async def show_balance(self, ctx, user: discord.User = None):
        """
        Display the user's balance
        """
        if user != None:
            chosen_user = user
        else:
            chosen_user = ctx.author

        user_balance = self.db.view_table(server_id=str(ctx.guild.id), type='economy')[str(chosen_user.id)]['val']
        try:
            user_multiplier = self.db.view_table(server_id=str(ctx.guild.id), type='multiplier')[str(chosen_user.id)]['val']
        except:
            user_multiplier=0

        balance_embed = discord.Embed(title=f'{chosen_user.name}#{chosen_user.discriminator}\'s Balance:', description=f'**{user_balance}**<:dollars:899250630919606324>\n**multiplier: {user_multiplier}%**', color=int(configs['colors']['economy'],16))
        balance_embed.set_thumbnail(url=chosen_user.avatar_url)

        await ctx.send(embed=balance_embed)

    @commands.command(name='sc', aliases=['setcash'])
    @has_role(configs['privileged_rank_name'])
    async def set_cash(self, ctx, user: discord.User, amount):
        self.db.save_in_table(server_id=str(ctx.guild.id), user_id=str(user.id), val=amount, type='economy')

    @commands.command(name='sm', aliases=['setmultiplier'])
    @has_role(configs['privileged_rank_name'])
    async def set_multiplier(self, ctx, user: discord.User, amount):
        self.db.save_in_table(server_id=str(ctx.guild.id), user_id=str(user.id), val=amount, type='multiplier')