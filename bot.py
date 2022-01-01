import discord
from discord.ext import commands
from discord_slash.client import SlashCommand

intents = discord.Intents().default()
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(client, sync_commands=True)
client.remove_command("help")
