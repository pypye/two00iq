import discord
from commands.generalCommands import GeneralCommands
from bot import client
from commands.musicCommands import MusicCommands

GeneralCommands.init()
MusicCommands.init()


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help"))
    print("Bot is running")
    print("--------------")


client.run("[Put token here]")
