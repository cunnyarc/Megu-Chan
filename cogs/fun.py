import json
import random

import discord
import praw
from discord.ext import commands
from utils import nekoslife


class Fun(commands.Cog, name='Fun'):
    """🎉 Fun"""

    def __init__(self, client):
        self.client = client

        with open("./secrets.json") as f:
            self.secrets = json.load(f)

        self.reddit = praw.Reddit(
            client_id=self.secrets["Megu-Reddit-ClientID"],
            client_secret=self.secrets["Megu-Reddit-Secret"],
            user_agent="Post Grabbing"
        )

    def get_post(self, sub: str):
        try:
            posts = [post for post in self.reddit.subreddit(sub).hot(limit=20)]
            random_post_number = random.randint(0, 19)
            random_post = posts[random_post_number]

            post_name = random_post.title
            post_comments = random_post.num_comments
            post_likes = random_post.score
            post_link = random_post.shortlink
            post_image = random_post.url

            return post_name, post_comments, post_likes, post_link, post_image

        except Exception:
            return

    @commands.command(name="animeme", description="`megu animeme`")
    async def animeme(self, ctx):
        """Gets a random post from r/goodanimemes"""
        data = self.get_post('goodanimemes')

        emb = discord.Embed(color=0xbc25cf, description=f"**[{data[0]}]({data[3]})**")
        emb.set_image(url=data[4])
        emb.set_footer(text=f"💬{data[1]} | ❤ {data[2]}")

        await ctx.send(embed=emb)

    @commands.command(name="bigtext", description="`megu bigtext <text>`")
    async def big_text(self, ctx, *, text: list):
        """Generates text with regional indicators"""
        for i in range(len(text)):

            if not str.isascii(str(text[i])):
                continue

            if str.isspace(text[i]):
                continue

            if text[i] == "?":
                text[i] = ":question:"
                continue

            if not str.isalpha(text[i]):
                text[i] = ""
                continue

            if text[i] == "!":
                text[i] = ":exclamation:"
                continue

            text[i] = f":regional_indicator_{str(text[i])}:"

        await ctx.send("".join(text))

    @commands.command(name="lenny", description="`megu lenny`")
    async def lenny(self, ctx):
        """Sends a lenny face"""
        message = ctx.message

        await discord.Message.delete(message)
        await ctx.send("( ͡° ͜ʖ ͡°)")

    @commands.command(name="rateme", description="`megu rateme [user]`")
    async def rateme(self, ctx, user=None):
        """Rates a user from 1-10"""
        user = ctx.author if not user else user
        rating = random.randint(1, 10)

        emb = discord.Embed(
            color=0xbc25cf, description=f"I rate {user.mention} a {rating}/10")
        emb.set_image(url=user.avatar_url)

        await ctx.send(embed=emb)

    @commands.command(name="fortune", description="`megu fortune <text>`")
    async def fortune(self, ctx, *, question: str):
        """It's an 8ball"""
        data = nekoslife.eightball()
        emb = discord.Embed(
            color=0xbc25cf, description=question,
            title=data['text'])
        emb.set_thumbnail(url=data['url'])
        await ctx.send(embed=emb)

    @commands.command(name="owoify", description="`megu owoify <text>")
    async def owoify(self, ctx, *, text: str):
        """Will owoify any text given to it"""
        owo = nekoslife.owoify(text)
        await ctx.send(owo)


def setup(client):
    client.add_cog(Fun(client))
