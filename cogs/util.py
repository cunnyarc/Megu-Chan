import discord
import datetime
from discord.ext import commands
import main


class Util(commands.Cog, name="Utility"):
    """⚙️ Utility"""
    def __init__(self, client):
        self.client = client
        self.logging = main.logging_channel

    @commands.command(name="userinfo")
    async def user_info(self, ctx, member: discord.Member = None):
        member = ctx.message.author if not member else member

        emb = discord.Embed(color=0xbc25cf)

    @commands.command(name="help", description="`m! help [Command]`")
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def help(self, ctx, cog: str = None):
        """Sends help"""
        cog = "All" if not cog else cog
        cog = cog.capitalize()

        # Shows all commands if no argument was given
        if cog == "All":
            emb = discord.Embed(color=0xbc25cf,
                                description="**Hello there! I'm Masumi-Chan!** \n Below you can see a list of commands that I know. \n")

            for c in self.client.cogs:
                if c == "Dev":
                    continue

                emb.add_field(name=self.client.get_cog(c).__doc__, value=", ".join([x.name for x in self.client.get_cog(c).get_commands() if not x.hidden]),
                              inline=False)

            emb.add_field(name="\u200b",
                          value="**Use `m! help [Command | Category]` for more information.**\n \n"
                                "**Example:** `m! help profile` **for detailed help for the profile command.**", inline=False)

        # Shows the cog and the cog's command if the argument was a cog
        elif cog in self.client.cogs:
            emb = discord.Embed(color=0xbc25cf, title=f"Help with {cog}")

            for c in self.client.get_cog(cog).get_commands():
                if not c.hidden:
                    command = f'{c.name}'
                    message = c.short_doc

                    emb.add_field(name=command, value=message, inline=False)

        # Shows command's info and usage if the argument wasn't a cog
        else:
            all_commands = [c.name for c in self.client.commands if not c.hidden]
            cog_lo = cog.lower()

            if cog.lower() in all_commands:
                emb = discord.Embed(color=0xbc25cf, title=f'{cog_lo} command')

                emb.add_field(name="Usage:", value=self.client.get_command(cog_lo).description)
                emb.add_field(name="Description:", value=self.client.get_command(cog_lo).short_doc)

            # Shows an error message if the given argument fails all statements
            else:
                emb = discord.Embed(color=discord.Color.red(), title="Error!",
                                    description=f"404 {cog} not found ¯\_(ツ)_/¯")

        emb.set_footer(text="<> = Required, [] = Optional")

        await ctx.send(embed=emb)

    @commands.command(name="purge", description="`m! purge [Amount]`", aliases=['prune', 'clear'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clean(self, ctx, amount: int = None):
        """I will delete a given amount of messages"""
        for message in ctx.channel.history(before=ctx.message, limit=amount):
            try:
                if message.author == self.client.user:
                    await discord.Message.delete(message)

            except discord.errors.NotFound:
                break

    @commands.command(name="kick", description="`y! kick <User>`")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        """Kicks a given user"""
        if user == ctx.author:
            await ctx.send("You cannot kick yourself!")

        emb = discord.Embed(color=0xbc25cf, timestamp=datetime.datetime.utcnow(), description=f"{user} was kicked by "
                                                                                              f"{ctx.author} with reason"
                                                                                              f"`{reason}`")
        emb.set_author(name=":bangbang: User Kicked", icon_url=user.avatar_url)

        await user.kick(reason=reason)
        await self.logging.send(embed=emb)

    @commands.command(name="ban", description="`y! ban <User>`")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        """Bans a given user"""
        if user == ctx.author:
            await ctx.send("You cannot ban yourself!")

        emb = discord.Embed(color=0xbc25cf, timestamp=datetime.datetime.utcnow(), description=f"{user} was banned by "
                                                                                              f"{ctx.author} with reason"
                                                                                              f"`{reason}`")
        emb.set_author(name=":bangbang: User Banned", icon_url=user.avatar_url)

        await user.ban(reason=reason, delete_message_days=1)
        await self.logging.send(embed=emb)

    @commands.command(name="unban", description="`y! unban <User>`")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.Member, *, reason=None):
        """Unbans a given user"""

        emb = discord.Embed(color=0xbc25cf, timestamp=datetime.datetime.utcnow(), description=f"{user} was unbanned by "
                                                                                              f"{ctx.author} with reason"
                                                                                              f"`{reason}`")
        emb.set_author(name=":bangbang: User Unbanned", icon_url=user.avatar_url)

        await user.unban(reason=reason)
        await self.logging.send(embed=emb)

    @commands.command(name="softban", description="`y! softban <User>`")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, user: discord.Member, *, reason=None):
        """Bans then unbans a user to clear their messages"""
        if user == ctx.author:
            await ctx.send("You cannot softban yourself!")

        emb = discord.Embed(color=0xbc25cf, timestamp=datetime.datetime.utcnow(), description=f"{user} was softbanned by "
                                                                                              f"{ctx.author} with reason"
                                                                                              f"`{reason}`")
        emb.set_author(name=":bangbang: User softbanned", icon_url=user.avatar_url)

        await user.ban(reason=reason, delete_message_days=7)
        await user.unban(reason=reason)
        await self.logging.send(embed=emb)

    @commands.command(name="mute", description="`y! mute <User>")
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, user: discord.Member, *, reason=None):
        """Mutes the given user from sending any messages"""
        if user == ctx.author:
            await ctx.send("You cannot mute yourself!")

        role = discord.utils.get(ctx.guild.roles, name="Muted")

        if role is None:
            await ctx.guild.create_role(name="Muted", reason="Bot Mute")
            role = discord.utils.get(ctx.guild.roles, name="Muted")

            for c in ctx.guild.categories:
                await c.set_permissions(role, send_messages=False, read_messages=True)

        await user.add_roles(role, reason=reason)

        emb = discord.Embed(color=0xbc25cf, timestamp=datetime.datetime.utcnow(), title=":bangbang: User muted",
                            description=f"{user} was muted by {ctx.author.mention} with reason `{reason}`")
        emb.set_thumbnail(url=user.avatar_url)

        await self.logging.send(embed=emb)

    @commands.command(name="unmute", description="`y! unmute <User>")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, user: discord.Member, *, reason=None):
        """Unmutes the giver user"""
        if user == ctx.author:
            await ctx.send("You cannot unmute yourself")

        role = discord.utils.get(ctx.guild.roles, name="Muted")

        await user.remove_roles(role, reason=reason)

        emb = discord.Embed(color=0xbc25cf, timestamp=datetime.datetime.utcnow(), title=":bangbang: User unmuted",
                            description=f"{user} was unmuted by {ctx.author.mention} with reason `{reason}`")
        emb.set_thumbnail(url=user.avatar_url)

        await self.logging.send(embed=emb)

    @commands.command(name="refreshmute", description="`y! refreshmute", hidden=True)
    @commands.has_permissions(mamage_messages=True)
    async def refreshmute(self, ctx):
        """Refreshes the mute command"""
        role = await discord.utils.get(ctx.guild.roles, name="Muted")

        for c in ctx.guild.categories:
            await c.set_permissions(role, send_messages=False, read_messages=True)

        emb = discord.Embed(color=0xbc25cf, title="Refreshed Mute Command!", description="The mute command has been "
                                                                                         "refreshed")
        await self.logging.send(embed=emb)


def setup(client):
    client.add_cog(Util(client))
