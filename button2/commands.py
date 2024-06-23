import random
import time
import asyncio

import discord

from button2.utils import format_elapsed_time
from button2.high_score import HighScore

@discord.commands.application_command(description="Press the button")
async def press(ctx: discord.ApplicationContext):
    
    difference = ctx.bot.press_button()
    
    # if the difference is less than zero that means they missed it
    if difference < 0:
        formatted_time_until_next_expire = format_elapsed_time(time.time() - ctx.bot.target_time)
        await ctx.respond(f"You  🚨 **FAILED** 🚨  to press the button before it expired.\n\nThe new button expires in **{formatted_time_until_next_expire}**")

        return
    
    await ctx.bot.update_high_score(ctx.author, difference)

    # send response
    formatted_difference = format_elapsed_time(difference)

    # send different responses based on how close they were

    if difference <= 1:
        response = f"<@{ctx.author.id}> pressed the button, with an 🎇 __***BUTT CLENCHING***__ 🎇 **{formatted_difference}** left!"

    elif difference <= 5:
        response = f"<@{ctx.author.id}> pressed the button, with an 🎆 ***TERRIFYING*** 🎆 **{formatted_difference}** left!"

    elif difference <= 10:
        response = f"<@{ctx.author.id}> pressed the button, with an 🎉 **AMAZING** 🎉 **{formatted_difference}** left!"

    elif difference <= 60:
        response = f"<@{ctx.author.id}> pressed the button, with an **respectable** **{formatted_difference}** left!"    

    elif difference >= 10800:
        response = f"<@{ctx.author.id}> pressed the button, with an **laughably bad** **{formatted_difference}** left."      
    
    elif difference >= 7200:
        response = f"<@{ctx.author.id}> pressed the button, with an **very unimpressive** **{formatted_difference}** left." 

    elif difference >= 3600:
        response = f"<@{ctx.author.id}> pressed the button, with an **unimpressive** **{formatted_difference}** left." 
       

    else:
        response = f"<@{ctx.author.id}> pressed the button, with **{formatted_difference}** left!"   

    await ctx.respond(
        response
    )

    await ctx.channel.send(f"The button has been reset and will now expire in **{format_elapsed_time(ctx.bot.target_time - time.time())}**")

    await ctx.bot.save_data()

@discord.commands.application_command(description="Display high scores")
async def highscores(ctx: discord.ApplicationContext):

    high_scores_embed = discord.Embed(title="High Scores")

    sorted_high_scores = sorted(
        ctx.bot.high_scores,
        key = lambda high_score: high_score["high_score"],
        reverse=False
    )

    print(sorted_high_scores)

    for high_score in sorted_high_scores:
        high_score: HighScore

        member = await ctx.guild.fetch_member(high_score["member_id"])
        
        formatted_high_score = format_elapsed_time(high_score["high_score"])

        high_scores_embed.add_field(
            name = formatted_high_score,
            value = member.mention,
            inline=False
        )
    
    await ctx.respond(embed=high_scores_embed)


