import os
import error
import music
import dotenv
import channel
import discord
import interactions
from discord.ext import commands
from typing import Optional

dotenv.load_dotenv()
devuser_id = int(os.getenv('DEVID'))
intents = discord.Intents.default()
intents.members = True # necessary for bot.get_user()
bot = commands.Bot('!', intents=intents)
sessions: dict[int, music.Session] = {}
last_play: Optional[discord.Interaction] = None


@bot.event
async def on_ready():
    dev = bot.get_user(devuser_id)
    on_error = error.on_error(dev)
    join.error(on_error)
    leave.error(on_error)
    play.error(on_error)
    await bot.tree.sync()


@bot.tree.command()
@commands.guild_only()
async def join(interaction: discord.Interaction):
    '''Connect the bot to your voice channel.'''
    try:
        member_channel = channel.get_channel(interaction.user)
    except channel.Error as error:
        await interactions.error(interaction.response, error)
        return
    try:
        voice = await channel.connect(member_channel)
    except channel.Error as error:
        await interactions.error(interaction.response, error)
        return
    await interactions.reply(
        interaction.response,
        'Connected to your voice channel.'
    )


@bot.tree.command()
@commands.guild_only()
async def leave(interaction: discord.Interaction):
    '''Disconnect the bot from your voice channel.'''
    try:
        member_channel = channel.get_channel(interaction.user)
    except channel.Error as error:
        await interactions.error(interaction.response, error)
        return
    if (session := sessions.pop(member_channel.guild.id, None)) is not None:
        if (voice := channel.get_voice(member_channel.guild)) is not None:
            session.stop(voice)
        if session.message is not None:
            await session.message.edit(view=None)
    try:
        await channel.disconnect(member_channel)
    except channel.Error as error:
        await interactions.error(interaction.response, error)
        return
    await interactions.reply(
        interaction.response,
        'Disconnected from your voice channel.'
    )


@bot.tree.command()
@commands.guild_only()
async def play(interaction: discord.Interaction, url: str, skip: bool = False):
    '''Play music from a given URL.'''
    try:
        member_channel = channel.get_channel(interaction.user)
    except channel.Error as error:
        await interactions.error(interaction.response, error)
        return
    await interaction.response.defer()
    song_info = music.download(url)
    if song_info is None:
        await interactions.error(
            interaction.followup,
            channel.Error('Invalid URL.')
        )
        return
    if (voice := channel.get_voice(interaction.guild)) is None:
        try:
            voice = await channel.connect(member_channel)
        except channel.Error as error:
            await interactions.error(interaction.followup, error)
            return
    session = sessions.setdefault(interaction.guild_id, music.Session())
    session.play(voice, song_info, skip)
    if session.song_info == song_info:
        content = f'Started playing: {song_info["webpage_url"]}'
    else:
        content = f'Added to queue: {song_info["webpage_url"]}'
    await interaction.followup.send(
        content,
        view=View(voice, session),
        silent=True
    )
    if session.message is not None:
        await session.message.edit(view=None)
    session.message = await interaction.original_response()


class View(discord.ui.View):
    def __init__(self, voice: discord.VoiceClient, session: music.Session):
        super().__init__()
        if session.looping:
            self.loop.style = discord.ButtonStyle.primary
        if voice.is_paused():
            self.pause.disabled = True
            self.resume.disabled = False
        if not voice.is_playing():
            self.loop.disabled = True
            self.pause.disabled = True
            self.resume.disabled = True
            self.stop.disabled = True
            self.skip.disabled = True
    
    async def on_error(
        self,
        interaction: discord.Interaction,
        exception: Exception,
        item: discord.ui.Item
    ):
        dev = bot.get_user(devuser_id)
        await error.on_error(dev, item)(interaction, exception)

    @discord.ui.button(emoji='🔁')
    async def loop(
        self,
        interaction: discord.Interaction,
        button: discord.Button
    ):
        if interaction.guild_id is None:
            raise discord.errors.InvalidData(
                f'button {button.custom_id} pressed in DM'
            )
        if (session := sessions.get(interaction.guild_id, None)) is None:
            await interaction.response.edit_message(view=None)
            return
        if session.looping:
            session.looping = False
            button.style = discord.ButtonStyle.secondary
        else:
            session.looping = True
            button.style = discord.ButtonStyle.primary
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label='⏸')
    async def pause(
        self,
        interaction: discord.Interaction,
        button: discord.Button
    ):
        if interaction.guild is None:
            raise discord.errors.InvalidData(
                f'button {button.custom_id} pressed in DM'
            )
        if (voice := channel.get_voice(interaction.guild)) is None:
            await interaction.response.edit_message(view=None)
            return
        if not voice.is_paused():
            voice.pause()
        button.disabled = True
        self.resume.disabled = False
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(
        label='⏵',
        disabled=True,
        style=discord.ButtonStyle.success
    )
    async def resume(
        self,
        interaction: discord.Interaction,
        button: discord.Button
    ):
        if interaction.guild is None:
            raise discord.errors.InvalidData(
                f'button {button.custom_id} pressed in DM'
            )
        if (voice := channel.get_voice(interaction.guild)) is None:
            await interaction.response.edit_message(view=None)
            return
        if voice.is_paused():
            voice.resume()
        button.disabled = True
        self.pause.disabled = False
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label='⏹')
    async def stop(
        self,
        interaction: discord.Interaction,
        button: discord.Button
    ):
        await interaction.response.edit_message(view=None)
        if interaction.guild is None:
            raise discord.errors.InvalidData(
                f'button {button.custom_id} pressed in DM'
            )
        if (voice := channel.get_voice(interaction.guild)) is None:
            return
        if (session := sessions.get(interaction.guild.id)) is None:
            if voice.is_playing():
                voice.stop()
            return
        session.queue.clear()
        if voice.is_playing():
            session.stop(voice)
    
    @discord.ui.button(label='⏭')
    async def skip(
        self,
        interaction: discord.Interaction,
        button: discord.Button
    ):
        if interaction.guild is None:
            raise discord.errors.InvalidData(
                f'button {button.custom_id} pressed in DM'
            )
        if (voice := channel.get_voice(interaction.guild)) is None:
            await interaction.response.edit_message(view=None)
            return
        if (session := sessions.get(interaction.guild.id)) is None:
            await interaction.response.edit_message(view=None)
            return
        session.skip(voice)
        if not voice.is_playing():
            await interaction.response.edit_message(view=None)
            return
        await interaction.response.edit_message(view=self)
