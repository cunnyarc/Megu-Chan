import discord
from discord.ext import commands
import asyncio
import random

class Fun(commands.Cog, name='Fun'):
    def __init__(self, client):
        self.client = client

    @commands.command(name="bigtext", description=">bigtext <text>")
    async def big_text(self, ctx, *, text: list):
        """Generates text with regional indicators"""
        for i in range(len(text)):

            if not str.isascii(str(text[i])):
                continue

            if str.isspace(text[i]):
                continue

            if text[i] == "?":
                text[i] = ":question:"
                continue

            if not str.isalpha(text[i]):
                text[i] = ""
                continue

            if text[i] == "!":
                text[i] = ":exclamation:"
                continue

            text[i] = f":regional_indicator_{str(text[i])}:"

        await ctx.send("".join(text))

    @commands.command(name="lenny", description="`y! lenny")
    async def lenny(self, ctx):
        """Sends a lenny face"""
        message = ctx.message

        await discord.Message.delete(message)
        await ctx.send("( ͡° ͜ʖ ͡°)")

    @commands.command(name="flip", description="`y! flip")
    async def flip(self, ctx):
        """Flips a coin"""

        coin = ["regional_indicator_h", "regional_indicator_t"]
        outcome = random.choice(coin)
        reactions = ["regional_indicator_h", "regional_indicator_t"]
        flip = discord.Embed(color=0xbc25cf, title=f"{ctx.author} wants to flip a coin!",
                             description="heads or tails?")

        message = await ctx.send(embed=flip)

        for r in reactions:
            await message.add_reaction(emoji=r)

        def check(reaction):
            return reaction == ctx.message.author and str(reaction.add) == "regional_indicator_h" or "regional_indicator_t"

        try:
            reaction = await self.client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await message.edit(content="Looks like you didn't want to play :disappointed:")
        else:
            if reaction == outcome:
                await message.edit(content="Congrats! You won!")

            else:
                await message.edit(content=f"Ouch, better luck next time it was {outcome[-19:]}")

    @commands.command(name="rateme", description="`y! rateme [user]`")
    async def rateme(self, ctx, user=None):
        """Rates a user from 1-10"""
        user = ctx.author if not user else user
        rating = random.randint(1, 10)

        emb = discord.Embed(color=0xbc25cf, description=f"I rate {user.mention} a {rating}/10")
        emb.set_image(url=user.avatar_url)

        await ctx.send(embed=emb)

    @commands.command(name="fortune", description="`y! fortune")
    async def fortune(self, ctx, *, question=None):
        """It's an 8ball"""

        outcomes = ["Positive", "Neutral", "Negative"]
        replyPos = ["It is certain!~", "Without a doubt!", "Definitely!", "Outlook good!"]
        replyNeu = ["Reply hazy, try again later", "Ask again later", "Better not tell you now"]
        replyNeg = ["Don't count on it...", "I'd say no...", "Very doubtful..."]

        if len(question) <= 5 or " " not in question:
            return

        # Outcome generator
        outcome = random.choice(outcomes)

        if outcome == "Positive":
            color = discord.Color.green()
            outcome = random.choice(replyPos)

        if outcome == "Neutral":
            color = 0xffff00
            outcome = random.choice(replyNeu)

        if outcome == "Negative":
            color = discord.Color.red()
            outcome == random.choice(replyNeg)

        emb = discord.Embed(color=color, description=outcome, title=f"🎱 {ctx.author.mention} Your Fortune Is...")
        emb.set_image(url=ctx.author.avatar_url)

        await ctx.send(emb)

def setup(client):
    client.add_cog(Fun(client))
