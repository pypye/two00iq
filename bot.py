import discord

intents = discord.Intents().all()
intents.members = True
client = discord.Bot(intents=intents)
