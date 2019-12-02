import datetime
import discord
import os
from discord.ext import commands
from utils import parsing


config = parsing.parse_json("config.json")
token = config["token"]
client = commands.AutoShardedBot(commands.when_mentioned_or(config["prefix"]), description=config["description"])
client.remove_command("help")
start_time = datetime.datetime.utcnow()


@client.event
async def on_ready():
    for e in os.listdir("./cogs"):
        if "__pycache__" in e:
            continue

        try:
            client.load_extension("cogs.{}".format(e[:-3]))
            print("Successfully loaded {}".format(e[:-3]))

        except Exception as error:
            print("Error while loading {}: [{}]".format(e[:-3], error))

    await client.wait_until_ready()
    print("Successfully Logged into {}".format(client.user.name))
    await client.change_presence(activity=discord.Game(">help"))


if __name__ == "__main__":
    client.run(token)
