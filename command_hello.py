import discord

import command


async def execute(interaction: discord.Interaction):
    response = interaction.response
    assert isinstance(response, discord.InteractionResponse)

    await response.send_message(f'Hi, {interaction.user.mention}')



class CommandHello(command.Command):

    def __init__(self):
        super().__init__("hello", "Says hello !", execute)
