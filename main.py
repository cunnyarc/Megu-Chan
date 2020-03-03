import discord
from discord.ext import commands
import os
import datetime
import utils
import json

with open("secrets.json", "r") as f:
        secrets = json.load(f)

client = commands.Bot(commands.when_mentioned_or(*['m! ', 'm!']), description=secrets["Masumi-Description"])
token = secrets["Masumi-Token"]
client.remove_command('help')
start_time = datetime.datetime.utcnow()
logging_channel = discord.utils.get(client.get_all_channels(), guild__name="Test", name="logs",
                                    type=discord.ChannelType.text)


@client.event
async def on_ready():
    # Loading all extensions
    for e in os.listdir("./cogs"):
        if "__pycache__" in e:
            continue
        else:
            try:
                client.load_extension("cogs.{}".format(e[:-3]))
                print(f"Successfully loaded {e[:-3]}")
            except Exception as e:
                print(f"Error loading {e[:-3]}")
                continue

    # Printing when successfully logged in
    await client.wait_until_ready()
    print(f"Successfully logged into {client.user.name}")
    await client.change_presence(activity=discord.Game("m! help"))


@client.event
async def on_member_join(member: discord.Member):
    # Logging to channel when member joins
    emb = discord.Embed(color=discord.Color.green(), timestamp=datetime.datetime.utcnow())
    emb.set_author(name=":tada: Member Joined", icon_url=member.avatar_url)
    emb.add_field(name=member.mention, value=member.name, inline=False)
    emb.set_footer(text=f"ID: {member.id}")

    await member.add_roles(662110138018299904, atomic=True)
    await logging_channel.send(embed=emb)


@client.event
async def on_member_remove(member: discord.Member):
    # Logging to channel when member is removed
    emb = discord.Embed(color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
    emb.set_author(name=":worried: Member Left", icon_url=member.avatar_url)
    emb.add_field(name=member.mention, value=member.name, inline=False)
    emb.set_footer(text=f"ID: {member.id}")

    await logging_channel.send(embed=emb)


@client.event
async def on_command_error(ctx, error):
    # Creating error embed
    err_emb = discord.Embed(color=discord.Color.red(), title="An Error Occurred", description=f"`{error}`",
                            timestamp=datetime.datetime.utcnow())
    err_emb.set_thumbnail(url=client.user.avatar_url)

    # checks if command had a local error handler
    if hasattr(ctx.command, 'on_error'):
        return

    # getting the original error
    error = getattr(error, 'original', error)

    # checking every instance for what the error was
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.NotOwner):
        return

    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send(embed=err_emb)

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=err_emb)

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=err_emb)

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=err_emb)


if __name__ == "__main__":
    client.run(token)
