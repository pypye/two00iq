from bot import client
from music import Music
from discord.ext import tasks


class MusicCommands(object):

    def init():
        MusicCommands.music_playing.start()
        MusicCommands.music_check_stop.start()

    @client.slash_command(name="play", description="Plays your radio/stream of choice or youtube links and searches")
    async def play(ctx, song: str):
        await Music.playMusic(ctx, song)

    @client.slash_command(name="stop", description="Stop music, clear the queue and leave the bot")
    async def stop(ctx):
        await Music.stopMusic(ctx)

    @client.slash_command(name="queue", description="Shows the music queue")
    async def queue(ctx):
        await Music.getQueue(ctx)

    @client.slash_command(name="loop", description="Loop the current queue")
    async def loop(ctx):
        await Music.loopQueue(ctx)

    @client.slash_command(name="skip", description="Skip the current song")
    async def skip(ctx):
        await Music.skip(ctx)

    @client.slash_command(name="remove", description="Remove song [index] from the queue")
    async def remove(ctx, index: int):
        await Music.remove(ctx, index)

    @tasks.loop(seconds=1)
    async def music_playing():
        await Music.playNext()

    @tasks.loop(seconds=1)
    async def music_check_stop():
        await Music.checkDisconnect()