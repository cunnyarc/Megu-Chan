import discord
from discord.ext import commands
import asyncio


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


def setup(client):
    client.add_cog(Fun(client))
