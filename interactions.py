import discord
import channel
import component
from typing import Union


async def send(
    response: Union[discord.InteractionResponse, discord.Webhook],
    embed: discord.Embed,
    ephemeral=False
):
    if isinstance(response, discord.Webhook):
        await response.send(embed=embed, silent=True, ephemeral=ephemeral)
        return
    await response.send_message(embed=embed, silent=True, ephemeral=ephemeral)


async def reply(
    response: Union[discord.InteractionResponse, discord.Webhook],
    message: str
):
    await send(response, component.embed('success', message))


async def error(
    response: Union[discord.InteractionResponse, discord.Webhook],
    error: channel.Error
):
    await send(response, component.error_embed(error), True)


async def warn(
    response: Union[discord.InteractionResponse, discord.Webhook],
    message: str
):
    await send(response, component.warning_embed(message), True)
