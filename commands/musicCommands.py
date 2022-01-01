from discord.ext import tasks
from discord_slash.context import SlashContext
import bot

from music import Music


class MusicCommands(object):
    def init():
        MusicCommands.music_playing.start()
        MusicCommands.music_check_stop.start()

    @bot.slash.slash(
        name="play",
        description="Plays your radio/stream of choice or youtube links and searches",
    )
    async def play(ctx, *, song):
        await Music.playMusic(ctx, song)

    @bot.slash.slash(
        name="stop", description="Stop music, clear the queue and leave the bot"
    )
    async def stop(ctx):
        await Music.stopMusic(bot.client, ctx)

    @bot.slash.slash(name="queue", description="Shows the music queue")
    async def queue(ctx):
        await Music.getQueue(ctx)

    @bot.slash.slash(name="loop", description="Loop the current queue")
    async def loop(ctx):
        await Music.loopQueue(ctx)

    @bot.slash.slash(name="skip", description="Skip the current song")
    async def skip(ctx):
        await Music.skip(bot.client, ctx)

    @bot.slash.slash(name="remove", description="Remove song [index] from the queue")
    async def remove(ctx, index):
        await Music.remove(bot.client, ctx, int(index))

    @bot.slash.slash(name="lyrics", description="Find lyrics of the current track")
    async def lyrics(ctx):
        await Music.getLyrics(ctx)

    @tasks.loop(seconds=1)
    async def music_playing():
        await Music.playNext(bot.client)

    @tasks.loop(seconds=1)
    async def music_check_stop():
        await Music.checkDisconnect(bot.client)
