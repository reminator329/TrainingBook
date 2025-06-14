from typing import Union

import discord
from discord import app_commands

import command


@app_commands.describe(channel='The channel to get info of')
async def execute(interaction: discord.Interaction, channel: Union[discord.VoiceChannel, discord.TextChannel]):

    embed = discord.Embed(title='Channel Info')
    embed.add_field(name='Name', value=channel.name, inline=True)
    embed.add_field(name='ID', value=channel.id, inline=True)
    embed.add_field(
        name='Type',
        value='Voice' if isinstance(channel, discord.VoiceChannel) else 'Text',
        inline=True,
    )

    embed.set_footer(text='Created').timestamp = channel.created_at

    response = interaction.response
    assert isinstance(response, discord.InteractionResponse)
    await response.send_message(embed=embed)


class CommandChannelInfo(command.Command):

    def __init__(self):
        super().__init__("channel_info", "Shows basic channel info for a text or voice channel.", execute)
