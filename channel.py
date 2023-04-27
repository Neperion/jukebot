import discord
from typing import Union


# discord.member.VocalGuildChannel not available at runtime
VocalGuildChannel = Union[discord.VoiceChannel, discord.StageChannel]


class Error(discord.ClientException):
    def __init__(self, value: str, failure=True):
        super().__init__(value)
        self.failure = failure


def get_channel(user: Union[discord.User, discord.Member]):
    if not isinstance(user, discord.Member):
        raise discord.errors.InvalidData('received guild only command in DM')
    if user.voice is None or user.voice.channel is None:
        raise Error('You are not connected to a voice channel.')
    return user.voice.channel


def get_voice(guild: discord.Guild):
    if (voice := guild.voice_client) is None:
        return
    if not isinstance(voice, discord.VoiceClient):
        raise discord.errors.InvalidData(
            'voice_client is of type '
            f'{type(voice).__name__} instead of '
            f'{discord.VoiceClient.__name__}'
        )
    if voice.is_connected():
        return voice
    

async def connect(channel: VocalGuildChannel):
    permissions = channel.permissions_for(channel.guild.me)
    if not permissions.connect:
        raise Error('The bot is not allowed to connect to your voice channel.')
    if not permissions.speak:
        raise Error('The bot is not allowed to speak in your voice channel.')
    if (voice := get_voice(channel.guild)) is None:
        return await channel.connect()
    if channel == voice.channel:
        raise Error('Already connected to your voice channel.', False)
    await voice.move_to(channel)
    if (voice := get_voice(channel.guild)) is None:
        raise discord.errors.ConnectionClosed(
            f'connection closed while moving to channel {channel}'
        )
    return voice


async def disconnect(channel: VocalGuildChannel):
    if (voice := get_voice(channel.guild)) is None:
        raise Error('The bot is not connected to a voice channel.', False)
    if channel != voice.channel:
        raise Error('The bot is not connected to **your** voice channel.')
    await voice.disconnect()
