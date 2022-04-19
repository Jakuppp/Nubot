# Cog containing Nubot's shop

import discord
from discord import Embed
from discord.ext import commands

import asyncio

from Scripts.utilities import get_shop, get_configs, truncate
from Scripts.database import Database

configs = get_configs()

class Shop(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = Database("database")

    @commands.cooldown(1, 8, commands.BucketType.user)
    @commands.command(name='sh', aliases=['shop', 'market', 'marketplace'])
    async def shop(self, ctx, subcommand=None, *, name=None):
        """
        a command, that let's  users use Nubot's shop

        - if no arguments are given, the bot will display the shop
        - if the buy subcommand is used, the bot will sell the chosen item
        """
        # Get shop data
        shop = get_shop()

        # Display the shop
        if subcommand == None:

            # Create the shop pages
            shop_embeds = []
            for id, data in shop.items():
                for name, inner_data in data.items():
                    item_embed = discord.Embed(title=inner_data['name'], description=inner_data['description'], color=int(configs['colors']['shop'],16))
                    item_embed.add_field(name='Price:', value=f'**{inner_data["price"]}**<:dollars:899250630919606324>\n|================| {len(shop_embeds)+1} |================|')
                    shop_embeds.append(item_embed)

            page = 0

            message = await ctx.send(embed=shop_embeds[0])

            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check_1(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check_1)

                    if str(reaction.emoji) == "▶️" and page < len(shop_embeds)-1:
                        page+=1
                        await message.edit(embed=shop_embeds[page])
                        await message.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️" and page != 0:
                        page-=1
                        await message.edit(embed=shop_embeds[page])
                        await message.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "▶️" and page == len(shop_embeds)-1:
                        page = 0
                        await message.edit(embed=shop_embeds[page])
                        await message.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️" and page == 0:
                        page = len(shop_embeds)-1
                        await message.edit(embed=shop_embeds[page])
                        await message.remove_reaction(reaction, user)

                    else:
                        await message.remove_reaction(reaction, user)

                except asyncio.TimeoutError:
                    await message.delete()
                    break

        # Sell something
        elif subcommand == 'buy' and name != None:

            economy_cells = self.db.view_table(server_id=str(ctx.guild.id), type='economy')
            price = int(shop['shop'][name]['price'])
            
            if float(economy_cells[str(ctx.author.id)]['val']) >= int(price):

                if name == 'Coin Multiplier':
                    try:
                        user_multiplier = self.db.view_table(server_id=str(ctx.guild.id), type='multiplier')[str(ctx.author.id)]['val']
                    except:
                        user_multiplier=0
                    if user_multiplier == 'None':
                        self.db.save_in_table(server_id=str(ctx.guild.id), user_id=str(ctx.author.id), val='0.2', type='multiplier')
                    else:
                        self.db.save_in_table(server_id=str(ctx.guild.id), user_id=str(ctx.author.id), val=str(truncate(float(user_multiplier) + 0.2,1)), type='multiplier')

                    self.db.save_in_table(server_id=str(ctx.guild.id), user_id=str(ctx.author.id), val=str(float(economy_cells[str(ctx.author.id)]['val']) - price), type='economy')
                    buy_embed = discord.Embed(title=f'Succesfuly bought {name}', description=f'for **{price}**<:dollars:899250630919606324>', color=int(configs['colors']['shop'],16))
                    await ctx.send(embed=buy_embed)

                elif name == 'Custom Rank':

                    def check_2(message):
                        return message.author == ctx.author and message.channel == ctx.channel

                    color_question = await ctx.send('What color would you like the rank to be? Supply a HEX code.')
                    color_answer = await self.bot.wait_for('message', check=check_2)

                    chosen_color = color_answer.content[1:len(color_answer.content)]
                    
                    name_question = await ctx.send('What name would you like the rank to have?')
                    name_answer = await self.bot.wait_for('message', check=check_2)

                    try:

                        custom_role = self.db.view_table(server_id=str(ctx.guild.id), type='custom_rank')[str(ctx.author.id)]['val']

                        role_to_change = ctx.guild.get_role(int(custom_role))
                        await role_to_change.edit(name=name_answer.content, colour=discord.Colour(int(chosen_color,16)))

                    except:
                        threshold = discord.utils.get(ctx.guild.roles, name=configs["custom_rank_threshold"])
                        if threshold == None:
                            ctx.send(f"I couldn't find any threshold for my custom ranks! A rank named \"{configs['custom_rank_threshold']}\" should be added")
                            return

                        new_role = await ctx.guild.create_role(name=name_answer.content, hoist=True, colour=discord.Colour(int(chosen_color,16)))
                        await ctx.guild.edit_role_positions(positions={new_role: threshold.position})
                        await ctx.author.add_roles(new_role)
                        self.db.save_in_table(server_id=str(ctx.guild.id), user_id=str(ctx.author.id), val=str(new_role.id), type='custom_rank')

                    self.db.save_in_table(server_id=str(ctx.guild.id), user_id=str(ctx.author.id), val=str(float(economy_cells[str(ctx.author.id)]['val']) - price), type='economy')
                    buy_embed = discord.Embed(title=f'Succesfuly bought {name}', description=f'for **{price}**<:dollars:899250630919606324>', color=int(configs['colors']['shop'],16))
                    await ctx.send(embed=buy_embed)