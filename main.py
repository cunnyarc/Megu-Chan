import datetime
import json
import os

import discord
from discord.ext import commands

# Client Secrets and Tokens
with open("secrets.json", "r") as f:
    secrets = json.load(f)

# Client Configuration
with open("config.json") as f:
    config = json.load(f)

# Set up client status and login
client = commands.Bot(commands.when_mentioned_or(
    *config["prefix"]), description=secrets["Megu-Description"])
token = secrets["Megu-Token"]
client.remove_command('help')


@client.event
async def on_ready():
    # Loading all extensions
    for e in os.listdir("./cogs"):
        if "__pycache__" in e:
            continue
        else:
            try:
                client.load_extension(f"cogs.{e[:-3]}")
                print(f"Successfully loaded {e[:-3]}")
            except Exception as e:
                print(f"Error loading {e}")
                continue

    # Printing when successfully logged in
    await client.wait_until_ready()
    print(f"Successfully logged into {client.user}")
    await client.change_presence(activity=discord.Game("megu help"))


@client.event
async def on_command_error(ctx, error):
    # Creating error embed
    err_emb = discord.Embed(color=discord.Color.red(), title="A Fucky Wucky Occurred", description=f"`{error}`",
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

    if isinstance(error, commands.BadArgument):
        await ctx.send(embed=err_emb)


if __name__ == "__main__":
    client.run(token)
