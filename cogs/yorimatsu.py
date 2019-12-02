import discord
from discord.ext import commands


class Yorimatsu(commands.Cog, name='Yorimatsu'):
    def __init__(self, client):
        self.client = client

    @commands.command(name='help', description="`>help [Command|Category]`")
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def help(self, ctx, cog: str = None):
        """Sends help"""
        cog = "All" if not cog else cog
        cog = cog.capitalize()

        if cog == "All":
            emb = discord.Embed(color=0xbc25cf,
                                description="**Hi there! I'm Yorimatsu <:Yorimatsu:649092496369909768>**\n \n"
                                            "Below you can see the list of commands that I know. \n"
                                            "If you need anymore help you can always join our [Discord Server]("
                                            "https://discord.gg/ZxbYHEh).")

            for c in self.client.cogs:
                if c == "Dev":
                    continue
                else:
                    emb.add_field(name=c, value=" , ".join([x.name for x in self.client.get_cog(c).get_commands()]),
                                  inline=False)

            emb.add_field(name="\u200b", value="**Use `>help <Category>` for more information about a category.** \n"
                                               "**Use `>help <Command>` for more information about a command.** \n  \n "
                                               "**Examples:** \n `>help yorimatsu` for an overview of the Yorimatsu "
                                               "category. \n "
                                               "`>help ping` for detailed help for the ping command.", inline=False)

        elif cog in self.client.cogs:
            emb = discord.Embed(color=0xbc25cf, title="Help with {}".format(cog),
                                description=self.client.cogs[cog].__doc__)

            for c in self.client.get_cog(cog).get_commands():
                if await c.can_run(ctx):
                    command = f'`{c.name}`'

                    if len(c.short_doc) == 0:
                        message = 'There seems to be no documentation for this command'

                    else:
                        message = c.short_doc

                    emb.add_field(name=command, value=message, inline=False)

        else:
            all_commands = [c.name for c in self.client.commands if await c.can_run(ctx)]
            cog_lo = cog.lower()
            if cog_lo in all_commands:
                emb = discord.Embed(color=0xbc25cf,
                                    title=f'{str(self.client.get_command(cog_lo)).capitalize()} command')

                if len(self.client.get_command(cog_lo).description) == 0:
                    message = 'There is no documentation for this command'

                else:
                    message = self.client.get_command(cog_lo).description
                emb.add_field(name='Usage:', value=message)

            else:
                emb = discord.Embed(title='Error!',
                                    description=f'**Error 404:** Command or Cog \"{cog}\" not found ¯\_(ツ)_/¯ \n  \n If '
                                                f'you need anymore help join our [Discord Server](https://discord.gg/ZxbYHEh)',
                                    color=discord.Color.red())

        emb.set_footer(text="Tada")

        await ctx.send(embed=emb)

    @commands.command(name="clean", description="`>clean [Amount]`")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True, read_message_history=True)
    async def clean(self, ctx, amount: int = None):
        """I will delete my messages in the last 100 messages"""
        amount = 100 if not amount else amount

        async for message in ctx.channel.history(before=ctx.message, limit=150):
            while amount > 0:
                try:
                    if message.author == self.client.user:
                        await discord.Message.delete(message)
                        amount -= 1
                except discord.errors.NotFound:
                    break

    @commands.command(name="invite", description='>invite')
    @commands.bot_has_permissions(embed_links=True, send_messages=True)
    async def invite(self, ctx):
        """Have me join your server!"""

        emb = discord.Embed(color=0xbc25cf, title="Invite me!", description="To invite me, please click on the link below!"
                                                                            "\n [Click Here](https://discordapp.com/oauth2/authorize?client_id=531212759988436992&scope=bot&permissions=1578626303)")

        await ctx.send(embed=emb)


def setup(client):
    client.add_cog(Yorimatsu(client))
