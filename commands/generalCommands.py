import discord
import json
import bot
from discord.ext import tasks
import requests
from quiz import Quiz
from utils import embed, sep

class GeneralCommands(object):
    def init():
        GeneralCommands.time_out.start()

    @bot.slash.slash(name="hello", description="Just send a message")
    async def hello(ctx):
        await ctx.send(embed=embed("Hello :rainbow_flag:", 0x197A43))

    @bot.slash.slash(name="help", description="Show some useful commands")
    async def help(ctx):
        embed = discord.Embed(title=":loudspeaker: General Commands", color=0xFFFFF)
        embed.add_field(name="/hello", value="Just send a message", inline=False)
        embed.add_field(
            name="/calc [expression]", value="A mini calculator", inline=False
        )
        embed.add_field(
            name="/covid [country_code]",
            value="Get covid info in a specific country",
            inline=False,
        )
        embed.add_field(name="/quiz", value="Try out a math quiz", inline=False)
        await ctx.send(embed=embed)
        embed = discord.Embed(title=":headphones: Music Commands", color=0xFFFFF)
        embed.add_field(
            name="/play [link/search_text]",
            value="Plays your radio/stream of choice or youtube links and searches",
            inline=False,
        )
        embed.add_field(name="/loop", value="Loop the current queue", inline=False)
        embed.add_field(
            name="/lyrics", value="Find lyrics of the current track", inline=False
        )
        embed.add_field(name="/queue", value="Shows the music queue", inline=False)
        embed.add_field(
            name="/remove [index]",
            value="Remove song [index] from the queue",
            inline=False,
        )
        embed.add_field(name="/skip", value="Skip the current song", inline=False)
        embed.add_field(
            name="/stop",
            value="Stop music, clear the queue and leave the bot",
            inline=False,
        )
        await ctx.send(embed=embed)

    @bot.slash.slash(name="calc", description="A mini calculator")
    async def calc(ctx, *, expression):
        try:
            await ctx.send(embed=embed(f" {expression} = {eval(expression)}", 0x1DBBFF))
        except:
            await ctx.send(
                embed=embed(f" {expression} is an invalid expression", 0x1DBBFF)
            )

    @bot.slash.slash(name="covid", description="Get covid info in a specific country")
    async def covid(ctx, *country_code):
        if not country_code:
            gb = json.loads(
                requests.get(
                    "https://api.coronatracker.com/v3/stats/worldometer/global"
                ).text
            )
            vn = json.loads(
                requests.get(
                    "https://api.coronatracker.com/v3/stats/worldometer/country?countryCode=VN"
                ).text
            )[0]
            await ctx.send(
                embed=embed(
                    f'**Global**\nCases: {sep(gb["totalConfirmed"])}\nDeaths: {sep(gb["totalDeaths"])}\nRecovered: {sep(gb["totalRecovered"])}\n\n'
                    f'**Vietnam**\nCases: {sep(vn["totalConfirmed"])}\nDeaths: {sep(vn["totalDeaths"])}\nRecovered: {sep(vn["totalRecovered"])}',
                    0x1DBBFF,
                )
            )
        else:
            ct = json.loads(
                requests.get(
                    f"https://api.coronatracker.com/v3/stats/worldometer/country?countryCode={country_code[0]}"
                ).text
            )[0]
            await ctx.send(
                embed=embed(
                    f'**{ct["country"]}**\nCases: {sep(ct["totalConfirmed"])}\nDeaths: {sep(ct["totalDeaths"])}\nRecovered: {sep(ct["totalRecovered"])}',
                    0x1DBBFF,
                )
            )

    @bot.slash.slash(name="quiz", description="Try out a math quiz")
    async def quiz(ctx):
        await Quiz.newGame(ctx)

    @bot.client.event
    async def on_message(message):
        if message.author == bot.client.user:
            return
        await Quiz.createQuiz(message)
        await bot.client.process_commands(message)

    @tasks.loop(seconds=1)
    async def time_out():
        await Quiz.checkTimeout(bot.client)
