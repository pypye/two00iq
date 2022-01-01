import discord


def embed(text, color):
    return discord.Embed(description=text, color=color)


def sep(number):
    return "{:,}".format(number)
