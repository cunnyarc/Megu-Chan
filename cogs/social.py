import discord
from discord.ext import commands
import json
import random
import datetime
import main

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
        await self.lvl_up(ctx.author, ctx)

    @commands.command(name="disabletxt", description="`y! disabletxt`", hidden=True)
    async def disabletxt(self, ctx):
        """Disables level up message"""
        self.users[f'{ctx.author.id}']['msg'] = False

        with open('server.json', 'w') as f:
            json.dump(self.users, f, indent=4)

        await ctx.send("You will no longer be notified when you level!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.content) < 5 or message.author.bot or 'm! ' in message.content:
            return

        if "https://discord.gg" in message.content:
            await discord.Message.delete(message)
            emb = discord.Embed(color=0xbc25cf, timestamp=datetime.datetime.utcnow(), title=":bangbang: Invite Deleted",
                                description=f"An invite was sent by {message.author.mention} in {message.channel}")
            emb.set_thumbnail(url=message.author.avatar_url)
            emb.set_footer(text=f"ID: {message.author.id}")

            await main.logging_channel.send(embed=emb)

        await self.update_data(message.author)
        await self.lvl_up(message.author, message.channel)

        self.users[f'{message.author.id}']['exp'] += 1

        with open('server.json', 'w') as f:
            json.dump(self.users, f, indent=4)

    async def update_data(self, user):
        if f'{user.id}' not in self.users:
            print('adding new user')
            print('===================')
            self.users[f'{user.id}'] = {}
            self.users[f'{user.id}']['lvl'] = 1
            self.users[f'{user.id}']['exp'] = 0
            self.users[f'{user.id}']['resp'] = 0
            self.users[f'{user.id}']['bal'] = 0
            self.users[f'{user.id}']['msg'] = True
            self.users[f'{user.id}']['inv'] = {}

    async def lvl_up(self, user, ctx):
        cur_exp = self.users[f'{user.id}']['exp']
        cur_lvl = self.users[f'{user.id}']['lvl']

        if cur_exp >= cur_lvl * 43:
            self.users[f'{user.id}']['lvl'] += 1
            self.users[f'{user.id}']['exp'] = 0

            with open('server.json', 'w') as f:
                json.dump(self.users, f, indent=4)

            if self.users[f'{user.id}']['msg'] is True:
                await ctx.send(f"{user.mention} just leveled up to level {self.users[f'{user.id}']['lvl']} \n"
                               f":information_source: `y! disabletext` to disable this message")

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("You've already claimed your daily! Check back tomorrow")


def setup(client):
    client.add_cog(Social(client))
