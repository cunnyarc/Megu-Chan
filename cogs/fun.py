import json
import random

import discord
import praw
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands

from utils import nekoslife


class Fun(commands.Cog, name='Fun'):
    """🎉 Fun"""

    def __init__(self, client):
        self.client = client

        with open("./secrets.json") as f:
            self.secrets = json.load(f)

        with open("./config.json") as f:
            self.config = json.load(f)

        self.reddit = praw.Reddit(
            client_id=self.secrets["Megu-Reddit-ClientID"],
            client_secret=self.secrets["Megu-Reddit-Secret"],
            user_agent="Post Grabbing"
        )

    @staticmethod
    async def update_json(file, data):
        with open(file, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    async def get_webhook(ctx):
        webhooks = await ctx.channel.webhooks()
        if f'megu-{ctx.channel.name}' not in [webhook.name for webhook in webhooks]:
            webhook = await ctx.channel.create_webhook(name=f'megu-{ctx.channel.name}',
                                                       reason="Megumin Command Webhook")
            webhook_id = webhook.id
            webhook_token = webhook.token

            return webhook_id, webhook_token
        else:
            for webhook in webhooks:
                if webhook.name == f'megu-{ctx.channel.name}':
                    webhook_id = webhook.id
                    webhook_token = webhook.token

                    return webhook_id, webhook_token

    async def get_post(self, sub: str):
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

        except Exception as e:
            print(e)

    @commands.command(name="reddit", description="`megu reddit <subreddit>`")
    async def get_reddit(self, ctx, *, subreddit):
        """Gets a random post from a specified subreddit"""
        if subreddit in self.config['banned_reddits']:
            await ctx.send("That subreddit has been banned!")

        if self.reddit.subreddit(subreddit).over18 and (ctx.channel.is_nsfw() is False):
            await ctx.send("Woah! That reddit is 18+ and you're not in a 18+ channel!")
            return

        data = await self.get_post(subreddit)

        emb = discord.Embed(color=0xbc25cf, description=f"**[{data[0]}]({data[3]})**")
        emb.set_image(url=data[4])
        emb.set_footer(text=f"💬{data[1]} | ❤ {data[2]}")

        await ctx.send(embed=emb)

    @commands.command(name="animeme", description="`megu animeme`")
    async def animeme(self, ctx):
        """Gets a random post from r/goodanimemes"""
        data = await self.get_post('goodanimemes')

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

        webhook_info = await self.get_webhook(ctx)

        big_text = Webhook.partial(webhook_info[0], webhook_info[1], adapter=RequestsWebhookAdapter())
        await discord.Message.delete(ctx.message)
        big_text.send("".join(text), username=ctx.author.display_name, avatar_url=ctx.author.avatar_url)

    @commands.command(name="lenny", description="`megu lenny`")
    async def lenny(self, ctx):
        """Makes you send a lenny face ( ͡° ͜ʖ ͡°)"""
        lennies = [
            "( ͡° ͜ʖ ͡°)",
            "(☭ ͜ʖ ☭)",
            "(ᴗ ͜ʖ ᴗ)",
            "( ° ͜ʖ °)",
            "(⟃ ͜ʖ ⟄) ",
            "( ‾ ʖ̫ ‾)",
            "(͠≖ ͜ʖ͠≖)",
            "( ͡° ʖ̯ ͡°)",
            "ʕ ͡° ʖ̯ ͡°ʔ",
            "( ͡° ل͜ ͡°)",
            "( ͠° ͟ʖ ͡°)",
            "( ͠° ͟ʖ ͠°)",
            "( ͡~ ͜ʖ ͡°)",
            "( ͡o ͜ʖ ͡o)",
            "( ͡◉ ͜ʖ ͡◉)",
            "( ͡☉ ͜ʖ ͡☉)",
            "( ͡° ͜V ͡°)"
        ]
        lenny_face = lennies[random.randint(0, 16)]
        webhook_info = await self.get_webhook(ctx)

        lenny = Webhook.partial(webhook_info[0], webhook_info[1], adapter=RequestsWebhookAdapter())
        await discord.Message.delete(ctx.message)
        lenny.send(lenny_face, username=ctx.author.display_name, avatar_url=ctx.author.avatar_url)

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
        webhook_info = await self.get_webhook(ctx)

        owoify_text = Webhook.partial(webhook_info[0], webhook_info[1], adapter=RequestsWebhookAdapter())
        await discord.Message.delete(ctx.message)
        owoify_text.send(owo, username=ctx.author.display_name, avatar_url=ctx.author.avatar_url)

    @commands.command(name="cat", description="`megu cat")
    async def cat_face(self, ctx):
        """Makes you send a cat face ~(=^‥^)"""
        cat = nekoslife.textcat()
        webhook_info = await self.get_webhook(ctx)

        cat_face = Webhook.partial(webhook_info[0], webhook_info[1], adapter=RequestsWebhookAdapter())
        await discord.Message.delete(ctx.message)
        cat_face.send(cat, username=ctx.author.display_name, avatar_url=ctx.author.avatar_url)

    @commands.command(name="fact", description="`megu fact")
    async def fact(self, ctx):
        """Gives you a random fact"""
        await ctx.send(nekoslife.fact())


def setup(client):
    client.add_cog(Fun(client))
