import discord
import json
import requests

from bot import client
from discord.ext import tasks

from quiz import Quiz


class GeneralCommands(object):

    def init():
        GeneralCommands.checkQuizTimeOut.start()

    @client.slash_command(name="hello", description="Just send a message")
    async def hello(ctx, name: str = None):
        name = name or ctx.author.name
        await ctx.respond(embed=discord.Embed(description=f"Hello {name}!", color=0x197A43))

    @client.slash_command(name="help", description="Show some useful commands")
    async def help(ctx):
        embed = discord.Embed(title=":loudspeaker: General Commands", color=0xFFFFF)
        embed.add_field(name="/hello", value="Just send a message", inline=False)
        embed.add_field(name="/calc [expression]", value="A mini calculator", inline=False)
        embed.add_field(name="/covid [country_code]", value="Get covid info in a specific country", inline=False)
        embed.add_field(name="/quiz", value="Try out a math quiz", inline=False)
        await ctx.respond(embed=embed)

        embed = discord.Embed(title=":headphones: Music Commands", color=0xFFFFF)
        embed.add_field(name="/play [link/search_text]", value="Plays your radio/stream of choice or youtube links and searches", inline=False)
        embed.add_field(name="/loop", value="Loop the current queue", inline=False)
        embed.add_field(name="/queue", value="Shows the music queue", inline=False)
        embed.add_field(name="/remove [index]", value="Remove song [index] from the queue", inline=False)
        embed.add_field(name="/skip", value="Skip the current song", inline=False)
        embed.add_field(name="/stop", value="Stop music, clear the queue and leave the bot", inline=False)
        await ctx.respond(embed=embed)

    @client.slash_command(name="calc", description="A mini calculator")
    async def calc(ctx, expression: str):
        try:
            await ctx.respond(embed=discord.Embed(description=f" {expression} = {eval(expression)}", color=0x1DBBFF))
        except:
            await ctx.respond(embed=discord.Embed(description=f" {expression} is an invalid expression", color=0x1DBBFF))

    @client.slash_command(name="covid", description="Get covid info in a specific country")
    async def covid(ctx, country_code: str = None):
        head = "https://api.coronatracker.com/v3/stats/worldometer/"
        if country_code == None:
            gb = json.loads(requests.get(f"{head}global").text)
            vn = json.loads(requests.get(f"{head}country?countryCode=VN").text)[0]
            await ctx.respond(embed=discord.Embed(
                description=
                f'**Global**\nCases: {sep(gb["totalConfirmed"])}\nDeaths: {sep(gb["totalDeaths"])}\nRecovered: {sep(gb["totalRecovered"])}\n\n'
                f'**Vietnam**\nCases: {sep(vn["totalConfirmed"])}\nDeaths: {sep(vn["totalDeaths"])}\nRecovered: {sep(vn["totalRecovered"])}',
                color=0x1DBBFF,
            ))
        else:
            ct = json.loads(requests.get(f"{head}country?countryCode={country_code}").text)[0]
            await ctx.respond(embed=discord.Embed(
                description=
                f'**{ct["country"]}**\nCases: {sep(ct["totalConfirmed"])}\nDeaths: {sep(ct["totalDeaths"])}\nRecovered: {sep(ct["totalRecovered"])}',
                color=0x1DBBFF,
            ))

    @client.slash_command(name="quiz", description="Try out a math quiz")
    async def quiz(ctx):
        await Quiz.newGame(ctx)

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        await Quiz.createQuiz(message)

    @tasks.loop(seconds=1)
    async def checkQuizTimeOut():
        await Quiz.checkTimeout()


def sep(number):
    return "{:,}".format(number)
