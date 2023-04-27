import discord
import channel


COLORS = {
    'empty': discord.Colour(0x80848e),
    'error': discord.Colour(0xf23f42),
    'warning': discord.Colour(0xffd836),
    'success': discord.Colour(0x00a8fc)
}


def embed(status: str, message: str):
    return discord.Embed(colour=COLORS[status], title=message)


def error_embed(error: channel.Error):
    return embed('error' if error.failure else 'empty', error)


def warning_embed(message: str):
    return embed('warning', message)


def panel():
    return discord.ui(components=(
        discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            custom_id='loop',
            label='Loop'
        ),
        discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            custom_id='pause',
            label='Pause'
        ),
        discord.ui.Button(
            style=discord.ButtonStyle.success,
            custom_id='play',
            label='Play'
        ),
        discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            custom_id='stop',
            label='Stop'
        ),
        discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            custom_id='next',
            label='Next'
        )
    ))
