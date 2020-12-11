import datetime
import json
import asyncio

import discord
from discord.ext import commands
from slugify import slugify


class Util(commands.Cog, name="Utility"):
    """⚙️ Utility"""

    def __init__(self, client):
        self.client = client
        with open('config.json') as config:
            self.config = json.load(config)

        self.logging = self.client.get_channel(self.config['log_channel'])
        self.blacklist_words = self.config['blacklist_words']
        self.blacklist_links = self.config['blacklist_links']

        with open('server.json') as f:
            self.users = json.load(f)

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

    @commands.command(name="help", description="`megu help [Command]`")
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def help(self, ctx, cog="All"):
        """Sends help"""
        cog = cog.capitalize()

        # Shows all commands if no argument was given
        if cog == "All":
            emb = discord.Embed(color=0xbc25cf,
                                description="**Hello there! I'm Megumin!** \n Below you can see a list of commands that I know. \n")

            for c in self.client.cogs:
                if c == "Dev":
                    continue

                emb.add_field(name=self.client.get_cog(c).__doc__, value=", ".join([x.name for x in self.client.get_cog(c).get_commands() if not x.hidden]),
                              inline=False)

            emb.add_field(name="\u200b",
                          value="**Use `megu help [Command | Category]` for more information.**\n \n"
                                "**Example:** `megu help profile` **for detailed help for the profile command.**", inline=False)

        # Shows the cog and the cog's command if the argument was a cog
        elif cog in self.client.cogs:
            emb = discord.Embed(color=0xbc25cf, title=f"Help with {cog}")

            messages = []
            for c in self.client.get_cog(cog).get_commands():
                if not c.hidden:
                    command = f'{c.name}'
                    help_message = c.short_doc
                    messages.append(f"**{command}** - {help_message}")

            message = " \n".join(messages)
            emb.add_field(name="Commands", value=message, inline=False)
            emb.set_footer(text="Use: megu help <command> to get more info")

        # Shows command's info and usage if the argument wasn't a cog
        else:
            all_commands = [
                c.name for c in self.client.commands if not c.hidden]
            cog_lo = cog.lower()

            if cog_lo in all_commands:
                emb = discord.Embed(color=0xbc25cf, title=f'{cog_lo} command')

                emb.add_field(
                    name="Usage:", value=self.client.get_command(cog_lo).description)
                emb.add_field(name="Description:",
                              value=self.client.get_command(cog_lo).short_doc)
                emb.set_footer(text="<> = Required, [] = Optional")
            # Shows an error message if the given argument fails all statements
            else:
                emb = discord.Embed(color=discord.Color.red(), title="Error!",
                                    description=f"404 {cog} not found ¯\_(ツ)_/¯")

        await ctx.send(embed=emb)

    # Cog Listeners
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.guild is None:
            return

        msg = await self.do_slugify(message.content)

        for bl_word in self.blacklist_words:
            if bl_word in msg:
                try:
                    await message.delete()
                    removed = await message.channel.send(
                        f"{message.author.mention} your message was removed for containing a blacklisted word")
                    await asyncio.sleep(5)
                    await removed.delete()
                    return
                except Exception as e:
                    await self.logging.send(f"Error trying to remove message {type(e).__name__}: {e}")
                    return

        for link in self.blacklist_links:
            if link in message.content:
                if message.author.guild_permissions.manage_guild:
                    return
                else:
                    try:
                        await message.delete()
                        await self.logging.send("An invite was sent")
                        return
                    except Exception as e:
                        await self.logging.send(f"Error trying to remove message {type(e).__name__}: {e}")
                        return

        if message.content.startswith(tuple(self.config['prefix'])):
            return

        await self.update_data(message.author)
        await self.lvl_up(message.author, message.channel)

        self.users[f'{message.author.id}']['exp'] += 1
        await self.update_json('server.json', self.users)

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

            await self.update_json('server.json', self.users)

            if self.users[f'{user.id}']['msg'] is True:
                await channel.send(f"{user.mention} just leveled up to level {self.users[f'{user.id}']['lvl']} \n"
                                   f":information_source: `megu disabletext` to disable this message")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        await self.logging.send(f"New member join {member.name}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return
        await self.logging.send(f"Member left {member.name}")

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):

        emb = discord.Embed(color=0xbc25cf)
        emb.add_field(name="Bulk Delete",
                      value=f"💣Messages Deleted: {len(messages)} \n"
                            f"💬Channel: {messages.channel}",
                      inline=False
                      )

        await self.logging.send(embed=emb)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        if message.content.startswith(tuple(self.config['prefix'])):
            return

        emb = discord.Embed(color=0xbc25cf)
        emb.add_field(name="Message Deleted",
                      value=f"👤**UserName:** {message.author.display_name} \n"
                            f"🔔**Ping:** {message.author.mention} \n"
                            f"💳**ID:** {message.author.id} \n"
                            f"💬**Channel**: {message.channel.mention}",
                      inline=False
                      )
        emb.add_field(name="Message", value=message.content)
        emb.set_footer(text=message.author)
        emb.set_thumbnail(url=message.author.avatar_url)

        await self.logging.send(embed=emb)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return

        emb = discord.Embed(
            color=0xbc25cf, timestamp=datetime.datetime.utcnow())
        emb.add_field(name="Message Edited",
                      value=f"👤**UserName:** {before.author.display_name} \n"
                            f"🔔**Ping:** {before.author.mention} \n"
                            f"💳**ID:** {before.author.id} \n"
                            f"💬**URL:** **[Jump To Message]({after.jump_url})**",
                      inline=False
                      )
        emb.add_field(name="Before", value=before.content, inline=True)
        emb.add_field(name="After", value=after.content, inline=True)
        emb.set_footer(text=before.author)
        emb.set_thumbnail(url=before.author.avatar_url)

        await self.logging.send(embed=emb)


def setup(client):
    client.add_cog(Util(client))
