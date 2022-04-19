# Cog containing Nubot's minesweeper

import discord
from discord import Embed
from discord.ext import commands

import asyncio

from Scripts.utilities import get_configs, truncate, transform_input
from Scripts.database import Database

class Minesweeper_Game():

    def __init__(self, height: int, width: int): # height = number of rows; width = number of columns

        import random

        # Create the grid
        grid = dict()
        for row in range(height):
            for col in range(width):
                grid[(row, col)] = [random.randint(0,5), (row, col), 0, 0]

        # Check how many bombs there are

        bomb_amount=0
        for cell, params in grid.items():
            if not params[0]:
                bomb_amount+=1

        self.grid = grid
        self.columns = width
        self.rows = height
        self.bombs = bomb_amount

        for cell, params in grid.items():
            tile_value = 0
            neighbors = self.neighbor_detection(params[1])
            for neighbor_cell, neighbor_params in neighbors.items():
                if neighbor_params[0] == 0:
                    tile_value+=1
            self.grid[cell][3] = tile_value

    def neighbor_detection(self, coords: tuple) -> dict:

        #  X X X
        #  X 0 X        - Search for the Xs
        #  X X X

        neighbors = {cell: params for (cell, params) in self.grid.items()
        if params[1] == (coords[0]-1, coords[1]-1) 
        or params[1] == (coords[0]-1, coords[1])
        or params[1] == (coords[0]-1, coords[1]+1)
        or params[1] == (coords[0], coords[1]-1)
        or params[1] == (coords[0], coords[1]+1)
        or params[1] == (coords[0]+1, coords[1]-1)
        or params[1] == (coords[0]+1, coords[1])
        or params[1] == (coords[0]+1, coords[1]+1)}

        return neighbors

    def reveal_cell(self, coords: tuple, isRecursion=False) -> bool: # True = the chosen cell was safe; False = the chosen cell was a bomb
        
        try:
            # Reveal the chosen cell, then reveal all of the neighbouring cells that
            # don't have more than one bomb around them, then do the same for the neighbouring cells
            if not isRecursion:
                self.grid[coords][2] = 1 # Uncovers the chosen cell
            for neighbor_cell, neighbor_params in self.neighbor_detection(coords).items():
                if not neighbor_params[2] and neighbor_params[0] and neighbor_params[3] <= 1:
                    neighbor_params[2] = 1
                    self.reveal_cell(neighbor_cell, True)                    
        except Exception as e:
            print(e)
            return True # If the chosen coordinates don't exist, the game continues
        
        if not isRecursion:
            if self.grid[coords][0]:
                return True
            else:
                return False

    def lose(self) -> str:
        # Reveal the whole board
        for cell, params in self.grid.items():
            params[2] = 1
        return f'You\'ve lost!'

    def win(self) -> str:
        # Reveal the whole board
        for cell, params in self.grid.items():
            params[2] = 1
        return f'You\'ve won, there were {self.bombs} bombs!'

    def check_if_won(self) -> bool: # True = the game is won; False = the game continues
        moves_amount=0
        for cell, params in self.grid.items():
            if params[2]:
                moves_amount+=1
        
        if moves_amount+self.bombs == self.columns*self.rows:
            return True
        else:
            return False

    def emoji_renderer(self):

        number_tiles = (
            '<:0_:909427029961748530>',
            '<:1_:909425506288541697>',
            '<:2_:909425554963456040>',
            '<:3_:909425591239966791>',
            '<:4_:909426155331923988>',
            '<:5_:909426206229790770>',
            '<:6_:909426252732059649>',
            '<:7_:909425912892768286>',
            '<:8_:909425806529417247>'
        )

        emoji_render = ''

        tiles = []
        for key, item in self.grid.items():
            tiles.append(item)

        for i in range(self.rows):
            for j in range(self.columns):
                if tiles[i*self.columns+j][2] == 0:
                    emoji_render += '\u25FC'
                elif tiles[i*self.columns+j][0] == 0:
                    emoji_render += '💣'
                else:
                    emoji_render += f'{number_tiles[tiles[i*self.columns+j][3]]}'
            emoji_render += '\n'

        return emoji_render

    def reveal_cells(self):
        """
        Function to reveal the whole board
        """
        for cell, params in self.grid.items():
            params[2] = 1

configs = get_configs()

class Minesweeper(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.db = Database('database')

    @commands.command(name='ms', aliases=['minesweeper'])
    async def minesweeper_game(self, ctx, rows=5, columns=5):

        if (int(rows) < 5 or int(columns) < 5):
            await ctx.send("The board is too small!")
            return

        if (int(rows) > 14 or int(columns) > 14):
            await ctx.send("The board is too big!")
            return
            
        game = Minesweeper_Game(int(rows), int(columns))
        game_embed = discord.Embed(title='Minesweeper', description=game.emoji_renderer(), color=int(configs['colors']['arcade'],16))
        game_embed.add_field(name='You have 60 seconds to move!', value='provide an input like this: \"3.2\".\nTop left corner is 0.0')

        game_display = await ctx.send(embed=game_embed)

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        is_won = False

        # main game loop
        while True:
            try:
                cell_input = await self.bot.wait_for('message', check=check, timeout=60)

                if transform_input(cell_input.content) != False:
                    move = game.reveal_cell(transform_input(cell_input.content))
                    if not move:
                        break
                    is_won = game.check_if_won()
                    if is_won:
                        break
                    new_display = discord.Embed(title='Minesweeper', description=game.emoji_renderer(), color=int(configs['colors']['arcade'],16))
                    new_display.add_field(name='You have 60 seconds to move!', value='provide an input like this: \"3.2\".\nTop left corner is 0.0')
                    await game_display.edit(embed=new_display)
                    await cell_input.delete()

            except asyncio.TimeoutError:
                await game_display.delete()
                break
        
        if is_won:

            game.reveal_cells()

            # non-multiplied award
            plus_cash = 500

            # getting users multiplier
            economy_cells = self.db.view_table(server_id=str(ctx.guild.id), type='economy')
            try:
                user_multiplier = self.db.view_table(server_id=str(ctx.guild.id), type='multiplier')[str(ctx.author.id)]['val']
            except:
                user_multiplier=0

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

            new_display = discord.Embed(title='Minesweeper', description=game.emoji_renderer(), color=0x0DB800)
            new_display.add_field(name='You\'ve won', value=f'You\'ve been awarded **{plus_cash}**<:dollars:899250630919606324>!')
            await game_display.edit(embed=new_display)
        elif not move:
            game.reveal_cells()
            new_display = discord.Embed(title='Minesweeper', description=game.emoji_renderer(), color=0xDB0000)
            new_display.add_field(name='You\'ve lost', value='uncool')
            await game_display.edit(embed=new_display)