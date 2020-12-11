import functools
import itertools
import math
import random

import asyncio
import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands

# Fuck your useless bug reports message that gets two link embeds and confuses users
youtube_dl.utils.bug_reports_message = lambda: ''


class YTDLSource(discord.PCMVolumeTransformer):
    ytdl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }

    ffmpeg_opts = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    ytdl = youtube_dl.YoutubeDL(ytdl_opts)

    def __init__(self, message, source, *, data, volume = 0.5):
        super().__init__(source, volume)

        self.requester = message.author
        self.channel = message.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        self.upload_date = f'{data.get("upload_date")[6:8]}.{data.get("upload_date")[4:6]}.{data.get("upload_date")[0:4]}'
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return f'**{self.title}** by **{self.uploader}** *[Duration: {self.duration}]*'

    @classmethod
    async def create_source(cls, message, search: str, *, loop=None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            await message.channel.send(f"Could not find anything that matches the search query `{search}`")

        if 'entries' not in data:
            process_info = data

        else:
            process_info = None
            for entry in data['entries']:
                if entry is not None:
                    process_info = entry
                    break

            if process_info is None:
                await message.channel.send(f"Could not retrieve any data for the search query `{search}`")

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            await message.channel.send(f"Error while trying to fetch the data for the url `{webpage_url}`")

        if 'entries' not in processed_info:
            info = processed_info

        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    await message.channel.send(f"Could not retrieve any matches for the url `{webpage_url}`")

        return cls(message, discord.FFmpegPCMAudio(info['url'], **cls.ffmpeg_opts), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append(f'{days} days')
        if hours > 0:
            duration.append(f'{hours} hours')
        if minutes > 0:
            duration.append(f'{minutes} minutes')
        if seconds > 0:
            duration.append(f'{seconds} seconds')

        return ', '.join(duration)


class Song:
    def __init__(self, state, source):
        self.state = state
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        emb = discord.Embed(title='Now playing:',
                            description=f'```css\n{self.source.title}\n```',
                            color=0xbc25cf
                            )

        emb.add_field(name='Duration:', value=self.source.duration)
        emb.add_field(name='Requested by:', value=self.requester.mention)
        emb.add_field(name='Uploader:', value=f'[{self.source.uploader}]({self.source.uploader_url})')
        emb.add_field(name='Song URL:', value=f'[Click here]({self.source.url})')
        emb.set_thumbnail(url=self.source.thumbnail)

        return emb


class SongQueue(asyncio.Queue):
    def __iter__(self):
        return self._queue.__iter__()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, value: int):
        self._queue.rotate(-value)
        self._queue.pop()
        self._queue.rotate(value - 1)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return list(itertools.islice(self._queue, index.start, index.stop, index.step))
        else:
            return self._queue[index]

    def __len__(self):
        return len(self._queue)


class VoiceState:
    def __init__(self, client, ctx):
        self.current = None
        self.voice = None
        self._volume = 0.5
        self.client = client
        self._ctx = ctx
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.skip_votes = set()
        self.audio_player = client.loop.create_task(self.audio_player_task())

    async def audio_player_task(self):
        while True:
            self.next.clear()

            try:
                async with timeout(300):
                    self.current = await self.songs.get()
            except asyncio.TimeoutError:
                return self.client.looop.create_task(self.stop())

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value

        if self.voice:
            self.voice.source.volume = value

    def is_done(self):
        if self.voice is None or self.current is None:
            return True

        return not self.voice.is_playing() and not self.voice.is_paused()

    def play_next_song(self, error=None):
        fut = asyncio.run_coroutine_threadsafe(self.next.set(), self.client.loop)

        try:
            fut.result()
        except:
            self.current.source.channel.send(error)

    def skip(self):
        self.skip_votes.clear()

        if not self.is_done():
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog, name="Music"):
    """🎶 Music"""
    def __init__(self, client):
        self.client = client
        self.voice_states = {}

    def get_voice_state(self, ctx):
        state = self.voice_states.get(ctx.guild.id)

        if state is None:
            state = VoiceState(self.client, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    @commands.command(name='join', invoke_without_command=True, description="`megu join`")
    async def join_voice(self, ctx):
        """Joins a voice channel."""
        if not ctx.author.voice:
            return await ctx.send("Baka! You aren't in a voice channel")

        if state.voice is not None:
            return await state.voice.move_to(ctx.author.voice.channel)

        state.voice = await ctx.author.voice.channel.connect()
        await ctx.send("Baka! I didn't join because you told me to!")

    @commands.command(name="play", description="`megu play <url>`")
    async def play_song(self, ctx, *, search: str):
        """Plays a given song"""
        if state.voice is None:
            await ctx.invoke(self.join_voice)

        try:
            source = await YTDLSource.create_source(ctx.message, search, loop=self.client.loop)
            print(source)
        except Exception as e:
            await ctx.send(f"A fucky wucky occurred when processing your request: {e}")
        else:
            song = Song(state.voice, source)

            await state.songs.put(song)
            await ctx.send(f"Queued up {str(source)}")

    @commands.command(name='pause', description="`megu pause`")
    @commands.has_permissions(manage_guild=True)
    async def pause_song(self, ctx):
        """Pauses the currently playing song."""

        if not state.is_done():
            state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name="stop", description="`megu stop`")
    async def stop_song(self, ctx):
        """Stops all playing audio and clears queue"""

        state.songs.clear()

        if not state.is_done():
            state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(name="skip", description="`megu skip`")
    async def skip_song(self, ctx):
        """Vote to skip a song. The requester can automatically skip."""

        if state.is_done():
            return await ctx.send("Baka! Nothing is playing right now")

        voter = ctx.message.author
        voice_channel = ctx.message.author.voice.channel
        if voter == state.current.requester:
            await ctx.message.add_reaction('⏭')
            state.skip()

        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            needed_votes = round(len(voice_channel.members) / 2, 1)

            if total_votes >= needed_votes:
                await ctx.message.add_reaction('⏭')
                state.skip()

            else:
                await ctx.send(f"Skip vote added, currently at **{total_votes}/{needed_votes}")

        else:
            await ctx.send('Baka! You have already voted to skip this song.')

    @commands.command(name='resume', description="`megu resume`")
    @commands.has_permissions(manage_guild=True)
    async def resume_song(self, ctx):
        """Resumes a currently paused song."""

        if not state.is_done():
            state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name="volume", description="`megu volume <volume>`")
    async def set_volume(self, ctx, *, volume: int):
        """Sets the music volume"""
        if state.is_done():
            return await ctx.send("Baka! Nothing is playing right now")

        if 0 > volume > 100:
            return await ctx.send("Baka! Volume must be between 0 and 100")

        state.volume = volume / 100

        await ctx.send(f"Volume has been set to {volume}%")

    @commands.command(name='now', aliases=['playing', 'current'], description="`megu now`")
    async def now_playing(self, ctx):
        """Displays the currently playing song."""

        await ctx.send(embed=state.current.create_embed())

    @commands.command(name='queue', description="`megu queue [page]`")
    async def song_queue(self, ctx, *, page: int = 1):
        """Shows the player's queue."""
        if len(state.songs) == 0:
            return await ctx.send("Baka! Nothing in the queue")

        items_per_page = 10
        pages = math.ceil(len(state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for index, song in enumerate(state.songs[start:end], start=start):
            queue += f'`{index + 1}.` [**{song.source.title}**]({song.source.url})\n'

        embed = discord.Embed(color=discord.Color.green(), description=f'**{len(state.songs)} tracks:**\n\n{queue}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command(name="shuffle", description="`megu shuffle`")
    async def shuffle_songs(self, ctx):
        """Shuffles the current queue"""
        if len(state.songs) == 0:
            return await ctx.send("Baka! Nothing in the queue")

        if len(state.songs) == 1:
            return await ctx.send("Baka! There's not enough songs to suffle")

        state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name="remove", description="`megu remove <number>`")
    async def remove_song(self, ctx, index: int):
        """Removes a song from the queue"""
        if len(state.songs) == 0:
            return await ctx.send("Baka! Nothing in the queue")

        state.songs.remove(index)
        await ctx.message.add_reaction('✅')

    @commands.command(name="disconnect", aliases=['leave'], description="`megu disconnect`")
    async def leave_voice(self, ctx):
        """Clears the queue and leaves the voice channel"""

        if state.voice is None:
            return await ctx.send("Baka! I'm not in a voice channel right now")

        await state.stop()

        del self.voice_states[str(ctx.guild.id)]

    @join_voice.before_invoke
    @play_song.before_invoke
    @pause_song.before_invoke
    @stop_song.before_invoke
    @skip_song.before_invoke
    @resume_song.before_invoke
    @set_volume.before_invoke
    @now_playing.before_invoke
    @song_queue.before_invoke
    @shuffle_songs.before_invoke
    @remove_song.before_invoke
    @leave_voice.before_invoke
    async def _before_invoke(self, ctx):
        global state
        state = self.get_voice_state(ctx)


def setup(client):
    client.add_cog(Music(client))
