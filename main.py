import discord
import bot

from commands.generalCommands import GeneralCommands
from commands.musicCommands import MusicCommands

GeneralCommands.init()
MusicCommands.init()


@bot.client.event
async def on_ready():
    await bot.client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="/help")
    )
    print("Bot is running")
    print("--------------")


bot.client.run('NzQwMTgwNzQxMzgzNjUxMzk4.XylRCA.exZ-rrW84xfGGpjQ0jLd8ujplVI')

