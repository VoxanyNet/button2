import json
import time
import os
from typing import Dict
import datetime
import random

import discord
from discord.ext import tasks

from button2 import commands
from button2.utils import format_elapsed_time, format_elapsed_time_short
from button2 import utils
from button2.high_score import HighScore

class ButtonBot2(discord.Bot):

    DEFAULT_BUTTON_DATA = {
        "target_time": 1000000000000000,
        "high_scores": [],
        "last_fail": time.time()
    }

    def __init__(self, button_data_directory, description=None, *args, **options):

        super().__init__(description, *args, **options)

        self.button_data_directory = button_data_directory

        # create button data file if it doesnt already exist
        if not os.path.exists(f"{self.button_data_directory}/buttondata.json"):

            os.makedirs(self.button_data_directory, exist_ok=True)

            with open(f"{self.button_data_directory}/buttondata.json", "w") as file:
                json.dump(ButtonBot2.DEFAULT_BUTTON_DATA, file)

        with open(f"{self.button_data_directory}/buttondata.json", "r") as file:
            data = json.load(file)

        self.target_time: int = data["target_time"]
        self.high_scores: Dict[HighScore] = data["high_scores"]
        self.last_fail = data["last_fail"]

        self.add_application_command(commands.press)
        self.add_application_command(commands.highscores)
    
    def press_button(self) -> float:

        # the difference in seconds from the target time
        difference: float = self.target_time - time.time()

        self.set_new_target_time()

        return difference

    def set_new_target_time(self):
        # set a new target time between 30 minutes and 24 hours from now
        self.target_time: float = time.time() + random.randrange(1800, 86400)

    async def update_high_score(self, member: discord.Member, score: float) -> bool:
        """Update high score if member has new high score"""

        # a lower high score is considered better

        query = {
            "member_id": member.id
        }

        existing_high_score: HighScore = utils.find_one(query, self.high_scores)
        
        if existing_high_score:

            # if the new high score is lower than the current one, we delete the old one
            if score < existing_high_score["high_score"]:

                utils.delete_one(query, self.high_scores)
            
            # if the new high score is not better than the current one, we dont do anything
            else:
                return

        # add the new high score to the board
        self.high_scores.append( 
            {
                "member_id": member.id,
                "high_score": score
            }
        )

    async def on_ready(self):
        self.check_if_expired.start()
        self.update_status.start()

    @tasks.loop(seconds=5.0)
    async def update_status(self):
        # update user status to show how long since last fail

        time_since_last_fail = time.time() - self.last_fail

        formatted_time_since_last_fail = format_elapsed_time_short(time_since_last_fail)

        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f"for {formatted_time_since_last_fail}")
        )

    @tasks.loop(seconds=5.0)
    async def check_if_expired(self):

        
        # checks if the players missed the target time, which will reset the button to a new target time 
        if time.time() > self.target_time:

            time_since_last_fail = time.time() - self.last_fail

            formatted_time_since_last_fail = format_elapsed_time(time_since_last_fail)

            # update last fail
            self.last_fail = time.time()
            
            self.set_new_target_time()

            # time until the next button expires
            time_until_next_expire = self.target_time - time.time()

            # pretty string representing how much time until the next button needs to be pressed
            formatted_time_until_next_expire = format_elapsed_time(time_until_next_expire)

            channel = await self.fetch_channel(945515760409792546)
            await channel.send(f"You  🚨 **FAILED** 🚨  to press the button before it expired, breaking the streak of **{formatted_time_since_last_fail}**!\n\nThe new button expires in **{formatted_time_until_next_expire}**")


            await self.save_data()

    async def save_data(self):

        data = {
            "target_time": self.target_time,
            "high_scores": self.high_scores,
            "last_fail": self.last_fail
        }

        with open(f"{self.button_data_directory}/buttondata.json", "w") as file:
            json.dump(data, file)