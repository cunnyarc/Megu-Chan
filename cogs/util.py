import discord
import datetime
from discord.ext import commands
from slugify import slugify
import json


class Util(commands.Cog, name="Utility"):
    """⚙️ Utility"""
    def __init__(self, client):
        self.client = client
        with open('config.json') as config:
            json.load(config)
        self.logging = self.client.get_channel(config["log_channel"])
        self.blacklist_words = config["blacklist_words"]
        self.blacklist_links = config["blacklist_links"]

        with open('server.json') as f:
            self.users = json.load(f)

    async def do_slugify(self, string):
        string = slugify(string)
        replacements = (('4', 'a'), ('@', 'a'), ('3', 'e'), ('1', 'i'), ('0', 'o'), ('7', 't'), ('5', 's'))
        for old, new in replacements:
            string = string.replace(old, new)

        return string   

    async def update_json(self, file):
        with open(file, 'w') as f:
            json.dump(file, f, indent=4) 

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

    @commands.command(name="unmute", description="`y! unmute <User>")
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

    @commands.command(name="refreshmute", description="`y! refreshmute", hidden=True)
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def refreshmute(self, ctx):
        """Refreshes the mute command"""
        role = await discord.utils.get(ctx.guild.roles, name="Muted")

        for c in ctx.guild.categories:
            await c.set_permissions(role, send_messages=False, read_messages=True)

        emb = discord.Embed(color=0xbc25cf, title="Refreshed Mute Command!", description="The mute command has been "
                                                                                         "refreshed")
        await self.logging.send(embed=emb)

    @commands.group(name="wordblacklist", aliases=["wbl"], invoke_without_command=True, description="m! wordblacklist <add/remove> <words>")
    @commands.guild_only()
    @commands.has_permissions(manage_server=True)
    async def word_blacklist(self, ctx):
        """Sets up a blacklist of words that will be deleted once said"""
        await ctx.send("```Usage: !wordblacklist add <word>\n!wordblacklist remove <word>\n!wordblacklist show```")

    @word_blacklist.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(manage_server=True)   
    async def add_word(self, ctx, *, blacklist_words: list):
        if len(blacklist_words) <= 0:
            await ctx.send("You need to specify a word/words to blacklisted")

        for bl_word in blacklist_words:
            slug_word = self.do_slugify(bl_word)

            if slug_word in self.blacklist_words:
                await ctx.send(f"{slug_word} is already in your blacklist!")
                continue
            
            self.blacklist_words[f"{slug_word}"]
            self.update_json(self.blacklist_words)


    @word_blacklist.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(manage_server=True)
    async def remove_word(self, ctx, *, remove_words: list):
        if len(remove_words) <= 0:
            await ctx.send("You need to specify a word/words to remove")

        for remove_word in remove_words:
            slug_word = self.do_slugify(remove_word)

            if slug_word not in self.blacklist_words:
                await ctx.send(f"{slug_word} is not in the blacklist")
                continue

            self.blacklist_words[f"{slug_word}"].pop()
            self.update_json(self.blacklist_words)

    @commands.group(name="linkblacklist", aliases=["lbl"], invoke_without_command=True, description="m! linkblacklist <add/remove> <links>")
    @commands.guild_only()
    @commands.has_permissions(manage_server=True)
    async def link_blacklist(self, ctx):
       """Sets up a blacklist of words that will be deleted once said"""
       await ctx.send("```Usage: !linkblacklist add <word>\n!linkblacklist remove <word>\n!linkblacklist show```")

    @link_blacklist.command(name="add")
    @commands.guild_only()
    @commands.has_permissions(manage_server=True)   
    async def add_link(self, ctx, *, blacklist_links: list):
        if len(blacklist_links) <= 0:
            await ctx.send("You need to specify a link/linkss to blacklisted")

        for bl_link in blacklist_links:
            slug_word = self.do_slugify(bl_link)

            if slug_word in self.blacklist_words:
                await ctx.send(f"{slug_word} is already in your blacklist!")
                continue
                
            self.blacklist_links[f"{slug_word}"]
            self.update_json(self.blacklist_links)    

    @link_blacklist.command(name="remove")
    @commands.guild_only()
    @commands.has_permissions(manage_server=True)
    async def remove_links(self, ctx, *, remove_links: list):
        if len(remove_links) <= 0:
            await ctx.send("You need to specify a word/words to remove")

        for remove_link in remove_links:
            slug_word = self.do_slugify(remove_link)

            if slug_word not in self.blacklist_links:
                await ctx.send(f"{slug_word} is not in the blacklist")
                continue

            self.blacklist_links[f"{slug_word}"].pop()
            self.update_json(self.blacklist_links)

    # Logging Events
    @commands.Cog.listener
    async def on_message(self, message):

        if message.author.bot:
            return

        if message.guild is None:
            return

        msg = self.do_slugify(message.content)

        for bl_word in self.blacklist_words:
            if bl_word in msg:
                try:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} your message was removed for containing a blacklisted word")
                    break
                except Exception as e:
                    await self.logging.send(f"Error trying to remove message {type(e).__name__}: {e}")
                    break

        for link in self.blacklist_links:
            if link in msg:
                await message.delete()
                await self.logging.send("An invite was sent")
                break
            
        await self.update_data(message.author)
        await self.lvl_up(message.author, message.channel)

        self.users[f'{message.author.id}']['exp'] += 1
        self.update_json(self.users)


    async def update_data(self, user):
        if f'{user.id}' not in self.users:
            self.users[f'{user.id}'] = {}
            self.users[f'{user.id}']['lvl'] = 1
            self.users[f'{user.id}']['exp'] = 0
            self.users[f'{user.id}']['resp'] = 0
            self.users[f'{user.id}']['bal'] = 0
            self.users[f'{user.id}']['msg'] = True
            self.users[f'{user.id}']['inv'] = {}

    async def lvl_up(self, user, channel):
        cur_exp = self.users[f'{user.id}']['exp']
        cur_lvl = self.users[f'{user.id}']['lvl']

        if cur_exp >= cur_lvl * 43:
            self.users[f'{user.id}']['lvl'] += 1
            self.users[f'{user.id}']['exp'] = 0

            self.update_json(self.users)

            if self.users[f'{user.id}']['msg'] is True:
                await channel.send(f"{user.mention} just leveled up to level {self.users[f'{user.id}']['lvl']} \n"
                                f":information_source: `y! disabletext` to disable this message")


    @commands.Cog.listener
    async def on_member_join(self, member):
        if member.bot:
            return
        await self.logging.send(f"New member join {member.name}")

    @commands.Cog.listener
    async def on_member_remove(self, member):
        if member.bot:
            return
        await self.logging.send(f"Member left {member.name}")

    @commands.Cog.listener
    async def on_bulk_message_delete(self, messages):
        await self.logging.send(f"{len(messages)} messages deleted in {messages.channel.mention}") 

    @commands.Cog.listener
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        emb = discord.Embed(color=0xbc25cf)
        emb.add_field(name="Message Deleted", 
        value=f"💮UserName: {message.author.display_name} \n"
            f"💮Ping: {message.author.mention} \n"
            f"💮ID: {message.author.id} \n"
            f"💮Channel: {message.channel}",
            inline=False
        )
        emb.add_field(name="Message", value=message.content)
        emb.set_footer(text=message.author)
        emb.set_thumbnail(url=message.author.avatar_url)
        

        await self.logging.send(embed=emb)

    @commands.Cog.listener
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return

        emb = discord.Embed(color=0xbc25cf, timestamp=datetime.datetime.utcnow())
        emb.add_field(name="Message Edited", 
        value=f"💮**UserName:** {before.author.display_name} \n"
            f"💮**Ping:** {before.author.mention} \n"
            f"💮**ID:** {before.author.id} \n"
            f"💮**URL:** **[Jump To Message]({after.jump_url})**",
            inline=False
        )
        emb.add_field(name="Before", value=before.content, inline=True)
        emb.add_field(name="After", value=after.content, inline=True)
        emb.set_footer(text=before.author)
        emb.set_thumbnail(url=before.author.avatar_url)
        

        await self.logging.send(embed=emb)


def setup(client):
    client.add_cog(Util(client))
