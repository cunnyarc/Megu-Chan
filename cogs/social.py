import discord
from discord.ext import commands
import json
import random
import datetime

class Social(commands.Cog, name="Social"):
    """:performing_arts: Social"""
    def __init__(self, client):
        self.client = client

        with open('server.json') as f:
            self.users = json.load(f)

    @commands.command(name="level", description="`y! level`")
    async def level(self, ctx, member: discord.User.id = None):
        """Shows the users level"""
        member = ctx.author.id if not member else member

        await ctx.send(self.users[f'{member}']['lvl'])

    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.command(name="daily", description="`y! daily`")
    async def daily(self, ctx):
        """Collects your daily reward"""
        d_exp = random.randint(1, 75)

        self.users[f'{ctx.author.id}']['exp'] += int(d_exp)

        with open('server.json', 'w') as f:
            json.dump(self.users, f, indent=4)

        await ctx.send(f"Congrats you have gained {d_exp} today!")

    @commands.command(name="disabletxt", description="`y! disabletxt`", hidden=True)
    async def disabletxt(self, ctx):
        """Disables level up message"""
        self.users[f'{ctx.author.id}']['msg'] = False

        with open('server.json', 'w') as f:
            json.dump(self.users, f, indent=4)

        await ctx.send("You will no longer be notified when you level!")

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("You've already claimed your daily! Check back tomorrow")


def setup(client):
    client.add_cog(Social(client))
