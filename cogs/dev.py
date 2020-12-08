import os

import discord
from discord.ext import commands


class Dev(commands.Cog, name="Dev", command_attrs=dict(hidden=True)):
    def __init__(self, client):
        self.client = client

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down...")
        await self.client.close()

    @commands.group(name="cogs", invoke_without_command=True, aliases=['ext'])
    @commands.is_owner()
    async def cogs(self, ctx):
        await ctx.send("```megu cogs [load/unload/reload] [cog]```")

    @cogs.command(name="load")
    async def load_cogs(self, ctx, ext=None):
        ext = 'All' if not ext else ext

        if ext == 'All':
            success = []
            failure = []
            for e in os.listdir("./cogs"):
                if "__pycache__" or 'dev.py' in e:
                    continue
                else:
                    try:
                        self.client.load_extension(f"cogs.{e[:-3]}")
                        print(f"Successfully loaded {e[:-3]}")
                        success.append(e[:-3])
                    except Exception as e:
                        print(f"Error loading {e[:-3]}")
                        failure.append(e[:-3])
                        continue
            emb = discord.Embed(color=0xbc25cf, description=f"Successfully loaded: [{success}] \n"
                                                            f"Failed to load: [{failure}]")
            ctx.send(embed=emb)

        else:
            try:
                self.client.load_extension(f"cogs.{ext}")
                await ctx.send(f"Successfully loaded {ext}")

            except Exception as error:
                await ctx.send(f"Error while reloading {ext}: [{error}]")

    @cogs.command(name="reload")
    async def reload_cogs(self, ctx, ext=None):
        ext = 'All' if not ext else ext

        if ext == 'All':
            success = []
            failure = []
            for e in os.listdir("./cogs"):
                if "__pycache__" or 'dev.py' in e:
                    continue
                else:
                    try:
                        self.client.unload_extension(f"cogs.{e[:-3]}")
                        self.client.load_extension(f"cogs.{e[:-3]}")
                        print(f"Successfully loaded {e[:-3]}")
                        success.append(e[:-3])
                    except Exception as e:
                        print(f"Error loading {e[:-3]}")
                        failure.append(e[:-3])
                        continue
            emb = discord.Embed(color=0xbc25cf, description=f"Successfully reloaded: [{success}] \n"
                                                            f"Failed to reload: [{failure}]")
            ctx.send(embed=emb)

        else:
            try:
                self.client.unload_extension(f"cogs.{ext}")
                self.client.load_extension(f"cogs.{ext}")
                await ctx.send(f"Successfully reloaded {ext}")

            except Exception as error:
                await ctx.send(f"Error while reloading {ext}: [{error}]")

    @cogs.command(name="unload")
    async def unload_cogs(self, ctx, ext=None):
        ext = 'All' if not ext else ext

        if ext == 'All':
            success = []
            failure = []
            for e in os.listdir("./cogs"):
                if "__pycache__" or 'dev.py' in e:
                    continue
                else:
                    try:
                        self.client.unload_extension(f"cogs.{e[:-3]}")
                        print(f"Successfully unloaded {e[:-3]}")
                        success.append(e[:-3])
                    except Exception as e:
                        print(f"Error loading {e[:-3]}")
                        failure.append(e[:-3])
                        continue
            emb = discord.Embed(color=0xbc25cf, description=f"Successfully unloaded: [{success}] \n"
                                                            f"Failed to unload: [{failure}]")
            ctx.send(embed=emb)

        else:
            try:
                self.client.unload_extension(f"cogs.{ext}")
                self.client.load_extension(f"cogs.{ext}")
                await ctx.send(f"Successfully unloaded {ext}")

            except Exception as error:
                await ctx.send(f"Error while unloading {ext}: [{error}]")


def setup(client):
    client.add_cog(Dev(client))
