# Cog with Nubot's snake

import discord
from discord import Embed
from discord.ext import commands, tasks

import random, asyncio

from Scripts.utilities import get_configs, filter, get_mode, Clock

# A class that represents a single cell inside a grid
class Cell:
    def __init__(self, coordinates: tuple, state: str):
        self.coordinates = coordinates

        # State is presented as a single character
        # b - blank
        # a - apple
        # h - snake's head
        # s - snake's body
        self.state = state

class Snake_Game:

    def __init__(self, rows, columns):

        self.rows = rows
        self.columns = columns

        self.grid = []

        for row in range(rows):
            for column in range(columns):
                self.grid.append(Cell((row, column), "b"))

        # Emojis' unicodes
        self.emojis = {
            "b": "\U00002B1B",
            "a": "\U0001F7E5",
            "s": "\U0001F7E2",
            "h": "\U0001F7E9"
        }

    def update_grid(self) -> str:
        """
        Function that turns the grid into a string of emojis
        """

        formated_string = ""

        for row in range(0, self.rows):
            for column in range(self.columns):
                # self.emojis[self.grid[row*self.columns+column].state] concatenates the right unicode character, based on the state, of a specific cell 
                formated_string = formated_string + self.emojis[self.grid[row*self.columns+column].state]
            formated_string += "\n"

        return formated_string

    def gbc(self, coordinates: tuple):
        """
        gbc - get by coordinates
        Returns the index of a specific cell, given its coordinates
        """
        return coordinates[0]*self.columns + coordinates[1]

    def up(self, index_or_coordinates, times=1):
        """
        Get the index of a cell above certain coordinates or index
        """
        if type(index_or_coordinates) == tuple:
            index_or_coordinates = self.gbc(index_or_coordinates)
        return index_or_coordinates-self.columns*times

    def down(self, index_or_coordinates, times=1):
        """
        Get the index of a cell below certain coordinates or index
        """
        if type(index_or_coordinates) == tuple:
            index_or_coordinates = self.gbc(index_or_coordinates)
        return index_or_coordinates+self.columns*times

    def left(self, index_or_coordinates, times=1):
        """
        Get the index of a cell left to certain coordinates or index
        """
        if type(index_or_coordinates) == tuple:
            index_or_coordinates = self.gbc(index_or_coordinates)
        return index_or_coordinates-times

    def right(self, index_or_coordinates, times=1):
        """
        Get the index of a cell right to certain coordinates or index
        """
        if type(index_or_coordinates) == tuple:
            index_or_coordinates = self.gbc(index_or_coordinates)
        return index_or_coordinates+times


    def initialize_snake(self, direction):
        """
        Function, that sets up the snake
        """
        # Sides of the board, from which the snake can teleport
        self.can_teleport_from = []

        # Self-explanatory
        self.growing = False
        self.score = 0

        # self.direction can only be:
        # - "up"
        # - "down"
        # - "left"
        # - "right"
        self.direction = direction

        # Put the head in the middle of the board
        self.head = self.grid[self.gbc((5,5))]

        # This list stores all of the cells, that the snake is made of
        self.body = [self.head, self.grid[self.left(self.head.coordinates)], self.grid[self.left(self.head.coordinates, times=2)], self.grid[self.left(self.head.coordinates, times=3)]]

        # Last part of snake's body
        self.tail = self.body[-1]

        # Set the correct state to all cells in self.body
        self.head.state = "h"
        for i in range(1, len(self.body)):
            self.body[i].state = "s"

    def move(self):
        """
        Function that moves the snake in the currently chosen direction
            if it returns 0, the game goes on,
            if 1 is returned, the game was lost
        """
        if self.growing:
            # Make the duplicate of the last cell in self.body and append it
            self.body.append(self.tail)
            self.growing = False

        # Save heads position before the move and make it dissapear
        temp_head = self.head
        self.head.state = "b"

        # This decides on where the snake is going to teleport
        if self.direction in self.can_teleport_from:
            if self.direction == "up" and "up" in self.can_teleport_from:
                self.head = self.grid[self.down(self.head.coordinates, times=self.rows-1)]
            elif self.direction == "down" and "down" in self.can_teleport_from:
                self.head = self.grid[self.up(self.head.coordinates, times=self.rows-1)]
            elif self.direction == "left" and "left" in self.can_teleport_from:
                self.head = self.grid[self.right(self.head.coordinates, times=self.columns-1)]
            elif self.direction == "right" and "right" in self.can_teleport_from:
                self.head = self.grid[self.left(self.head.coordinates, times=self.columns-1)]
        else:
            # If the snake isn't teleporting, move the head in the current direction
            if self.direction == "right":
                self.head = self.grid[self.right(self.head.coordinates)]
            elif self.direction == "left":
                self.head = self.grid[self.left(self.head.coordinates)]
            elif self.direction == "up":
                self.head = self.grid[self.up(self.head.coordinates)]
            else:
                self.head = self.grid[self.down(self.head.coordinates)]

        # Check if the head encounters an apple
        if self.head.state == "a":
            self.score += 1
            self.spawn_apple()
            self.growing = True
            # Get the newest tail
            self.tail = self.body[-1]

        if self.check_if_lost():
            # Make the head go back to it's last spot, and reveal it
            self.head = temp_head
            self.head.state = "h"
            return 1

        # Reveal the head and update it in self.body
        self.head.state = "h"
        self.body[0] = self.head

        for i in range(1, len(self.body)):
            if i != 1:
                # Save the position of the cell in self.body[i]
                before = self.body[i]
                # Blank the cell
                self.body[i].state = "b"
                # Set the index to the earlier position of the cell of index i-1
                self.body[i] = temp_body
                self.body[i].state = "s"
                # Save the cell of index i
                temp_body = before
            else:
                # Save the position of the current cell in self.body[i]
                temp_body = self.body[i]
                # Blank the index
                self.body[i].state = "b"
                # Set the cellx to the position of the head before the move
                self.body[i] = temp_head
                self.body[i].state = "s"

        # Force the cells from self.body into self.grid
        for j in range(1, len(self.body)):
            self.grid[self.gbc(self.body[j].coordinates)] = self.body[j]

        self.can_teleport_from = []

        # Check from which sides the snake can teleport
        if self.head.coordinates[0] == 0:
            self.can_teleport_from.append("up")
        if self.head.coordinates[0] == self.rows-1:
            self.can_teleport_from.append("down")
        if self.head.coordinates[1] == 0:
            self.can_teleport_from.append("left")
        if self.head.coordinates[1] == self.columns-1:
            self.can_teleport_from.append("right")

        return 0
            
    def spawn_apple(self):
        # Check where apples can be spawned
        free_space = []
        for cell in self.grid:
            if cell not in self.body and cell.state != "a":
                free_space.append(cell)
        # Chose a random spot out of the free space, and make it an apple
        if (len(free_space)!=0):
            self.grid[self.gbc(free_space[random.randint(0, len(free_space))].coordinates)].state = "a"

    def check_if_lost(self):
        if self.head.state == "s":
            return True
        else:
            return False

configs = get_configs()

# Since classes are passed by reference in Python, data about the game state is stored in a class. This allows the main game task to communicate with the input task
class Snake_Data:
    def __init__(self):
        self.game_on = True

class Snake(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def output_task(self, display, game_object: Snake_Game, game_data: Snake_Data, clock: Clock):
        clock.reset()
        try:
            while True:
                await asyncio.sleep(1)
                # The user was timed out
                if clock.time > 100:
                    updated_display = discord.Embed(title=f'Snake     Score: {game_object.score}', description=game_object.update_grid(), color=0xDB0000)
                    updated_display.add_field(name="Timed Out", value=f"Your score was: {game_object.score}")
                    await display.edit(embed=updated_display)
                    game_data.game_on = False
                    return
                # Game continues
                if game_object.move() == 0:
                    updated_display = discord.Embed(title=f'Snake     Score: {game_object.score}', description=game_object.update_grid(), color=int(configs['colors']['arcade'],16))
                    updated_display.add_field(name="How to play", value="• Collect apples to increase your score\n• Change snake's direction by reacting.\n• After chosing the direction, you must manually delete the reaction (You can change the direction infinitely).\n• If no moves are registered for around 100 seconds, the game stops.\n Have fun!")
                    await display.edit(embed=updated_display)
                # The game was lost
                else:
                    updated_display = discord.Embed(title=f'Snake     Score: {game_object.score}', description=game_object.update_grid(), color=0xDB0000)
                    updated_display.add_field(name="Game Over", value=f"Your score was **{game_object.score}**")
                    await display.edit(embed=updated_display)
                    game_data.game_on = False
                    return
        # In case something goes wrong, stop the input task
        except Exception as e:
            print(e)
            game_data.game_on == False

    async def input_task(self, display, game_object: Snake_Game, game_data: Snake_Data, clock: Clock):
        while True:
            # If the game was lost stop running the input task
            if game_data.game_on == False:
                return
            
            clock.progress(0.1)
            reactions = display.reactions
            reactions_content = []

            for reaction in reactions:
                for i in range(reaction.count):
                    reactions_content.append(reaction.emoji)

            most_voted = get_mode(filter(reactions_content, ["◀️", "🔼", "▶️", "🔽"]))
            # If there was no most-voted move option (most_voted==False), do nothing
            if most_voted != False:
                saved_direction = game_object.direction
                if most_voted == "◀️" and game_object.direction != "right":
                    game_object.direction = "left"
                elif most_voted == "▶️" and game_object.direction != "left":
                    game_object.direction = "right"
                elif most_voted == "🔼" and game_object.direction != "down":
                    game_object.direction = "up"
                elif most_voted == "🔽" and game_object.direction != "up":
                    game_object.direction = "down"
                
                # If the direction was changed, reset the clock
                if game_object.direction != saved_direction:
                    clock.reset()

            await asyncio.sleep(0.1)

    @commands.command(name="sn", aliases=["snake"])
    async def snake_game(self, ctx):
        snake_clock = Clock()
        snake_data = Snake_Data()

        # Start the game, and spawn in the entities
        g = Snake_Game(11,11)
        g.initialize_snake("right")
        g.spawn_apple()
        g.spawn_apple()
        g.spawn_apple()
        
        game_embed = discord.Embed(title=f'Snake     Score: {g.score}', description=g.update_grid(), color=int(configs['colors']['arcade'],16))
        game_embed.add_field(name="How to play", value="• Collect apples to increase your score\n• Change snake's direction by reacting.\n• After chosing the direction, you must manually delete the reaction (You can change the direction infinitely).\n•If no moves are registered for around 100 seconds, the game stops.\n Have fun!")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️", "🔼", "🔽"]

        game_display = await ctx.send(embed=game_embed)

        await game_display.add_reaction("◀️")
        await game_display.add_reaction("🔼")
        await game_display.add_reaction("▶️")
        await game_display.add_reaction("🔽")

        # Getting the message from the cache lets you get the reactions
        cached_display = discord.utils.get(self.bot.cached_messages, id=game_display.id)

        output_task = asyncio.create_task(self.output_task(cached_display, g, snake_data, snake_clock))
        input_task = asyncio.create_task(self.input_task(cached_display, g, snake_data, snake_clock))

        await output_task
        await input_task