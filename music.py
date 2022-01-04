import discord
import time
from bot import client
from discord.utils import get
from youtube_dl import YoutubeDL

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "outtmpl": "downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "skip_unavailable_fragments": True,
    "hls_use_mpegts": True,
    "hls_prefer_native": True,
    "source_address": "0.0.0.0",
}
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class Music(object):
    musicQueue = {}
    countQueue = {}
    loopEnable = {}
    ctxSave = {}
    inactiveTime = {}

    async def playMusic(ctx, url):
        if not ctx.author.voice:
            await ctx.respond(embed=discord.Embed(description="To use the /play command, you must be connected to a channel.", color=0x9C5FFF))
            return

        voice = get(client.voice_clients, guild=ctx.guild)
        if voice and ctx.author.voice.channel != voice.channel:
            await ctx.respond(embed=discord.Embed(
                description=f"Bot is playing in **#{voice.channel}**. Please join that channel in order to use the /play command.", color=0x9C5FFF))
            return
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)

        audio = None
        if "entries" in info:
            audio = info["entries"][0]["formats"][0]
        elif "formats" in info:
            audio = info["formats"][0]
        else:
            await ctx.respond(embed=discord.Embed(description=f"Can't found that song.", color=0x9C5FFF))
            return

        URL = audio["url"]
        if ctx.guild.id not in Music.musicQueue:
            Music.musicQueue[ctx.guild.id] = []
            Music.countQueue[ctx.guild.id] = 0
        if "entries" not in info:
            Music.musicQueue[ctx.guild.id].append((URL, info["title"], info["webpage_url"], ctx))
            await ctx.respond(embed=discord.Embed(
                title=f'{info["title"]}',
                url=f'{info["webpage_url"]}',
                description=f":arrow_down: Queued by <@{ctx.author.id}>",
                color=0x1DBBFF,
            ))
        else:
            Music.musicQueue[ctx.guild.id].append((
                URL,
                info["entries"][0]["title"],
                info["entries"][0]["webpage_url"],
                ctx,
            ))
            await ctx.respond(embed=discord.Embed(
                title=f'{info["entries"][0]["title"]}',
                url=f'{info["entries"][0]["webpage_url"]}',
                description=f":arrow_down: Queued by <@{ctx.author.id}>",
                color=0x1DBBFF,
            ))

    async def playNext():

        for serverId, value in list(Music.musicQueue.items()):
            
                if Music.countQueue[serverId] < len(Music.musicQueue[serverId]):
                    URL, title, wp_url, ctx = Music.musicQueue[serverId][Music.countQueue[serverId]]
                else:
                    URL, title, wp_url, ctx = Music.musicQueue[serverId][-1]

                voice = get(client.voice_clients, guild=ctx.guild)
                
                if not (voice and voice.is_connected()):
                    channel = ctx.author.voice.channel
                    try:
                        voice = await channel.connect()
                    except Exception as e:
                        print(e)
                
                Music.ctxSave[serverId] = ctx

                if voice and not voice.is_playing():
                    if Music.countQueue[serverId] >= len(Music.musicQueue[serverId]):
                        if serverId in Music.loopEnable:
                            Music.countQueue[serverId] = 0
                            URL, title, wp_url, ctx = Music.musicQueue[serverId][0]
                        else:
                            del Music.countQueue[serverId]
                            del Music.musicQueue[serverId]
                            Music.inactiveTime[serverId] = time.perf_counter()
                            return
                    else:
                        Music.countQueue[serverId] += 1
                        await ctx.send(embed=discord.Embed(title=f"{title}", url=f"{wp_url}", description=":notes: Now playing", color=0x07ABA5))
                        if ctx.guild.id in Music.inactiveTime:
                            del Music.inactiveTime[ctx.guild.id]

                        voice.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
            


    async def getQueue(ctx):
        ans = ""
        if ctx.guild.id not in Music.musicQueue or Music.musicQueue[ctx.guild.id] == 0:
            return await ctx.respond(embed=discord.Embed(description=f"**:musical_note: Music Queue**\nnull", color=0x1DBBFF))

        if Music.countQueue[ctx.guild.id] > 1:
            ans += "**Previous**\n"
            for i in range(0, Music.countQueue[ctx.guild.id] - 1):
                ans += f"{i + 1}. [{Music.musicQueue[ctx.guild.id][i][1]}]({Music.musicQueue[ctx.guild.id][i][2]})\n"

        ans += f"**Now playing**\n{Music.countQueue[ctx.guild.id]}. [{Music.musicQueue[ctx.guild.id][Music.countQueue[ctx.guild.id] - 1][1]}]({Music.musicQueue[ctx.guild.id][Music.countQueue[ctx.guild.id] - 1][2]})\n"

        if len(Music.musicQueue[ctx.guild.id]) - Music.countQueue[ctx.guild.id] >= 1:
            ans += f"**Next**\n"
            for i in range(Music.countQueue[ctx.guild.id], len(Music.musicQueue[ctx.guild.id])):
                ans += f"{i + 1}. [{Music.musicQueue[ctx.guild.id][i][1]}]({Music.musicQueue[ctx.guild.id][i][2]})\n"

        await ctx.respond(embed=discord.Embed(description=f"**:musical_note: Music Queue**\n\n{ans}", color=0x1DBBFF))

    async def loopQueue(ctx):
        if ctx.guild.id in Music.musicQueue:
            if ctx.guild.id not in Music.loopEnable:
                Music.loopEnable[ctx.guild.id] = 1
                await ctx.respond(embed=discord.Embed(description=f":arrows_counterclockwise: Loop enabled.", color=0x9C5FFF))
            else:
                del Music.loopEnable[ctx.guild.id]
                await ctx.respond(embed=discord.Embed(description=f":arrows_counterclockwise: Loop disabled.", color=0x9C5FFF))
        else:
            await ctx.respond(embed=discord.Embed(description=f"Please play music before using /loop command.", color=0x9C5FFF))

    async def remove(ctx, arg):
        if ctx.guild.id in Music.musicQueue:
            if arg <= 0 or arg > len(Music.musicQueue[ctx.guild.id]):
                return
            if arg == Music.countQueue[ctx.guild.id]:
                voice = get(client.voice_clients, guild=ctx.guild)
                await ctx.respond(embed=discord.Embed(
                    title=f"{Music.musicQueue[ctx.guild.id][arg - 1][1]}",
                    url=f"{Music.musicQueue[ctx.guild.id][arg - 1][2]}",
                    description=":x: Removed",
                    color=0x07ABA5,
                ))
                Music.musicQueue[ctx.guild.id].pop(arg - 1)
                Music.countQueue[ctx.guild.id] -= 1

                if len(Music.musicQueue[ctx.guild.id]) == 0:
                    del Music.musicQueue[ctx.guild.id]
                    del Music.countQueue[ctx.guild.id]
                    Music.inactiveTime[ctx.guild.id] = time.perf_counter()

                if voice:
                    voice.stop()
            elif arg < Music.countQueue[ctx.guild.id]:
                await ctx.respond(embed=discord.Embed(
                    title=f"{Music.musicQueue[ctx.guild.id][arg - 1][1]}",
                    url=f"{Music.musicQueue[ctx.guild.id][arg - 1][2]}",
                    description=":x: Removed",
                    color=0x07ABA5,
                ))
                Music.musicQueue[ctx.guild.id].pop(arg - 1)
                Music.countQueue[ctx.guild.id] -= 1

    async def skip(ctx):
        voice = get(client.voice_clients, guild=ctx.guild)
        if voice:
            voice.stop()
            await ctx.respond(embed=discord.Embed(description=f":fast_forward: Music skipped", color=0x9C5FFF))

    async def stopMusic(ctx):
        voice = get(client.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.stop()
            if ctx.guild.id in Music.musicQueue:
                del Music.countQueue[ctx.guild.id]
                del Music.musicQueue[ctx.guild.id]
            if ctx.guild.id in Music.loopEnable:
                del Music.loopEnable[ctx.guild.id]
            Music.inactiveTime[ctx.guild.id] = time.perf_counter()
            await ctx.respond(embed=discord.Embed(description=f":stop_button: Music stopped", color=0x9C5FFF))

    async def checkDisconnect():
        for serverId, value in list(Music.ctxSave.items()):
            voice = get(client.voice_clients, guild=Music.ctxSave[serverId].guild)
            if voice:
                if (serverId in Music.inactiveTime and time.perf_counter() - Music.inactiveTime[serverId] >= 90) or len(voice.channel.members) == 1:
                    await Music.ctxSave[serverId].send(embed=discord.Embed(description=f":white_check_mark: Goodbye!!!", color=0x9C5FFF))
                    await voice.disconnect()
                    del Music.ctxSave[serverId]
                    if serverId in Music.inactiveTime:
                        del Music.inactiveTime[serverId]
                    if serverId in Music.musicQueue:
                        del Music.countQueue[serverId]
                        del Music.musicQueue[serverId]
                    if serverId in Music.loopEnable:
                        del Music.loopEnable[serverId]