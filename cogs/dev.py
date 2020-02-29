from discord.ext import commands
import os


class Dev(commands.Cog, name="Dev", command_attrs=dict(hidden=True)):
    def __init__(self, client):
        self.client = client

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down")
        await self.client.close()

    @commands.group(name="extension", invoke_without_command=True)
    @commands.is_owner()
    async def extension_group(self, ctx):
        await ctx.send("Usage: ```m!extension [command] [extension]```")

    @extension_group.command(name="load")
    async def load_subcommand(self, ctx, extension):
        try:
            self.client.load_extension("cogs.{}".format(extension))
            await ctx.send("Successfully loaded {}".format(extension))

        except Exception as error:
            await ctx.send("Error while loading {}: [{}]".format(extension, error))

    @extension_group.command(name="unload")
    async def unload_subcommand(self, ctx, extension):
        try:
            self.client.unload_extension("cogs.{}".format(extension))
            await ctx.send("Successfully unloaded {}".format(extension))

        except Exception as error:
            await ctx.send("Error while unloading {}: [{}]".format(extension, error))

    @extension_group.command(name="reload")
    async def reload_subcommand(self, ctx, extension=None):
        extension = "all" if not extension else extension

        if extension == "all":
            for e in os.listdir("./cogs"):
                if "dev.py" or "__pycache__" in e:
                    continue

                try:
                    self.client.unload_extension("cogs.{}".format(e[:-3]))
                    self.client.load_extension("cogs.{}".format(e[:-3]))
                    await ctx.send("Successfully reloaded {}".format(e[:-3]))

                except Exception as error:
                    await ctx.send("Error while reloading {}: [{}]".format(extension, error))
                    continue
        else:
            try:
                self.client.unload_extension("cogs.{}".format(extension))
                self.client.load_extension("cogs.{}".format(extension))
                await ctx.send("Successfully reloaded {}".format(extension))

            except Exception as error:
                await ctx.send("Error while reloading {}: [{}]".format(extension, error))


def setup(client):
    client.add_cog(Dev(client))
