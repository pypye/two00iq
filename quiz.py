import math
import random
import time
from utils import embed


class Expression(object):
    OPS = ["+", "-", "*"]
    GROUP_PROB = 0.2

    def __init__(self, maxNumbers, MIN_NUM, MAX_NUM, _maxdepth=None, _depth=0):
        if _maxdepth is None:
            _maxdepth = math.log(maxNumbers, 2) - 1
        if _depth < _maxdepth and random.randint(0, _maxdepth) > _depth:
            self.left = Expression(maxNumbers, MIN_NUM, MAX_NUM, _maxdepth, _depth + 1)
        else:
            self.left = random.randint(MIN_NUM, MAX_NUM)
        if _depth < _maxdepth and random.randint(0, _maxdepth) > _depth:
            self.right = Expression(maxNumbers, MIN_NUM, MAX_NUM, _maxdepth, _depth + 1)
        else:
            self.right = random.randint(MIN_NUM, MAX_NUM)
        self.grouped = random.random() < Expression.GROUP_PROB
        self.operator = random.choice(Expression.OPS)

    def __str__(self):
        s = "{0!s} {1} {2!s}".format(self.left, self.operator, self.right)
        return "({0})".format(s) if self.grouped else s


class QuizInfo(object):
    def __init__(
        self,
        level=1,
        playerId="",
        answer="",
        expression="",
        channelId="",
        startTime=0,
        endTime=0,
    ):

        self.level = level
        self.playerId = playerId
        self.answer = answer
        self.expression = expression
        self.channelId = channelId
        self.startTime = startTime
        self.endTime = endTime


class Quiz(object):
    quiz = {}

    def reset(id):
        del Quiz.quiz[id]

    async def newGame(ctx):
        if ctx.guild.id not in Quiz.quiz:
            Quiz.quiz[ctx.guild.id] = QuizInfo()

        if Quiz.quiz[ctx.guild.id].playerId == "":
            Quiz.quiz[ctx.guild.id] = QuizInfo(
                1,
                ctx.author.id,
                "",
                str(Expression(4, 1, 10 * Quiz.quiz[ctx.guild.id].level)),
                ctx.channel.id,
                time.perf_counter(),
                0,
            )
            await ctx.send(
                embed=embed(
                    f"<@{ctx.author.id}> Start a quiz. Reply to answer!", 0x1DBBFF
                )
            )
            await ctx.send(
                embed=embed(
                    f"<@{ctx.author.id}> Level {Quiz.quiz[ctx.guild.id].level}: {Quiz.quiz[ctx.guild.id].expression}",
                    0x1DBBFF,
                )
            )
            Quiz.quiz[ctx.guild.id].answer = eval(Quiz.quiz[ctx.guild.id].expression)
        else:
            await ctx.send(
                embed=embed(
                    f"<@{ctx.author.id}> Game is being played by <@{Quiz.quiz[ctx.guild.id].playerId}>. Wait it be completed!",
                    0x9C5FFF,
                )
            )

    async def createQuiz(message):
        if message.guild.id not in Quiz.quiz:
            Quiz.quiz[message.guild.id] = QuizInfo()
        if Quiz.quiz[message.guild.id].playerId == message.author.id:
            if str(Quiz.quiz[message.guild.id].answer) == message.content:
                Quiz.quiz[message.guild.id].level += 1
                Quiz.quiz[message.guild.id].expression = str(
                    Expression(4, 1, 10 * Quiz.quiz[message.guild.id].level)
                )
                Quiz.quiz[message.guild.id].endTime = time.perf_counter()
                await message.channel.send(
                    embed=embed(
                        f"<@{message.author.id}> Correct! Time: {str(round(Quiz.quiz[message.guild.id].endTime - Quiz.quiz[message.guild.id].startTime, 2))}s",
                        0x1DBBFF,
                    )
                )
                await message.channel.send(
                    embed=embed(
                        f"<@{message.author.id}> Level {Quiz.quiz[message.guild.id].level}: {Quiz.quiz[message.guild.id].expression}",
                        0x1DBBFF,
                    )
                )
                Quiz.quiz[message.guild.id].startTime = Quiz.quiz[
                    message.guild.id
                ].endTime
                Quiz.quiz[message.guild.id].answer = eval(
                    Quiz.quiz[message.guild.id].expression
                )
            else:
                Quiz.quiz[message.guild.id].endTime = time.perf_counter()
                await message.channel.send(
                    embed=embed(
                        f"<@{message.author.id}> Incorrect! Time: {str(round(Quiz.quiz[message.guild.id].endTime - Quiz.quiz[message.guild.id].startTime, 2))}s \n{Quiz.quiz[message.guild.id].expression} = {Quiz.quiz[message.guild.id].answer}",
                        0x1DBBFF,
                    )
                )
                if Quiz.quiz[message.guild.id].level != 1:
                    await message.channel.send(
                        embed=embed(
                            f"Game over! <@{Quiz.quiz[message.guild.id].playerId}> got {Quiz.quiz[message.guild.id].level - 1} points.",
                            0x9C5FFF,
                        )
                    )
                else:
                    await message.channel.send(
                        embed=embed(
                            f"Game over! <@{Quiz.quiz[message.guild.id].playerId}> got {Quiz.quiz[message.guild.id].level - 1} point.",
                            0x9C5FFF,
                        )
                    )
                Quiz.reset(message.guild.id)

    async def checkTimeout(client):
        for id, value in list(Quiz.quiz.items()):
            if (
                Quiz.quiz[id].channelId != ""
                and Quiz.quiz[id].playerId != ""
                and time.perf_counter() - Quiz.quiz[id].startTime >= 30
            ):
                channel = client.get_channel(Quiz.quiz[id].channelId)
                if Quiz.quiz[id].level != 1:
                    await channel.send(
                        embed=embed(
                            f"30 seconds time out!. You can make a new game\n"
                            f"{Quiz.quiz[id].expression} = {Quiz.quiz[id].answer}\n"
                            f"Game over! <@{Quiz.quiz[id].playerId}> got {Quiz.quiz[id].level - 1} points.",
                            0x9C5FFF,
                        )
                    )
                else:
                    await channel.send(
                        embed=embed(
                            f"30 seconds time out!. You can make a new game\n"
                            f"{Quiz.quiz[id].expression} = {Quiz.quiz[id].answer}\n"
                            f"Game over! <@{Quiz.quiz[id].playerId}> got {Quiz.quiz[id].level - 1} point.",
                            0x9C5FFF,
                        )
                    )
                Quiz.reset(id)
