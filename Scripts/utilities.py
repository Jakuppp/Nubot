def distort_text(text):
    """
    Distort given string
    ex.
    Eggs are cool => EgGs ARe cOOl
    """
    import random
    text = text.lower()
    output = ''
    for letter in text:
        gen = random.randint(1, 2)
        if gen == 2:
            letter = letter.upper()
        output = output + letter
    return output

################################################################

def get_configs():
    """
    parse the JSON with bot's configuration data
    """
    import json
    with open("Configs\\config.json") as JSON_file:
        return json.load(JSON_file)

################################################################

def get_shop():
    """
    Get shop info from a JSON file
    """
    import json
    with open('Configs\\shop.json') as json_file:
        return json.load(json_file)

################################################################

def get_quotes():
    """
    Get shop info from a JSON file
    """
    import csv
    with open('configs\\quotes.csv') as f:
        f_reader = csv.reader(f, delimiter=',')
        quotes=[]
        for row in f_reader:
            quotes.append((row[0], row[1]))
    return quotes

################################################################

def activity(status, activity_type, activity_name):
    """
    Return needed activity and status based on configuration file
    """
    import discord
    if status == 'online':
        bot_status = discord.Status.online
    elif status == 'offline':
        bot_status = discord.Status.offline
    elif status == 'idle':
        bot_status = discord.Status.idle
    elif status == 'dnd':
        bot_status = discord.Status.dnd
    if activity_type == 'Game':
        bot_activity = discord.Game(name=activity_name)
    elif activity_type == 'listening':
        bot_activity = discord.Activity(type=discord.ActivityType.listening, name=activity_name)
    elif activity_type == 'watching':
        bot_activity = discord.Activity(type=discord.ActivityType.watching, name=activity_name)
    else:
        bot_activity = None
    return bot_status, bot_activity

################################################################

def RNG(min, max):
    """
    Function that generates random numbers
    """
    import random
    return random.randint(min, max)

################################################################

def get_second_element(value):
    return value[1]

################################################################

def truncate(number, decimals=0):
    """
    truncate a given number to the chosen decimal place
    """
    multiplier = 10**decimals
    return int(number * multiplier) / multiplier

################################################################

def transform_input(input: str) -> tuple:
    """
    Function to transform users' minesweeper input. eg. "2.6" -> (2, 6)
    """
    try:
        x, dot, y = input.partition('.')
        out = (int(x), int(y))
        return out
    except Exception as e:
        print(e)
        return False

################################################################

def filter(input_list: list, allowed_elements: list):
    """
    Function that filters out only the chosen elements of a list
    """
    output_list = []
    for element in input_list:
        if element in allowed_elements:
            output_list.append(element)
            
    return output_list

################################################################

def get_mode(input_list: list):
    """
    Get's the mode of a certain list. If there are few modes, the function returns False.
    This is a very slow way to accomplish this, but it gets a mode, which can only be 4 things, so it should be OK
    """

    if len(input_list) == 0:
        return False

    distinguished_elements = {}
    for element in input_list:
        if element not in distinguished_elements:
            distinguished_elements[element] = 0

    # Count all of the elements and save them in a dictionary     
    for key, value in distinguished_elements.items():
        distinguished_elements[key] = input_list.count(key)

    # Get the mode
    max_key = None
    max_value = 0
    for key, value in distinguished_elements.items():
        if value > max_value:
            max_key = key
            max_value = value

    # If there's a second mode, return False
    for key, value in distinguished_elements.items():
        if value == max_value and key != max_key:
            return False
            
    return max_key

################################################################

class Clock:
    """
    Simple clock for games like Snake
    """
    def __init__(self):
        self.time = 0
    def progress(self, time_jump: int):
        self.time += time_jump
    def reset(self):
        self.time = 0
    def set_time(self, time_to_set: int):
        self.time = time_to_set

################################################################