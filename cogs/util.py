import discord
import datetime
import main
from discord.ext import commands


class Util(commands.Cog, name='Util'):
    def __init__(self, client):
        self.client = client

    @commands.command(name="info", description="`>info`")
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def info(self, ctx):
        """Sends the bots info"""
        guilds = len([g for g in self.client.guilds])
        users = len([u for u in self.client.get_all_members()])
        uptime = datetime.datetime.utcnow() - main.start_time

        day = uptime.days
        day = str(day)

        uptime = str(uptime)
        uptime = uptime.split(":")

        hours = uptime[0]
        hours = hours.replace(" days,", "일")
        hours = hours.replace(" day,", "일")

        minitues = uptime[1]

        seconds = uptime[2]
        seconds = seconds.split(".")
        seconds = seconds[0]

        emb = discord.Embed(color=0xbc25cf, title="**Yorimatsu**")
        emb.set_thumbnail(url=self.client.user.avatar_url)
        emb.add_field(name="**Version**", value="0.0.1", inline=True)
        emb.add_field(name="**Library**", value="[discord.py](https://github.com/Rapptz/discord.py)", inline=True)
        emb.add_field(name="**Github**", value="[Click Here](https://github.com/Glitchy-Chan/Yorimatsu)", inline=True)
        emb.add_field(name="**Prefix**", value=">", inline=True)
        emb.add_field(name="**Guilds**", value=str(guilds), inline=True)
        emb.add_field(name="**Users**", value=str(users), inline=True)
        emb.add_field(name="**Shard**", value="{} / {}".format(ctx.guild.shard_id + 1, self.client.shard_count), inline=True)
        emb.add_field(name="**Invite**", value="[Click Here](https://discordapp.com/oauth2/authorize?client_id=531212759988436992&scope=bot&permissions=1578626303)", inline=True)
        emb.add_field(name="**Discord**", value="[Click Here](https://discord.gg/ZxbYHEh)", inline=True)
        emb.set_footer(text="Created by: GlitchyChan#6969  •  Uptime {} days, {} hours, {} minutes, and {} seconds".format(day, hours, minitues, seconds))
        emb.set_thumbnail(url=self.client.user.avatar_url)

        await ctx.send(embed=emb)

    @commands.command(name="ping", description="`>ping`")
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def ping(self, ctx):
        """Sends the bots ping"""
        ping = self.client.latencies

        for l in ping:
            if ctx.guild.shard_id in l:
                ping = l[1]

        shard_latency = str(round(self.client.latency, 1)) + "ms"
        guild_latency = str(round(ping, 1)) + "ms"

        emb = discord.Embed(color=0xbc25cf, title=":ping_pong: Pong!", description="Bot Latency: **{}** \n Guild Latency: **{}**"
                            .format(shard_latency, guild_latency))

        await ctx.send(embed=emb)


def setup(client):
    client.add_cog(Util(client))
