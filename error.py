import discord
import logging
import traceback
import component
import interactions
from discord.ext import commands
from typing import Optional


def on_error(
    dev: Optional[discord.User] = None,
    item: Optional[discord.ui.Item] = None
):
    logger = logging.getLogger(__name__)
    title = 'An unexpected error occured {} handling your interaction.'
    if dev is None:
        description = None
    else:
        description = f'Please contact my developper {dev.mention}.'
    button: Optional[discord.ui.Button] = None
    if item is not None and isinstance(item, discord.ui.Button):
        button = item
    async def on_error(
        interaction: discord.Interaction,
        error: commands.CommandInvokeError
    ):
        exc = traceback.format_exc()
        logger.error(exc)
        if dev is not None:
            content = interaction.user.mention
            if interaction.command is not None:
                content += f' used `{interaction.command.name}`'
            elif button is not None:
                if button.label is not None:
                    content += f' used {button.label}'
                elif button.emoji is not None:
                    content += f' used {button.emoji}'
            if interaction.channel is not None:
                content += f' in {interaction.channel.mention}'
            await dev.send(f'{content}```py\n{exc}```')
        if interaction.is_expired():
            return
        embed = discord.Embed(description=description)
        if interaction.response.is_done():
            response = interaction.followup
            embed.title = title.format('after')
            embed.colour = component.COLORS['warning']
        else:
            response = interaction.response
            embed.title = title.format('while')
            embed.colour = component.COLORS['error']
        await interactions.send(response, embed, True)
    return on_error
