import discord
import datetime
import json
from discord.ext import commands
from slugify import slugify


class Mod(commands.Cog, name="Moderation"):
    """📜 Moderation"""

    def __init__(self, client):
        self.client = client
        with open('config.json') as config:
            self.config = json.load(config)

        self.logging = self.client.get_channel(self.config['log_channel'])
        self.blacklist_words = self.config['blacklist_words']
        self.blacklist_links = self.config['blacklist_links']

        with open('server.json') as f:
            self.users = json.load(f)

    async def do_slugify(self, string):
        string = slugify(string)
        replacements = (('4', 'a'), ('@', 'a'), ('3', 'e'),
                        ('1', 'i'), ('0', 'o'), ('7', 't'), ('5', 's'))
        for old, new in replacements:
            string = string.replace(old, new)

        return string

    async def update_json(self, file, data):
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)

    @commands.command(name="log channel", description="`megu logchannel <channel>`", aliases=['lc'])
    @commands.guild_only()
    @commands.has_permissions(admininstrator=True)
    async def logchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel that logs are sent to"""
        if channel is None:
            await self.update_json('config.json', self.config['log_channel'][f'{ctx.channel.id}'])
            await ctx.send(f"The logging channel is now set to {ctx.channel.mention}")
        else:
            await self.update_json('config.json', self.config['log_channel'][f'{channel.id}'])
            await ctx.send(f"The logging channel is now set to {channel.mention}")

    @commands.command(name="purge", description="`megu purge [Amount]`", aliases=['prune', 'clear'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clean(self, ctx, amount: int = None):
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
    async def nuke(self, ctx, channel: discord.TextChannel):
        if ctx.author != ctx.guild.owner:
            await ctx.send("Only owners can use this command!")
        else:
            if channel is None:
                channel = ctx.channel

            await channel.clone(name=channel.name)
            await channel.delete()

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

        emb = discord.Embed(color=0xbc25cf, timestamp=datetime.datetime.utcnow(), description=f"{user} was softbanned by "
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
        """Add or remove server prefixes"""
        await ctx.send(self.config["prefix"])

    @prefix.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def add_prefix(self, ctx, *, prefixes: list):
        if len(prefixes) <= 0:
            await ctx.send("You need to specify a prefix/prefixes to add")

        for prefix in prefixes:
            if prefix in self.config["prefix"]:
                await ctx.send(f"{prefix} is already in your prefixes")
                continue

            self.config["prefix"][f'{prefix}']
            await self.update_json('config.json', self.config['prefix'])

    @prefix.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def remove_prefix(self, ctx, *, prefixes: list):
        if len(prefixes) <= 0:
            await ctx.send("You need to specify a prefix/prefixes to remove")

        for prefix in prefixes:
            if prefix not in self.config["prefix"]:
                await ctx.send(f"{prefix} is not in your prefixes")
                continue

            self.config["prefix"][f'{prefix}'].pop()
            await self.update_json('config.json', self.config['prefix'])

    @commands.group(name="wordblacklist", aliases=['wbl'], invoke_without_command=True, description="megu wordblacklist <add/remove> <words>")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def word_blacklist(self, ctx):
        """Sets up a blacklist of words that will be deleted once said"""
        await ctx.send("```Usage: megu wordblacklist add <word>\n!wordblacklist remove <word>\n!wordblacklist show```")

    @word_blacklist.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def add_word(self, ctx, *, blacklist_words: list):
        if len(blacklist_words) <= 0:
            await ctx.send("You need to specify a word/words to blacklist")

        for bl_word in blacklist_words:
            slug_word = await self.do_slugify(bl_word)

            if slug_word in self.blacklist_words:
                await ctx.send(f"{slug_word} is already in your blacklist!")
                continue

            self.blacklist_words[f'{slug_word}']
            await self.update_json('config.json', self.blacklist_words)

    @word_blacklist.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def remove_word(self, ctx, *, remove_words: list):
        if len(remove_words) <= 0:
            await ctx.send("You need to specify a word/words to remove")

        for remove_word in remove_words:
            slug_word = await self.do_slugify(remove_word)

            if slug_word not in self.blacklist_words:
                await ctx.send(f"{slug_word} is not in the blacklist")
                continue

            self.blacklist_words[f'{slug_word}'].pop()
            await self.update_json('config.json', self.blacklist_words)

    @word_blacklist.command(name="list")
    @commands.guild_only()
    async def list_words(self, ctx):
        if len(self.blacklist_words) <= 0:
            await ctx.send("You don't have any blacklisted words!")
        else:
            await ctx.send("Heres a list of the words " + "` `".join(self.blacklist_words))

    @commands.group(name="linkblacklist", aliases=['lbl'], invoke_without_command=True, description="megu linklacklist <add/remove> <links>")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def link_blacklist(self, ctx):
        """Sets up a blacklist of words that will be deleted once said"""
        await ctx.send("```Usage: megu linkblacklist add <link>\nmegu linkblacklist remove <link>\nmegu linkblacklist show```")

    @link_blacklist.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def add_link(self, ctx, *, add_links: list):
        if len(add_links) <= 0:
            await ctx.send("You need to specify a word/words to add")

        for add_link in add_links:
            slug_word = await self.do_slugify(add_link)

            if slug_word in self.blacklist_links:
                await ctx.send(f"{slug_word} is already in the blacklist")
                continue

            self.blacklist_links[f'{self.blacklist_links}']
            await self.update_json('config.json', self.blacklist_links)

    @link_blacklist.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def remove_link(self, ctx, *, remove_links: list):
        if len(remove_links) <= 0:
            await ctx.send("Please specify a link/links to remove")

        for remove_link in remove_links:
            slug_word = self.do_slugify(remove_link)

            if slug_word not in self.blacklist_links:
                await ctx.send(f"{slug_word} is not in your blacklist")
                continue

            self.blacklist_links[f'{slug_word}'].pop()
            await self.update_json('config.json', self.blacklist_links)

    @link_blacklist.command(name="list")
    @commands.guild_only()
    async def list_links(self, ctx):
        if len(self.blacklist_links) <= 0:
            await ctx.send("You don't have any blacklisted links!")
        else:
            await ctx.send("Heres a list of the links " + "` `".join(self.blacklist_links))


def setup(client):
    client.add_cog(Mod(client))
