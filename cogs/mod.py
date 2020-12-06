import discord
import datetime
import json
import asyncio
from discord.ext import commands
from slugify import slugify


class Mod(commands.Cog, name="Moderation"):
    """🔨 Moderation"""

    def __init__(self, client):
        self.client = client
        with open('config.json') as f:
            self.config = json.load(f)

        with open('server.json') as f:
            self.users = json.load(f)

        self.logging = self.client.get_channel(self.config['log_channel'])

    @staticmethod
    async def do_slugify(string):
        string = slugify(string)
        replacements = (('4', 'a'), ('@', 'a'), ('3', 'e'),
                        ('1', 'i'), ('0', 'o'), ('7', 't'), ('5', 's'))
        for old, new in replacements:
            string = string.replace(old, new)

        return string

    @staticmethod
    async def update_json(file, data):
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)

    @commands.command(name="logchannel", description="`megu logchannel <channel>`", aliases=['lc'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def logchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel that logs are sent to"""
        try:
            self.config['log_channel'] = channel.id
            await self.update_json('config.json', self.config)
            await ctx.send(f"The logging channel is now set to {channel.mention}")
        except Exception as error:
            await ctx.send(f"There was an error setting the log channel: [{error}]")

    @commands.command(name="purge", description="`megu purge [Amount]`", aliases=['prune', 'clear'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = None):
        """I will delete a given amount of messages"""
        for message in ctx.channel.history(before=ctx.message, limit=amount):
            try:
                if message.author == self.client.user:
                    await discord.Message.delete(message)

            except discord.errors.NotFound:
                continue

    @commands.command(name="nuke", description="`megu nuke <channel>")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def nuke(self, ctx, channel: discord.TextChannel = None):
        if ctx.author != ctx.guild.owner:
            await ctx.send("Only owners can use this command!")
            return
        else:
            if channel is None:
                channel = ctx.channel
        nuke_message = await ctx.send("Are you sure you want to nuke this? \n"
                                      f"Type `Yes nuke {channel.name}`")

        # Checking if the message sent was same user and check content
        def nuke_check(m):
            return m.author == ctx.message.author and m.content

        # Client waits for response of owner
        try:
            nuke = await self.client.wait_for('message', check=nuke_check, timeout=8.0)
        except asyncio.TimeoutError:
            failure = await ctx.send('Nuke canceled due to timeout')
            await asyncio.sleep(3.0)
            await failure.delete()
            await nuke_message.delete()
            await ctx.message.delete()

        # Checking if message sent was correct if not cancel nuke
        # If true delete channel and delete traces of nuking channel
        if nuke.content.capitalize() == f'Yes nuke {channel.name}':
            new_channel = await channel.clone(name=channel.name)
            await channel.delete()
            await new_channel.send("The channel has been wiped by the owner!")

            try:
                await nuke_message.delete()
                await ctx.message.delete()
                await nuke.delete()
            except discord.NotFound:
                return
        else:
            failure = await ctx.send('Nuke has been canceled')
            await asyncio.sleep(5.0)
            await failure.delete()
            await nuke_message.delete()
            await ctx.message.delete()

    @commands.command(name="kick", description="`megu kick <User>`")
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

    @commands.command(name="ban", description="`megu ban <User>`")
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

    @commands.command(name="unban", description="`megu unban <User>`")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.Member, *, reason=None):
        """Unbans a given user"""

        emb = discord.Embed(color=0xbc25cf, timestamp=datetime.datetime.utcnow(), description=f"{user} was unbanned by "
                                                                                              f"{ctx.author} with reason"
                                                                                              f"`{reason}`")
        emb.set_author(name=":bangbang: User Unbanned",
                       icon_url=user.avatar_url)

        await user.unban(reason=reason)
        await self.logging.send(embed=emb)

    @commands.command(name="softban", description="`megu softban <User>`")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, user: discord.Member, *, reason=None):
        """Bans then unbans a user to clear their messages"""
        if user == ctx.author:
            await ctx.send("You cannot softban yourself!")

        emb = discord.Embed(color=0xbc25cf, timestamp=datetime.datetime.utcnow(),
                            description=f"{user} was softbanned by "
                                        f"{ctx.author} with reason"
                                        f"`{reason}`")
        emb.set_author(name=":bangbang: User softbanned",
                       icon_url=user.avatar_url)

        await user.ban(reason=reason, delete_message_days=7)
        await user.unban(reason=reason)
        await self.logging.send(embed=emb)

    @commands.command(name="mute", description="`megu mute <User>")
    @commands.guild_only()
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

    @commands.command(name="unmute", description="`megu unmute <User>")
    @commands.guild_only()
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

    @commands.group(name="prefix", invoke_without_command=True, description="`megu prefix [add/remove] [prefix]`")
    @commands.guild_only()
    async def prefix(self, ctx):
        """Add, remove, or list the server prefixes"""
        await ctx.send(f"The prefixes are: `{self.config['prefix']}`")

    @prefix.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def prefix_add(self, ctx, prefix):
        if prefix in self.config['prefix']:
            await ctx.send(f"{prefix} is already in your prefixes")
        else:
            try:
                self.config['prefix'].append(f'{prefix}')
                await self.update_json('config.json', self.config)

            except Exception as error:
                await ctx.send(f"An error occured when trying to add a prefix to config: [{error}]")

    @prefix.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def prefix_remove(self, ctx, prefix):
        if prefix not in self.config['prefix']:
            await ctx.send(f'{prefix} is not in your prefixes')
        else:
            try:
                self.config['prefix'].remove(f'{prefix}')
                await self.update_json('config.json', self.config)

            except Exception as error:
                await ctx.send(f"An error occurred when trying to remove a prefix: [{error}]")

    @commands.group(name="wordblacklist", aliases=['wbl'], invoke_without_command=True,
                    description="megu wordblacklist <add/remove> <words>")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def word_blacklist(self, ctx):
        """Sets up a blacklist of words that will be deleted once said"""
        if len(self.config['blacklist_words']) <= 0:
            await ctx.send("You don't have any blacklisted words!")
        else:
            await ctx.send(f"Here's a list of the words `{self.config['blacklist_words']}`")

    @word_blacklist.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def add_word(self, ctx, bl_word):
        slug_word = await self.do_slugify(bl_word)

        if slug_word in self.config['blacklist_words']:
            await ctx.send(f"{bl_word} is already in your blacklist!")
        else:
            try:
                self.config['blacklist_words'].append(f'{slug_word}')
                await self.update_json('config.json', self.config)
            except Exception as error:
                await ctx.send(f"An error occurred when trying to add a word: [{error}]")

    @word_blacklist.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def remove_word(self, ctx, bl_word):
        slug_word = await self.do_slugify(bl_word)

        if slug_word not in self.config['blacklist_words']:
            await ctx.send(f"{bl_word} is not in your blacklist!")
        else:
            try:
                self.config['blacklist_words'].remove(f'{slug_word}')
                await self.update_json('config.json', self.config)
            except Exception as error:
                await ctx.send(f"An error occurred when trying to remove a word: [{error}]")

    @commands.group(name="linkblacklist", aliases=['lbl'], invoke_without_command=True,
                    description="megu linklacklist <add/remove> <links>")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def link_blacklist(self, ctx):
        """Sets up a blacklist of words that will be deleted once said"""
        if len(self.config['blacklist_links']) <= 0:
            await ctx.send("You don't have any blacklisted links!")
        else:
            await ctx.send(f"Here's a list of the links `{self.config['blacklist_links']}`")

    @link_blacklist.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def add_link(self, ctx, bl_link):
        if bl_link in self.config['blacklist_links']:
            await ctx.send(f"{bl_link} is already in your blacklist!")
        else:
            try:
                self.config['blacklist_links'].append(f'{bl_link}')
                await self.update_json('config.json', self.config)
            except Exception as error:
                await ctx.send(f"An error occurred when trying to add a link: [{error}]")

    @link_blacklist.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def remove_link(self, ctx, bl_link):
        if bl_link not in self.config['blacklist_links']:
            await ctx.send(f"{bl_link} is not in your blacklist!")
        else:
            try:
                self.config['blacklist_links'].remove(f'{bl_link}')
                await self.update_json('config.json', self.config)
            except Exception as error:
                await ctx.send(f"An error occurred when trying to add a link: [{error}]")


def setup(client):
    client.add_cog(Mod(client))
