import discord
from discord import app_commands

import command


@app_commands.describe(
    first_value='The first value you want to add something to',
    second_value='The value you want to add to the first value',
)
async def execute(interaction: discord.Interaction, first_value: app_commands.Range[int, 0, 100], second_value: app_commands.Range[int, 0, None]):
    response = interaction.response
    assert isinstance(response, discord.InteractionResponse)

    await response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')


class CommandAdd(command.Command):

    def __init__(self):
        super().__init__("add", "Adds two numbers together.", execute)