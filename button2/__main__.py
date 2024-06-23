import os

from button2 import bot

BOT_DISCORD_TOKEN = os.environ["BOT_DISCORD_TOKEN"] 
BOT_DATA_DIRECTORY = os.environ["BOT_DATA_DIRECTORY"]

bot = bot.ButtonBot2(BOT_DATA_DIRECTORY)

bot.run(BOT_DISCORD_TOKEN)